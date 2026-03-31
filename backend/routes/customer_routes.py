from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from backend.models.transaction_model import Transaction 
from backend.extensions import db
from backend.models.user_model import SavedCard

customer_bp = Blueprint("customer", __name__, url_prefix="/customer")

@customer_bp.route("/dashboard")
@login_required
def dashboard():
    tx_history = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.created_at.desc()).all()
    return render_template("customer_dashboard.html", transactions=tx_history)

@customer_bp.route("/recharge", methods=["POST"])
@login_required
def recharge_money():
    amount_val = request.form.get("amount")
    card_id = request.form.get("saved_card_id")
    save_checkbox = request.form.get("save_card_checkbox")

    if not amount_val or float(amount_val) <= 0:
        flash("Invalid amount! 😅", "warning")
        return redirect(url_for('customer.dashboard'))

    amount = float(amount_val)
    last_four = "0000"

    # Logic: Saved Card use ho raha hai ya Naya?
    if card_id and card_id != "new":
        card = SavedCard.query.get(card_id)
        last_four = card.card_last_four
    else:
        card_no = request.form.get("card_number")
        last_four = card_no[-4:] if card_no else "0000"
        
        if save_checkbox == "on":
            new_card = SavedCard(
                user_id=current_user.id,
                card_holder_name=request.form.get("card_name"),
                card_last_four=last_four,
                card_type="Visa",
                expiry_date=request.form.get("expiry")
            )
            db.session.add(new_card)

    # Update Balance
    current_user.wallet_balance += amount

    # Record Transaction
    new_tx = Transaction(
        user_id=current_user.id,
        amount=amount,
        type='Credit',
        purpose=f'Wallet Recharge (Card ****{last_four})'
    )
    db.session.add(new_tx)
    db.session.commit()
    
    flash(f"₹{amount} added to wallet! 💳🎉", "success")
    return redirect(url_for("customer.dashboard"))