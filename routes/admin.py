# routes/admin.py — Admin Panel Blueprint

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from utils.helpers import login_required, role_required
from models.student    import Student
from models.attendance import Attendance
from models.marks      import Marks
from models.fees       import Fees
from models.user       import User
from database.connection import get_db
from datetime import date, datetime
from bson import ObjectId

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def _is_demo():
    """Return the is_demo flag stored in session for this login."""
    return session.get("is_demo", False)


def admin_context():
    return {"user_name": session.get("name"), "user_role": "admin", "user_email": session.get("email")}


# ── DASHBOARD ─────────────────────────────────────────────────────────────────
@admin_bp.route("/dashboard")
@login_required
@role_required("admin")
def dashboard():
    return render_template("admin/dashboard.html", active="dashboard", **admin_context())


@admin_bp.route("/api/stats")
@login_required
@role_required("admin")
def stats():
    demo = _is_demo()
    db   = get_db()

    total_students = Student.count(is_demo=demo)
    today_total, today_present = Attendance.overall_today(is_demo=demo)
    att_pct = round(today_present / today_total * 100, 1) if today_total > 0 else 0

    months, present_counts, absent_counts = Attendance.monthly_trend(is_demo=demo)

    # Count only demo or real teachers
    total_teachers = db.users.count_documents({"role": "teacher", "is_demo": demo})
    total_users    = db.users.count_documents({"is_demo": demo})

    return jsonify({
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_users":    total_users,
        "attendance_pct": att_pct,
        "fees_collected": Fees.total_collected(is_demo=demo),
        "fees_pending":   Fees.total_pending(is_demo=demo),
        "months":         months,
        "present_counts": present_counts,
        "absent_counts":  absent_counts,
        "fee_breakdown":  Fees.breakdown_by_type(is_demo=demo),
    })


# ── STUDENTS ──────────────────────────────────────────────────────────────────
@admin_bp.route("/students")
@login_required
@role_required("admin")
def students():
    return render_template("admin/students.html", active="students", **admin_context())


@admin_bp.route("/api/students")
@login_required
@role_required("admin")
def api_students():
    page   = int(request.args.get("page", 1))
    search = request.args.get("search", "")
    cls    = request.args.get("class", "")
    students, total = Student.get_all(page=page, per_page=10, search=search, cls=cls, is_demo=_is_demo())
    return jsonify({"students": students, "total": total, "page": page})


@admin_bp.route("/api/students", methods=["POST"])
@login_required
@role_required("admin")
def add_student():
    data = request.get_json() or request.form.to_dict()
    if not data.get("name") or not data.get("email"):
        return jsonify({"success": False, "message": "Name and email are required."}), 400
    # New students created by real admin are real; demo admin creates demo students
    sid = Student.create(data, is_demo=_is_demo())
    return jsonify({"success": True, "message": "Student added successfully!", "id": sid})


@admin_bp.route("/api/students/<student_id>", methods=["PUT"])
@login_required
@role_required("admin")
def update_student(student_id):
    data = request.get_json()
    Student.update(student_id, data)
    return jsonify({"success": True, "message": "Student updated successfully!"})


@admin_bp.route("/api/students/<student_id>", methods=["DELETE"])
@login_required
@role_required("admin")
def delete_student(student_id):
    Student.delete(student_id)
    return jsonify({"success": True, "message": "Student deleted."})


@admin_bp.route("/api/students/<student_id>", methods=["GET"])
@login_required
@role_required("admin")
def get_student(student_id):
    s = Student.find_by_id(student_id)
    if not s:
        return jsonify({"error": "Student not found"}), 404
    return jsonify({"student": s})


# ── TEACHERS ──────────────────────────────────────────────────────────────────
@admin_bp.route("/teachers")
@login_required
@role_required("admin")
def teachers():
    return render_template("admin/teachers.html", active="teachers", **admin_context())


@admin_bp.route("/api/teachers")
@login_required
@role_required("admin")
def api_teachers():
    demo = _is_demo()
    db   = get_db()
    teachers = list(db.users.find({"role": "teacher", "is_demo": demo}, {"password": 0}))
    for t in teachers:
        t["_id"] = str(t["_id"])
        t["created_at"] = t["created_at"].strftime("%Y-%m-%d") if isinstance(t.get("created_at"), datetime) else str(t.get("created_at", ""))
    return jsonify({"teachers": teachers})


@admin_bp.route("/api/teachers", methods=["POST"])
@login_required
@role_required("admin")
def add_teacher():
    data = request.get_json()
    if not data.get("name") or not data.get("email") or not data.get("password"):
        return jsonify({"success": False, "message": "Name, email, and password are required."}), 400
    if User.find_by_email(data["email"]):
        return jsonify({"success": False, "message": "Email already exists."}), 400
    # Teachers added by real admin are real; by demo admin are demo
    uid = User.create(data["name"], data["email"], data["password"], "teacher", is_demo=_is_demo())
    return jsonify({"success": True, "message": "Teacher added successfully!", "id": uid})


@admin_bp.route("/api/teachers/<teacher_id>", methods=["DELETE"])
@login_required
@role_required("admin")
def delete_teacher(teacher_id):
    get_db().users.delete_one({"_id": ObjectId(teacher_id)})
    return jsonify({"success": True, "message": "Teacher removed."})


# ── ATTENDANCE ────────────────────────────────────────────────────────────────
@admin_bp.route("/attendance")
@login_required
@role_required("admin")
def attendance():
    return render_template("admin/attendance.html", active="attendance", **admin_context())


