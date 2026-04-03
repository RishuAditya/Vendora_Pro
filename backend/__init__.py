# ---------------------------------------------------------
# VENDORA PRO - STABLE VERCEL FACTORY
# ---------------------------------------------------------
import os
from flask import Flask, render_template, request
from backend.config import Config
from backend.extensions import db, login_manager, bcrypt

def create_app():
    # 🚨 PATH FIX FOR VERCEL
    base_dir = os.path.abspath(os.path.dirname(__file__))
    root_dir = os.path.abspath(os.path.join(base_dir, ".."))
    template_dir = os.path.join(root_dir, 'frontend', 'templates')
    static_dir = os.path.join(root_dir, 'frontend', 'static')

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(Config)

    # 🚨 CLOUD DB SSL FIX
    app.config.update(
        SQLALCHEMY_ENGINE_OPTIONS={
            "connect_args": {"ssl": None} 
        }
    )

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    from backend.models.user_model import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 🚀 BLUEPRINTS REGISTRATION
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

    # 🏠 HOME ROUTE
    @app.route('/')
    def index():
        from backend.models.product_model import Product, Category
        search_query = request.args.get('search', '')
        category_id = request.args.get('category', '')
        query = Product.query.filter_by(is_active=True)
        if search_query:
            query = query.filter(Product.name.ilike(f'%{search_query}%'))
        if category_id:
            query = query.filter_by(category_id=category_id)
        products = query.order_by(Product.id.desc()).all()
        categories = Category.query.all()
        return render_template("index.html", products=products, categories=categories)

    # 🛠️ MANUAL DATABASE SETUP (Run this once after deployment)
    @app.route('/deploy-setup')
    def deploy_setup():
        try:
            # Import models inside function to avoid circular imports
            from backend.models.user_model import User, SavedCard, Notification
            from backend.models.seller_model import Seller
            from backend.models.product_model import Category, Product, ProductImage
            from backend.models.order_model import Order, OrderItem, Coupon, UsedCoupon
            from backend.models.transaction_model import Transaction
            from backend.models.review_model import Review
            
            # Create Tables
            db.create_all()

            # Create Default Admin & Categories if missing
            if not Category.query.first():
                names = ['Electronics', 'Fashion', 'Groceries', 'Gadgets', 'Home Decor']
                for n in names: db.session.add(Category(name=n))
            
            admin_email = "admin@vendora.com"
            if not User.query.filter_by(email=admin_email).first():
                hashed_pw = bcrypt.generate_password_hash("admin123").decode('utf-8')
                db.session.add(User(name="Admin", email=admin_email, password=hashed_pw, role="admin", wallet_balance=0.0))
            
            db.session.commit()
            return "<h1>Database Sync Success! ✅</h1><a href='/'>Go to Home</a>"
        except Exception as e:
            return f"<h1>Setup Failed ❌</h1><p>{str(e)}</p>"

    return app