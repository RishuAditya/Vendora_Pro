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

    # Import Models to create tables
    from backend import models

    # Abhi humne routes nahi banaye hain, baad me yahan register karenge
    # app.register_blueprint(auth_bp)

    @app.route('/')
    def index():
        return "Vendora Pro Engine is Running Successfully! 🚀"

    with app.app_context():
        db.create_all() # Ye saari tables MySQL me bana dega

    return app