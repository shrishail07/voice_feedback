import streamlit as st
import hashlib
import os
import datetime
import certifi
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

# ============================================================
# CONNECTION
# ============================================================

@st.cache_resource
def get_mongo_client():
    """
    Reads MONGO_URI from Streamlit secrets (or env var as fallback).
    On Streamlit Cloud: Settings -> Secrets -> add
        MONGO_URI = "mongodb+srv://user:password@cluster.mongodb.net/?retryWrites=true&w=majority"
    """
    uri = st.secrets.get("MONGO_URI", os.environ.get("MONGO_URI", ""))

    if not uri:
        st.error(
            "MongoDB connection string not configured. "
            "Add MONGO_URI under Streamlit Cloud → Settings → Secrets."
        )
        st.stop()

    try:
        client = MongoClient(
            uri,
            tls=True,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000,
        )
        client.admin.command("ping")  # fail fast if URI/creds are wrong
        return client
    except Exception as e:
        st.error(f"Could not connect to MongoDB: {e}")
        st.stop()


def get_students_collection():
    client = get_mongo_client()
    db = client["pragyanai_feedback"]
    collection = db["students"]
    collection.create_index("roll_number", unique=True)
    return collection

# ============================================================
# PASSWORD HASHING (PBKDF2 — no extra native dependency needed)
# ============================================================

def _hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return pwd_hash, salt


def _verify_password(password, salt, stored_hash):
    pwd_hash, _ = _hash_password(password, salt)
    return pwd_hash == stored_hash

# ============================================================
# AUTH ACTIONS
# ============================================================

def signup_student(roll_number, full_name, email, phone, college, department, password):
    roll_number = (roll_number or "").strip()
    full_name = (full_name or "").strip()

    if not roll_number or not full_name or not password:
        return False, "Roll number, name and password are required."

    collection = get_students_collection()

    if collection.find_one({"roll_number": roll_number}):
        return False, "An account with this roll number already exists. Please log in instead."

    pwd_hash, salt = _hash_password(password)

    doc = {
        "roll_number": roll_number,
        "full_name": full_name,
        "email": (email or "").strip(),
        "phone": (phone or "").strip(),
        "college": (college or "").strip(),
        "department": (department or "").strip(),
        "password_hash": pwd_hash,
        "password_salt": salt,
        "created_at": datetime.datetime.utcnow(),
    }

    try:
        collection.insert_one(doc)
    except DuplicateKeyError:
        return False, "An account with this roll number already exists. Please log in instead."

    return True, "Account created successfully."


def login_student(roll_number, password):
    roll_number = (roll_number or "").strip()

    if not roll_number or not password:
        return False, "Roll number and password are required."

    collection = get_students_collection()
    student = collection.find_one({"roll_number": roll_number})

    if not student:
        return False, "No account found with that roll number. Please sign up first."

    if not _verify_password(password, student["password_salt"], student["password_hash"]):
        return False, "Incorrect password."

    st.session_state["authenticated"] = True
    st.session_state["student"] = {
        "full_name": student["full_name"],
        "roll_number": student["roll_number"],
        "email": student.get("email", ""),
        "phone": student.get("phone", ""),
        "college": student.get("college", ""),
        "department": student.get("department", ""),
    }

    return True, f"Welcome back, {student['full_name']}!"


def logout_student():
    st.session_state["authenticated"] = False
    st.session_state.pop("student", None)


def is_authenticated():
    return st.session_state.get("authenticated", False)
