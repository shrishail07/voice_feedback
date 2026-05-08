
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

# # --- PAGE CONFIGURATION ---
# st.set_page_config(page_title="Student Voice Feedback System", page_icon="🎤", layout="wide")

# # st.image("pragyan_ai_school_cover.jpg", width=1200)
# col1, col2, col3 = st.columns([1, 4, 1]) 

# with col2:
#     st.image("pragyan_ai_school_cover.jpg", use_container_width=True)

# # --- PASSWORD CONFIGURATION ---
# ADMIN_PASSWORD = "PRAGYANAI"

# # ============================================================
# # FIXED CSS: ENSURES BUTTON TEXT IS WHITE AND VISIBLE
# # ============================================================
# def apply_black_white_theme():
#     st.markdown("""
#     <style>
#         /* 1. Main Background to White */
#         .stApp {
#             background-color: #FFFFFF !important;
#         }

#         /* 2. Force general text to Black */
#         h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stText, 
#         [data-testid="stMetricLabel"], [data-testid="stHeader"] {
#             color: #000000 !important;
#         }

#         /* 3. Typing Text Color inside Inputs */
#         input, textarea {
#             color: #000000 !important;
#             -webkit-text-fill-color: #000000 !important;
#         }

#         /* 4. Metric Values to Black */
#         [data-testid="stMetricValue"] {
#             color: #000000 !important;
#             font-weight: bold;
#         }

#         /* 5. BUTTONS: FIXED TEXT VISIBILITY */
#         /* We target the button and any span/p tags inside it to force them to white */
#         div.stButton > button, 
#         div.stDownloadButton > button, 
#         div.stFormSubmitButton > button {
#             background-color: #000000 !important;
#             color: #FFFFFF !important;
#             border: 1px solid #000000;
#             border-radius: 5px;
#             font-weight: bold;
#             height: 3em;
#             width: 100%;
#         }

#         /* Ensure the text inside the button is white */
#         div.stButton > button *, 
#         div.stDownloadButton > button *,
#         div.stFormSubmitButton > button * {
#            color: #FFFFFF !important;
#         }
        
#         /* Hover state */
#         div.stButton > button:hover, 
#         div.stDownloadButton > button:hover {
#             background-color: #333333 !important;
#             border-color: #333333 !important;
#         }

#         /* 6. Icons & Logos */
#         svg {
#             fill: #000000 !important;
#         }

#         /* 7. Input field borders */
#         .stTextInput > div > div > input, 
#         .stTextArea > div > div > textarea, 
#         .stSelectbox > div {
#             border: 1px solid #000000 !important;
#             background-color: #FFFFFF !important;
#             color: #000000 !important;
#         }
        
#         /* 8. Sidebar Styling */
#         [data-testid="stSidebar"] {
#             background-color: #F8F9FA !important;
#             border-right: 1px solid #EEEEEE;
#         }
#     </style>
#     """, unsafe_allow_html=True)

# apply_black_white_theme()

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
#     if not os.path.exists(EXCEL_FILE):
#         wb = Workbook()
#         ws = wb.active
#         ws.title = "Feedback Data"
#         wb.save(EXCEL_FILE)

# def append_to_excel(record: dict):
#     create_excel_if_not_exists()
#     try:
#         wb = load_workbook(EXCEL_FILE)
#         ws = wb.active
#         next_row = ws.max_row + 1
#         row_data = [record.get(col, '') for col in COLUMNS]
#         for col_idx, value in enumerate(row_data, 1):
#             ws.cell(row=next_row, column=col_idx, value=value)
#         wb.save(EXCEL_FILE)
#         return True
#     except Exception as e:
#         st.error(f"⚠️ Error: {e}")
#         return False

