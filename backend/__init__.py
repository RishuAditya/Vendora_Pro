import os
from flask import Flask, render_template, request
from backend.config import Config
from backend.extensions import db, login_manager, bcrypt

def create_app():
    # 1. Path Setup
    base_dir = os.path.abspath(os.path.dirname(__file__))
    root_dir = os.path.abspath(os.path.join(base_dir, ".."))
    template_dir = os.path.join(root_dir, 'frontend', 'templates')
    static_dir = os.path.join(root_dir, 'frontend', 'static')

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(Config)

    # 2. Database Optimization for Vercel
    app.config.update(
        SQLALCHEMY_ENGINE_OPTIONS={
            "connect_args": {"ssl": None},
            "pool_pre_ping": True, # Connection check
        }
    )

    # 3. Initialize Extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    from backend.models.user_model import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 4. Blueprints (Saare features yahan se load honge)
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

    # 5. Home Route
    @app.route('/')
    def index():
        from backend.models.product_model import Product, Category
        search_query = request.args.get('search', '')
        category_id = request.args.get('category', '')
        query = Product.query.filter_by(is_active=True)
        if search_query: query = query.filter(Product.name.ilike(f'%{search_query}%'))
        if category_id: query = query.filter_by(category_id=category_id)
        products = query.order_by(Product.id.desc()).all()
        categories = Category.query.all()
        return render_template("index.html", products=products, categories=categories)

    return app