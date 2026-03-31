# ---------------------------------------------------------
# TOPIC: ADMIN COMMAND TOWER & GOVERNANCE
# ---------------------------------------------------------
import os
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from backend.extensions import db
from backend.models.user_model import User
from backend.models.seller_model import Seller
from backend.models.product_model import Product
from backend.models.transaction_model import Transaction

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# 1.1 ADMIN DASHBOARD (CENTRAL STATS)
@admin_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != "admin": return "Access Denied", 403
    
    # ✅ Sabhi queries function ke andar honi chahiye (Context Fix)
    total_gmv = db.session.query(db.func.sum(Transaction.amount)).filter_by(type='Credit').scalar() or 0
    locked_funds = db.session.query(db.func.sum(User.locked_balance)).scalar() or 0
    
    stats = {
        'total_customers': User.query.filter_by(role='customer').count(),
        'total_sellers': Seller.query.count(),
        'total_products': Product.query.count(),
        'pending_sellers': Seller.query.filter_by(status='pending').count(),
        'total_revenue': total_gmv,
        'locked_funds': locked_funds
    }
    return render_template("admin_dashboard.html", stats=stats)

# 1.2 CUSTOMER DIRECTORY (VIEW ONLY)
@admin_bp.route("/customer-list")
@login_required
def customer_list():
    if current_user.role != "admin": return "Denied", 403
    customers = User.query.filter_by(role='customer').all()
    return render_template("admin_customer_list.html", customers=customers)

# 1.3 SELLER DIRECTORY (APPROVALS)
@admin_bp.route("/seller-directory")
@login_required
def seller_directory():
    if current_user.role != "admin": return "Denied", 403
    status_filter = request.args.get('status')
    if status_filter:
        sellers = Seller.query.filter_by(status=status_filter).all()
    else:
        sellers = Seller.query.all()
    return render_template("admin_seller_directory.html", sellers=sellers, current_status=status_filter)

# 1.4 USER ACCESS CONTROL (DELETE/BAN)
@admin_bp.route("/user-management")
@login_required
def user_management():
    if current_user.role != "admin": return "Denied", 403
    users = User.query.filter(User.role != 'admin').all()
    return render_template("admin_user_management.html", users=users)

@admin_bp.route("/delete-user-action/<int:user_id>")
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role != 'admin':
        db.session.delete(user)
        db.session.commit()
        flash("Account deleted successfully.", "danger")
    return redirect(url_for('admin.user_management'))

# 1.5 PRODUCT MODERATION
@admin_bp.route("/product-moderation")
@login_required
def product_moderation():
    if current_user.role != "admin": return "Denied", 403
    products = Product.query.order_by(Product.id.desc()).all()
    return render_template("admin_product_moderation.html", products=products)

@admin_bp.route("/delete-product-admin/<int:product_id>")
@login_required
def delete_product_admin(product_id):
    product = Product.query.get_or_404(product_id)
    if product.image:
        try:
            os.remove(os.path.join('frontend/static/images/products', product.image))
        except: pass
    db.session.delete(product)
    db.session.commit()
    flash("Product removed.", "info")
    return redirect(url_for('admin.product_moderation'))

# 1.6 FINANCIAL AUDIT LEDGER
@admin_bp.route("/transactions")
@login_required
def view_transactions():
    if current_user.role != "admin": return "Denied", 403
    all_tx = Transaction.query.order_by(Transaction.created_at.desc()).all()
    return render_template("admin_transactions.html", transactions=all_tx)

# 1.7 SELLER VERIFICATION LOGIC
@admin_bp.route("/verify-action/<int:seller_id>/<string:action>")
@login_required
def verify_seller(seller_id, action):
    seller = Seller.query.get_or_404(seller_id)
    seller.status = 'approved' if action == 'approve' else 'rejected'
    db.session.commit()
    return redirect(url_for('admin.seller_directory', status='pending'))