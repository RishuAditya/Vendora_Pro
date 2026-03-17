from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from backend.extensions import db
from backend.models.order_model import OrderItem
from backend.models.seller_model import Seller

seller_bp = Blueprint("seller", __name__, url_prefix="/seller")

@seller_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != "seller":
        return "Access Denied", 403
    
    seller = Seller.query.filter_by(user_id=current_user.id).first()
    # Analytics for dashboard
    total_sales = db.session.query(db.func.sum(OrderItem.price_at_time * OrderItem.quantity)).filter_by(seller_id=seller.id, status='Delivered').scalar() or 0
    pending_orders = OrderItem.query.filter_by(seller_id=seller.id, status='Pending').count()
    
    return render_template("seller_dashboard.html", total_sales=total_sales, pending_orders=pending_orders, seller=seller)

@seller_bp.route("/orders")
@login_required
def manage_orders():
    if current_user.role != "seller":
        return "Access Denied", 403
    
    seller = Seller.query.filter_by(user_id=current_user.id).first()
    # Sirf is Seller ke products wale orders uthao
    orders_received = OrderItem.query.filter_by(seller_id=seller.id).order_by(OrderItem.id.desc()).all()
    
    return render_template("seller_orders.html", orders=orders_received)

@seller_bp.route("/update-status/<int:item_id>/<string:new_status>")
@login_required
def update_order_status(item_id, new_status):
    item = OrderItem.query.get_or_404(item_id)
    seller = Seller.query.filter_by(user_id=current_user.id).first()
    
    # Check if this order belongs to this seller
    if item.seller_id == seller.id:
        item.status = new_status
        db.session.commit()
        flash(f"Order status updated to {new_status}!", "success")
    
    return redirect(url_for('seller.manage_orders'))