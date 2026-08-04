# routes/auth.py

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models.user import User, is_demo_account
from models.student import Student

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _ensure_student_record(name, email, is_demo=False):
    """
    If a student user has no linked student record, create one automatically.
    This makes the student visible to admin/teacher immediately after registration.
    """
    existing = Student.find_by_email(email, is_demo=is_demo)
    if not existing:
        Student.create({
            "name":  name,
            "email": email,
        }, is_demo=is_demo)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return _redirect_by_role(session.get("role"))

    if request.method == "POST":
        data     = request.get_json() or request.form
        email    = data.get("email", "").strip().lower()
        password = data.get("password", "")
        role     = data.get("role", "")

        user = User.find_by_email(email)
        if user and User.verify_password(user, password):
            if role and user["role"] != role:
                msg = f"This account is registered as '{user['role']}', not '{role}'."
                if request.is_json:
                    return jsonify({"success": False, "message": msg}), 401
                flash(msg, "danger")
                return render_template("login.html")

            demo = is_demo_account(user["email"])

            # Auto-create student record on first login if missing
            if user["role"] == "student":
                _ensure_student_record(user["name"], user["email"], is_demo=demo)

            session.permanent  = True
            session["user_id"] = str(user["_id"])
            session["name"]    = user["name"]
            session["email"]   = user["email"]
            session["role"]    = user["role"]
            session["is_demo"] = demo

            redirect_url = _get_dashboard_url(user["role"])
            if request.is_json:
                return jsonify({"success": True, "redirect": redirect_url})
            return redirect(redirect_url)

        msg = "Invalid email or password."
        if request.is_json:
            return jsonify({"success": False, "message": msg}), 401
        flash(msg, "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data     = request.get_json() or request.form
        name     = data.get("name", "").strip()
        email    = data.get("email", "").strip().lower()
        password = data.get("password", "")
        role     = data.get("role", "student")

        if not name or not email or not password:
            msg = "All fields are required."
            if request.is_json:
                return jsonify({"success": False, "message": msg}), 400
            flash(msg, "danger")
            return render_template("register.html")

        if len(password) < 6:
            msg = "Password must be at least 6 characters."
            if request.is_json:
                return jsonify({"success": False, "message": msg}), 400
            flash(msg, "danger")
            return render_template("register.html")

        if User.find_by_email(email):
            msg = "Email already registered."
            if request.is_json:
                return jsonify({"success": False, "message": msg}), 400
            flash(msg, "danger")
            return render_template("register.html")

        # Create the user account (never demo)
        User.create(name, email, password, role, is_demo=False)

        # If registering as student, immediately create a students record too
        # so admin/teacher can see this student right away
        if role == "student":
            _ensure_student_record(name, email, is_demo=False)

        if request.is_json:
            return jsonify({"success": True, "message": "Account created! Please login."})

        flash("Account created successfully! Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


def _get_dashboard_url(role):
    return {
        "admin":   "/admin/dashboard",
        "teacher": "/teacher/dashboard",
        "student": "/student/dashboard",
    }.get(role, "/auth/login")


def _redirect_by_role(role):
    return redirect(_get_dashboard_url(role))
