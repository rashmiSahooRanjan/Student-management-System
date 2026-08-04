# models/marks.py

from datetime import datetime
from bson import ObjectId
from database.connection import get_db


class Marks:

    @staticmethod
    def add(student_id, subject, exam_type, marks_obtained, total_marks, teacher_id, is_demo=False):
        db  = get_db()
        pct = round(float(marks_obtained) / float(total_marks) * 100, 2)
        db.marks.insert_one({
            "student_id":     student_id,
            "subject":        subject,
            "exam_type":      exam_type,
            "marks_obtained": float(marks_obtained),
            "total_marks":    float(total_marks),
            "percentage":     pct,
            "grade":          Marks.get_grade(pct),
            "teacher_id":     teacher_id,
            "is_demo":        is_demo,
            "created_at":     datetime.utcnow(),
        })

    @staticmethod
    def get_grade(pct):
        if pct >= 90: return "A+"
        if pct >= 80: return "A"
        if pct >= 70: return "B+"
        if pct >= 60: return "B"
        if pct >= 50: return "C"
        if pct >= 40: return "D"
        return "F"

    @staticmethod
    def get_student_marks(student_id):
        db      = get_db()
        records = list(db.marks.find({"student_id": student_id}).sort("created_at", -1))
        for r in records:
            r["_id"] = str(r["_id"])
            if hasattr(r.get("created_at"), "strftime"):
                r["created_at"] = r["created_at"].strftime("%Y-%m-%d")
        return records

    @staticmethod
    def get_gpa(student_id):
        db    = get_db()
        marks = list(db.marks.find({"student_id": student_id}))
        if not marks:
            return 0.0
        avg = sum(m["percentage"] for m in marks) / len(marks)
        return round(avg / 100 * 4, 2)

    @staticmethod
    def delete(mark_id):
        get_db().marks.delete_one({"_id": ObjectId(mark_id)})

    @staticmethod
    def subject_averages(is_demo=False):
        pipeline = [
            {"$match": {"is_demo": is_demo}},
            {"$group": {"_id": "$subject", "avg": {"$avg": "$percentage"}, "count": {"$sum": 1}}},
            {"$sort": {"avg": -1}},
        ]
        return list(get_db().marks.aggregate(pipeline))

    @staticmethod
    def ranklist(is_demo=False, limit=20):
        db = get_db()
        # Get student_ids scoped to demo/real
        student_ids = [s["student_id"] for s in db.students.find({"is_demo": is_demo}, {"student_id": 1})]
        pipeline = [
            {"$match": {"student_id": {"$in": student_ids}}},
            {"$group": {"_id": "$student_id", "avg": {"$avg": "$percentage"}, "count": {"$sum": 1}}},
            {"$sort": {"avg": -1}},
            {"$limit": limit},
        ]
        ranks = list(db.marks.aggregate(pipeline))
        for i, r in enumerate(ranks):
            s         = db.students.find_one({"student_id": r["_id"]})
            r["rank"] = i + 1
            r["name"] = s["name"]         if s else "Unknown"
            r["class"]= s.get("class","") if s else ""
            r["avg"]  = round(r["avg"], 2)
        return ranks

    @staticmethod
    def seed_demo(student_ids):
        db = get_db()
        if db.marks.count_documents({"is_demo": True}) > 0:
            return
        import random
        subjects   = ["Mathematics", "Science", "English", "History", "Computer Science"]
        exam_types = ["mid_term", "final", "unit_test"]
        for sid in student_ids:
            for subj in subjects:
                for etype in exam_types:
                    obt = random.randint(52, 98)
                    Marks.add(sid, subj, etype, obt, 100, "demo_teacher", is_demo=True)
