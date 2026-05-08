import streamlit as st
import pandas as pd
from textblob import TextBlob
import plotly.express as px
import datetime
import io
import os
import cv2
import numpy as np
from PIL import Image
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Student Voice Feedback System", page_icon="🎤", layout="wide")

# Optional: Speech recognition setup
try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False

# --- EXCEL CONFIGURATION ---
EXCEL_FILE = "feedback_data.xlsx"
ADMIN_PASSWORD = "PRAGYANAI"
COLUMNS = [
    'Timestamp', 'Student_Name', 'Roll_Number', 'College_Name', 'Department_name', 
    'E_mail', 'Phone_number', 'Event_Name', 'Face_Detected', 'Transcript', 'Sentiment', 'Polarity'
]

# ============================================================
# EXCEL & DATA FUNCTIONS
# ============================================================

def create_excel_if_not_exists():
    """Create Excel file with styled header if it doesn't exist."""
    if not os.path.exists(EXCEL_FILE):
        wb = Workbook()
        ws = wb.active
        ws.title = "Feedback Data"

        header_fill = PatternFill("solid", start_color="1F4E79")
        header_font = Font(bold=True, color="FFFFFF", name="Arial", size=11)
        thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), 
                             top=Side(style='thin'), bottom=Side(style='thin'))

        for col_idx, header in enumerate(COLUMNS, 1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border

        wb.save(EXCEL_FILE)

def append_to_excel(record: dict):
    """Append one row to the Excel file with styling."""
    create_excel_if_not_exists()
    try:
        wb = load_workbook(EXCEL_FILE)
        ws = wb.active
        next_row = ws.max_row + 1

        row_fill = PatternFill("solid", start_color="D6E4F0") if next_row % 2 == 0 else PatternFill("solid", start_color="FFFFFF")
        sentiment_colors = {"Positive": "C6EFCE", "Negative": "FFC7CE", "Neutral": "FFEB9C"}
        sentiment_fill = PatternFill("solid", start_color=sentiment_colors.get(record.get('Sentiment', 'Neutral'), "FFFFFF"))

        row_data = [record.get(col, '') for col in COLUMNS]
        
        for col_idx, value in enumerate(row_data, 1):
            cell = ws.cell(row=next_row, column=col_idx, value=value)
            cell.fill = sentiment_fill if col_idx == 11 else row_fill
            cell.alignment = Alignment(vertical="center", wrap_text=(col_idx == 10))
            if col_idx == 12: cell.value = round(float(value), 4)

        wb.save(EXCEL_FILE)
        return True
    except Exception as e:
        st.error(f"⚠️ Excel Save Error: {e}")
        return False

def load_from_excel():
    """Load all data from Excel into a DataFrame safely."""
    create_excel_if_not_exists()
    try:
        df = pd.read_excel(EXCEL_FILE, engine='openpyxl')
        if df.empty: return pd.DataFrame(columns=COLUMNS + ['Photo'])
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df['Face_Detected'] = df['Face_Detected'].astype(bool)
        df['Photo'] = None 
        return df
    except Exception:
        return pd.DataFrame(columns=COLUMNS + ['Photo'])

def get_excel_download():
    """Read Excel file as bytes for download."""
    if os.path.exists(EXCEL_FILE):
        with open(EXCEL_FILE, "rb") as f:
            return f.read()
    return None

# ============================================================
# LOGIC FUNCTIONS
# ============================================================

def analyze_sentiment(text):
    if not text or len(text.strip()) < 2: return "Neutral", 0.0
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1: return "Positive", polarity
    elif polarity < -0.1: return "Negative", polarity
    else: return "Neutral", polarity

def detect_faces(image_bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img_bgr is None: return None, 0, False
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))
    img_annotated = img_bgr.copy()
    for (x, y, w, h) in faces:
        cv2.rectangle(img_annotated, (x, y), (x+w, y+h), (0, 255, 0), 3)
    return Image.fromarray(cv2.cvtColor(img_annotated, cv2.COLOR_BGR2RGB)), len(faces), len(faces) > 0

def transcribe_audio(audio_bytes):
    if not HAS_SR: return "SpeechRecognition not installed."
    r = sr.Recognizer()
    try:
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio = r.record(source)
            return r.recognize_google(audio)
    except Exception: return "Audio unclear. Manual text used."

# ============================================================
# MAIN APP INTERFACE
# ============================================================

if 'feedbacks' not in st.session_state:
    st.session_state['feedbacks'] = load_from_excel()

st.title("🎤 Student Voice Feedback System")
page = st.sidebar.radio("Navigate", ["Record Feedback", "Analysis Dashboard"])

# --- SIDEBAR ADMIN CONTROLS ---
st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Admin Access")
pwd_input = st.sidebar.text_input("Enter Password to Download Data", type="password")

is_admin = (pwd_input == ADMIN_PASSWORD)

