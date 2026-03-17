from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from backend.extensions import db
from backend.models.cart_model import Cart
from backend.models.order_model import Order, OrderItem
from backend.models.product_model import Product

order_bp = Blueprint("order", __name__)

@order_bp.route("/checkout")
@login_required
def checkout():
    # 1. Cart se items uthao
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash("Your cart is empty!", "warning")
        return redirect(url_for('index'))

    # 2. Total calculation
    total_amount = sum(item.product.price * item.quantity for item in cart_items)

    # 3. Check Wallet Balance
    if current_user.wallet_balance < total_amount:
        flash(f"Insufficient Balance! You need ₹{total_amount}. Please add money to your wallet.", "danger")
        return redirect(url_for('customer.dashboard'))

    # 4. Create Main Order
    new_order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        payment_method="Wallet",
        payment_status="Paid"
    )
    db.session.add(new_order)
    db.session.flush() # Order ID generate karne ke liye bina commit kiye

    # 5. Items ko OrderItem mein shift karein aur Stock kam karein
    for item in cart_items:
        if item.product.stock < item.quantity:
            flash(f"Sorry, {item.product.name} is out of stock!", "danger")
            return redirect(url_for('cart.view_cart'))
        
        # Order Item record
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            seller_id=item.product.seller_id,
            quantity=item.quantity,
            price_at_time=item.product.price,
            status="Pending"
        )
        # Stock update
        item.product.stock -= item.quantity
        db.session.add(order_item)

    # 6. User Wallet balance deduct karein
    current_user.wallet_balance -= total_amount

    # 7. Cart khali karein
    Cart.query.filter_by(user_id=current_user.id).delete()

    db.session.commit()
    flash("Order Placed Successfully! 🎉 Money deducted from wallet.", "success")
    return redirect(url_for('order.my_orders'))

@order_bp.route("/my-orders")
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template("my_orders.html", orders=orders)