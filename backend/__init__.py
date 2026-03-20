from flask import Flask, render_template, request
from backend.config import Config
from backend.extensions import db, login_manager, bcrypt

def create_app():
    app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
    app.config.from_object(Config)

    # 1. Initialize Extensions (Using global imports from top)
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # 2. User Loader for Flask-Login
    from backend.models.user_model import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 3. Context ke andar saare Models import karein (Very Important)
    with app.app_context():
        from backend.models.user_model import User
        from backend.models.seller_model import Seller
        from backend.models.product_model import Category, Product
        from backend.models.order_model import Order, OrderItem
        from backend.models.cart_model import Cart
        from backend.models.transaction_model import Transaction # Naya model add kiya
        
        # db.create_all() # Agar tables manually banayi hain toh comment rehne dein

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

    # 5. Home Page Route
    @app.route('/')
    def index():
        from backend.models.product_model import Product, Category
        
        search_query = request.args.get('search', '')
        category_id = request.args.get('category', '')

        # Base Query: Sirf active products dikhao
        query = Product.query.filter_by(is_active=True)

        if search_query:
            query = query.filter(Product.name.ilike(f'%{search_query}%'))
        
        if category_id:
            query = query.filter_by(category_id=category_id)

        products = query.order_by(Product.created_at.desc()).all()
        categories = Category.query.all()

        return render_template("index.html", products=products, categories=categories)

    return app