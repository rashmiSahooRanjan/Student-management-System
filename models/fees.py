# models/fees.py

import random, string
from datetime import datetime
from bson import ObjectId
from database.connection import get_db


class Fees:

    @staticmethod
    def create(student_id, amount, fee_type, due_date, is_demo=False):
        get_db().fees.insert_one({
            "student_id": student_id,
            "amount":     float(amount),
            "fee_type":   fee_type,
            "due_date":   due_date,
            "paid":       False,
            "paid_date":  None,
            "receipt_no": None,
            "is_demo":    is_demo,
            "created_at": datetime.utcnow(),
        })

    @staticmethod
    def mark_paid(fee_id):
        receipt = "RCPT-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        get_db().fees.update_one(
            {"_id": ObjectId(fee_id)},
            {"$set": {"paid": True, "paid_date": datetime.utcnow().isoformat(), "receipt_no": receipt}},
        )
        return receipt

    @staticmethod
    def get_student_fees(student_id):
        records = list(get_db().fees.find({"student_id": student_id}).sort("due_date", -1))
        for r in records:
            r["_id"] = str(r["_id"])
            if hasattr(r.get("created_at"), "strftime"):
                r["created_at"] = r["created_at"].strftime("%Y-%m-%d")
        return records

    @staticmethod
    def get_all(paid=None, is_demo=False, limit=200):
        query = {"is_demo": is_demo}
        if paid is not None:
            query["paid"] = paid
        records = list(get_db().fees.find(query).sort("due_date", -1).limit(limit))
        for r in records:
            r["_id"] = str(r["_id"])
            if hasattr(r.get("created_at"), "strftime"):
                r["created_at"] = r["created_at"].strftime("%Y-%m-%d")
        return records

    @staticmethod
    def total_collected(is_demo=False):
        res = list(get_db().fees.aggregate([
            {"$match": {"paid": True, "is_demo": is_demo}},
            {"$group": {"_id": None, "t": {"$sum": "$amount"}}},
        ]))
        return res[0]["t"] if res else 0.0

    @staticmethod
    def total_pending(is_demo=False):
        res = list(get_db().fees.aggregate([
            {"$match": {"paid": False, "is_demo": is_demo}},
            {"$group": {"_id": None, "t": {"$sum": "$amount"}}},
        ]))
        return res[0]["t"] if res else 0.0

    @staticmethod
    def breakdown_by_type(is_demo=False):
        res = list(get_db().fees.aggregate([
            {"$match": {"paid": True, "is_demo": is_demo}},
            {"$group": {"_id": "$fee_type", "total": {"$sum": "$amount"}}},
        ]))
        return {r["_id"]: r["total"] for r in res}

    @staticmethod
    def seed_demo(student_ids):
        db = get_db()
        if db.fees.count_documents({"is_demo": True}) > 0:
            return
        types = [("tuition", 5000), ("exam", 1200), ("library", 500), ("transport", 2000)]
        for sid in student_ids:
            for ft, amt in types:
                Fees.create(sid, amt, ft, "2025-03-31", is_demo=True)
            recs = list(db.fees.find({"student_id": sid, "is_demo": True}))
            for r in random.sample(recs, k=random.randint(1, len(recs))):
                Fees.mark_paid(str(r["_id"]))
