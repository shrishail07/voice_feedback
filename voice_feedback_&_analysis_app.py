# import streamlit as st
# import pandas as pd
# from textblob import TextBlob
# import plotly.express as px
# import datetime
# import io
# import os
# import cv2
# import numpy as np
# from PIL import Image
# from openpyxl import Workbook, load_workbook
# from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
# from openpyxl.utils import get_column_letter

# # --- PAGE CONFIGURATION ---
# st.set_page_config(page_title="Student Voice Feedback System", page_icon="🎤", layout="wide")

# # Optional: Speech recognition setup
# try:
#     import speech_recognition as sr
#     HAS_SR = True
# except ImportError:
#     HAS_SR = False

# # --- EXCEL CONFIGURATION ---
# EXCEL_FILE = "feedback_data.xlsx"
# COLUMNS = [
#     'Timestamp', 'Student_Name', 'Roll_Number', 'College_Name', 'Department_name', 
#     'E_mail', 'Phone_number', 'Event_Name', 'Face_Detected', 'Transcript', 'Sentiment', 'Polarity'
# ]

# # ============================================================
# # EXCEL & DATA FUNCTIONS
# # ============================================================

# def create_excel_if_not_exists():
#     """Create Excel file with styled header if it doesn't exist."""
#     if not os.path.exists(EXCEL_FILE):
#         wb = Workbook()
#         ws = wb.active
#         ws.title = "Feedback Data"

#         header_fill = PatternFill("solid", start_color="1F4E79")
#         header_font = Font(bold=True, color="FFFFFF", name="Arial", size=11)
#         thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), 
#                              top=Side(style='thin'), bottom=Side(style='thin'))

#         for col_idx, header in enumerate(COLUMNS, 1):
#             cell = ws.cell(row=1, column=col_idx, value=header)
#             cell.fill = header_fill
#             cell.font = header_font
#             cell.alignment = Alignment(horizontal="center", vertical="center")
#             cell.border = thin_border

#         # Set column widths
#         col_widths = {'Timestamp': 22, 'Student_Name': 20, 'Transcript': 50, 'Sentiment': 12}
#         for col_idx, col_name in enumerate(COLUMNS, 1):
#             ws.column_dimensions[get_column_letter(col_idx)].width = col_widths.get(col_name, 18)

#         wb.save(EXCEL_FILE)

# def append_to_excel(record: dict):
#     """Append one row to the Excel file with styling."""
#     create_excel_if_not_exists()
#     try:
#         wb = load_workbook(EXCEL_FILE)
#         ws = wb.active
#         next_row = ws.max_row + 1

#         # Styling
#         row_fill = PatternFill("solid", start_color="D6E4F0") if next_row % 2 == 0 else PatternFill("solid", start_color="FFFFFF")
#         sentiment_colors = {"Positive": "C6EFCE", "Negative": "FFC7CE", "Neutral": "FFEB9C"}
#         sentiment_fill = PatternFill("solid", start_color=sentiment_colors.get(record.get('Sentiment', 'Neutral'), "FFFFFF"))

#         row_data = [record.get(col, '') for col in COLUMNS]
        
#         for col_idx, value in enumerate(row_data, 1):
#             cell = ws.cell(row=next_row, column=col_idx, value=value)
#             cell.fill = sentiment_fill if col_idx == 11 else row_fill
#             cell.alignment = Alignment(vertical="center", wrap_text=(col_idx == 10))
#             if col_idx == 12: # Polarity
#                 cell.value = round(float(value), 4)

#         wb.save(EXCEL_FILE)
#         return True
#     except Exception as e:
#         st.error(f"⚠️ Excel Save Error: {e}")
#         return False

# def load_from_excel():
#     """Load all data from Excel into a DataFrame safely."""
#     create_excel_if_not_exists()
#     try:
#         df = pd.read_excel(EXCEL_FILE, engine='openpyxl')
#         if df.empty:
#             return pd.DataFrame(columns=COLUMNS + ['Photo'])
#         df['Timestamp'] = pd.to_datetime(df['Timestamp'])
#         df['Face_Detected'] = df['Face_Detected'].astype(bool)
#         df['Photo'] = None 
#         return df
#     except Exception:
#         return pd.DataFrame(columns=COLUMNS + ['Photo'])

# # ============================================================
# # LOGIC FUNCTIONS
# # ============================================================

# def analyze_sentiment(text):
#     if not text or len(text.strip()) < 2:
#         return "Neutral", 0.0
#     polarity = TextBlob(text).sentiment.polarity
#     if polarity > 0.1: return "Positive", polarity
#     elif polarity < -0.1: return "Negative", polarity
#     else: return "Neutral", polarity

