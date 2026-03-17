from backend.extensions import db
from datetime import datetime

class Seller(db.Model):
    __tablename__ = "sellers"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    company_name = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(20), default="pending") # pending, approved, rejected
    
    # Seller Performance (Intelligence)
    total_sales = db.Column(db.Float, default=0.0)
    seller_score = db.Column(db.Integer, default=100) # Out of 100
    badge = db.Column(db.String(20), default="Bronze") # Bronze, Silver, Gold, Platinum
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship("User", backref=db.backref("seller_profile", uselist=False))