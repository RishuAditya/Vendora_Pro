# Vendora_Pro/create_admin.py
from backend import create_app
from backend.extensions import db, bcrypt
from backend.models.user_model import User

app = create_app()
with app.app_context():
    hashed_password = bcrypt.generate_password_hash("admin123").decode('utf-8')
    admin = User(name="Super Admin", email="admin@vendora.com", password=hashed_password, role="admin")
    db.session.add(admin)
    db.session.commit()
    print("Admin Account Created Successfully! Login with admin@vendora.com / admin123")