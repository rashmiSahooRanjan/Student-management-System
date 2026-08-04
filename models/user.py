# models/user.py

from datetime import datetime
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from database.connection import get_db

# The 3 built-in demo email addresses
DEMO_EMAILS = {
    "admin@school.com",
    "teacher@school.com",
    "student@school.com",
}

def is_demo_account(email: str) -> bool:
    """Return True if this is a built-in demo account."""
    return (email or "").strip().lower() in DEMO_EMAILS


class User:
    ROLES = ("admin", "teacher", "student")

    @staticmethod
    def create(name, email, password, role="student", is_demo=False):
        db = get_db()
        doc = {
            "name":       name,
            "email":      email.lower().strip(),
            "password":   generate_password_hash(password),
            "role":       role,
            "is_demo":    is_demo,
            "created_at": datetime.utcnow(),
            "is_active":  True,
        }
        result = db.users.insert_one(doc)
        return str(result.inserted_id)

    @staticmethod
    def find_by_email(email):
        return get_db().users.find_one({"email": email.lower().strip()})

    @staticmethod
    def find_by_id(user_id):
        return get_db().users.find_one({"_id": ObjectId(user_id)})

    @staticmethod
    def verify_password(user, password):
        return check_password_hash(user["password"], password)

    @staticmethod
    def update(user_id, data):
        if "password" in data:
            data["password"] = generate_password_hash(data["password"])
        get_db().users.update_one({"_id": ObjectId(user_id)}, {"$set": data})

    @staticmethod
    def seed_admin():
        """Create default demo accounts (flagged is_demo=True)."""
        defaults = [
            ("Administrator", "admin@school.com",   "admin123",   "admin"),
            ("John Teacher",  "teacher@school.com", "teacher123", "teacher"),
            ("Jane Student",  "student@school.com", "student123", "student"),
        ]
        for name, email, pwd, role in defaults:
            if not User.find_by_email(email):
                User.create(name, email, pwd, role, is_demo=True)
            else:
                # Ensure existing demo accounts are flagged
                get_db().users.update_one(
                    {"email": email},
                    {"$set": {"is_demo": True}}
                )
