from backend.extensions import db
from datetime import datetime

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
 
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

    
    brand = db.Column(db.String(100))
    weight_qty = db.Column(db.String(50))
    warranty = db.Column(db.String(100))
    specifications = db.Column(db.Text) 
    expiry_date = db.Column(db.Date, nullable=True)
    is_food = db.Column(db.Boolean, default=False)

    category = db.relationship("Category", back_populates="products")
    seller = db.relationship("Seller", back_populates="products")
    extra_images = db.relationship('ProductImage', backref='product', cascade="all, delete-orphan")
    reviews = db.relationship('Review', backref='product_info', lazy=True)
   
class ProductImage(db.Model):
    __tablename__ = 'product_images'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete="CASCADE"), nullable=False)
    image_filename = db.Column(db.String(255), nullable=False)

