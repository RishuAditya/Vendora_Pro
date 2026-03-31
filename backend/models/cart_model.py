from backend.extensions import db
from datetime import datetime

class Cart(db.Model):
    __tablename__ = "cart"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.now)
    variant = db.Column(db.String(50), nullable=True)

    # Relationships
    product = db.relationship("Product")
    user = db.relationship("User")