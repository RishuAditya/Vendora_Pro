# ---------------------------------------------------------
# 2.0 TOPIC: SELLER BUSINESS OPERATIONS & FINANCIAL INTELLIGENCE
# ---------------------------------------------------------
import json
import os
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from backend.extensions import db
from backend.models.order_model import Order, OrderItem
from backend.models.seller_model import Seller
from backend.models.transaction_model import Transaction
from backend.models.user_model import User, Notification, SavedCard
from datetime import datetime, timedelta

seller_bp = Blueprint("seller", __name__, url_prefix="/seller")

# 2.1 SELLER DASHBOARD: STATS, CHARTS, AND AUTO-PAYOUT LOGIC
@seller_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != "seller": 
        return "Access Denied", 403
    
    seller = Seller.query.filter_by(user_id=current_user.id).first()
    if not seller: 
        return redirect(url_for('index'))

    # ✅ AUTO-PAYOUT ENGINE: 7-Day Return Window Check
    # Isse wo negative balance wala bug hamesha ke liye khatam ho jayega
    overdue_items = OrderItem.query.filter_by(seller_id=seller.id, status='Delivered').all()
    for item in overdue_items:
        if item.return_deadline and datetime.now() > item.return_deadline:
            amount = item.price_at_time * item.quantity
            # Sakt Math Guard: Available Balance tabhi badhega agar Locked mein paisa hai
            if current_user.locked_balance >= amount:
                current_user.locked_balance -= amount
                current_user.wallet_balance += amount
                item.status = 'Completed' # Final Stage
                
                # Notification for Seller
                db.session.add(Notification(receiver_id=current_user.id, 
                    message=f"System Auto-Payout: ₹{amount} released for Order #{item.order_id}."))
    db.session.commit()

    # Dashboard Statistics (Real-time IST)
    total_sales_val = db.session.query(db.func.sum(OrderItem.price_at_time * OrderItem.quantity))\
        .filter(OrderItem.seller_id == seller.id, OrderItem.status == 'Completed').scalar() or 0
    
    pending_orders_count = OrderItem.query.filter_by(seller_id=seller.id, status='Pending').count()
    
    # [LOGIC]: Real-Time 7 Days Analytics
    labels, values = [], []
    for i in range(6, -1, -1):
        d = (datetime.now() - timedelta(days=i)).date()
        labels.append(d.strftime('%d %b'))
        day_total = (db.session.query(db.func.sum(OrderItem.price_at_time * OrderItem.quantity))
                     .join(Order).filter(OrderItem.seller_id == seller.id, OrderItem.status == 'Completed')
                     .filter(db.func.date(Order.created_at) == d).scalar()) or 0
        values.append(float(day_total))

    # Passbook Data (Limit hata di taaki poora dikhe)
    tx_history = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.created_at.desc()).all()

    return render_template("seller_dashboard.html", 
                           total_sales=total_sales_val, 
                           pending_orders=pending_orders_count, 
                           seller=seller, 
                           transactions=tx_history,
                           current_score=seller.seller_score or 100,
                           l_js=json.dumps(labels), 
                           v_js=json.dumps(values),
                           today_date=datetime.now().strftime('%d %B, %Y'))

# 2.2 SALES PORTAL: MANAGE CUSTOMER ORDERS
@seller_bp.route("/orders")
@login_required
def manage_orders():
    if current_user.role != "seller": return "Denied", 403
    seller = Seller.query.filter_by(user_id=current_user.id).first()
    orders = OrderItem.query.filter_by(seller_id=seller.id).order_by(OrderItem.id.desc()).all()
    return render_template("seller_orders.html", orders=orders)

# 2.3 STATUS UPDATE LOGIC: (INCLUDING OUT FOR DELIVERY)
@seller_bp.route("/update-status/<int:item_id>/<string:new_status>")
@login_required
def update_order_status(item_id, new_status):
    item = OrderItem.query.get_or_404(item_id)
    seller = Seller.query.filter_by(user_id=current_user.id).first()
    
    if item.seller_id == seller.id:
        item.status = new_status
        
        # [LOGIC]: Jab status 'Delivered' ho, tab 7-day window shuru karo
        if new_status == 'Delivered':
            item.delivered_at = datetime.now()
            item.return_deadline = datetime.now() + timedelta(days=7)
            # Notify Customer
            db.session.add(Notification(receiver_id=item.order.user_id, 
                message=f"Your Order #{item.order_id} is Delivered! 7-day satisfaction window starts now."))

        db.session.commit()
        flash(f"Success: Order #{item.order_id} is now {new_status}! 🚀", "success")
    
    return redirect(url_for('seller.manage_orders'))

# 2.4 WITHDRAWAL LOGIC: (FIXED WITH CARD DETAILS LOGGING)
@seller_bp.route("/withdraw", methods=["POST"])
@login_required
def withdraw_money():
    amount_str = request.form.get("amount")
    card_id = request.form.get("saved_card_id")
    
    if not amount_str: 
        return redirect(url_for('seller.dashboard'))
        
    amount = float(amount_str)

    if 0 < amount <= current_user.wallet_balance:
        # ✅ NAYA LOGIC: Card ke last 4 digits nikalna Passbook ke liye
        last_four = "0000"
        if card_id and card_id != "new":
            card = SavedCard.query.get(card_id)
            last_four = card.card_last_four
        else:
            card_no = request.form.get("card_number")
            last_four = card_no[-4:] if card_no else "0000"

        # Deduct from Wallet
        current_user.wallet_balance -= amount
        
        # [AUDIT]: Detailed record with card number
        purpose_str = f"Transfer to Bank Card (****{last_four})"
        db.session.add(Transaction(
            user_id=current_user.id, 
            amount=amount, 
            type='Debit', 
            purpose=purpose_str, 
            created_at=datetime.now()
        ))
        
        db.session.commit()
        flash(f"₹{amount} successfully sent to card ****{last_four}! 💳", "success")
    else:
        flash("Insufficient balance or invalid amount!", "danger")
        
    return redirect(url_for('seller.dashboard'))

# 2.5 RE-APPLY LOGIC
@seller_bp.route("/reapply")
@login_required
def reapply_seller():
    seller = Seller.query.filter_by(user_id=current_user.id).first()
    if seller and seller.status == 'rejected':
        seller.status = 'pending'
        db.session.commit()
        flash("Resubmitted! Wait for Admin approval. ⏳", "info")
    return redirect(url_for('seller.dashboard'))