if is_admin:
    st.sidebar.success("Access Granted")
    st.sidebar.subheader("⚙️ Data Management")
    if st.sidebar.button("🔄 Refresh Data from Excel"):
        st.session_state['feedbacks'] = load_from_excel()
        st.sidebar.info("Data refreshed!")
    
    excel_data = get_excel_download()
    if excel_data:
        st.sidebar.download_button(
            label="📥 Download Excel Database",
            data=excel_data,
            file_name=f"feedback_master_{datetime.date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
elif pwd_input != "":
    st.sidebar.error("Incorrect Password")

# --- PAGE 1: RECORD FEEDBACK ---
if page == "Record Feedback":
    st.header("Submit Your Feedback")
    
    with st.container(border=True):
        st.subheader("1️⃣ Student Details")
        c1, c2 = st.columns(2)
        with c1:
            s_name = st.text_input("Full Name *")
            s_roll = st.text_input("Roll Number *")
            s_college = st.text_input("College Name")
        with c2:
            s_event = st.selectbox("Event", ["Hackathon 2026", "Science Fair", "Sports Meet", "Other"])
            s_email = st.text_input("Email ID")
            s_phone = st.text_input("Phone Number")

    st.subheader("2️⃣ 📸 Identity Verification")
    img_file = st.camera_input("Capture Photo")
    if img_file:
        preview, count, detected = detect_faces(img_file.getvalue())
        if preview:
            st.image(preview, width=300)
            if detected: st.success(f"✅ Face Verified!")

    st.subheader("3️⃣ 🎙️ Feedback")
    with st.form("main_form", clear_on_submit=True):
        audio_data = st.audio_input("Record Voice Feedback")
        text_data = st.text_area("Or type feedback here...")
        submitted = st.form_submit_button("🚀 Submit Feedback", type="primary")

        if submitted:
            if not s_name or not s_roll:
                st.error("Name and Roll Number are required!")
            else:
                with st.spinner("Saving..."):
                    transcript = transcribe_audio(audio_data.getvalue()) if audio_data else text_data
                    sentiment, score = analyze_sentiment(transcript)
                    
                    face_verified = False
                    if img_file:
                        _, _, face_verified = detect_faces(img_file.getvalue())

                    record = {
                        'Timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'Student_Name': s_name, 'Roll_Number': s_roll,
                        'College_Name': s_college, 'Department_name': "General",
                        'E_mail': s_email, 'Phone_number': s_phone,
                        'Event_Name': s_event, 'Face_Detected': face_verified,
                        'Transcript': transcript, 'Sentiment': sentiment, 'Polarity': score
                    }
                    
                    if append_to_excel(record):
                        st.success(f"✅ Feedback Saved! Sentiment: {sentiment}")
                        st.session_state['feedbacks'] = load_from_excel()
                        st.balloons()

# --- PAGE 2: ANALYSIS DASHBOARD ---
elif page == "Analysis Dashboard":
    st.header("📊 Feedback Analysis Dashboard")
    df = st.session_state['feedbacks']

    if df.empty:
        st.info("No data available yet. Please record feedback first.")
    else:
        # Dashboard Summary
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Feedbacks", len(df))
        m2.metric("Unique Students", df['Roll_Number'].nunique())
        avg_pol = df['Polarity'].mean()
        m3.metric("Avg Polarity", f"{avg_pol:.2f}", delta="Positive" if avg_pol > 0 else "Negative")

        t1, t2, t3 = st.tabs(["Event Summary", "Individual History", "Data Log"])

        with t1:
            event_pick = st.selectbox("Select Event", df['Event_Name'].unique())
            edf = df[df['Event_Name'] == event_pick]
            fig = px.pie(edf, names='Sentiment', color='Sentiment', 
                         color_discrete_map={'Positive':'#2ecc71','Negative':'#e74c3c','Neutral':'#f1c40f'})
            st.plotly_chart(fig, use_container_width=True)

        with t2:
            student_opts = df.apply(lambda x: f"{x['Student_Name']} ({x['Roll_Number']})", axis=1).unique()
            selected_s = st.selectbox("Select Student", student_opts)
            target_roll = str(selected_s.rsplit('(', 1)[-1].rstrip(')'))
            sdf = df[df['Roll_Number'].astype(str) == target_roll]

            if not sdf.empty:
                st.subheader(f"History for {sdf.iloc[-1]['Student_Name']}")
                for _, row in sdf.sort_values('Timestamp', ascending=False).iterrows():
                    color = "green" if row['Sentiment'] == 'Positive' else "red" if row['Sentiment'] == 'Negative' else "orange"
                    with st.expander(f"{row['Event_Name']} | {row['Timestamp']}"):
                        st.markdown(f"**Sentiment:** :{color}[{row['Sentiment']}]")
                        st.write(f"💬 {row['Transcript']}")
                        st.caption(f"Face Verified: {'✅' if row['Face_Detected'] else '❌'}")

        with t3:
            st.subheader("Complete Data Records")
            st.dataframe(df, use_container_width=True)
            
            if is_admin:
                st.write("---")
                st.markdown("### 📥 Admin Downloads")
                col_a, col_b = st.columns(2)
                with col_a:
                    csv_data = df.to_csv(index=False).encode('utf-8')
                    st.download_button("Download as CSV", csv_data, "feedback.csv", "text/csv")
                with col_b:
                    if excel_data:
                        st.download_button("Download as Excel (.xlsx)", excel_data, "feedback.xlsx")
            else:
                st.warning("⚠️ Enter password in sidebar to enable data download buttons.")
