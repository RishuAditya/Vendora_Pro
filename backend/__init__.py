import os
import json
from flask import Flask, render_template, request
from backend.config import Config
from backend.extensions import db, login_manager, bcrypt

def create_app():
    # 🚨 [DEPLOYMENT FIX 1]: Absolute paths for Render server templates/static
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.join(base_dir, '../frontend/templates')
    static_dir = os.path.join(base_dir, '../frontend/static')

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(Config)

    # 🚨 [DEPLOYMENT FIX 2]: SSL Connection Fix for Cloud Database
    app.config.update(
        SQLALCHEMY_ENGINE_OPTIONS={
            "connect_args": {
                "ssl": None  # SSL disable for Aiven Cloud compatibility
            }
        }
    )

    # 1. Initialize Extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # 2. User Loader Logic for Login
    from backend.models.user_model import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 3. Context ke andar Database Initialization (Auto-Create Tables)
    with app.app_context():
        # Import all models to ensure SQLAlchemy detects them
        from backend.models.user_model import User, SavedCard, Notification
        from backend.models.seller_model import Seller
        from backend.models.product_model import Category, Product, ProductImage
        from backend.models.order_model import Order, OrderItem, Coupon, UsedCoupon
        from backend.models.transaction_model import Transaction
        from backend.models.review_model import Review
        
        # 🚀 Create tables automatically on Cloud if they don't exist
        db.create_all()

    # 4. Register Blueprints (Routes)
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

    # 5. Global Home Route with Smart Search/Filter Logic
    @app.route('/')
    def index():
        from backend.models.product_model import Product, Category
        search_query = request.args.get('search', '')
        category_id = request.args.get('category', '')
        
        # Base query to fetch only active products
        query = Product.query.filter_by(is_active=True)
        
        if search_query:
            query = query.filter(Product.name.ilike(f'%{search_query}%'))
        if category_id:
            query = query.filter_by(category_id=category_id)
            
        products = query.order_by(Product.id.desc()).all()
        categories = Category.query.all()
        return render_template("index.html", products=products, categories=categories)

    # 🛠️ 6. SECRET CLOUD INITIALIZATION (15 Categories + Admin Account)
    @app.route('/setup-everything-secretly')
    def setup_cloud():
        from backend.models.product_model import Category
        from backend.models.user_model import User
        
        # A. 15 Professional Categories setup
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

        # B. Secret Admin Creation (admin@vendora.com / admin123)
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
                full_address="Vendora HQ, Cloud Server",
                profile_pic="default_pro.png"
            )
            db.session.add(new_admin)
            db.session.commit()
            return "<h1>Success! 15 Categories & Admin Created. ✅</h1><p>Login: admin@vendora.com / admin123</p><a href='/'>Go Home</a>"
        
        return "<h1>Platform is already initialized!</h1><a href='/'>Go Home</a>"

    return app