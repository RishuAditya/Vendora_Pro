# ---------------------------------------------------------
# 2.0 TOPIC: ENTERPRISE FINANCIAL AUDIT & ORDER SYSTEM
# ---------------------------------------------------------
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from backend.extensions import db
from backend.models.cart_model import Cart
from backend.models.order_model import Order, OrderItem, Coupon, UsedCoupon 
from backend.models.transaction_model import Transaction 
from backend.models.user_model import User, SavedCard, Notification 
from backend.models.seller_model import Seller
from datetime import datetime, timedelta

order_bp = Blueprint("order", __name__)

# 2.1 CHECKOUT SELECTION PAGE (With Coupon & Wallet Context)
@order_bp.route("/checkout-selection")
@login_required
def checkout_page():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash("Bhai, cart khali hai!", "warning")
        return redirect(url_for('index'))
    
    base_total = sum(item.product.price * item.quantity for item in cart_items if item.product)
    
    # Calculate Coupon Discount
    discount = 0.0
    applied_code = session.get('applied_coupon')
    if applied_code:
        cp = Coupon.query.filter_by(code=applied_code, is_active=True).first()
        if cp and base_total >= cp.min_purchase:
            discount = (base_total * cp.discount_value / 100) if cp.is_percentage else cp.discount_value
        else:
            session.pop('applied_coupon', None)

    final_total = base_total - discount
    user_cards = SavedCard.query.filter_by(user_id=current_user.id).all()
    all_offers = Coupon.query.filter_by(is_active=True).all()
    
    return render_template("checkout.html", total=base_total, discount=discount, 
                           final_total=final_total, saved_cards=user_cards, offers=all_offers)

# 2.2 APPLY COUPON ROUTE (With Range & Usage Tracking)
@order_bp.route("/apply-coupon", methods=["POST"])
@login_required
def apply_coupon():
    code = request.form.get("coupon_code").upper().strip()
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    total = sum(i.product.price * i.quantity for i in cart_items if i.product)
    
    cp = Coupon.query.filter_by(code=code, is_active=True).first()
    if cp:
        if UsedCoupon.query.filter_by(user_id=current_user.id, coupon_id=cp.id).first():
            flash("You have already used this coupon once! 🚫", "warning")
        elif total < cp.min_purchase:
            flash(f"Shop for ₹{cp.min_purchase - total} more to use this code!", "info")
        elif cp.max_purchase and total > cp.max_purchase:
            flash(f"Order value too high for this coupon (Max: ₹{cp.max_purchase})", "warning")
        else:
            session['applied_coupon'] = code
            flash(f"Coupon '{code}' Applied! 🎉", "success")
    else:
        flash("Invalid Coupon Code! ❌", "danger")
    return redirect(url_for('order.checkout_page'))

# 2.3 PROCESS CHECKOUT (FINAL HYBRID + AUDIT + SHIPPING LOGIC)
@order_bp.route("/process-checkout", methods=["POST"])
@login_required
def process_checkout():
    pay_mode = request.form.get("pay_mode")
    s_name = request.form.get("shipping_name")
    s_phone = request.form.get("shipping_phone")
    s_address = request.form.get("shipping_address")
    
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    if not cart_items: return redirect(url_for('index'))

    # Re-calculate Final Amounts
    base_total = sum(item.product.price * item.quantity for item in cart_items if item.product)
    discount = 0.0
    applied_cp_obj = None
    if session.get('applied_coupon'):
        applied_cp_obj = Coupon.query.filter_by(code=session['applied_coupon']).first()
        if applied_cp_obj:
            discount = (base_total * applied_cp_obj.discount_value / 100) if applied_cp_obj.is_percentage else applied_cp_obj.discount_value
    
    final_amount = base_total - discount
    wallet_paid, card_paid = 0.0, 0.0

    # Payment Validation Logic
    if pay_mode == 'wallet':
        if current_user.wallet_balance < final_amount:
            flash("Insufficient wallet balance!", "danger")
            return redirect(url_for('order.checkout_page'))
        wallet_paid = final_amount
        current_user.wallet_balance -= final_amount
    elif pay_mode == 'hybrid':
        wallet_paid = current_user.wallet_balance
        card_paid = final_amount - wallet_paid
        current_user.wallet_balance = 0
    else:
        card_paid = final_amount

    # Card Details Saving Logic
    card_id = request.form.get("saved_card_id")
    last_four = "0000"
    if pay_mode in ['card', 'hybrid']:
        if card_id and card_id != "new":
            card = SavedCard.query.get(card_id)
            last_four = card.card_last_four
        else:
            card_no = request.form.get("card_number")
            last_four = card_no[-4:] if card_no else "0000"
            if request.form.get("save_card") == "on":
                db.session.add(SavedCard(user_id=current_user.id, card_holder_name=s_name, card_last_four=last_four, card_type="Visa", expiry_date=request.form.get("expiry")))

    # Step 1: Create Master Order Header
    inv_no = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}-{current_user.id}"
    new_order = Order(
        user_id=current_user.id, total_amount=final_amount,
        wallet_amount_paid=wallet_paid, card_amount_paid=card_paid,
        payment_mode=pay_mode.upper(), payment_status="Paid" if pay_mode != 'cod' else "COD",
        invoice_no=inv_no, shipping_address=s_address, # Update: using 'shipping_address' column
        customer_name_snapshot=current_user.name, customer_email_snapshot=current_user.email,
        created_at=datetime.now() # IST Fix
    )
    db.session.add(new_order)
    db.session.flush()

    seller_info_list = []

    # Step 2: Process Items & ESCROW LOCKING
    for item in cart_items:
        order_item = OrderItem(
            order_id=new_order.id, product_id=item.product_id, seller_id=item.product.seller_id,
            quantity=item.quantity, price_at_time=item.product.price, variant=item.variant, status="Pending"
        )
        item.product.stock -= item.quantity
        db.session.add(order_item)

        # Money to Seller's LOCKED balance
        seller_profile = Seller.query.get(item.product.seller_id)
        seller_user = User.query.get(seller_profile.user_id)
        seller_info_list.append(seller_profile.company_name)
        
        item_total = item.product.price * item.quantity
        seller_user.locked_balance += item_total # Hold money in Escrow

        # [AUDIT]: Seller detailed entry
        db.session.add(Transaction(
            user_id=seller_user.id, amount=item_total, type='Credit',
            purpose=f"SALE: From {current_user.name} for {item.product.name} (Order #{new_order.id})",
            created_at=datetime.now()
        ))

    # [AUDIT]: Customer detailed entry
    shops_str = ", ".join(list(set(seller_info_list)))
    customer_purpose = f"PURCHASE: To {shops_str} via {pay_mode.upper()} (Order #{new_order.id})"
    if pay_mode in ['card', 'hybrid']: customer_purpose += f" (Card ****{last_four})"
    
    db.session.add(Transaction(user_id=current_user.id, amount=final_amount, type='Debit',
                               purpose=customer_purpose, created_at=datetime.now()))

    # Cleanup
    if applied_cp_obj: db.session.add(UsedCoupon(user_id=current_user.id, coupon_id=applied_cp_obj.id))
    session.pop('applied_coupon', None)
    Cart.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    
    flash(f"Order #{new_order.id} placed! Passbooks updated. 🛒🎉", "success")
    return redirect(url_for('order.my_orders'))

