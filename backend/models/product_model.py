from backend.extensions import db
from datetime import datetime

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey("sellers.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    
    is_active = db.Column(db.Boolean, default=True) # For Pause/Resume selling
    views = db.Column(db.Integer, default=0) # For Trending Products Logic
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    category = db.relationship("Category", backref="products")
    seller = db.relationship("Seller", backref="products")