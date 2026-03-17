from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from backend.extensions import db
from backend.models.product_model import Product, Category
from backend.models.seller_model import Seller

product_bp = Blueprint("product", __name__)

@product_bp.route("/seller/add-product", methods=["GET", "POST"])
@login_required
def add_product():
    if current_user.role != "seller":
        return "Unauthorized", 403
    
    categories = Category.query.all()
    
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        price = float(request.form.get("price"))
        stock = int(request.form.get("stock"))
        category_id = request.form.get("category_id")
        
        # Get Seller ID
        seller = Seller.query.filter_by(user_id=current_user.id).first()
        
        new_product = Product(
            name=name, 
            description=description, 
            price=price, 
            stock=stock, 
            category_id=category_id,
            seller_id=seller.id
        )
        
        db.session.add(new_product)
        db.session.commit()
        
        flash("Product added successfully!", "success")
        return redirect(url_for("seller.dashboard"))

    return render_template("add_product.html", categories=categories)