# 2.4 DELIVERY CONFIRMATION (RELEASING FUNDS)
@order_bp.route("/confirm-receipt/<int:item_id>")
@login_required
def confirm_receipt(item_id):
    item = OrderItem.query.get_or_404(item_id)
    if item.order.user_id != current_user.id or item.status != 'Delivered': return redirect(url_for('order.my_orders'))
    
    amount = item.price_at_time * item.quantity
    seller_user = User.query.join(Seller).filter(Seller.id == item.seller_id).first()
    
    if seller_user.locked_balance >= amount:
        seller_user.locked_balance -= amount
        seller_user.wallet_balance += amount
        item.status = 'Completed'
        db.session.add(Transaction(user_id=seller_user.id, amount=amount, type='Credit', 
                                   purpose=f'PAYMENT RELEASED: Order #{item.order_id}', created_at=datetime.now()))
        db.session.commit()
        flash("Payment released to seller. Thank you! ✅", "success")
    return redirect(url_for('order.my_orders'))

# 2.5 CANCEL & REFUND
@order_bp.route("/cancel-order/<int:item_id>")
@login_required
def cancel_order(item_id):
    item = OrderItem.query.get_or_404(item_id)
    if current_user.id != item.order.user_id: return "Denied", 403
    if item.status in ['Delivered', 'Completed']:
        flash("Cannot cancel after delivery!", "warning")
        return redirect(url_for('order.my_orders'))

    refund = item.price_at_time * item.quantity
    current_user.wallet_balance += refund
    seller_user = User.query.join(Seller).filter(Seller.id == item.seller_id).first()
    if seller_user.locked_balance >= refund: seller_user.locked_balance -= refund

    item.status = 'Cancelled'
    item.product.stock += item.quantity
    db.session.add(Transaction(user_id=current_user.id, amount=refund, type='Credit', 
                               purpose=f'REFUND: Order #{item.order_id} cancelled', created_at=datetime.now()))
    db.session.commit()
    flash("Cancelled and Refunded. 💰", "info")
    return redirect(url_for('order.my_orders'))

# 2.6 HELPERS (My Orders, Invoice, Buy Now, Statement)
@order_bp.route("/my-orders")
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.id.desc()).all()
    return render_template("my_orders.html", orders=orders)

@order_bp.route("/order/invoice/<int:order_id>")
@login_required
def view_invoice(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template("invoice.html", order=order)

@order_bp.route("/generate-statement")
@login_required
def generate_statement():
    days = request.args.get('days', 'all')
    query = Transaction.query.filter_by(user_id=current_user.id)
    if days == '7': query = query.filter(Transaction.created_at >= datetime.now() - timedelta(days=7))
    transactions = query.order_by(Transaction.created_at.desc()).all()
    return render_template("statement_report.html", transactions=transactions, filter_days=days, report_date=datetime.now().strftime('%d %b, %Y'))

@order_bp.route("/buy-now/<int:product_id>")
@login_required
def buy_now(product_id):
    Cart.query.filter_by(user_id=current_user.id).delete()
    new_item = Cart(user_id=current_user.id, product_id=product_id, quantity=1, variant="Standard Edition")
    db.session.add(new_item)
    db.session.commit()
    return redirect(url_for('order.checkout_page'))