import streamlit as st
import pandas as pd
from textblob import TextBlob
import plotly.express as px
import datetime
import io
import os
import numpy as np
from PIL import Image
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from supabase_auth import signup_student, login_student, logout_student, is_authenticated
from events_db import get_events, add_event

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Student Voice Feedback System",
    page_icon="🎤",
    layout="wide"
)

if os.path.exists("pragyan_ai_school_cover.jpg"):
    st.image("pragyan_ai_school_cover.jpg", width='stretch')

# ============================================================
# OPTIONAL: OPENCV FACE DETECTION
# Wrapped so a broken / missing OpenCV build never crashes the
# app — it just disables face verification silently in the UI.
# ============================================================

HAS_CV2 = False
FACE_CASCADE = None

try:
    import cv2
    if hasattr(cv2, "CascadeClassifier") and hasattr(cv2, "data"):
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        if os.path.exists(cascade_path):
            FACE_CASCADE = cv2.CascadeClassifier(cascade_path)
            if not FACE_CASCADE.empty():
                HAS_CV2 = True
except Exception:
    HAS_CV2 = False

# ============================================================
# OPTIONAL: SPEECH RECOGNITION
# ============================================================

try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False

# ============================================================
# CONFIGURATION
# ============================================================

EXCEL_FILE = "feedback_data.xlsx"
ADMIN_PASSWORD = "PRAGYANAI"

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

COLUMNS = [
    'Timestamp', 'Student_Name', 'Roll_Number', 'College_Name',
    'Department_name', 'E_mail', 'Phone_number', 'Event_Name',
    'Face_Detected', 'Transcript', 'Sentiment', 'Polarity',
    'Photo_Path', 'Audio_Path'
]


def save_uploaded_file(file_bytes, prefix, roll_no, extension):
    """Saves bytes to /uploads with a unique name, returns the relative path."""
    safe_roll = "".join(c for c in str(roll_no) if c.isalnum()) or "unknown"
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{safe_roll}_{timestamp}.{extension}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(file_bytes)
    return filepath

# ============================================================
# CSS — WHITE BACKGROUND / BLACK BUTTONS / WHITE BUTTON TEXT
# ============================================================

