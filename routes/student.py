from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from bson.objectid import ObjectId
from database.db import students
import os

student_bp = Blueprint('student', __name__)

# ===================== STUDENT CRUD =====================

@student_bp.route('/students')
def all_students():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    
    search = request.args.get('search', '')
    filter_course = request.args.get('course', '')
    
    query = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"roll_no": {"$regex": search, "$options": "i"}}
        ]
    if filter_course:
        query["course"] = filter_course
    
    all_students = list(students.find(query).sort("name", 1))
    return render_template('students.html', students=all_students, search=search, course=filter_course)

@student_bp.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        student_data = {
            "name": request.form['name'],
            "roll_no": request.form['roll_no'],
            "email": request.form['email'],
            "phone": request.form['phone'],
            "course": request.form['course'],
            "semester": request.form['semester'],
            "address": request.form['address'],
            "attendance_percentage": 0.0,
            "fees_status": "Pending"
        }
        
        # Handle photo upload
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename != '':
                upload_path = os.path.join('uploads', photo.filename)
                photo.save(upload_path)
                student_data['photo'] = photo.filename
        
        students.insert_one(student_data)
        flash("Student added successfully!", "success")
        return redirect(url_for('student.all_students'))
    
    return render_template('add_student.html')

@student_bp.route('/edit_student/<student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    
    student = students.find_one({"_id": ObjectId(student_id)})
    
    if request.method == 'POST':
        update_data = {
            "name": request.form['name'],
            "roll_no": request.form['roll_no'],
            "email": request.form['email'],
            "phone": request.form['phone'],
            "course": request.form['course'],
            "semester": request.form['semester'],
            "address": request.form['address']
        }
        
        students.update_one({"_id": ObjectId(student_id)}, {"$set": update_data})
        flash("Student updated successfully!", "success")
        return redirect(url_for('student.all_students'))
    
    return render_template('edit_student.html', student=student)

@student_bp.route('/delete_student/<student_id>')
def delete_student(student_id):
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    
    students.delete_one({"_id": ObjectId(student_id)})
    flash("Student deleted successfully!", "success")
    return redirect(url_for('student.all_students'))

@student_bp.route('/student/<student_id>')
def view_student(student_id):
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    
    student = students.find_one({"_id": ObjectId(student_id)})
    return render_template('view_student.html', student=student)  # Optional