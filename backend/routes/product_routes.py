import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from backend.extensions import db
from backend.models.product_model import Product, Category
from backend.models.seller_model import Seller

product_bp = Blueprint("product", __name__)

# Image Upload Configuration
UPLOAD_FOLDER = 'frontend/static/images/products'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@product_bp.route("/seller/add-product", methods=["GET", "POST"])
@login_required
def add_product():
    if current_user.role != "seller":
        return "Unauthorized", 403
    
    categories = Category.query.all()
    seller = Seller.query.filter_by(user_id=current_user.id).first()

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        price = float(request.form.get("price"))
        stock = int(request.form.get("stock"))
        category_id = request.form.get("category_id")
        
        # Image Handling logic
        file = request.files.get('image')
        filename = None

        if file and allowed_file(file.filename):
            filename = secure_filename(f"{current_user.id}_{file.filename}")
            file.save(os.path.join(UPLOAD_FOLDER, filename))
        
        new_product = Product(
            name=name, 
            description=description, 
            price=price, 
            stock=stock, 
            category_id=category_id,
            seller_id=seller.id,
            image=filename # Database mein file ka naam save hoga
        )
        
        db.session.add(new_product)
        db.session.commit()
        
        flash("Product added successfully with image! 📦", "success")
        return redirect(url_for("seller.dashboard"))

    return render_template("add_product.html", categories=categories)

# Naya Route: Seller apne products dekh sake
@product_bp.route("/seller/my-products")
@login_required
def manage_products():
    if current_user.role != "seller":
        return "Unauthorized", 403
    
    seller = Seller.query.filter_by(user_id=current_user.id).first()
    products = Product.query.filter_by(seller_id=seller.id).all()
    return render_template("manage_products.html", products=products)

# for product detail -
@product_bp.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product_detail.html", product=product)