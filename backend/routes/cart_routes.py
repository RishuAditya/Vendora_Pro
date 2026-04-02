from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from backend.extensions import db
from backend.models.product_model import Product
from backend.models.cart_model import Cart

cart_bp = Blueprint("cart", __name__)

@cart_bp.route("/add-to-cart/<int:product_id>", methods=["GET", "POST"])
@login_required
def add_to_cart(product_id):
    product = Product.query.get(product_id)
    if not product:
        flash("Product not found!", "warning")
        return redirect(url_for('index'))

    # Agar form se data aaya toh wo uthao, warna default
    if request.method == "POST":
        variant = request.form.get("selected_variant", "Standard")
        action = request.form.get("action", "cart")
    else:
        variant = "Standard"
        action = "cart"

    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id, variant=variant).first()
    
    if cart_item:
        cart_item.quantity += 1
    else:
        new_item = Cart(user_id=current_user.id, product_id=product_id, variant=variant)
        db.session.add(new_item)
    
    db.session.commit()

    if action == "buy":
        return redirect(url_for('order.checkout_page'))
        
    flash(f"{product.name} added to cart! 🛒", "success")
    return redirect(url_for('product.product_detail', product_id=product_id))

@cart_bp.route("/cart")
@login_required
def view_cart():
    items = Cart.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in items if item.product)
    return render_template("cart.html", items=items, total=total)

@cart_bp.route("/remove-from-cart/<int:cart_id>")
@login_required
def remove_cart(cart_id):
    item = Cart.query.get_or_404(cart_id)
    if item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('cart.view_cart'))