from backend.extensions import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), default="Wallet")
    payment_status = db.Column(db.String(50), default="Paid")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    invoice_no = db.Column(db.String(100), unique=True)

    shipping_address = db.Column(db.Text)

    payment_mode = db.Column(db.String(50)) 

    customer_name_snapshot = db.Column(db.String(100))

    customer_email_snapshot = db.Column(db.String(100))

  
    user = db.relationship("User", back_populates="orders")

class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(db.Integer, db.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)

    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False)

    seller_id = db.Column(db.Integer, db.ForeignKey("sellers.id", ondelete="CASCADE"), nullable=False)
    
    quantity = db.Column(db.Integer, nullable=False)
    price_at_time = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default="Pending")
    
    order = db.relationship("Order", backref="items")
    product = db.relationship("Product")

    seller = db.relationship("Seller")