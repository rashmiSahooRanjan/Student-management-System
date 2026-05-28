from flask import Blueprint, render_template, session, jsonify, redirect, url_for
from database.db import students, attendance, fees

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
def analytics_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    
    total_students = students.count_documents({})
    total_attendance = attendance.count_documents({})
    present_count = attendance.count_documents({"status": "Present"})
    avg_attendance = round((present_count / total_attendance * 100), 2) if total_attendance else 0
    
    return render_template('analytics.html', total_students=total_students, avg_attendance=avg_attendance)

# API for Chart.js
@analytics_bp.route('/api/student_growth')
def student_growth():
    # Dummy data for chart - you can make it dynamic
    return jsonify({
        "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "students": [980, 1050, 1120, 1180, 1210, 1248]
    })

@analytics_bp.route('/api/attendance_trend')
def attendance_trend():
    pipeline = [
        {
            "$group": {
                "_id": "$date",
                "present": {"$sum": {"$cond": [{"$eq": ["$status", "Present"]}, 1, 0]}},
                "total": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}}
    ]

    trend_data = list(attendance.aggregate(pipeline))
    labels = [item["_id"] for item in trend_data]
    attendance_rate = [round((item["present"] / item["total"] * 100), 2) if item["total"] else 0 for item in trend_data]

    return jsonify({
        "labels": labels,
        "attendance": attendance_rate
    })