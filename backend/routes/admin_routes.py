from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from backend.extensions import db
from backend.models.user_model import User
from backend.models.seller_model import Seller
from backend.models.product_model import Product
from backend.models.order_model import Order

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != "admin":
        return "Access Denied", 403
    
    stats = {
        'total_users': User.query.count(),
        'total_sellers': Seller.query.count(),
        'total_products': Product.query.count(),
        'total_orders': Order.query.count(),
        'pending_approvals': Seller.query.filter_by(status='pending').count()
    }
    return render_template("admin_dashboard.html", stats=stats)

# --- USER MANAGEMENT ---
@admin_bp.route("/manage-users")
@login_required
def manage_users():
    if current_user.role != "admin": return "Access Denied", 403
    users = User.query.all()
    return render_template("manage_users.html", users=users)

@admin_bp.route("/delete-user/<int:user_id>")
@login_required
def delete_user(user_id):
    if current_user.role != "admin": return "Access Denied", 403
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash("Cannot delete an Admin!", "danger")
    else:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully.", "info")
    return redirect(url_for('admin.manage_users'))

# --- SELLER MANAGEMENT ---
@admin_bp.route("/manage-sellers")
@login_required
def manage_sellers():
    if current_user.role != "admin": return "Access Denied", 403
    all_sellers = Seller.query.all()
    return render_template("manage_sellers.html", sellers=all_sellers)

@admin_bp.route("/verify-seller/<int:seller_id>/<string:action>")
@login_required
def verify_seller(seller_id, action):
    if current_user.role != "admin": return "Access Denied", 403
    seller = Seller.query.get_or_404(seller_id)
    seller.status = 'approved' if action == 'approve' else 'rejected'
    db.session.commit()
    flash(f"Seller status updated to {seller.status}!", "success")
    return redirect(url_for('admin.manage_sellers'))

# --- PRODUCT MANAGEMENT (Admin View) ---
@admin_bp.route("/manage-products")
@login_required
def manage_products():
    if current_user.role != "admin": return "Access Denied", 403
    products = Product.query.all()
    return render_template("manage_products_admin.html", products=products)