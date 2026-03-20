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
    wallet_balance = db.Column(db.Float, default=0.0)
    reset_token = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    seller_profile = db.relationship('Seller', back_populates='user', cascade="all, delete-orphan", uselist=False)
    orders = db.relationship('Order', back_populates='user', cascade="all, delete-orphan")