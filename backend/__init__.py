from flask import Flask, render_template # render_template add kiya
from backend.config import Config
from backend.extensions import db, login_manager, bcrypt

def create_app():
    app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
    app.config.from_object(Config)

    # Initialize Extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # User Loader for Flask-Login
    from backend.models.user_model import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Context ke andar models import karna zaroori hai
    with app.app_context():
        from backend.models.user_model import User
        from backend.models.seller_model import Seller
        from backend.models.product_model import Category, Product
        from backend.models.order_model import Order, OrderItem
        # db.create_all() # Manual SQL use kar rahe hain isliye ise comment rakhein

    # Register Blueprints (Routes)
    from backend.routes.auth_routes import auth_bp
    from backend.routes.seller_routes import seller_bp
    from backend.routes.admin_routes import admin_bp
    from backend.routes.customer_routes import customer_bp
    from backend.routes.product_routes import product_bp # Product BP bhi add kiya

    app.register_blueprint(auth_bp)
    app.register_blueprint(seller_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(product_bp)

    # Final Home Page Route (Plain text hat gaya!)
    @app.route('/')
    def index():
        from backend.models.product_model import Product
        products = Product.query.all()
        return render_template("index.html", products=products)

    return app