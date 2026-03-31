import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from backend.extensions import db, bcrypt
from backend.models.user_model import User
from backend.models.seller_model import Seller

auth_bp = Blueprint("auth", __name__)

# --- CONFIGURATION FOR PROFILE UPLOADS ---
# Images yahan save hongi: frontend/static/images/profiles/
UPLOAD_FOLDER = 'frontend/static/images/profiles'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == "POST":
        # Purana data
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")
        
        # Naya Advanced Data (Phase 3)
        age = request.form.get("age")
        gender = request.form.get("gender")
        address = request.form.get("address")

        # 1. Check if email already exists
        if User.query.filter_by(email=email).first():
            flash("Email already registered! Please login.", "danger")
            return redirect(url_for("auth.register"))

        # 2. Profile Picture Handling
        file = request.files.get('profile_pic')
        profile_filename = "default_pro.png" # Default value

        if file and allowed_file(file.filename):
            # Create folder if it doesn't exist
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            
            # Save file with unique name
            ext = file.filename.rsplit('.', 1)[1].lower()
            profile_filename = f"user_{email.split('@')[0]}.{ext}"
            file.save(os.path.join(UPLOAD_FOLDER, profile_filename))

        # 3. Secure Password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # 4. Create User Object with New Fields
        new_user = User(
            name=name, 
            email=email, 
            password=hashed_password, 
            role=role,
            age=age,
            gender=gender,
            full_address=address,
            profile_pic=f"profiles/{profile_filename}" # Path saved in DB
        )
        
        db.session.add(new_user)
        db.session.commit()

        # 5. Seller Auto-Profile Setup
        if role == "seller":
            new_seller = Seller(user_id=new_user.id, company_name=f"{name}'s Store")
            db.session.add(new_seller)
            db.session.commit()

        flash("Account created successfully! Welcome to Vendora Pro.", "success")
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

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            
            # --- SESSION SYNC LOGIC ---
            # Browser storage ko batane ke liye ki user login ho gaya hai
            session['user_id'] = user.id 
            
            flash(f"Welcome back, {user.name}!", "success")
            
            if user.role == "admin":
                return redirect(url_for("admin.dashboard"))
            elif user.role == "seller":
                return redirect(url_for("seller.dashboard"))
            else:
                return redirect(url_for("customer.dashboard"))
        else:
            flash("Invalid credentials. Please try again.", "danger")

    return render_template("login.html")
# --- PROFILE & SETTINGS ROUTE ---
@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        # Details update karne ka logic
        current_user.name = request.form.get("name")
        current_user.age = request.form.get("age")
        current_user.gender = request.form.get("gender")
        current_user.full_address = request.form.get("address")
        
        # Profile Picture update (Optional)
        file = request.files.get('profile_pic')
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"user_{current_user.email.split('@')[0]}.{ext}"
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            current_user.profile_pic = f"profiles/{filename}"

        db.session.commit()
        flash("Profile updated successfully! ✨", "success")
        return redirect(url_for('auth.profile'))

    return render_template("profile.html", user=current_user)

@auth_bp.route("/change-password", methods=["POST"])
@login_required
def change_password():
    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    # 1. Check if current password is correct
    if not bcrypt.check_password_hash(current_user.password, old_password):
        flash("Current password is incorrect! ❌", "danger")
        return redirect(url_for('auth.profile'))

    # 2. Check if new passwords match
    if new_password != confirm_password:
        flash("New passwords do not match! ❌", "danger")
        return redirect(url_for('auth.profile'))

    # 3. Hash and Save new password
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    current_user.password = hashed_password
    db.session.commit()

    flash("Password updated successfully! ✅", "success")
    return redirect(url_for('auth.profile'))

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear() # Multi-tab sync ke liye session clear karna zaroori hai
    flash("Successfully logged out.", "info")
    return redirect(url_for("auth.login"))