# def detect_faces(image_bytes):
#     nparr = np.frombuffer(image_bytes, np.uint8)
#     img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#     if img_bgr is None: return None, 0, False
    
#     gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
#     face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
#     faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))
    
#     img_annotated = img_bgr.copy()
#     for (x, y, w, h) in faces:
#         cv2.rectangle(img_annotated, (x, y), (x+w, y+h), (0, 255, 0), 3)
        
#     img_rgb = cv2.cvtColor(img_annotated, cv2.COLOR_BGR2RGB)
#     return Image.fromarray(img_rgb), len(faces), len(faces) > 0

# def transcribe_audio(audio_bytes):
#     if not HAS_SR: return "SpeechRecognition not installed."
#     r = sr.Recognizer()
#     try:
#         with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
#             audio = r.record(source)
#             return r.recognize_google(audio)
#     except Exception:
#         return "Audio unclear. Manual text used."

# # ============================================================
# # MAIN APP INTERFACE
# # ============================================================

# if 'feedbacks' not in st.session_state:
#     st.session_state['feedbacks'] = load_from_excel()
# if 'captured_photo' not in st.session_state:
#     st.session_state['captured_photo'] = None

# st.title("🎤 Student Voice Feedback System")
# page = st.sidebar.radio("Navigate", ["Record Feedback", "Analysis Dashboard"])

# # Sidebar Tools
# st.sidebar.markdown("---")
# if st.sidebar.button("🔄 Refresh Data"):
#     st.session_state['feedbacks'] = load_from_excel()
#     st.sidebar.success("Data Updated!")

# # --- PAGE 1: RECORD FEEDBACK ---
# if page == "Record Feedback":
#     st.header("Submit Your Feedback")
    
#     with st.container(border=True):
#         st.subheader("1️⃣ Student Details")
#         c1, c2 = st.columns(2)
#         with c1:
#             s_name = st.text_input("Full Name *")
#             s_roll = st.text_input("Roll Number *")
#             s_college = st.text_input("College Name")
#         with c2:
#             s_event = st.selectbox("Event", ["Hackathon 2026", "Science Fair", "Sports Meet", "Other"])
#             s_email = st.text_input("Email ID")
#             s_phone = st.text_input("Phone Number")

#     st.subheader("2️⃣ 📸 Identity Verification")
#     method = st.radio("Photo Source", ["Camera", "Upload"], horizontal=True)
#     if method == "Camera":
#         img_file = st.camera_input("Capture Photo")
#     else:
#         img_file = st.file_uploader("Upload Photo", type=['jpg', 'png'])

#     if img_file:
#         st.session_state['captured_photo'] = img_file
#         preview, count, detected = detect_faces(img_file.getvalue())
#         if preview:
#             st.image(preview, width=300)
#             if detected: st.success(f"✅ Face Detected!")
#             else: st.warning("⚠️ No face detected. Try again.")

#     st.subheader("3️⃣ 🎙️ Feedback")
#     with st.form("main_form"):
#         audio_data = st.audio_input("Record Voice Feedback")
#         text_data = st.text_area("Or type here...")
#         submitted = st.form_submit_button("Submit Submission", type="primary")

#         if submitted:
#             if not s_name or not s_roll:
#                 st.error("Name and Roll Number are required!")
#             else:
#                 with st.spinner("Processing..."):
#                     transcript = transcribe_audio(audio_data.getvalue()) if audio_data else text_data
#                     sentiment, score = analyze_sentiment(transcript)
                    
#                     # Face check
#                     face_verified = False
#                     if st.session_state['captured_photo']:
#                         _, _, face_verified = detect_faces(st.session_state['captured_photo'].getvalue())

#                     record = {
#                         'Timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                         'Student_Name': s_name, 'Roll_Number': s_roll,
#                         'College_Name': s_college, 'Department_name': "N/A",
#                         'E_mail': s_email, 'Phone_number': s_phone,
#                         'Event_Name': s_event, 'Face_Detected': face_verified,
#                         'Transcript': transcript, 'Sentiment': sentiment, 'Polarity': score
#                     }
                    
#                     if append_to_excel(record):
#                         st.success("Feedback saved successfully!")
#                         st.session_state['feedbacks'] = load_from_excel()
#                         st.balloons()

# # --- PAGE 2: ANALYSIS DASHBOARD ---
# elif page == "Analysis Dashboard":
#     st.header("📊 Feedback Analysis Dashboard")
#     df = st.session_state['feedbacks']

