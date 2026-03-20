from backend.extensions import db
from datetime import datetime

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # Category se products tak pahunchne ke liye
    products = db.relationship("Product", back_populates="category")

class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey("sellers.id", ondelete="CASCADE"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Connections using back_populates
    category = db.relationship("Category", back_populates="products")
    seller = db.relationship("Seller", back_populates="products")