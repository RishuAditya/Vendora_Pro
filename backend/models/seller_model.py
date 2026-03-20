from backend.extensions import db
from datetime import datetime

class Seller(db.Model):
    __tablename__ = "sellers"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    company_name = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(20), default="pending")
    total_sales = db.Column(db.Float, default=0.0)
    seller_score = db.Column(db.Integer, default=100)
    badge = db.Column(db.String(20), default="Bronze")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="seller_profile")
    products = db.relationship("Product", back_populates="seller", cascade="all, delete-orphan")