#     if df.empty:
#         st.info("No data available yet.")
#     else:
#         # Top Metrics
#         m1, m2, m3 = st.columns(3)
#         m1.metric("Total Submissions", len(df))
#         m2.metric("Unique Students", df['Roll_Number'].nunique())
#         m3.metric("Avg Sentiment Score", round(df['Polarity'].mean(), 2))

#         tab1, tab2, tab3 = st.tabs(["Event View", "Student History", "Raw Data"])

#         with tab1:
#             event = st.selectbox("Select Event", df['Event_Name'].unique())
#             edf = df[df['Event_Name'] == event]
#             fig = px.pie(edf, names='Sentiment', title=f"Sentiments for {event}", 
#                          color='Sentiment', color_discrete_map={'Positive':'#2ecc71', 'Negative':'#e74c3c', 'Neutral':'#f1c40f'})
#             st.plotly_chart(fig)

#         with tab2:
#             # FIX: Robust selection and filtering
#             student_options = df[['Student_Name', 'Roll_Number']].drop_duplicates()
#             student_labels = [f"{r['Student_Name']} ({r['Roll_Number']})" for _, r in student_options.iterrows()]
            
#             selected = st.selectbox("Select Student", student_labels)
#             # Safe extraction of Roll Number
#             target_roll = str(selected.rsplit('(', 1)[-1].rstrip(')'))
            
#             # Ensure type matching for filter
#             sdf = df[df['Roll_Number'].astype(str) == target_roll]

#             if not sdf.empty:
#                 latest = sdf.iloc[-1]
#                 st.subheader(f"History for {latest['Student_Name']}")
                
#                 for _, row in sdf.sort_values('Timestamp', ascending=False).iterrows():
#                     with st.expander(f"{row['Event_Name']} - {row['Timestamp']}"):
#                         st.write(f"**Sentiment:** {row['Sentiment']}")
#                         st.write(f"**Feedback:** {row['Transcript']}")
#                         st.write(f"**Face Verified:** {'✅' if row['Face_Detected'] else '❌'}")

#         with tab3:
#             st.dataframe(df.drop(columns=['Photo'], errors='ignore'), use_container_width=True)
#             csv = df.to_csv(index=False).encode('utf-8')
#             st.download_button("Download CSV", csv, "feedback.csv", "text/csv")


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

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Student Voice Feedback System", page_icon="🎤", layout="wide")

# ============================================================
# FIXED CSS: ENSURES TYPED TEXT IS BLACK
# ============================================================
def apply_black_white_theme():
    st.markdown("""
    <style>
        /* 1. Main Background to White */
        .stApp {
            background-color: #FFFFFF !important;
        }

        /* 2. Force ALL text (Typed, Label, Header) to Black */
        h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stText, span, 
        [data-testid="stMetricLabel"], [data-testid="stHeader"] {
            color: #000000 !important;
        }

        /* 3. FIXED: Typing Text Color inside Inputs/Textareas */
        input, textarea {
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important; /* For Safari/Chrome */
        }

        /* 4. Metric Values to Black */
        [data-testid="stMetricValue"] {
            color: #000000 !important;
            font-weight: bold;
        }

        /* 5. Buttons: Black with White Text */
        div.stButton > button, .stDownloadButton > button {
            background-color: #000000 !important;
            color: #FFFFFF !important;
            border: 1px solid #000000;
        }
        
        div.stButton > button:hover {
            background-color: #333333 !important;
            color: #FFFFFF !important;
        }

        /* 6. Form Submission Button */
        div.stFormSubmitButton > button {
            background-color: #000000 !important;
            color: #FFFFFF !important;
            width: 100%;
        }

        /* 7. Icons & Logos (Force them to black) */
        svg {
            fill: #000000 !important;
        }

        /* 8. Input field borders visibility */
        .stTextInput > div > div > input, 
        .stTextArea > div > div > textarea, 
        .stSelectbox > div {
            border: 1px solid #000000 !important;
            background-color: #FFFFFF !important;
        }
        
        /* 9. Sidebar Text */
        [data-testid="stSidebar"] {
            background-color: #F8F9FA !important;
            border-right: 1px solid #EEEEEE;
        }
        [data-testid="stSidebar"] .stRadio label {
            color: #000000 !important;
        }
    </style>
    """, unsafe_allow_html=True)

apply_black_white_theme()

# Optional: Speech recognition setup
try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False

# --- EXCEL CONFIGURATION ---
EXCEL_FILE = "feedback_data.xlsx"
COLUMNS = [
    'Timestamp', 'Student_Name', 'Roll_Number', 'College_Name', 'Department_name', 
    'E_mail', 'Phone_number', 'Event_Name', 'Face_Detected', 'Transcript', 'Sentiment', 'Polarity'
]

