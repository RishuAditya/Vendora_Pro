from flask import Flask, render_template, request
from backend.config import Config
from backend.extensions import db, login_manager, bcrypt

def create_app():
    app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    from backend.models.user_model import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        from backend.models.user_model import User, SavedCard, Notification
        from backend.models.seller_model import Seller
        from backend.models.product_model import Category, Product, ProductImage
        from backend.models.order_model import Order, OrderItem
        from backend.models.transaction_model import Transaction
        from backend.models.review_model import Review

    # Register Blueprints
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

    @app.route('/')
    def index():
        from backend.models.product_model import Product, Category
        search_query = request.args.get('search', '')
        category_id = request.args.get('category', '')
        query = Product.query.filter_by(is_active=True)
        if search_query: query = query.filter(Product.name.ilike(f'%{search_query}%'))
        if category_id: query = query.filter_by(category_id=category_id)
        products = query.order_by(Product.created_at.desc()).all()
        categories = Category.query.all()
        return render_template("index.html", products=products, categories=categories)

    return app