st.markdown("""
<style>
.stApp { background-color: #ffffff; }
h1, h2, h3, h4, h5, h6, p, label, span, div { color: #000000; }

div.stButton > button,
div.stDownloadButton > button,
div.stFormSubmitButton > button {
    background-color: #000000 !important;
    color: #ffffff !important;
    border-radius: 8px;
    border: none;
    height: 3em;
    font-weight: 600;
    transition: background-color 0.2s ease;
}
div.stButton > button *,
div.stDownloadButton > button *,
div.stFormSubmitButton > button * { color: #ffffff !important; }

div.stButton > button:hover,
div.stDownloadButton > button:hover,
div.stFormSubmitButton > button:hover { background-color: #333333 !important; }

input, textarea {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    background-color: #ffffff !important;
}
.stTextInput > div > div > input, .stTextArea textarea {
    border: 1px solid #000000 !important;
    border-radius: 6px;
}
section[data-testid="stSidebar"] { background-color: #f5f5f5; border-right: 1px solid #ddd; }
div[data-testid="stMetric"] { background-color: #f9f9f9; border: 1px solid #eee; border-radius: 10px; padding: 10px; }
button[data-baseweb="tab"] { font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# LOGIN / SIGNUP GATE (Supabase-backed)
# Signed-up students never see the signup form again — they
# just log in with roll number + password.
# ============================================================

if not is_authenticated():

    st.title("🎤 Student Voice Feedback System")
    st.caption("PragyanAI · Grow with Gyan")

    tab_login, tab_signup = st.tabs(["🔑 Login", "📝 Sign Up"])

    with tab_login:
        with st.form("login_form"):
            st.subheader("Welcome back")
            l_roll = st.text_input("Roll Number", key="login_roll")
            l_password = st.text_input("Password", type="password", key="login_pass")
            login_submitted = st.form_submit_button("Login")

            if login_submitted:
                success, message = login_student(l_roll, l_password)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    with tab_signup:
        with st.form("signup_form"):
            st.subheader("Create your account")

            sc1, sc2 = st.columns(2)
            with sc1:
                su_name = st.text_input("Full Name *")
                su_roll = st.text_input("Roll Number *")
                su_college = st.text_input("College Name")
            with sc2:
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
                        st.success(message + " Switch to the Login tab to sign in.")
                    else:
                        st.error(message)

    st.stop()

# From here on, the student is authenticated.
student = st.session_state["student"]

# ============================================================
# EXCEL HELPERS
# ============================================================

def create_excel_if_not_exists():
    if not os.path.exists(EXCEL_FILE):
        wb = Workbook()
        ws = wb.active
        ws.title = "Feedback Data"
        header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        thin_border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )
        for col_idx, header in enumerate(COLUMNS, 1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")
            cell.border = thin_border
        wb.save(EXCEL_FILE)


def append_to_excel(record):
    create_excel_if_not_exists()
    try:
        wb = load_workbook(EXCEL_FILE)
        ws = wb.active
        ws.append([record.get(col, '') for col in COLUMNS])
        wb.save(EXCEL_FILE)
        return True
    except Exception as e:
        st.error(f"Excel Save Error: {e}")
        return False


def load_from_excel():
    create_excel_if_not_exists()
    try:
        df = pd.read_excel(EXCEL_FILE, engine='openpyxl', header=0)
        if df.empty:
            return pd.DataFrame(columns=COLUMNS)
        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        if 'Polarity' in df.columns:
            df['Polarity'] = pd.to_numeric(df['Polarity'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Excel Load Error: {e}")
        return pd.DataFrame(columns=COLUMNS)


def get_excel_download():
    if os.path.exists(EXCEL_FILE):
        with open(EXCEL_FILE, "rb") as f:
            return f.read()
    return None

# ============================================================
# LOGIC
# ============================================================

def analyze_sentiment(text):
    if not text:
        return "Neutral", 0.0
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        return "Positive", polarity
    elif polarity < -0.1:
        return "Negative", polarity
    return "Neutral", polarity


def detect_faces(image_bytes):
    """Never raises. Falls back gracefully if OpenCV is unavailable/broken."""
    if not HAS_CV2 or FACE_CASCADE is None:
        try:
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            return img, 0, False
        except Exception:
            return None, 0, False
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img_bgr is None:
            return None, 0, False
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        faces = FACE_CASCADE.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))
        pil_img = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
        return pil_img, len(faces), len(faces) > 0
    except Exception:
        return None, 0, False


def transcribe_audio(audio_bytes):
    if not HAS_SR:
        return "SpeechRecognition not installed."
    r = sr.Recognizer()
    try:
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio = r.record(source)
            return r.recognize_google(audio)
    except Exception:
        return "Audio Transcription Error"

# ============================================================
# MAIN APP
# ============================================================

st.title("🎤 Student Voice Feedback System")

st.sidebar.success(f"👤 {student['full_name']} ({student['roll_number']})")
if st.sidebar.button("Log Out"):
    logout_student()
    st.rerun()

if not HAS_CV2:
    st.sidebar.warning(
        "⚠️ Face verification is disabled on this server "
        "(OpenCV face detector unavailable). Feedback submission still works."
    )

page = st.sidebar.radio("Navigate", ["Record Feedback", "Analysis Dashboard"])

st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Admin Access")
pwd_input = st.sidebar.text_input("Enter Password", type="password")
is_admin = (pwd_input == ADMIN_PASSWORD)

if is_admin:
    st.sidebar.success("Access Granted")
    excel_data = get_excel_download()
    if excel_data:
        st.sidebar.download_button(
            "📥 Download Excel", excel_data, "feedback_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with st.sidebar.expander("➕ Add New Event"):
        new_event_name = st.text_input("Event Name", key="new_event_input")
        if st.button("Add Event", key="add_event_btn"):
            success, msg = add_event(new_event_name)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

elif pwd_input != "":
    st.sidebar.error("Incorrect Password")

# ------------------------------------------------------------
# PAGE 1 — RECORD FEEDBACK
# ------------------------------------------------------------

if page == "Record Feedback":

    st.header("Submit Your Feedback")

    col1, col2 = st.columns(2)
    with col1:
        s_name = st.text_input("Full Name *", value=student['full_name'], disabled=True)
        s_roll = st.text_input("Roll Number *", value=student['roll_number'], disabled=True)
        s_college = st.text_input("College Name", value=student.get('college', ''))
    with col2:
        event_options = get_events()
        s_event = st.selectbox("Event", event_options)
        s_email = st.text_input("Email", value=student.get('email', ''))
        s_phone = st.text_input("Phone Number", value=student.get('phone', ''))

    st.subheader("📸 Capture Photo")
    img_file = st.camera_input("Take Photo")

    st.subheader("🎙️ Feedback")
    with st.form("feedback_form"):
        audio_data = st.audio_input("Record Voice")
        text_data = st.text_area("Or Type Feedback")
        submitted = st.form_submit_button("Submit Feedback")

    if submitted:
        if not s_name or not s_roll:
            st.error("Name and Roll Number required!")
        else:
            transcript = transcribe_audio(audio_data.getvalue()) if audio_data else text_data
            sentiment, score = analyze_sentiment(transcript)

            face_verified = False
            photo_path = ""
            audio_path = ""

            if img_file:
                _, _, face_verified = detect_faces(img_file.getvalue())
                photo_path = save_uploaded_file(img_file.getvalue(), "photo", s_roll, "jpg")

            if audio_data:
                audio_path = save_uploaded_file(audio_data.getvalue(), "audio", s_roll, "wav")

            record = {
                'Timestamp': datetime.datetime.now(),
                'Student_Name': s_name,
                'Roll_Number': s_roll,
                'College_Name': s_college,
                'Department_name': "General",
                'E_mail': s_email,
                'Phone_number': s_phone,
                'Event_Name': s_event,
                'Face_Detected': face_verified,
                'Transcript': transcript,
                'Sentiment': sentiment,
                'Polarity': score,
                'Photo_Path': photo_path,
                'Audio_Path': audio_path
            }

            if append_to_excel(record):
                st.success(f"✅ Feedback Saved! Sentiment: {sentiment}")
                st.balloons()

# ------------------------------------------------------------
# PAGE 2 — ANALYTICS DASHBOARD
# ------------------------------------------------------------

elif page == "Analysis Dashboard":

    st.header("📊 Feedback Analysis Dashboard")

    df = load_from_excel()

    required_cols = ['Timestamp', 'Student_Name', 'Roll_Number', 'Event_Name', 'Sentiment', 'Polarity']
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        st.error(f"❌ Missing columns in Excel: {missing_cols}")
        st.stop()

    if df.empty:
        st.warning("⚠️ No data available yet. Submit feedback first.")
        st.stop()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Active Users", len(df))
    m2.metric("Unique Students", df['Roll_Number'].nunique())
    positive_percent = round((df['Sentiment'] == "Positive").mean() * 100, 2)
    m3.metric("Positive %", f"{positive_percent}%")
    m4.metric("Avg Polarity", round(df['Polarity'].mean(), 2))

    st.markdown("---")

    tabs = ["📌 Event Analysis", "👨‍🎓 Student Analysis", "😊 Sentiment Analysis", "📂 Raw Data"]
    if is_admin:
        tabs.append("🖼️ Media")

    tab_objs = st.tabs(tabs)
    tab1, tab2, tab3, tab4 = tab_objs[0], tab_objs[1], tab_objs[2], tab_objs[3]
    tab5 = tab_objs[4] if is_admin else None

    with tab1:
        st.subheader("Event-wise Analysis")
        event = st.selectbox("Select Event", df['Event_Name'].unique())
        edf = df[df['Event_Name'] == event]
        fig = px.pie(
            edf, names='Sentiment', color='Sentiment',
            color_discrete_map={'Positive': '#2ecc71', 'Negative': '#e74c3c', 'Neutral': '#f1c40f'}
        )
        st.plotly_chart(fig, width='stretch')
        st.dataframe(edf, width='stretch')

    with tab2:
        student_list = sorted(df['Student_Name'].dropna().unique())
        selected_student = st.selectbox("Select Student", student_list)
        sdf = df[df['Student_Name'] == selected_student]
        st.dataframe(sdf, width='stretch')

    with tab3:
        sentiment_counts = df['Sentiment'].value_counts().reset_index()
        sentiment_counts.columns = ['Sentiment', 'Count']
        fig = px.bar(
            sentiment_counts, x='Sentiment', y='Count', color='Sentiment',
            color_discrete_map={'Positive': '#2ecc71', 'Negative': '#e74c3c', 'Neutral': '#f1c40f'}
        )
        st.plotly_chart(fig, width='stretch')

    with tab4:
        st.dataframe(df, width='stretch')
        if is_admin:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download CSV", csv, "feedback.csv", "text/csv")

    if is_admin and tab5 is not None:
        with tab5:
            st.subheader("Uploaded Photos & Audio")
            options = [
                f"{row['Student_Name']} ({row['Roll_Number']}) — {row['Timestamp']}"
                for _, row in df.iterrows()
            ]
            if not options:
                st.info("No submissions yet.")
            else:
                choice = st.selectbox("Select submission", options)
                idx = options.index(choice)
                row = df.iloc[idx]

                photo_path = row.get('Photo_Path', '')
                audio_path = row.get('Audio_Path', '')

                if isinstance(photo_path, str) and photo_path and os.path.exists(photo_path):
                    st.image(photo_path, caption="Captured Photo", width=350)
                else:
                    st.caption("No photo saved for this submission.")

                if isinstance(audio_path, str) and audio_path and os.path.exists(audio_path):
                    st.audio(audio_path)
                else:
                    st.caption("No audio saved for this submission.")