# def load_from_excel():
#     create_excel_if_not_exists()
#     try:
#         df = pd.read_excel(EXCEL_FILE, engine='openpyxl')
#         if df.empty: return pd.DataFrame(columns=COLUMNS)
#         df['Timestamp'] = pd.to_datetime(df['Timestamp'])
#         return df
#     except Exception:
#         return pd.DataFrame(columns=COLUMNS)

# def get_excel_download():
#     if os.path.exists(EXCEL_FILE):
#         with open(EXCEL_FILE, "rb") as f:
#             return f.read()
#     return None

# # ============================================================
# # LOGIC FUNCTIONS
# # ============================================================

# def analyze_sentiment(text):
#     if not text: return "Neutral", 0.0
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
#     return Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)), len(faces), len(faces) > 0

# def transcribe_audio(audio_bytes):
#     if not HAS_SR: return "SpeechRecognition not installed."
#     r = sr.Recognizer()
#     try:
#         with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
#             audio = r.record(source)
#             return r.recognize_google(audio)
#     except Exception: return "Transcription error."

# # ============================================================
# # MAIN APP INTERFACE
# # ============================================================

# if 'feedbacks' not in st.session_state:
#     st.session_state['feedbacks'] = load_from_excel()

# st.title("🎤 Student Voice Feedback System")
# page = st.sidebar.radio("Navigate", ["Record Feedback", "Analysis Dashboard"])

# # --- SIDEBAR PASSWORD CHECK ---
# st.sidebar.markdown("---")
# st.sidebar.subheader("🔒 Admin Controls")
# pwd_input = st.sidebar.text_input("Enter Password to Download Data", type="password")
# is_admin = (pwd_input == ADMIN_PASSWORD)

# if is_admin:
#     st.sidebar.success("Access Granted")
#     excel_data = get_excel_download()
#     if excel_data:
#         st.sidebar.download_button(
#             label="📥 Download Master Excel",
#             data=excel_data,
#             file_name=f"feedback_master_{datetime.date.today()}.xlsx",
#             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         )
# elif pwd_input != "":
#     st.sidebar.error("Incorrect Password")

# # --- PAGE 1: RECORD FEEDBACK ---
# if page == "Record Feedback":
#     st.header("Submit Your Feedback")
    
#     with st.container():
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
#     img_file = st.camera_input("Capture Photo")

#     st.subheader("3️⃣ 🎙️ Feedback")
#     with st.form("main_form"):
#         audio_data = st.audio_input("Record Voice Feedback")
#         text_data = st.text_area("Or type here...")
#         submitted = st.form_submit_button("Submit Submission")

#         if submitted:
#             if not s_name or not s_roll:
#                 st.error("Name and Roll Number are required!")
#             else:
#                 transcript = transcribe_audio(audio_data.getvalue()) if audio_data else text_data
#                 sentiment, score = analyze_sentiment(transcript)
                
#                 face_verified = False
#                 if img_file:
#                     _, _, face_verified = detect_faces(img_file.getvalue())

#                 record = {
#                     'Timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                     'Student_Name': s_name, 'Roll_Number': s_roll,
#                     'College_Name': s_college, 'Department_name': "N/A",
#                     'E_mail': s_email, 'Phone_number': s_phone,
#                     'Event_Name': s_event, 'Face_Detected': face_verified,
#                     'Transcript': transcript, 'Sentiment': sentiment, 'Polarity': score
#                 }
                
#                 if append_to_excel(record):
#                     st.success("Feedback saved successfully!")
#                     st.session_state['feedbacks'] = load_from_excel()
#                     st.balloons()

# # --- PAGE 2: ANALYSIS DASHBOARD ---
# elif page == "Analysis Dashboard":
#     st.header("📊 Feedback Analysis Dashboard")
#     df = st.session_state['feedbacks']

#     if df.empty:
#         st.info("No data available yet.")
#     else:
#         m1, m2, m3 = st.columns(3)
#         m1.metric("Total Submissions", len(df))
#         m2.metric("Unique Students", df['Roll_Number'].nunique())
#         m3.metric("Avg Sentiment Score", round(df['Polarity'].mean(), 2))

