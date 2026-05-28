from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from bson.objectid import ObjectId
from datetime import datetime
from database.db import courses, students

courses_bp = Blueprint('courses', __name__)

@courses_bp.route('/courses')
def courses_menu():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('courses_menu.html')

@courses_bp.route('/courses/update', methods=['GET', 'POST'])
def courses_update():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))

    course_id = request.args.get('course_id')
    edit_course = None
    if course_id:
        edit_course = courses.find_one({"_id": ObjectId(course_id)})

    if request.method == 'POST':
        course_name = request.form['course_name'].strip()
        course_code = request.form['course_code'].strip()
        duration = request.form['duration'].strip()
        course_fees = float(request.form['course_fees'])
        time_required = request.form['time_required'].strip()

        record = {
            "course_name": course_name,
            "course_code": course_code,
            "duration": duration,
            "course_fees": course_fees,
            "time_required": time_required,
            "updated_at": datetime.utcnow()
        }

        if request.form.get('course_id'):
            courses.update_one(
                {"_id": ObjectId(request.form['course_id'])},
                {"$set": record}
            )
            flash("Course updated successfully.", "success")
        else:
            existing = courses.find_one({"course_code": course_code})
            if existing:
                courses.update_one({"_id": existing['_id']}, {"$set": record})
                flash("Course updated successfully.", "success")
            else:
                record['created_at'] = datetime.utcnow()
                courses.insert_one(record)
                flash("Course added successfully.", "success")

        return redirect(url_for('courses.courses_update'))

    all_courses = list(courses.find().sort("course_name", 1))
    return render_template('courses_update.html', courses=all_courses, edit_course=edit_course)

@courses_bp.route('/courses/view')
def courses_view():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))

    all_courses = list(courses.find().sort("course_name", 1))
    return render_template('courses_view.html', courses=all_courses)
