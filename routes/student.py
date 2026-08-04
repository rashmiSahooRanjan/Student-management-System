# routes/student.py — Student Panel Blueprint

from flask import Blueprint, render_template, request, jsonify, session
from utils.helpers import login_required, role_required
from models.student    import Student
from models.attendance import Attendance
from models.marks      import Marks
from models.fees       import Fees
from models.user       import User
from database.connection import get_db
from datetime import date

student_bp = Blueprint("student", __name__, url_prefix="/student")


def _is_demo():
    return session.get("is_demo", False)


def _get_linked_student():
    """
    Return the student record for this logged-in user.
    is_demo scoping ensures demo login → demo record, real login → real record.
    """
    email = session.get("email", "")
    return Student.find_by_email(email, is_demo=_is_demo())


def student_context():
    return {
        "user_name":  session.get("name"),
        "user_role":  "student",
        "user_email": session.get("email"),
    }


# ── DASHBOARD ─────────────────────────────────────────────────────────────────
@student_bp.route("/dashboard")
@login_required
@role_required("student")
def dashboard():
    return render_template("student/dashboard.html", active="dashboard", **student_context())


@student_bp.route("/api/stats")
@login_required
@role_required("student")
def stats():
    s = _get_linked_student()
    if not s:
        # Should not happen since register now always creates the record,
        # but handle gracefully just in case.
        return jsonify({"error": "no_record"}), 404

    sid        = s["student_id"]
    att_pct    = Attendance.get_percentage(sid)
    marks_list = Marks.get_student_marks(sid)
    gpa        = Marks.get_gpa(sid)
    fees_list  = Fees.get_student_fees(sid)

    pending_fees   = sum(f["amount"] for f in fees_list if not f.get("paid"))
    collected_fees = sum(f["amount"] for f in fees_list if f.get("paid"))

    recent_marks = sorted(marks_list, key=lambda x: x.get("created_at", ""), reverse=True)[:5]

    return jsonify({
        "student":        s,
        "attendance_pct": att_pct,
        "gpa":            gpa,
        "total_subjects": len(set(m["subject"] for m in marks_list)),
        "pending_fees":   pending_fees,
        "collected_fees": collected_fees,
        "recent_marks":   recent_marks,
    })


# ── PROFILE ───────────────────────────────────────────────────────────────────
@student_bp.route("/profile")
@login_required
@role_required("student")
def profile():
    return render_template("student/profile.html", active="profile", **student_context())


@student_bp.route("/api/profile")
@login_required
@role_required("student")
def get_profile():
    s = _get_linked_student()
    if not s:
        return jsonify({"error": "no_record"}), 404
    return jsonify({"student": s})


@student_bp.route("/api/profile/update", methods=["POST"])
@login_required
@role_required("student")
def update_profile():
    """
    Allow students to fill in their own profile details.
    Only safe fields are accepted — email and student_id cannot be changed.
    """
    s = _get_linked_student()
    if not s:
        return jsonify({"success": False, "message": "No student record found."}), 404

    data = request.get_json() or {}
    allowed = ["name", "phone", "dob", "gender", "address",
               "class", "section", "guardian_name", "guardian_phone"]
    update = {k: v for k, v in data.items() if k in allowed and v is not None}

    if not update:
        return jsonify({"success": False, "message": "No valid fields to update."}), 400

    # Use the MongoDB _id from the found record
    from bson import ObjectId
    db = get_db()
    db.students.update_one(
        {"student_id": s["student_id"]},
        {"$set": update}
    )

    # Also sync name to user account if name changed
    if "name" in update:
        uid = session.get("user_id")
        if uid:
            from models.user import User
            User.update(uid, {"name": update["name"]})
            session["name"] = update["name"]

    return jsonify({"success": True, "message": "Profile updated successfully!"})


# ── ATTENDANCE ────────────────────────────────────────────────────────────────
@student_bp.route("/attendance")
@login_required
@role_required("student")
def attendance():
    return render_template("student/attendance.html", active="attendance", **student_context())


@student_bp.route("/api/attendance")
@login_required
@role_required("student")
def get_attendance():
    s = _get_linked_student()
    if not s:
        return jsonify({"records": [], "percentage": 0, "student_id": None})

    sid     = s["student_id"]
    month   = request.args.get("month")
    year    = request.args.get("year")
    records = Attendance.get_student_attendance(sid, month, year)

    return jsonify({
        "records":    records,
        "percentage": Attendance.get_percentage(sid),
        "student_id": sid,
    })


# ── MARKS ─────────────────────────────────────────────────────────────────────
@student_bp.route("/marks")
@login_required
@role_required("student")
def marks():
    return render_template("student/marks.html", active="marks", **student_context())


@student_bp.route("/api/marks")
@login_required
@role_required("student")
def get_marks():
    s = _get_linked_student()
    if not s:
        return jsonify({"marks": [], "gpa": 0})

    sid = s["student_id"]
    return jsonify({
        "marks": Marks.get_student_marks(sid),
        "gpa":   Marks.get_gpa(sid),
    })


# ── FEES ──────────────────────────────────────────────────────────────────────
@student_bp.route("/fees")
@login_required
@role_required("student")
def fees():
    return render_template("student/fees.html", active="fees", **student_context())


@student_bp.route("/api/fees")
@login_required
@role_required("student")
def get_fees():
    s = _get_linked_student()
    if not s:
        return jsonify({"fees": [], "pending": 0, "collected": 0})

    sid      = s["student_id"]
    fee_list = Fees.get_student_fees(sid)

    return jsonify({
        "fees":      fee_list,
        "pending":   sum(f["amount"] for f in fee_list if not f.get("paid")),
        "collected": sum(f["amount"] for f in fee_list if f.get("paid")),
    })


# ── CHANGE PASSWORD ───────────────────────────────────────────────────────────
@student_bp.route("/api/change-password", methods=["POST"])
@login_required
@role_required("student")
def change_password():
    data = request.get_json() or {}
    pw   = data.get("password", "")
    if not pw or len(pw) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters."}), 400
    uid = session.get("user_id")
    User.update(uid, {"password": pw})
    return jsonify({"success": True, "message": "Password changed successfully!"})
