from flask import Blueprint, render_template
from flask_login import login_required, current_user

seller_bp = Blueprint("seller", __name__, url_prefix="/seller")

@seller_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != "seller":
        return "Access Denied: You are not a seller!", 403
    return render_template("seller_dashboard.html")