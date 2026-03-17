from flask import Blueprint, render_template
from flask_login import login_required, current_user

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != "admin":
        return "Access Denied: Only Admins allowed!", 403
    return render_template("admin_dashboard.html")