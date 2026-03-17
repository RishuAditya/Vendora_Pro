from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from backend.extensions import db, bcrypt
from backend.models.user_model import User
from backend.models.seller_model import Seller

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered! Please login.", "danger")
            return redirect(url_for("auth.register"))

        # Hash Password securely using Bcrypt
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Create User
        new_user = User(name=name, email=email, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit() # Save user first to get User ID

        # Auto-create Seller Profile if role is 'seller'
        if role == "seller":
            new_seller = Seller(user_id=new_user.id, company_name=f"{name}'s Store")
            db.session.add(new_seller)
            db.session.commit()

        flash("Registration successful! You can now login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        # Verify User and Password
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash(f"Welcome back, {user.name}!", "success")
            
            # Smart Redirection based on Roles
            if user.role == "admin":
                return redirect("/admin/dashboard") # Dummy URL for now
            elif user.role == "seller":
                return redirect("/seller/dashboard") # Dummy URL for now
            else:
                return redirect("/")
        else:
            flash("Login failed. Check email and password.", "danger")

    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))