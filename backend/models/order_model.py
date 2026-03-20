from backend.extensions import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), default="COD") # COD, Wallet, Card
    payment_status = db.Column(db.String(50), default="Pending")
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", back_populates="orders")

class OrderItem(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey("sellers.id"), nullable=False)
    
    quantity = db.Column(db.Integer, nullable=False)
    price_at_time = db.Column(db.Float, nullable=False) # Price jab order kiya tha
    
    # Advanced Order Tracking
    status = db.Column(db.String(50), default="Pending") # Pending, Packed, Shipped, Delivered, Cancelled, Returned
    
    order = db.relationship("Order", backref="items")
    product = db.relationship("Product")