#         tab1, tab2, tab3 = st.tabs(["Event View", "Student History", "Raw Data"])

#         with tab1:
#             event = st.selectbox("Select Event", df['Event_Name'].unique())
#             edf = df[df['Event_Name'] == event]
#             fig = px.pie(edf, names='Sentiment', color='Sentiment', 
#                          color_discrete_map={'Positive':'#000000', 'Negative':'#333333', 'Neutral':'#666666'})
#             st.plotly_chart(fig)

#         with tab2:
#             student_list = df['Student_Name'].unique()
#             sel_student = st.selectbox("Select Student", student_list)
#             sdf = df[df['Student_Name'] == sel_student]
#             st.dataframe(sdf)

#         with tab3:
#             st.dataframe(df)
#             if is_admin:
#                 csv = df.to_csv(index=False).encode('utf-8')
#                 st.download_button("Download CSV Data", csv, "feedback.csv", "text/csv")
#             else:
#                 st.warning("🔒 Please enter the password in the sidebar to download data.")

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

# Center the cover image
col1, col2, col3 = st.columns([1, 4, 1]) 
with col2:
    # Ensure the image file exists in your directory
    try:
        st.image("pragyan_ai_school_cover.jpg", use_container_width=True)
    except:
        st.warning("Cover image 'pragyan_ai_school_cover.jpg' not found.")

# --- PASSWORD CONFIGURATION ---
ADMIN_PASSWORD = "PRAGYANAI"

