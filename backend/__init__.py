# ---------------------------------------------------------
# VENDORA PRO - MASTER APPLICATION FACTORY
# ---------------------------------------------------------
import os
import json
from flask import Flask, render_template, request
from backend.config import Config
from backend.extensions import db, login_manager, bcrypt

def create_app():
    # 🚨 [DEPLOYMENT FIX 1]: Absolute paths resolution for Render/Cloud
    # Isse server ko HTML aur CSS dhoondhne mein kabhi dikat nahi hogi
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.join(base_dir, '../frontend/templates')
    static_dir = os.path.join(base_dir, '../frontend/static')

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(Config)

    # 🚨 [DEPLOYMENT FIX 2]: Universal Cloud Database SSL Fix
    # Isse Aiven MySQL connection bina kisi TypeError ke chalega
    app.config.update(
        SQLALCHEMY_ENGINE_OPTIONS={
            "connect_args": {
                "ssl": None # Bypass SSL mode for cloud compatibility
            }
        }
    )

    # 1. Initialize Global Extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # 2. Flask-Login: User Loader Logic
    from backend.models.user_model import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 3. Database Context: Import All Models & Auto-Create Tables
    with app.app_context():
        print("Initialising Cloud Database Sync...")
        # Sari tables ko context mein lana zaroori hai
        from backend.models.user_model import User, SavedCard, Notification
        from backend.models.seller_model import Seller
        from backend.models.product_model import Category, Product, ProductImage
        from backend.models.order_model import Order, OrderItem, Coupon, UsedCoupon
        from backend.models.transaction_model import Transaction
        from backend.models.review_model import Review
        
        # 🚀 [CRITICAL]: Create tables automatically on Aiven Cloud
        db.create_all()
        print("All Tables Verified/Created Successfully! ✅")

    # 4. Blueprint Registration (Connecting all Routes)
    from backend.routes.auth_routes import auth_bp
    from backend.routes.seller_routes import seller_bp 
    from backend.routes.admin_routes import admin_bp
    from backend.routes.customer_routes import customer_bp
    from backend.routes.product_routes import product_bp
    from backend.routes.cart_routes import cart_bp 
    from backend.routes.order_routes import order_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(seller_bp) 
    app.register_blueprint(admin_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(order_bp)

    # 5. Global Home Route: Integrated Smart Search & Category Filter
    @app.route('/')
    def index():
        from backend.models.product_model import Product, Category
        search_query = request.args.get('search', '')
        category_id = request.args.get('category', '')
        
        # Base query to fetch active items
        query = Product.query.filter_by(is_active=True)
        
        if search_query:
            query = query.filter(Product.name.ilike(f'%{search_query}%'))
        if category_id:
            query = query.filter_by(category_id=category_id)
            
        products = query.order_by(Product.id.desc()).all()
        categories = Category.query.all()
        return render_template("index.html", products=products, categories=categories)

    # 🛠️ 6. MASTER SETUP ROUTE (For Cloud Initialization)
    # Ise sirf 1 baar run karna: /setup-everything-secretly
    @app.route('/setup-everything-secretly')
    def setup_cloud():
        from backend.models.product_model import Category
        from backend.models.user_model import User
        
        # A. 15 Pro-Level Categories
        if not Category.query.first():
            names = [
                'Electronics', 'Fashion', 'Groceries', 'Home Decor', 
                'Gadgets', 'Perfumes', 'Books', 'Sports & Fitness', 
                'Beauty & Care', 'Kitchen Appliances', 'Toys & Baby',
                'Watches', 'Footwear', 'Health', 'Automotive'
            ]
            for n in names:
                db.session.add(Category(name=n))
            db.session.commit()

        # B. Initial Admin Account (User ID: 1)
        admin_email = "admin@vendora.com"
        if not User.query.filter_by(email=admin_email).first():
            hashed_pw = bcrypt.generate_password_hash("admin123").decode('utf-8')
            new_admin = User(
                name="Super Admin",
                email=admin_email,
                password=hashed_pw,
                role="admin",
                wallet_balance=0.0,
                age=30,
                gender="Male",
                full_address="Vendora Cloud Headquarters",
                profile_pic="default_pro.png"
            )
            db.session.add(new_admin)
            db.session.commit()
            return "<h1>Cloud Setup Complete! ✅</h1><p>15 Categories added. Admin: admin@vendora.com created.</p><a href='/'>Go to Home</a>"
        
        return "<h1>System already initialized.</h1><a href='/'>Go to Home</a>"

    return app