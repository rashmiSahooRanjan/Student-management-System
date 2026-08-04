# database/connection.py — MongoDB Atlas connection helper

import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

_client = None
_db     = None


def get_db():
    """Return the database instance (lazy singleton)."""
    global _client, _db
    if _db is None:
        uri     = os.getenv("MONGO_URI", "mongodb://localhost:27017/student_management")
        _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        _db     = _client["student_management"]
        _setup_indexes(_db)
    return _db


def _setup_indexes(db):
    """Create indexes for performance (safe – idempotent)."""
    try:
        db.users.create_index("email",      unique=True)
        db.students.create_index("student_id", unique=True)
        db.students.create_index("email")
        db.attendance.create_index([("student_id", 1), ("date", 1)])
        db.marks.create_index([("student_id", 1), ("subject", 1)])
        db.fees.create_index("student_id")
    except Exception:
        pass   # Indexes may already exist


def close_db():
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db     = None
