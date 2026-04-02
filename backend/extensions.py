from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

# Initialize objects
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

# Login settings
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"

# 🚨 [DEPLOYMENT FIX]: Ye function database connection errors ko rokega
# Isse SQLAlchemy driver ko koi faltu flag nahi bhejega
def get_db_args():
    return {
        "engine_options": {
            "connect_args": {
                "ssl": None # SSL disable karne ka sahi tarika
            }
        }
    }