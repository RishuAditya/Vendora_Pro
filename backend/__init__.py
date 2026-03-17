from flask import Flask
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

    # Register Blueprints (Routes)
    from backend.routes.auth_routes import auth_bp
    from backend.routes.seller_routes import seller_bp    
    from backend.routes.admin_routes import admin_bp      
    from backend.routes.customer_routes import customer_bp
    from backend.routes.product_routes import product_bp



    app.register_blueprint(auth_bp)
    app.register_blueprint(seller_bp)                     
    app.register_blueprint(admin_bp)                      
    app.register_blueprint(customer_bp)
    app.register_blueprint(product_bp)
    

    @app.route('/')
    def index():
        from flask_login import current_user
        if current_user.is_authenticated:
            return f"Welcome to Vendora Pro! You are logged in as {current_user.name} ({current_user.role}). <a href='/logout'>Logout</a>"
        return "Vendora Pro Engine is Running! <a href='/login'>Login Here</a> or <a href='/register'>Register Here</a>"

    return app