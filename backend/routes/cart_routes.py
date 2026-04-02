# ---------------------------------------------------------
# TOPIC: SHOPPING CART MANAGEMENT
# ---------------------------------------------------------
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from backend.extensions import db
from backend.models.product_model import Product
from backend.models.cart_model import Cart

cart_bp = Blueprint("cart", __name__)

# 1.1 ADD TO CART / BUY NOW LOGIC
@cart_bp.route("/add-to-cart/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):
    # Form se variant aur action (cart/buy) uthao
    variant = request.form.get("selected_variant", "Standard")
    action = request.form.get("action", "cart") # Button ki value 'buy' ya 'cart'

    # Check if same product with SAME variant already in cart
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id, variant=variant).first()
    
    if cart_item:
        cart_item.quantity += 1
    else:
        new_item = Cart(user_id=current_user.id, product_id=product_id, variant=variant)
        db.session.add(new_item)
    
    db.session.commit()

    # ✅ Redirect to Smart Checkout Selection
    if action == "buy":
        return redirect(url_for('order.checkout_page'))
        
    flash(f"Item ({variant}) added to cart! 🛒", "success")
    return redirect(url_for('product.product_detail', product_id=product_id))

# 1.2 VIEW CART
@cart_bp.route("/cart")
@login_required
def view_cart():
    items = Cart.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in items if item.product)
    return render_template("cart.html", items=items, total=total)

# 1.3 REMOVE FROM CART
@cart_bp.route("/remove-from-cart/<int:cart_id>")
@login_required
def remove_cart(cart_id):
    item = Cart.query.get_or_404(cart_id)
    if item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
        flash("Item removed from cart.", "info")
    return redirect(url_for('cart.view_cart'))