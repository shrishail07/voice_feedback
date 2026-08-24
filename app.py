import streamlit as st
import os
from auth.auth_utils import signup_student, login_student, logout_student, is_authenticated

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Student Voice Feedback System",
    page_icon="🎤",
    layout="centered",
)

# ============================================================
# CUSTOM CSS — LOGIN CARD
# ============================================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f2027 0%, #1F4E79 50%, #2c5364 100%);
}

.login-card {
    background: #ffffff;
    padding: 2.5rem 2.5rem 1.5rem 2.5rem;
    border-radius: 18px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.35);
    max-width: 480px;
    margin: 1.5rem auto 0 auto;
}

h1, h2, h3, p, label, span {
    color: #0f2027;
}

.hero-title {
    text-align: center;
    color: white !important;
    font-size: 2.2rem;
    font-weight: 800;
    margin-bottom: 0;
}

.hero-subtitle {
    text-align: center;
    color: #d9e6f2 !important;
    font-size: 1rem;
    margin-top: 0.2rem;
    margin-bottom: 1.5rem;
}

div.stButton > button,
div.stFormSubmitButton > button {
    background-color: #1F4E79 !important;
    color: white !important;
    border-radius: 8px;
    border: none;
    height: 3em;
    width: 100%;
    font-weight: bold;
    transition: 0.2s;
}

div.stButton > button:hover,
div.stFormSubmitButton > button:hover {
    background-color: #163a5c !important;
}

input {
    color: #0f2027 !important;
}

[data-testid="stTabs"] button p {
    font-weight: 600;
    color: #0f2027 !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HERO HEADER
# ============================================================

st.markdown('<p class="hero-title">🎤 Student Voice Feedback System</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">PragyanAI · Grow with Gyan</p>', unsafe_allow_html=True)

cover_path = os.path.join("assets", "pragyan_ai_school_cover.jpg")
if os.path.exists(cover_path):
    st.image(cover_path, use_container_width=True)

# ============================================================
# ALREADY LOGGED IN
# ============================================================

if is_authenticated():
    student = st.session_state["student"]

    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.success(f"✅ You're logged in as **{student['full_name']}** ({student['roll_number']})")
    st.write("Use the sidebar to navigate to **Record Feedback** or the **Analysis Dashboard**.")

    if st.button("Log Out"):
        logout_student()
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ============================================================
# LOGIN / SIGNUP CARD
# ============================================================

st.markdown('<div class="login-card">', unsafe_allow_html=True)

tab_login, tab_signup = st.tabs(["🔑 Login", "📝 Sign Up"])

# ---------------- LOGIN TAB ----------------
with tab_login:
    with st.form("login_form"):
        st.subheader("Welcome back")

        roll_number = st.text_input("Roll Number", key="login_roll")
        password = st.text_input("Password", type="password", key="login_pass")

        submitted = st.form_submit_button("Login")

        if submitted:
            success, message = login_student(roll_number, password)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

# ---------------- SIGNUP TAB ----------------
with tab_signup:
    with st.form("signup_form"):
        st.subheader("Create your account")

        col1, col2 = st.columns(2)

        with col1:
            su_name = st.text_input("Full Name *")
            su_roll = st.text_input("Roll Number *")
            su_college = st.text_input("College Name")

        with col2:
            su_email = st.text_input("Email")
            su_phone = st.text_input("Phone Number")
            su_dept = st.text_input("Department")

        su_password = st.text_input("Create Password *", type="password")
        su_password_confirm = st.text_input("Confirm Password *", type="password")

        signup_submitted = st.form_submit_button("Create Account")

        if signup_submitted:
            if su_password != su_password_confirm:
                st.error("Passwords do not match.")
            else:
                success, message = signup_student(
                    su_roll, su_name, su_email, su_phone,
                    su_college, su_dept, su_password
                )
                if success:
                    st.success(message + " Switch to the Login tab.")
                else:
                    st.error(message)

st.markdown('</div>', unsafe_allow_html=True)
