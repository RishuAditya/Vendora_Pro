import os
import uuid 
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from backend.extensions import db
from backend.models.product_model import Product, Category, ProductImage
from backend.models.seller_model import Seller
from datetime import datetime
from backend.models.review_model import Review

# Blueprint setup
product_bp = Blueprint("product", __name__)

# --- IMAGE UPLOAD SETTINGS ---
UPLOAD_FOLDER = 'frontend/static/images/products'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Function to check valid image extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------------------------------------------------
# 📦 1. ADD PRODUCT ROUTE (With Full Intelligence & Multi-Images)
# ---------------------------------------------------------
@product_bp.route("/seller/add-product", methods=["GET", "POST"])
@login_required
def add_product():
    # Role Check: Sirf Seller hi product dal sakta hai
    if current_user.role != "seller": 
        return "Unauthorized Access: Sellers Only", 403
    
    # 🛡️ GATEKEEPER logic: Check if Admin has approved this seller
    seller = Seller.query.filter_by(user_id=current_user.id).first()
    if not seller or seller.status != 'approved':
        return render_template("seller_pending_notice.html")

    # Categories load karein dropdown ke liye
    categories = Category.query.all()

    if request.method == "POST":
        # A. Basic Details Extraction
        name = request.form.get("name")
        description = request.form.get("description")
        price = float(request.form.get("price", 0))
        stock = int(request.form.get("stock", 0))
        category_id = request.form.get("category_id")
        
        # B. Intelligence Fields (Phase 3 features)
        brand = request.form.get("brand") 
        weight_qty = request.form.get("weight_qty")
        warranty = request.form.get("warranty")
        specifications = request.form.get("specifications") # Multi-line data
        
        # C. Expiry & Food Safety Logic
        is_food = True if request.form.get("is_food") == "on" else False
        expiry_date_str = request.form.get("expiry_date")
        expiry_date = None
        if expiry_date_str:
            try:
                expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
            except ValueError:
                expiry_date = None

        # 1. Database mein main Product record create karein
        new_product = Product(
            name=name, 
            description=description, 
            price=price, 
            stock=stock, 
            category_id=category_id,
            seller_id=seller.id,
            brand=brand, 
            weight_qty=weight_qty, 
            warranty=warranty,
            specifications=specifications,
            expiry_date=expiry_date,
            is_food=is_food
        )
        db.session.add(new_product)
        db.session.flush() # Isse product ID mil jayegi taaki images link ho sakein

        # 2. Multi-Image Handling (Carousel/Slider logic)
        files = request.files.getlist('images')
        main_image_set = False
        
        for file in files:
            if file and allowed_file(file.filename):
                # Unique name generator to avoid file overwriting
                unique_name = f"{current_user.id}_{uuid.uuid4().hex[:8]}_{secure_filename(file.filename)}"
                
                # Folder check and save
                if not os.path.exists(UPLOAD_FOLDER):
                    os.makedirs(UPLOAD_FOLDER)
                file.save(os.path.join(UPLOAD_FOLDER, unique_name))
                
                # First image is the thumbnail/cover photo
                if not main_image_set:
                    new_product.image = unique_name
                    main_image_set = True
                
                # Extra images table mein entry
                db.session.add(ProductImage(product_id=new_product.id, image_filename=unique_name))
        
        db.session.commit() # Save everything permanently
        flash(f"Product '{name}' is now LIVE on Vendora Marketplace! 📦🚀", "success")
        return redirect(url_for("seller.dashboard"))

    return render_template("add_product.html", categories=categories)

# ---------------------------------------------------------
# 📋 2. MANAGE INVENTORY (Seller Private View)
# ---------------------------------------------------------
@product_bp.route("/seller/my-products")
@login_required
def manage_products():
    if current_user.role != "seller": return "Unauthorized", 403
    
    seller = Seller.query.filter_by(user_id=current_user.id).first()
    if not seller or seller.status != 'approved':
        return render_template("seller_pending_notice.html")

    # Seller ke saare products descending order mein (Newest first)
    products = Product.query.filter_by(seller_id=seller.id).order_by(Product.id.desc()).all()
    return render_template("manage_products.html", products=products)

