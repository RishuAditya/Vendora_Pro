from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from backend.extensions import db

customer_bp = Blueprint("customer", __name__, url_prefix="/customer")

@customer_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("customer_dashboard.html")

# 1. Recharge Shuru karne ka route
@customer_bp.route("/recharge-money", methods=["POST"])
@login_required
def recharge_money():
    # User ne kitna paisa dala dashboard pe wo uthao
    amount = request.form.get("amount")
    
    if not amount or float(amount) <= 0:
        flash("Bhai, sahi amount toh daalo! 😅", "warning")
        return redirect(url_for('customer.dashboard'))
    
    # Ab user ko Payment Gateway page par bhej do amount ke saath
    return render_template("payment_gateway.html", amount=amount)

# 2. Payment hone ke baad asli Wallet Update logic
@customer_bp.route("/payment-success", methods=["POST"])
@login_required
def payment_success():
    amount = request.form.get("amount")
    
    # Asliyat mein yahan bank verify karta hai, hum simulate kar rahe hain
    if amount:
        # Wallet mein naya balance add karo
        current_user.wallet_balance += float(amount)
        db.session.commit()
        
        flash(f"Mubarak ho! ₹{amount} aapke wallet mein add ho gaye. 💳🎉", "success")
    else:
        flash("Oops! Payment fail ho gayi. Phir se try karo.", "danger")
        
    return redirect(url_for("customer.dashboard"))