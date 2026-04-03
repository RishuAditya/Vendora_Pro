from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

login_manager.login_view = "auth.login"

# 🚨 VERCEL & AIVEN CLOUD SSL FIX
def get_db_args():
    return {
        "engine_options": {
            "connect_args": {
                "ssl": {"ssl_mode": "REQUIRED"} # Aiven cloud demands this
            }
        }
    }