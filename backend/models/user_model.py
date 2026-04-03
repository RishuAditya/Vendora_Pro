# ---------------------------------------------------------
# TOPIC: USER, SAVED CARDS & NOTIFICATION MODELS
# ---------------------------------------------------------
from backend.extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="customer")
    
    # Financial Fields
    wallet_balance = db.Column(db.Float, default=0.0)
    locked_balance = db.Column(db.Float, default=0.0) # 🔒 Escrow (7-Day Lock)
    
    # Profile Details
    reset_token = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    profile_pic = db.Column(db.String(255), default='default_pro.png')
    full_address = db.Column(db.Text)

    # --- Relationships ---
    seller_profile = db.relationship('Seller', back_populates='user', cascade="all, delete-orphan", uselist=False)
    saved_cards = db.relationship('SavedCard', backref='owner', cascade="all, delete-orphan", lazy=True)
    orders = db.relationship('Order', back_populates='user', cascade="all, delete-orphan")
    reviews = db.relationship('Review', backref='user_info', lazy=True)
    notifications = db.relationship('Notification', backref='receiver', foreign_keys='Notification.receiver_id', lazy=True)

class SavedCard(db.Model):
    __tablename__ = 'saved_cards'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    card_holder_name = db.Column(db.String(100))
    card_last_four = db.Column(db.String(4), nullable=False)
    card_type = db.Column(db.String(20)) # Visa/Mastercard
    expiry_date = db.Column(db.String(7)) # MM/YYYY
    created_at = db.Column(db.DateTime, default=datetime.now)

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)