# ---------------------------------------------------------
# 🔍 3. PRODUCT DETAIL PAGE (Public View for Customers)
# ---------------------------------------------------------
@product_bp.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Expiry Check logic for UI alerts
    is_expired = False
    if product.expiry_date and product.expiry_date < datetime.now().date():
        is_expired = True
    
    # Simple view counter for analytics
    product.views += 1
    db.session.commit()
    
    return render_template("product_detail.html", product=product, is_expired=is_expired)

# ---------------------------------------------------------
# ✏️ 4. EDIT PRODUCT (Advanced Update Logic)
# ---------------------------------------------------------
@product_bp.route("/seller/edit-product/<int:product_id>", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    seller = Seller.query.filter_by(user_id=current_user.id).first()

    # Security: Ensure only the owner can edit
    if current_user.role != "seller" or product.seller_id != seller.id:
        flash("Unauthorized! You can only edit your own products.", "danger")
        return redirect(url_for('index'))
    
    categories = Category.query.all()

    if request.method == "POST":
        # Update fields
        product.name = request.form.get("name")
        product.description = request.form.get("description")
        product.price = float(request.form.get("price"))
        product.stock = int(request.form.get("stock"))
        product.category_id = request.form.get("category_id")
        product.brand = request.form.get("brand")
        product.weight_qty = request.form.get("weight_qty")
        product.warranty = request.form.get("warranty")
        product.specifications = request.form.get("specifications")
        
        # Expiry date parsing
        expiry_str = request.form.get("expiry_date")
        if expiry_str:
            product.expiry_date = datetime.strptime(expiry_str, '%Y-%m-%d').date()

        # Handle New Image Upload during Edit (Optional)
        new_files = request.files.getlist('images')
        for file in new_files:
            if file and allowed_file(file.filename):
                unique_name = f"update_{uuid.uuid4().hex[:6]}_{secure_filename(file.filename)}"
                file.save(os.path.join(UPLOAD_FOLDER, unique_name))
                db.session.add(ProductImage(product_id=product.id, image_filename=unique_name))

        db.session.commit()
        flash(f"Changes for '{product.name}' saved successfully! ✨", "success")
        return redirect(url_for('product.manage_products'))

    return render_template("edit_product.html", product=product, categories=categories)

# ---------------------------------------------------------
# 🗑️ 5. DELETE PRODUCT (With File System Cleanup)
# ---------------------------------------------------------
@product_bp.route("/seller/delete-product/<int:product_id>")
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    seller = Seller.query.filter_by(user_id=current_user.id).first()

    # Integrity Check
    if product.seller_id != seller.id:
        flash("Action denied! Security violation.", "danger")
        return redirect(url_for('product.manage_products'))

    # Physical cleanup: Delete all associated images from server folder
    images_to_delete = ProductImage.query.filter_by(product_id=product.id).all()
    for img in images_to_delete:
        try:
            os.remove(os.path.join(UPLOAD_FOLDER, img.image_filename))
        except Exception as e:
            print(f"File delete error: {e}")

    # Database cleanup
    db.session.delete(product)
    db.session.commit()
    
    flash("Product and all its data removed permanently. 🗑️", "info")
    return redirect(url_for('product.manage_products'))

# ---------------------------------------------------------
# TOPIC: RATINGS & REVIEWS SYSTEM
# ---------------------------------------------------------
@product_bp.route("/add-review/<int:product_id>", methods=["POST"])
@login_required
def add_review(product_id):
    if current_user.role != 'customer':
        flash("Only customers can write reviews!", "warning")
        return redirect(request.referrer)

    rating = request.form.get("rating")
    comment = request.form.get("comment")
    file = request.files.get('review_image')
    
    filename = None
    if file and allowed_file(file.filename):
        # Review images folder: frontend/static/images/reviews/
        REVIEW_FOLDER = 'frontend/static/images/reviews'
        if not os.path.exists(REVIEW_FOLDER): os.makedirs(REVIEW_FOLDER)
        filename = f"rev_{current_user.id}_{uuid.uuid4().hex[:5]}_{secure_filename(file.filename)}"
        file.save(os.path.join(REVIEW_FOLDER, filename))

    new_review = Review(
        user_id=current_user.id,
        product_id=product_id,
        rating=int(rating),
        comment=comment,
        review_image=filename
    )
    db.session.add(new_review)
    db.session.commit()

    flash("Thank you for your feedback! ⭐", "success")
    return redirect(request.referrer)