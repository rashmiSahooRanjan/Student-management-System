from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.db import attendance, students
from datetime import datetime

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/attendance')
def attendance_menu():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))

    return render_template('attendance_menu.html')

@attendance_bp.route('/attendance/update', methods=['GET', 'POST'])
def attendance_update():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        date = request.form['date']
        for key, value in request.form.items():
            if key.startswith('student_'):
                student_id = key.split('_')[1]
                status = value  # 'Present' or 'Absent'

                attendance.update_one(
                    {"student_id": student_id, "date": date},
                    {
                        "$set": {
                            "student_id": student_id,
                            "date": date,
                            "status": status,
                            "timestamp": datetime.utcnow()
                        }
                    },
                    upsert=True
                )

        flash("Attendance marked successfully!", "success")
        return redirect(url_for('attendance.attendance_update', update_date=date))

    all_students = list(students.find())
    today = datetime.now().strftime("%Y-%m-%d")
    selected_date = request.args.get('update_date', today)

    return render_template(
        'attendance.html',
        students=all_students,
        today=today,
        selected_date=selected_date
    )

@attendance_bp.route('/attendance/view')
def attendance_view():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))

    all_students = list(students.find())
    today = datetime.now().strftime("%Y-%m-%d")
    selected_date = request.args.get('report_date', today)
    attendance_records = list(attendance.find({"date": selected_date}))
    attendance_map = {str(record['student_id']): record for record in attendance_records}

    present_count = attendance.count_documents({"date": selected_date, "status": "Present"})
    absent_count = attendance.count_documents({"date": selected_date, "status": "Absent"})
    total_students = len(all_students)
    present_average = round((present_count / total_students * 100), 2) if total_students else 0
    absent_average = round((absent_count / total_students * 100), 2) if total_students else 0

    return render_template(
        'attendance_view.html',
        students=all_students,
        selected_date=selected_date,
        attendance_map=attendance_map,
        present_count=present_count,
        absent_count=absent_count,
        total_students=total_students,
        present_average=present_average,
        absent_average=absent_average
    )

@attendance_bp.route('/attendance_report')
def attendance_report():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    
    reports = []
    all_students = list(students.find())
    
    for student in all_students:
        total = attendance.count_documents({"student_id": str(student['_id'])})
        present = attendance.count_documents({"student_id": str(student['_id']), "status": "Present"})
        percentage = round((present / total * 100), 2) if total > 0 else 0
        
        reports.append({
            "student": student,
            "total_days": total,
            "present_days": present,
            "percentage": percentage
        })
    
    return render_template('attendance_report.html', reports=reports)