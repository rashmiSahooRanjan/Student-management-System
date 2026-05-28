from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from bson.objectid import ObjectId
from database.db import marks, students
from datetime import datetime
marks_bp = Blueprint('marks', __name__)

@marks_bp.route('/marks')
def all_marks():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    all_students = list(students.find())
    return render_template('marks.html', students=all_students)

@marks_bp.route('/add_marks/<student_id>', methods=['GET', 'POST'])
def add_marks(student_id):
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        subjects = request.form.getlist('subject[]')
        scores = request.form.getlist('score[]')
        
        total = sum(int(s) for s in scores)
        gpa = round(total / len(scores) / 25, 2)  # Simple GPA calculation
        
        marks.insert_one({
            "student_id": student_id,
            "subjects": dict(zip(subjects, scores)),
            "total_marks": total,
            "gpa": gpa,
            "date": datetime.utcnow()
        })
        
        flash("Marks added successfully!", "success")
        return redirect(url_for('marks.all_marks'))
    
    student = students.find_one({"_id": ObjectId(student_id)})
    return render_template('add_marks.html', student=student)