# ============================================================
# FIXED CSS: BLACK & WHITE THEME
# ============================================================
def apply_black_white_theme():
    st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF !important; }
        h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stText, 
        [data-testid="stMetricLabel"], [data-testid="stHeader"] {
            color: #000000 !important;
        }
        input, textarea {
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important;
        }
        [data-testid="stMetricValue"] {
            color: #000000 !important;
            font-weight: bold;
        }
        /* Button Styling */
        div.stButton > button, 
        div.stDownloadButton > button, 
        div.stFormSubmitButton > button {
            background-color: #000000 !important;
            color: #FFFFFF !important;
            border: 1px solid #000000;
            border-radius: 5px;
            font-weight: bold;
            height: 3em;
            width: 100%;
        }
        /* Force button text to white */
        div.stButton > button *, 
        div.stDownloadButton > button *,
        div.stFormSubmitButton > button * {
            color: #FFFFFF !important;
        }
        div.stButton > button:hover {
            background-color: #333333 !important;
        }
        /* Form Inputs */
        .stTextInput > div > div > input, 
        .stTextArea > div > div > textarea, 
        .stSelectbox > div {
            border: 1px solid #000000 !important;
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }
        [data-testid="stSidebar"] {
            background-color: #F8F9FA !important;
            border-right: 1px solid #EEEEEE;
        }
    </style>
    """, unsafe_allow_html=True)

apply_black_white_theme()

# --- EXCEL FUNCTIONS ---
EXCEL_FILE = "feedback_data.xlsx"
COLUMNS = [
    'Timestamp', 'Student_Name', 'Roll_Number', 'College_Name', 
    'Department_name', 'E_mail', 'Phone_number', 'Event_Name', 
    'Face_Detected', 'Transcript', 'Sentiment', 'Polarity'
]

def create_excel_if_not_exists():
    if not os.path.exists(EXCEL_FILE):
        wb = Workbook()
        ws = wb.active
        ws.title = "Feedback Data"
        ws.append(COLUMNS)
        wb.save(EXCEL_FILE)

def append_to_excel(record: dict):
    create_excel_if_not_exists()
    try:
        wb = load_workbook(EXCEL_FILE)
        ws = wb.active
        ws.append([record.get(col, '') for col in COLUMNS])
        wb.save(EXCEL_FILE)
        return True
    except Exception as e:
        st.error(f"⚠️ Error saving to Excel: {e}")
        return False

def load_from_excel():
    create_excel_if_not_exists()
    try:
        df = pd.read_excel(EXCEL_FILE, engine='openpyxl')
        if df.empty:
            return pd.DataFrame(columns=COLUMNS)
        return df
    except Exception:
        return pd.DataFrame(columns=COLUMNS)

# --- LOGIC FUNCTIONS ---
def analyze_sentiment(text):
    if not text: return "Neutral", 0.0
    pol = TextBlob(text).sentiment.polarity
    if pol > 0.1: return "Positive", pol
    elif pol < -0.1: return "Negative", pol
    return "Neutral", pol

def detect_faces(image_bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img_bgr is None: return None, 0, False
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))
    return Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)), len(faces), len(faces) > 0

# ============================================================
# MAIN APP
# ============================================================

st.title("🎤 Student Voice Feedback System")
page = st.sidebar.radio("Navigate", ["Record Feedback", "Analysis Dashboard"])

# Sidebar Password Check
st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Admin Controls")
pwd_input = st.sidebar.text_input("Enter Password", type="password")
is_admin = (pwd_input == ADMIN_PASSWORD)

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
        # Note: audio_input and text_area for feedback
        # st.audio_input is a newer feature, ensure your streamlit is updated
        audio_data = None
        try:
            audio_data = st.audio_input("Record Voice Feedback")
        except:
            st.info("Audio input not supported in this version, please type below.")
            
        text_data = st.text_area("Or type your feedback here...")
        submitted = st.form_submit_button("Submit Submission")

        if submitted:
            if not s_name or not s_roll:
                st.error("Name and Roll Number are required!")
            else:
                with st.spinner("Saving data..."):
                    # Basic transcription placeholder or typed text
                    transcript = text_data 
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
                        st.success("✅ Feedback saved successfully!")
                        st.balloons()
                        # Force refresh the session state data
                        st.session_state['feedbacks'] = load_from_excel()
                        # Small delay then rerun to clear form and update dashboard
                        st.rerun()

# --- PAGE 2: ANALYSIS DASHBOARD ---
elif page == "Analysis Dashboard":
    # 1. ALWAYS REFRESH DATA FROM EXCEL ON DASHBOARD LOAD
    df = load_from_excel()
    st.session_state['feedbacks'] = df

    if not is_admin:
        st.warning("🔒 Access Denied. Please enter the correct password in the sidebar.")
    else:
        st.header("📊 Feedback Analysis Dashboard")
        
        if df.empty or len(df) == 0:
            st.info("No data available in the Excel file yet.")
        else:
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Submissions", len(df))
            m2.metric("Unique Students", df['Roll_Number'].nunique())
            m3.metric("Avg Sentiment Score", f"{df['Polarity'].mean():.2f}")

            tab1, tab2, tab3 = st.tabs(["Event View", "Student History", "Raw Data Log"])

            with tab1:
                event_list = df['Event_Name'].unique()
                sel_event = st.selectbox("Select Event", event_list)
                edf = df[df['Event_Name'] == sel_event]
                fig = px.pie(edf, names='Sentiment', color='Sentiment', 
                             color_discrete_map={'Positive':'#000000', 'Negative':'#555555', 'Neutral':'#AAAAAA'})
                st.plotly_chart(fig, use_container_width=True)

            with tab2:
                student_list = sorted(df['Student_Name'].unique())
                sel_student = st.selectbox("Select Student", student_list)
                sdf = df[df['Student_Name'] == sel_student]
                st.write(f"Showing history for: **{sel_student}**")
                st.table(sdf[['Timestamp', 'Event_Name', 'Sentiment', 'Transcript']])

            with tab3:
                st.subheader("Complete Records")
                st.dataframe(df, use_container_width=True)
                
                # Admin Download Button
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Data as CSV",
                    data=csv,
                    file_name="feedback_export.csv",
                    mime="text/csv"
                )


