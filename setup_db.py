from backend import create_app
from backend.extensions import db, bcrypt

app = create_app()
with app.app_context():
    # Import models
    from backend.models.user_model import User, SavedCard, Notification
    from backend.models.seller_model import Seller
    from backend.models.product_model import Category, Product, ProductImage
    from backend.models.order_model import Order, OrderItem, Coupon, UsedCoupon
    from backend.models.transaction_model import Transaction
    from backend.models.review_model import Review
    
    print("Creating tables in Aiven Cloud...")
    db.create_all()

    # Admin Creation
    if not User.query.filter_by(role='admin').first():
        hashed_pw = bcrypt.generate_password_hash("admin123").decode('utf-8')
        db.session.add(User(name="Admin", email="admin@vendora.com", password=hashed_pw, role="admin"))
        db.session.commit()
        print("Admin created!")

    print("Success! Cloud DB is ready.")