from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from backend.models.transaction_model import Transaction 
from backend.extensions import db

customer_bp = Blueprint("customer", __name__, url_prefix="/customer")

@customer_bp.route("/dashboard")
@login_required
def dashboard():
    # Transaction history fetch karna taaki dashboard pe dikha sakein
    tx_history = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.created_at.desc()).all()
    return render_template("customer_dashboard.html", transactions=tx_history)

@customer_bp.route("/recharge-money", methods=["POST"])
@login_required
def recharge_money():
    amount = request.form.get("amount")
    if not amount or float(amount) <= 0:
        flash("Bhai, sahi amount toh daalo! 😅", "warning")
        return redirect(url_for('customer.dashboard'))
    return render_template("payment_gateway.html", amount=amount)

@customer_bp.route("/payment-success", methods=["POST"])
@login_required
def payment_success():
    amount = request.form.get("amount")
    
    if amount:
        # 1. Database mein recharge ka record (Transaction) dalo
        new_tx = Transaction(
            user_id=current_user.id,
            amount=float(amount),
            type='Credit',
            purpose='Wallet Recharge'
        )
        db.session.add(new_tx)
        
        # 2. Wallet balance update karo
        current_user.wallet_balance += float(amount)
        db.session.commit()
        
        flash(f"Mubarak ho! ₹{amount} add ho gaye. 💳🎉", "success")
    else:
        flash("Oops! Payment fail ho gayi.", "danger")
        
    return redirect(url_for("customer.dashboard"))