@admin_bp.route("/api/attendance/today")
@login_required
@role_required("admin")
def attendance_today():
    demo    = _is_demo()
    students, _ = Student.get_all(per_page=500, is_demo=demo)
    records     = Attendance.get_by_date(date.today().isoformat(), is_demo=demo)
    att_map     = {r["student_id"]: r["status"] for r in records}
    for s in students:
        s["attendance_status"] = att_map.get(s["student_id"], "not_marked")
    return jsonify({"students": students, "date": date.today().isoformat()})


@admin_bp.route("/api/attendance/mark", methods=["POST"])
@login_required
@role_required("admin")
def mark_attendance():
    demo    = _is_demo()
    data    = request.get_json()
    records = data.get("records", [])
    tid     = session.get("user_id")
    for r in records:
        Attendance.mark(r["student_id"], r["date"], r["status"], tid, is_demo=demo)
    return jsonify({"success": True, "message": f"Attendance saved for {len(records)} student(s)."})


@admin_bp.route("/api/attendance/monthly")
@login_required
@role_required("admin")
def attendance_monthly():
    year  = int(request.args.get("year",  date.today().year))
    month = int(request.args.get("month", date.today().month))
    return jsonify({"summary": Attendance.monthly_summary(year, month, is_demo=_is_demo())})


# ── MARKS ─────────────────────────────────────────────────────────────────────
@admin_bp.route("/marks")
@login_required
@role_required("admin")
def marks():
    return render_template("admin/marks.html", active="marks", **admin_context())


@admin_bp.route("/api/marks/add", methods=["POST"])
@login_required
@role_required("admin")
def add_marks():
    demo = _is_demo()
    d    = request.get_json()
    if not all(d.get(k) for k in ["student_id", "subject", "exam_type", "marks_obtained", "total_marks"]):
        return jsonify({"success": False, "message": "All fields are required."}), 400
    Marks.add(d["student_id"], d["subject"], d["exam_type"],
              d["marks_obtained"], d["total_marks"], session.get("user_id"), is_demo=demo)
    return jsonify({"success": True, "message": "Marks added successfully!"})


@admin_bp.route("/api/marks/student/<student_id>")
@login_required
@role_required("admin")
def student_marks(student_id):
    return jsonify({"marks": Marks.get_student_marks(student_id), "gpa": Marks.get_gpa(student_id)})


@admin_bp.route("/api/marks/ranklist")
@login_required
@role_required("admin")
def ranklist():
    return jsonify({"ranklist": Marks.ranklist(is_demo=_is_demo())})


@admin_bp.route("/api/marks/delete/<mark_id>", methods=["DELETE"])
@login_required
@role_required("admin")
def delete_mark(mark_id):
    Marks.delete(mark_id)
    return jsonify({"success": True, "message": "Mark deleted."})


@admin_bp.route("/api/marks/subjects")
@login_required
@role_required("admin")
def subjects():
    return jsonify({"subjects": Marks.subject_averages(is_demo=_is_demo())})


# ── FEES ──────────────────────────────────────────────────────────────────────
@admin_bp.route("/fees")
@login_required
@role_required("admin")
def fees():
    return render_template("admin/fees.html", active="fees", **admin_context())


@admin_bp.route("/api/fees/add", methods=["POST"])
@login_required
@role_required("admin")
def add_fee():
    demo = _is_demo()
    d    = request.get_json()
    if not all(d.get(k) for k in ["student_id", "amount", "fee_type", "due_date"]):
        return jsonify({"success": False, "message": "All fields are required."}), 400
    Fees.create(d["student_id"], d["amount"], d["fee_type"], d["due_date"], is_demo=demo)
    return jsonify({"success": True, "message": "Fee record added!"})


@admin_bp.route("/api/fees/pay/<fee_id>", methods=["POST"])
@login_required
@role_required("admin")
def pay_fee(fee_id):
    receipt = Fees.mark_paid(fee_id)
    return jsonify({"success": True, "receipt_no": receipt, "message": "Fee marked as paid!"})


@admin_bp.route("/api/fees/list")
@login_required
@role_required("admin")
def list_fees():
    demo = _is_demo()
    db   = get_db()
    pf   = request.args.get("paid", "")
    paid = True if pf == "true" else (False if pf == "false" else None)
    fees = Fees.get_all(paid=paid, is_demo=demo)
    for f in fees:
        s = db.students.find_one({"student_id": f["student_id"], "is_demo": demo})
        f["student_name"]  = s["name"]         if s else "Unknown"
        f["student_class"] = s.get("class","") if s else ""
    return jsonify({"fees": fees, "total_collected": Fees.total_collected(is_demo=demo), "total_pending": Fees.total_pending(is_demo=demo)})


@admin_bp.route("/api/fees/summary")
@login_required
@role_required("admin")
def fees_summary():
    demo = _is_demo()
    return jsonify({
        "collected": Fees.total_collected(is_demo=demo),
        "pending":   Fees.total_pending(is_demo=demo),
        "breakdown": Fees.breakdown_by_type(is_demo=demo),
    })


# ── PROFILE ───────────────────────────────────────────────────────────────────
@admin_bp.route("/profile")
@login_required
@role_required("admin")
def profile():
    return render_template("admin/profile.html", active="profile", **admin_context())


@admin_bp.route("/api/profile/update", methods=["POST"])
@login_required
@role_required("admin")
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
