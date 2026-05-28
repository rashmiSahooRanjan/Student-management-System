from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.db import fees, students
from bson.objectid import ObjectId
from datetime import datetime

fees_bp = Blueprint('fees', __name__)

@fees_bp.route('/fees')
def fees_menu():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))

    return render_template('fees_menu.html')

@fees_bp.route('/fees/update', methods=['GET', 'POST'])
def fees_update():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))

    all_students = list(students.find())
    fee_records = list(fees.find())
    fee_map = {str(fee['student_id']): fee for fee in fee_records}

    if request.method == 'POST':
        student_id = request.form['student_id']
        course = request.form['course'].strip()
        pending_amount = float(request.form['pending_amount'])
        status = request.form['status']

        student = students.find_one({"_id": ObjectId(student_id)})
        student_name = student['name'] if student else None

        record = {
            "student_id": student_id,
            "student_name": student_name,
            "course": course,
            "pending_amount": pending_amount,
            "status": status,
            "updated_at": datetime.utcnow()
        }

        if status == 'Paid':
            record['payment_date'] = datetime.utcnow()
        else:
            record['payment_date'] = None

        fees.update_one(
            {"student_id": student_id},
            {"$set": record},
            upsert=True
        )

        flash("Fees record saved successfully!", "success")
        return redirect(url_for('fees.fees_update'))

    return render_template('fees_update.html', students=all_students, fee_map=fee_map)

@fees_bp.route('/fees/view')
def fees_view():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))

    all_fees = list(fees.find())
    return render_template('fees_view.html', fees=all_fees)