# ============================================================
# EXCEL & DATA FUNCTIONS
# ============================================================

def create_excel_if_not_exists():
    if not os.path.exists(EXCEL_FILE):
        wb = Workbook()
        ws = wb.active
        ws.title = "Feedback Data"
        wb.save(EXCEL_FILE)

def append_to_excel(record: dict):
    create_excel_if_not_exists()
    try:
        wb = load_workbook(EXCEL_FILE)
        ws = wb.active
        next_row = ws.max_row + 1
        row_data = [record.get(col, '') for col in COLUMNS]
        for col_idx, value in enumerate(row_data, 1):
            ws.cell(row=next_row, column=col_idx, value=value)
        wb.save(EXCEL_FILE)
        return True
    except Exception as e:
        st.error(f"⚠️ Error: {e}")
        return False

def load_from_excel():
    create_excel_if_not_exists()
    try:
        df = pd.read_excel(EXCEL_FILE, engine='openpyxl')
        if df.empty: return pd.DataFrame(columns=COLUMNS)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        return df
    except Exception:
        return pd.DataFrame(columns=COLUMNS)

# ============================================================
# LOGIC FUNCTIONS
# ============================================================

def analyze_sentiment(text):
    if not text: return "Neutral", 0.0
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
    return Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)), len(faces), len(faces) > 0

def transcribe_audio(audio_bytes):
    if not HAS_SR: return "SpeechRecognition not installed."
    r = sr.Recognizer()
    try:
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio = r.record(source)
            return r.recognize_google(audio)
    except Exception: return "Transcription error."

# ============================================================
# MAIN APP INTERFACE
# ============================================================

if 'feedbacks' not in st.session_state:
    st.session_state['feedbacks'] = load_from_excel()

st.title("🎤 Student Voice Feedback System")
page = st.sidebar.radio("Navigate", ["Record Feedback", "Analysis Dashboard"])

# --- PAGE 1: RECORD FEEDBACK ---
if page == "Record Feedback":
    st.header("Submit Your Feedback")
    
    with st.container():
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

    st.subheader("3️⃣ 🎙️ Feedback")
    with st.form("main_form"):
        audio_data = st.audio_input("Record Voice Feedback")
        text_data = st.text_area("Or type here...")
        submitted = st.form_submit_button("Submit Submission")

        if submitted:
            if not s_name or not s_roll:
                st.error("Name and Roll Number are required!")
            else:
                transcript = transcribe_audio(audio_data.getvalue()) if audio_data else text_data
                sentiment, score = analyze_sentiment(transcript)
                
                face_verified = False
                if img_file:
                    _, _, face_verified = detect_faces(img_file.getvalue())

                record = {
                    'Timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'Student_Name': s_name, 'Roll_Number': s_roll,
                    'College_Name': s_college, 'Department_name': "N/A",
                    'E_mail': s_email, 'Phone_number': s_phone,
                    'Event_Name': s_event, 'Face_Detected': face_verified,
                    'Transcript': transcript, 'Sentiment': sentiment, 'Polarity': score
                }
                
                if append_to_excel(record):
                    st.success("Feedback saved successfully!")
                    st.session_state['feedbacks'] = load_from_excel()
                    st.balloons()

# --- PAGE 2: ANALYSIS DASHBOARD ---
elif page == "Analysis Dashboard":
    st.header("📊 Feedback Analysis Dashboard")
    df = st.session_state['feedbacks']

    if df.empty:
        st.info("No data available yet.")
    else:
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Submissions", len(df))
        m2.metric("Unique Students", df['Roll_Number'].nunique())
        m3.metric("Avg Sentiment Score", round(df['Polarity'].mean(), 2))

        tab1, tab2, tab3 = st.tabs(["Event View", "Student History", "Raw Data"])

        with tab1:
            event = st.selectbox("Select Event", df['Event_Name'].unique())
            edf = df[df['Event_Name'] == event]
            fig = px.pie(edf, names='Sentiment', color='Sentiment', 
                         color_discrete_map={'Positive':'#000000', 'Negative':'#333333', 'Neutral':'#666666'})
            st.plotly_chart(fig)

        with tab2:
            student_list = df['Student_Name'].unique()
            sel_student = st.selectbox("Select Student", student_list)
            sdf = df[df['Student_Name'] == sel_student]
            st.dataframe(sdf)

        with tab3:
            st.dataframe(df)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV Data", csv, "feedback.csv", "text/csv")
