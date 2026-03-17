from flask import Blueprint, render_template
from flask_login import login_required, current_user

customer_bp = Blueprint("customer", __name__, url_prefix="/customer")

@customer_bp.route("/dashboard")
@login_required
def dashboard():
    # Customer ka dashboard usually home page ya profile page hota hai
    return render_template("customer_dashboard.html")