# routes/teacher.py — Teacher Panel Blueprint

from flask import Blueprint, render_template, request, jsonify, session
from utils.helpers import login_required, role_required
from models.student    import Student
from models.attendance import Attendance
from models.marks      import Marks
from models.fees       import Fees
from models.user       import User
from database.connection import get_db
from datetime import date, datetime

teacher_bp = Blueprint("teacher", __name__, url_prefix="/teacher")


def _is_demo():
    return session.get("is_demo", False)


def teacher_context():
    return {"user_name": session.get("name"), "user_role": "teacher", "user_email": session.get("email")}


# ── DASHBOARD ─────────────────────────────────────────────────────────────────
@teacher_bp.route("/dashboard")
@login_required
@role_required("teacher")
def dashboard():
    return render_template("teacher/dashboard.html", active="dashboard", **teacher_context())


@teacher_bp.route("/api/stats")
@login_required
@role_required("teacher")
def stats():
    demo = _is_demo()
    total_students = Student.count(is_demo=demo)
    today_total, today_present = Attendance.overall_today(is_demo=demo)
    att_pct = round(today_present / today_total * 100, 1) if today_total > 0 else 0
    months, present_counts, absent_counts = Attendance.monthly_trend(is_demo=demo)

    return jsonify({
        "total_students": total_students,
        "attendance_pct": att_pct,
        "months":         months,
        "present_counts": present_counts,
        "absent_counts":  absent_counts,
        "subjects":       Marks.subject_averages(is_demo=demo),
    })


# ── STUDENTS (view only) ──────────────────────────────────────────────────────
@teacher_bp.route("/students")
@login_required
@role_required("teacher")
def students():
    return render_template("teacher/students.html", active="students", **teacher_context())


@teacher_bp.route("/api/students")
@login_required
@role_required("teacher")
def api_students():
    page   = int(request.args.get("page", 1))
    search = request.args.get("search", "")
    cls    = request.args.get("class", "")
    students, total = Student.get_all(page=page, per_page=10, search=search, cls=cls, is_demo=_is_demo())
    return jsonify({"students": students, "total": total, "page": page})


@teacher_bp.route("/api/students/<student_id>")
@login_required
@role_required("teacher")
def get_student(student_id):
    s = Student.find_by_id(student_id)
    if not s:
        return jsonify({"error": "Student not found"}), 404
    return jsonify({"student": s})


# ── ATTENDANCE ────────────────────────────────────────────────────────────────
@teacher_bp.route("/attendance")
@login_required
@role_required("teacher")
def attendance():
    return render_template("teacher/attendance.html", active="attendance", **teacher_context())


@teacher_bp.route("/api/attendance/today")
@login_required
@role_required("teacher")
def attendance_today():
    demo    = _is_demo()
    students, _ = Student.get_all(per_page=500, is_demo=demo)
    records     = Attendance.get_by_date(date.today().isoformat(), is_demo=demo)
    att_map     = {r["student_id"]: r["status"] for r in records}
    for s in students:
        s["attendance_status"] = att_map.get(s["student_id"], "not_marked")
    return jsonify({"students": students, "date": date.today().isoformat()})


@teacher_bp.route("/api/attendance/mark", methods=["POST"])
@login_required
@role_required("teacher")
def mark_attendance():
    demo    = _is_demo()
    data    = request.get_json()
    records = data.get("records", [])
    tid     = session.get("user_id")
    for r in records:
        Attendance.mark(r["student_id"], r["date"], r["status"], tid, is_demo=demo)
    return jsonify({"success": True, "message": f"Attendance saved for {len(records)} student(s)."})


@teacher_bp.route("/api/attendance/report")
@login_required
@role_required("teacher")
def attendance_report():
    sid   = request.args.get("student_id")
    month = request.args.get("month")
    year  = request.args.get("year")
    return jsonify({
        "records":    Attendance.get_student_attendance(sid, month, year),
        "percentage": Attendance.get_percentage(sid),
    })


# ── MARKS ─────────────────────────────────────────────────────────────────────
@teacher_bp.route("/marks")
@login_required
@role_required("teacher")
def marks():
    return render_template("teacher/marks.html", active="marks", **teacher_context())


@teacher_bp.route("/api/marks/add", methods=["POST"])
@login_required
@role_required("teacher")
def add_marks():
    demo = _is_demo()
    d    = request.get_json()
    if not all(d.get(k) for k in ["student_id", "subject", "exam_type", "marks_obtained", "total_marks"]):
        return jsonify({"success": False, "message": "All fields are required."}), 400
    Marks.add(d["student_id"], d["subject"], d["exam_type"],
              d["marks_obtained"], d["total_marks"], session.get("user_id"), is_demo=demo)
    return jsonify({"success": True, "message": "Marks added successfully!"})


@teacher_bp.route("/api/marks/student/<student_id>")
@login_required
@role_required("teacher")
def student_marks(student_id):
    return jsonify({"marks": Marks.get_student_marks(student_id), "gpa": Marks.get_gpa(student_id)})


@teacher_bp.route("/api/marks/delete/<mark_id>", methods=["DELETE"])
@login_required
@role_required("teacher")
def delete_mark(mark_id):
    Marks.delete(mark_id)
    return jsonify({"success": True, "message": "Mark deleted."})


@teacher_bp.route("/api/marks/ranklist")
@login_required
@role_required("teacher")
def ranklist():
    return jsonify({"ranklist": Marks.ranklist(is_demo=_is_demo())})


@teacher_bp.route("/api/marks/subjects")
@login_required
@role_required("teacher")
def subjects():
    return jsonify({"subjects": Marks.subject_averages(is_demo=_is_demo())})


# ── FEES (view only) ──────────────────────────────────────────────────────────
@teacher_bp.route("/fees")
@login_required
@role_required("teacher")
def fees():
    return render_template("teacher/fees.html", active="fees", **teacher_context())


@teacher_bp.route("/api/fees/student/<student_id>")
@login_required
@role_required("teacher")
def student_fees(student_id):
    return jsonify({"fees": Fees.get_student_fees(student_id)})


@teacher_bp.route("/api/fees/summary")
@login_required
@role_required("teacher")
def fees_summary():
    demo = _is_demo()
    return jsonify({
        "collected": Fees.total_collected(is_demo=demo),
        "pending":   Fees.total_pending(is_demo=demo),
    })


# ── PROFILE ───────────────────────────────────────────────────────────────────
@teacher_bp.route("/profile")
@login_required
@role_required("teacher")
def profile():
    return render_template("teacher/profile.html", active="profile", **teacher_context())


@teacher_bp.route("/api/profile/update", methods=["POST"])
@login_required
@role_required("teacher")
def update_profile():
    data    = request.get_json()
    uid     = session.get("user_id")
    allowed = ["name"]
    update  = {k: v for k, v in data.items() if k in allowed}
    if "password" in data and data["password"]:
        update["password"] = data["password"]
    User.update(uid, update)
    if "name" in update:
        session["name"] = update["name"]
    return jsonify({"success": True, "message": "Profile updated!"})
