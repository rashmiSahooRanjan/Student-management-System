# models/student.py

import random, string
from datetime import datetime
from bson import ObjectId
from database.connection import get_db


class Student:

    @staticmethod
    def _gen_id():
        year   = datetime.now().year
        suffix = "".join(random.choices(string.digits, k=4))
        return f"STU-{year}-{suffix}"

    @staticmethod
    def _serialize(s):
        """Convert a raw MongoDB student doc to a JSON-safe dict."""
        if s is None:
            return None
        s["_id"] = str(s["_id"])
        if hasattr(s.get("created_at"), "strftime"):
            s["created_at"] = s["created_at"].strftime("%Y-%m-%d")
        if hasattr(s.get("updated_at"), "strftime"):
            s["updated_at"] = s["updated_at"].strftime("%Y-%m-%d")
        return s

    @staticmethod
    def create(data, is_demo=False):
        db  = get_db()
        doc = {
            "student_id":     Student._gen_id(),
            "name":           data.get("name", "").strip(),
            "email":          data.get("email", "").strip().lower(),
            "phone":          data.get("phone", ""),
            "dob":            data.get("dob", ""),
            "gender":         data.get("gender", ""),
            "address":        data.get("address", ""),
            "class":          data.get("class", ""),
            "section":        data.get("section", "A"),
            "guardian_name":  data.get("guardian_name", ""),
            "guardian_phone": data.get("guardian_phone", ""),
            "photo":          data.get("photo", None),
            "is_demo":        is_demo,
            "created_at":     datetime.utcnow(),
            "is_active":      True,
        }
        return str(db.students.insert_one(doc).inserted_id)

    @staticmethod
    def get_all(page=1, per_page=10, search="", cls="", is_demo=False):
        db    = get_db()
        query = {"is_demo": is_demo}
        if search:
            query["$or"] = [
                {"name":       {"$regex": search, "$options": "i"}},
                {"student_id": {"$regex": search, "$options": "i"}},
                {"email":      {"$regex": search, "$options": "i"}},
            ]
        if cls:
            query["class"] = cls
        total    = db.students.count_documents(query)
        students = list(
            db.students.find(query)
            .skip((page - 1) * per_page)
            .limit(per_page)
            .sort("created_at", -1)
        )
        return [Student._serialize(s) for s in students], total

    @staticmethod
    def find_by_id(student_id):
        db = get_db()
        s  = db.students.find_one({"_id": ObjectId(student_id)})
        return Student._serialize(s)

    @staticmethod
    def find_by_email(email, is_demo=False):
        """
        Find student record by email scoped to demo/real.
        Also handles records that may have been created before is_demo field existed.
        """
        db    = get_db()
        email = email.lower().strip()

        # Primary lookup — exact match with is_demo flag
        s = db.students.find_one({"email": email, "is_demo": is_demo})
        if s:
            return Student._serialize(s)

        # Fallback for real accounts: find records where is_demo field is missing
        # (created before the field was added) — only for non-demo users
        if not is_demo:
            s = db.students.find_one({"email": email, "is_demo": {"$exists": False}})
            if s:
                # Backfill the is_demo field so future lookups are clean
                db.students.update_one({"_id": s["_id"]}, {"$set": {"is_demo": False}})
                return Student._serialize(s)

        return None

    @staticmethod
    def update(student_id, data):
        data["updated_at"] = datetime.utcnow()
        get_db().students.update_one({"_id": ObjectId(student_id)}, {"$set": data})

    @staticmethod
    def delete(student_id):
        get_db().students.delete_one({"_id": ObjectId(student_id)})

    @staticmethod
    def count(is_demo=False):
        return get_db().students.count_documents({"is_demo": is_demo})

    @staticmethod
    def get_ids(is_demo=False):
        db = get_db()
        return [s["student_id"] for s in db.students.find({"is_demo": is_demo}, {"student_id": 1})]

    @staticmethod
    def seed_demo():
        db = get_db()
        if db.students.count_documents({"is_demo": True}) > 0:
            return
        demos = [
            {"name": "Alice Johnson",  "email": "alice@school.com",  "phone": "9876543210",
             "dob": "2006-03-15", "gender": "Female", "address": "123 Oak Street",
             "class": "10", "section": "A", "guardian_name": "Bob Johnson",   "guardian_phone": "9876543211"},
            {"name": "Bob Smith",      "email": "bob@school.com",    "phone": "9876543212",
             "dob": "2006-07-22", "gender": "Male",   "address": "456 Elm Street",
             "class": "10", "section": "B", "guardian_name": "Carol Smith",   "guardian_phone": "9876543213"},
            {"name": "Carol White",    "email": "carol@school.com",  "phone": "9876543214",
             "dob": "2007-01-10", "gender": "Female", "address": "789 Pine Street",
             "class": "9",  "section": "A", "guardian_name": "Dave White",    "guardian_phone": "9876543215"},
            {"name": "David Brown",    "email": "david@school.com",  "phone": "9876543216",
             "dob": "2007-05-18", "gender": "Male",   "address": "321 Maple Avenue",
             "class": "9",  "section": "B", "guardian_name": "Eve Brown",     "guardian_phone": "9876543217"},
            {"name": "Emma Davis",     "email": "emma@school.com",   "phone": "9876543218",
             "dob": "2008-11-03", "gender": "Female", "address": "654 Cedar Lane",
             "class": "8",  "section": "A", "guardian_name": "Frank Davis",   "guardian_phone": "9876543219"},
            {"name": "Frank Miller",   "email": "frank@school.com",  "phone": "9876543220",
             "dob": "2008-04-25", "gender": "Male",   "address": "987 Birch Road",
             "class": "8",  "section": "B", "guardian_name": "Grace Miller",  "guardian_phone": "9876543221"},
            {"name": "Grace Wilson",   "email": "grace@school.com",  "phone": "9876543222",
             "dob": "2009-08-14", "gender": "Female", "address": "147 Spruce Way",
             "class": "7",  "section": "A", "guardian_name": "Henry Wilson",  "guardian_phone": "9876543223"},
            {"name": "Henry Moore",    "email": "henry@school.com",  "phone": "9876543224",
             "dob": "2009-02-28", "gender": "Male",   "address": "258 Walnut Drive",
             "class": "7",  "section": "B", "guardian_name": "Irene Moore",   "guardian_phone": "9876543225"},
            # Linked to demo student login: student@school.com
            {"name": "Jane Student",   "email": "student@school.com","phone": "9876543226",
             "dob": "2007-06-12", "gender": "Female", "address": "999 School Road",
             "class": "10", "section": "A", "guardian_name": "James Student", "guardian_phone": "9876543227"},
        ]
        for d in demos:
            Student.create(d, is_demo=True)
