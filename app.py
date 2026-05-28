# ========================================================
# Smart Student Management System
# Full Stack Flask Application
# Author: Grok (Built for Rashmi Ranjan)
# ========================================================

from flask import Flask, render_template, redirect, url_for, session, flash, request, send_from_directory
from flask_session import Session
from dotenv import load_dotenv
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
import os

# Load environment variables
load_dotenv()

# Initialize Flask App
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "super-secret-key-2026-change-in-production")

# Upload configuration
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Flask Session Configuration
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = 3600  # 1 hour

Session(app)

# ===================== DATABASE IMPORT =====================
from database.db import db, admins, students, attendance, marks, fees, courses

# ===================== BLUEPRINTS IMPORT =====================
from routes.auth import auth_bp
from routes.student import student_bp
from routes.attendance import attendance_bp
from routes.marks import marks_bp
from routes.fees import fees_bp
from routes.analytics import analytics_bp
from routes.courses import courses_bp

# ===================== REGISTER BLUEPRINTS =====================
app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(marks_bp)
app.register_blueprint(fees_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(courses_bp)

# ===================== GLOBAL CONTEXT PROCESSOR =====================
@app.context_processor
def inject_user():
    """Make admin info available in all templates"""
    if 'admin_id' in session:
        return {'admin_name': session.get('admin_name')}
    return {'admin_name': 'Guest'}

# ===================== MAIN ROUTES =====================

@app.route('/')
def index():
    """Homepage"""
    if 'admin_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Main Dashboard"""
    if 'admin_id' not in session:
        flash("Please login to access dashboard", "error")
        return redirect(url_for('auth.login'))
    
    total_students = students.count_documents({})

    pending_fees = 0
    for fee in fees.find({"status": {"$ne": "Paid"}}):
        pending_fees += float(fee.get("pending_amount", 0) or 0)

    total_attendance = attendance.count_documents({})
    present_count = attendance.count_documents({"status": "Present"})
    avg_attendance = round((present_count / total_attendance * 100), 2) if total_attendance else 0

    latest_marks = list(marks.aggregate([
        {"$sort": {"student_id": 1, "date": -1}},
        {"$group": {"_id": "$student_id", "gpa": {"$first": "$gpa"}}}
    ]))
    avg_gpa = round(sum(item.get("gpa", 0) for item in latest_marks) / len(latest_marks), 2) if latest_marks else 0

    context = {
        "total_students": total_students,
        "avg_attendance": avg_attendance,
        "pending_fees": pending_fees,
        "avg_gpa": avg_gpa
    }
    
    return render_template('dashboard.html', **context)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'admin_id' not in session:
        flash("Please login to access profile", "error")
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        admin_id = ObjectId(session['admin_id'])
        admin = admins.find_one({"_id": admin_id})
        if not admin:
            flash("Admin not found.", "error")
            return redirect(url_for('auth.login'))

        username = request.form.get('username', '').strip()
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        age = request.form.get('age', '').strip()
        password = request.form.get('password', '').strip()
        profile_pic = request.files.get('profile_pic')

        update_data = {}
        if username:
            update_data['username'] = username
        if full_name:
            update_data['full_name'] = full_name
            update_data['name'] = full_name
        if email:
            existing_admin = admins.find_one({"email": email, "_id": {"$ne": admin_id}})
            if existing_admin:
                flash("Email is already used by another account.", "error")
                return redirect(url_for('profile'))
            update_data['email'] = email
        if age:
            try:
                update_data['age'] = int(age)
            except ValueError:
                update_data['age'] = age
        if password:
            from werkzeug.security import generate_password_hash
            update_data['password'] = generate_password_hash(password)

        if profile_pic and profile_pic.filename:
            filename = secure_filename(profile_pic.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile_pic.save(upload_path)
            update_data['profile_pic'] = filename
            flash("Profile updated successfully!", "success")
        else:
            flash("Profile updated successfully!", "success")

        if update_data:
            admins.update_one({"_id": admin_id}, {"$set": update_data})
            if full_name:
                session['admin_name'] = full_name

    admin = None
    if 'admin_id' in session:
        admin = admins.find_one({"_id": ObjectId(session['admin_id'])})

    return render_template('profile.html', admin=admin)

# ===================== ERROR HANDLING =====================

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404  # Create 404.html later if needed

@app.errorhandler(500)
def internal_error(e):
    return "Internal Server Error. Please try again later.", 500

# ===================== RUN APP =====================

if __name__ == '__main__':
    print("🚀 Smart Student Management System Starting...")
    print("🌐 Access at: http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)