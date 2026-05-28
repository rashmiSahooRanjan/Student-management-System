from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise RuntimeError(
        "Missing environment variable MONGO_URI. Create a .env file with MONGO_URI=... (MongoDB Atlas connection string)."
    )

try:
    # Force an early connection attempt so errors are clearer
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
    )
    client.admin.command("ping")
except Exception as e:
    # Common Atlas SRV/DNS failure: _mongodb._tcp.<cluster>.mongodb.net
    # Provide an actionable hint. We also try a best-effort fallback for mongodb+srv -> mongodb.
    fallback = None
    if MONGO_URI.startswith("mongodb+srv://"):
        fallback = "mongodb://" + MONGO_URI[len("mongodb+srv://"):]

    if fallback:
        try:
            client = MongoClient(
                fallback,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
            )
            client.admin.command("ping")
            MONGO_URI = fallback
        except Exception:
            raise RuntimeError(
                "Failed to connect to MongoDB using MONGO_URI. "
                "Most likely Atlas SRV DNS is blocked/misconfigured in your network or the cluster hostname is wrong. "
                "Original error: " + str(e)
            )
    else:
        raise RuntimeError(
            "Failed to connect to MongoDB using MONGO_URI. "
            "Most likely Atlas SRV DNS is blocked/misconfigured in your network or the cluster hostname is wrong. "
            "Original error: " + str(e)
        )

db = client.get_database("studentdb")

# Collections
admins = db.admins
students = db.students
attendance = db.attendance
marks = db.marks
fees = db.fees
courses = db.courses