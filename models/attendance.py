# models/attendance.py

import random
from datetime import datetime, date, timedelta
from bson import ObjectId
from database.connection import get_db


class Attendance:

    @staticmethod
    def mark(student_id, date_str, status, marked_by, is_demo=False):
        db       = get_db()
        existing = db.attendance.find_one({"student_id": student_id, "date": date_str})
        if existing:
            db.attendance.update_one(
                {"_id": existing["_id"]},
                {"$set": {"status": status, "marked_by": marked_by}}
            )
        else:
            db.attendance.insert_one({
                "student_id": student_id,
                "date":       date_str,
                "status":     status,
                "marked_by":  marked_by,
                "is_demo":    is_demo,
                "created_at": datetime.utcnow(),
            })

    @staticmethod
    def get_by_date(date_str, is_demo=False):
        db      = get_db()
        records = list(db.attendance.find({"date": date_str, "is_demo": is_demo}))
        for r in records:
            r["_id"] = str(r["_id"])
        return records

    @staticmethod
    def get_student_attendance(student_id, month=None, year=None):
        db    = get_db()
        query = {"student_id": student_id}
        if month and year:
            prefix        = f"{year}-{str(month).zfill(2)}"
            query["date"] = {"$regex": f"^{prefix}"}
        records = list(db.attendance.find(query).sort("date", -1))
        for r in records:
            r["_id"] = str(r["_id"])
        return records

    @staticmethod
    def get_percentage(student_id):
        db      = get_db()
        total   = db.attendance.count_documents({"student_id": student_id})
        present = db.attendance.count_documents({"student_id": student_id, "status": "present"})
        return round(present / total * 100, 1) if total > 0 else 0.0

    @staticmethod
    def overall_today(is_demo=False):
        db      = get_db()
        today   = date.today().isoformat()
        total   = db.attendance.count_documents({"date": today, "is_demo": is_demo})
        present = db.attendance.count_documents({"date": today, "is_demo": is_demo, "status": "present"})
        return total, present

    @staticmethod
    def monthly_summary(year, month, is_demo=False):
        db     = get_db()
        prefix = f"{year}-{str(month).zfill(2)}"
        records = list(db.attendance.find({"date": {"$regex": f"^{prefix}"}, "is_demo": is_demo}))
        summary = {}
        for r in records:
            d = r["date"]
            if d not in summary:
                summary[d] = {"present": 0, "absent": 0, "late": 0}
            s = r.get("status", "absent")
            summary[d][s] = summary[d].get(s, 0) + 1
        return summary

    @staticmethod
    def monthly_trend(is_demo=False):
        """Return 6-month present/absent counts for dashboard charts."""
        db = get_db()
        months, present_counts, absent_counts = [], [], []
        today = datetime.now()
        for i in range(5, -1, -1):
            # Go back i months
            month_dt = (today.replace(day=1) - timedelta(days=i * 28)).replace(day=1)
            prefix   = month_dt.strftime("%Y-%m")
            months.append(month_dt.strftime("%b"))
            present_counts.append(db.attendance.count_documents(
                {"date": {"$regex": f"^{prefix}"}, "is_demo": is_demo, "status": "present"}))
            absent_counts.append(db.attendance.count_documents(
                {"date": {"$regex": f"^{prefix}"}, "is_demo": is_demo, "status": "absent"}))
        return months, present_counts, absent_counts

    @staticmethod
    def seed_demo(student_ids):
        db = get_db()
        if db.attendance.count_documents({"is_demo": True}) > 0:
            return
        statuses = ["present", "present", "present", "present", "absent", "late"]
        today = date.today()
        # Seed last 30 days for each demo student
        for sid in student_ids:
            for day_offset in range(30):
                d      = today - timedelta(days=day_offset)
                if d.weekday() >= 5:   # skip weekends
                    continue
                status = random.choice(statuses)
                db.attendance.insert_one({
                    "student_id": sid,
                    "date":       d.isoformat(),
                    "status":     status,
                    "marked_by":  "demo_teacher",
                    "is_demo":    True,
                    "created_at": datetime.utcnow(),
                })
