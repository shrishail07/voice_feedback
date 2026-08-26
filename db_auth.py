import streamlit as st
import hashlib
import os
import datetime
from supabase import create_client, Client

# ============================================================
# CONNECTION
# ============================================================

@st.cache_resource
def get_supabase_client() -> Client:
    """
    Reads SUPABASE_URL and SUPABASE_KEY from Streamlit secrets (or env vars).
    On Streamlit Cloud: Settings -> Secrets -> add
        SUPABASE_URL = "https://xxxxx.supabase.co"
        SUPABASE_KEY = "your-anon-or-service-role-key"
    """
    url = st.secrets.get("SUPABASE_URL", os.environ.get("SUPABASE_URL", ""))
    key = st.secrets.get("SUPABASE_KEY", os.environ.get("SUPABASE_KEY", ""))

    if not url or not key:
        st.error(
            "Supabase credentials not configured. "
            "Add SUPABASE_URL and SUPABASE_KEY under Streamlit Cloud → Settings → Secrets."
        )
        st.stop()

    try:
        return create_client(url, key)
    except Exception as e:
        st.error(f"Could not connect to Supabase: {e}")
        st.stop()


TABLE = "students"

# ============================================================
# PASSWORD HASHING (PBKDF2, stored as hex strings — Postgres friendly)
# ============================================================

def _hash_password(password, salt_hex=None):
    salt = bytes.fromhex(salt_hex) if salt_hex else os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return pwd_hash.hex(), salt.hex()


def _verify_password(password, salt_hex, stored_hash_hex):
    pwd_hash_hex, _ = _hash_password(password, salt_hex)
    return pwd_hash_hex == stored_hash_hex

# ============================================================
# AUTH ACTIONS
# ============================================================

def signup_student(roll_number, full_name, email, phone, college, department, password):
    roll_number = (roll_number or "").strip()
    full_name = (full_name or "").strip()

    if not roll_number or not full_name or not password:
        return False, "Roll number, name and password are required."

    client = get_supabase_client()

    existing = (
        client.table(TABLE)
        .select("roll_number")
        .eq("roll_number", roll_number)
        .execute()
    )
    if existing.data:
        return False, "An account with this roll number already exists. Please log in instead."

    pwd_hash_hex, salt_hex = _hash_password(password)

    row = {
        "roll_number": roll_number,
        "full_name": full_name,
        "email": (email or "").strip(),
        "phone": (phone or "").strip(),
        "college": (college or "").strip(),
        "department": (department or "").strip(),
        "password_hash": pwd_hash_hex,
        "password_salt": salt_hex,
        "created_at": datetime.datetime.utcnow().isoformat(),
    }

    try:
        client.table(TABLE).insert(row).execute()
    except Exception as e:
        return False, f"Signup failed: {e}"

    return True, "Account created successfully."


def login_student(roll_number, password):
    roll_number = (roll_number or "").strip()

    if not roll_number or not password:
        return False, "Roll number and password are required."

    client = get_supabase_client()

    try:
        result = (
            client.table(TABLE)
            .select("*")
            .eq("roll_number", roll_number)
            .execute()
        )
    except Exception as e:
        return False, f"Login failed: {e}"

    if not result.data:
        return False, "No account found with that roll number. Please sign up first."

    student = result.data[0]

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
