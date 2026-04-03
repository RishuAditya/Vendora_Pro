# ---------------------------------------------------------
# TOPIC: ENTERPRISE ORDERING, ITEM TRACKING & COUPONS
# ---------------------------------------------------------
from backend.extensions import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), default="Wallet")
    payment_status = db.Column(db.String(50), default="Paid")
    created_at = db.Column(db.DateTime, default=datetime.now)

    # ✅ FIXED: Shipping Details (Crucial for Checkout)
    invoice_no = db.Column(db.String(100), unique=True)
    shipping_name = db.Column(db.String(100))
    shipping_phone = db.Column(db.String(20))
    shipping_address = db.Column(db.Text)
    
    # Financial Snapshots
    customer_name_snapshot = db.Column(db.String(100))
    customer_email_snapshot = db.Column(db.String(100))
    wallet_amount_paid = db.Column(db.Float, default=0.0)
    card_amount_paid = db.Column(db.Float, default=0.0)
    payment_mode = db.Column(db.String(50)) # WALLET, CARD, HYBRID, COD

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
    variant = db.Column(db.String(50))
    
    # 🚚 Tracking & Return Timelines
    delivered_at = db.Column(db.DateTime)
    return_deadline = db.Column(db.DateTime)
    return_status = db.Column(db.String(50), default='None')

    order = db.relationship("Order", backref="items")
    product = db.relationship("Product")
    seller = db.relationship("Seller")

class Coupon(db.Model):
    __tablename__ = 'coupons'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    discount_value = db.Column(db.Float, nullable=False)
    is_percentage = db.Column(db.Boolean, default=False)
    min_purchase = db.Column(db.Float, default=0.0)
    max_purchase = db.Column(db.Float, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

class UsedCoupon(db.Model):
    __tablename__ = 'used_coupons'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'), nullable=False)
    used_at = db.Column(db.DateTime, default=datetime.now)