from flask import Blueprint, request, redirect, url_for, flash, render_template, session
import models
from functools import wraps

# ---------------- Decorators ---------------- #
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_id"):
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

def master_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("admin_role") != "master":
            flash("You do not have permission to perform this action.", "danger")
            return redirect(url_for("admin.dashboard"))
        return f(*args, **kwargs)
    return decorated_function

# ---------------- Blueprint ---------------- #
auth = Blueprint("auth", __name__)

# ---------------- Registration ---------------- #
@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        password2 = request.form.get("password2")
        if not username or not password:
            flash("Username and password required.", "warning")
            return redirect(url_for("auth.register"))
        if password != password2:
            flash("Passwords do not match.", "warning")
            return redirect(url_for("auth.register"))
        if models.get_admin_by_username(username):
            flash("Username already exists.", "warning")
            return redirect(url_for("auth.register"))
        models.create_admin(username, password, role="admin")  # regular admin
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html")

# ---------------- Login ---------------- #
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        admin = models.get_admin_by_username(username)
        if admin and models.verify_password(admin["password_hash"], password):
            session["admin_id"] = admin["id"]
            session["admin_role"] = admin["role"] if "role" in admin.keys() else "admin"
            flash("Login successful!", "success")
            return redirect(url_for("admin.dashboard"))
        else:
            flash("Invalid username or password", "danger")
    return render_template("login.html")

# ---------------- Logout ---------------- #
@auth.route("/logout")
def logout():
    session.pop("admin_id", None)
    session.pop("admin_role", None)
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth.login"))
