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

# # ============================================================
# # PAGE CONFIGURATION
# # ============================================================

# st.set_page_config(
#     page_title="Student Voice Feedback System",
#     page_icon="🎤",
#     layout="wide"
# )
# st.image("pragyan_ai_school_cover.jpg", width=1200)

# # ============================================================
# # OPTIONAL SPEECH RECOGNITION
# # ============================================================

# try:
#     import speech_recognition as sr
#     HAS_SR = True
# except ImportError:
#     HAS_SR = False

# # ============================================================
# # CONFIGURATION
# # ============================================================

# EXCEL_FILE = "feedback_data.xlsx"
# ADMIN_PASSWORD = "PRAGYANAI"

# COLUMNS = [
#     'Timestamp',
#     'Student_Name',
#     'Roll_Number',
#     'College_Name',
#     'Department_name',
#     'E_mail',
#     'Phone_number',
#     'Event_Name',
#     'Face_Detected',
#     'Transcript',
#     'Sentiment',
#     'Polarity'
# ]

# # ============================================================
# # CUSTOM CSS
# # ============================================================

# st.markdown("""
# <style>

# .stApp {
#     background-color: white;
# }

# h1, h2, h3, h4, h5, h6, p, label {
#     color: black !important;
# }

# button, button p, button span {
#     color: white !important;
# }

# div.stButton > button,
# div.stDownloadButton > button,
# div.stFormSubmitButton > button {
#     background-color: black !important;
#     border-radius: 8px;
#     border: none;
#     height: 3em;
#     font-weight: bold;
# }

# div.stButton > button:hover,
# div.stDownloadButton > button:hover {
#     background-color: #333333 !important;
# }

# input, textarea {
#     color: black !important;
#     -webkit-text-fill-color: black !important;
# }

# .stTextInput > div > div > input,
# .stTextArea textarea {
#     border: 1px solid black !important;
# }

# </style>
# """, unsafe_allow_html=True)

# # ============================================================
# # EXCEL FUNCTIONS
# # ============================================================

# def create_excel_if_not_exists():

#     if not os.path.exists(EXCEL_FILE):

#         wb = Workbook()
#         ws = wb.active
#         ws.title = "Feedback Data"

#         header_fill = PatternFill(
#             start_color="1F4E79",
#             end_color="1F4E79",
#             fill_type="solid"
#         )

#         header_font = Font(
#             bold=True,
#             color="FFFFFF"
#         )

#         thin_border = Border(
#             left=Side(style='thin'),
#             right=Side(style='thin'),
#             top=Side(style='thin'),
#             bottom=Side(style='thin')
#         )

#         # Add headers
#         for col_idx, header in enumerate(COLUMNS, 1):

#             cell = ws.cell(row=1, column=col_idx, value=header)

#             cell.fill = header_fill
#             cell.font = header_font
#             cell.alignment = Alignment(horizontal="center")
#             cell.border = thin_border

#         wb.save(EXCEL_FILE)

# # ============================================================

# def append_to_excel(record):

#     create_excel_if_not_exists()

#     try:

#         wb = load_workbook(EXCEL_FILE)
#         ws = wb.active

#         row_data = [record.get(col, '') for col in COLUMNS]

#         ws.append(row_data)

#         wb.save(EXCEL_FILE)

#         return True

#     except Exception as e:

#         st.error(f"Excel Save Error: {e}")

#         return False

# # ============================================================

# def load_from_excel():

#     create_excel_if_not_exists()

#     try:

#         df = pd.read_excel(
#             EXCEL_FILE,
#             engine='openpyxl',
#             header=0
#         )

#         if df.empty:
#             return pd.DataFrame(columns=COLUMNS)

#         # Safe conversions
#         if 'Timestamp' in df.columns:
#             df['Timestamp'] = pd.to_datetime(
#                 df['Timestamp'],
#                 errors='coerce'
#             )

#         if 'Polarity' in df.columns:
#             df['Polarity'] = pd.to_numeric(
#                 df['Polarity'],
#                 errors='coerce'
#             )

#         return df

#     except Exception as e:

#         st.error(f"Excel Load Error: {e}")

#         return pd.DataFrame(columns=COLUMNS)

# # ============================================================

# def get_excel_download():

#     if os.path.exists(EXCEL_FILE):

#         with open(EXCEL_FILE, "rb") as f:
#             return f.read()

#     return None

# # ============================================================
# # LOGIC FUNCTIONS
# # ============================================================

# def analyze_sentiment(text):

#     if not text:
#         return "Neutral", 0.0

#     polarity = TextBlob(text).sentiment.polarity

#     if polarity > 0.1:
#         return "Positive", polarity

#     elif polarity < -0.1:
#         return "Negative", polarity

#     else:
#         return "Neutral", polarity

# # ============================================================

# def detect_faces(image_bytes):

#     nparr = np.frombuffer(image_bytes, np.uint8)

#     img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

#     if img_bgr is None:
#         return None, 0, False

#     gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

#     face_cascade = cv2.CascadeClassifier(
#         cv2.data.haarcascades +
#         'haarcascade_frontalface_default.xml'
#     )

#     faces = face_cascade.detectMultiScale(
#         gray,
#         1.1,
#         5,
#         minSize=(60, 60)
#     )

#     return (
#         Image.fromarray(
#             cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
#         ),
#         len(faces),
#         len(faces) > 0
#     )

# # ============================================================

# def transcribe_audio(audio_bytes):

#     if not HAS_SR:
#         return "SpeechRecognition not installed."

#     r = sr.Recognizer()

#     try:

#         with sr.AudioFile(io.BytesIO(audio_bytes)) as source:

#             audio = r.record(source)

#             return r.recognize_google(audio)

#     except Exception:

#         return "Audio Transcription Error"

# # ============================================================
# # MAIN APP
# # ============================================================

# st.title("🎤 Student Voice Feedback System")

# page = st.sidebar.radio(
#     "Navigate",
#     ["Record Feedback", "Analysis Dashboard"]
# )

# # ============================================================
# # SIDEBAR
# # ============================================================

# st.sidebar.markdown("---")

# st.sidebar.subheader("🔒 Admin Access")

# pwd_input = st.sidebar.text_input(
#     "Enter Password",
#     type="password"
# )

# is_admin = (pwd_input == ADMIN_PASSWORD)

# if is_admin:

#     st.sidebar.success("Access Granted")

#     excel_data = get_excel_download()

#     if excel_data:

#         st.sidebar.download_button(
#             "📥 Download Excel",
#             excel_data,
#             "feedback_data.xlsx",
#             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         )

# elif pwd_input != "":

#     st.sidebar.error("Incorrect Password")

# # ============================================================
# # PAGE 1 - RECORD FEEDBACK
# # ============================================================

# if page == "Record Feedback":

#     st.header("Submit Your Feedback")

#     col1, col2 = st.columns(2)

#     with col1:

#         s_name = st.text_input("Full Name *")

#         s_roll = st.text_input("Roll Number *")

#         s_college = st.text_input("College Name")

#     with col2:

#         s_event = st.selectbox(
#             "Event",
#             [
#                 "Hackathon 2026",
#                 "Science Fair",
#                 "Sports Meet",
#                 "Other"
#             ]
#         )

#         s_email = st.text_input("Email")

#         s_phone = st.text_input("Phone Number")

#     st.subheader("📸 Capture Photo")

#     img_file = st.camera_input("Take Photo")

#     st.subheader("🎙️ Feedback")

#     with st.form("feedback_form"):

#         audio_data = st.audio_input("Record Voice")

#         text_data = st.text_area("Or Type Feedback")

#         submitted = st.form_submit_button(
#             "Submit Feedback"
#         )

#     # ========================================================

#     if submitted:

#         if not s_name or not s_roll:

#             st.error("Name and Roll Number required!")

#         else:

#             transcript = (
#                 transcribe_audio(audio_data.getvalue())
#                 if audio_data else text_data
#             )

#             sentiment, score = analyze_sentiment(
#                 transcript
#             )

#             face_verified = False

#             if img_file:

#                 _, _, face_verified = detect_faces(
#                     img_file.getvalue()
#                 )

#             record = {

#                 'Timestamp': datetime.datetime.now(),

#                 'Student_Name': s_name,

#                 'Roll_Number': s_roll,

#                 'College_Name': s_college,

#                 'Department_name': "General",

#                 'E_mail': s_email,

#                 'Phone_number': s_phone,

#                 'Event_Name': s_event,

#                 'Face_Detected': face_verified,

#                 'Transcript': transcript,

#                 'Sentiment': sentiment,

#                 'Polarity': score
#             }

#             if append_to_excel(record):

#                 st.success(
#                     f"✅ Feedback Saved! Sentiment: {sentiment}"
#                 )

#                 st.balloons()

# # ============================================================
# # PAGE 2 - ANALYTICS DASHBOARD
# # ============================================================

# elif page == "Analysis Dashboard":

#     st.header("📊 Feedback Analysis Dashboard")

#     # ALWAYS LOAD FRESH DATA
#     df = load_from_excel()

#     required_cols = [
#         'Timestamp',
#         'Student_Name',
#         'Roll_Number',
#         'Event_Name',
#         'Sentiment',
#         'Polarity'
#     ]

#     missing_cols = [
#         col for col in required_cols
#         if col not in df.columns
#     ]

#     if missing_cols:

#         st.error(
#             f"❌ Missing columns in Excel: {missing_cols}"
#         )

#         st.stop()

#     if df.empty:

#         st.warning(
#             "⚠️ No data available yet. Submit feedback first."
#         )

#         st.stop()

#     # ========================================================
#     # TOP METRICS
#     # ========================================================

#     m1, m2, m3, m4 = st.columns(4)

#     m1.metric(
#         "Total Feedbacks",
#         len(df)
#     )

#     m2.metric(
#         "Unique Students",
#         df['Roll_Number'].nunique()
#     )

#     positive_percent = round(
#         (df['Sentiment'] == "Positive").mean() * 100,
#         2
#     )

#     m3.metric(
#         "Positive %",
#         f"{positive_percent}%"
#     )

#     m4.metric(
#         "Avg Polarity",
#         round(df['Polarity'].mean(), 2)
#     )

#     st.markdown("---")

#     # ========================================================
#     # TABS
#     # ========================================================

#     tab1, tab2, tab3, tab4 = st.tabs([
#         "📌 Event Analysis",
#         "👨‍🎓 Student Analysis",
#         "😊 Sentiment Analysis",
#         "📂 Raw Data"
#     ])

#     # ========================================================
#     # TAB 1
#     # ========================================================

#     with tab1:

#         st.subheader("Event-wise Analysis")

#         event = st.selectbox(
#             "Select Event",
#             df['Event_Name'].unique()
#         )

#         edf = df[df['Event_Name'] == event]

#         fig = px.pie(
#             edf,
#             names='Sentiment',
#             color='Sentiment',
#             color_discrete_map={
#                 'Positive': '#2ecc71',
#                 'Negative': '#e74c3c',
#                 'Neutral': '#f1c40f'
#             }
#         )

#         st.plotly_chart(
#             fig,
#             use_container_width=True
#         )

#         st.dataframe(
#             edf,
#             use_container_width=True
#         )

#     # ========================================================
#     # TAB 2
#     # ========================================================

#     with tab2:

#         student_list = sorted(
#             df['Student_Name'].dropna().unique()
#         )

#         student = st.selectbox(
#             "Select Student",
#             student_list
#         )

#         sdf = df[df['Student_Name'] == student]

#         st.dataframe(
#             sdf,
#             use_container_width=True
#         )

#     # ========================================================
#     # TAB 3
#     # ========================================================

#     with tab3:

#         sentiment_counts = (
#             df['Sentiment']
#             .value_counts()
#             .reset_index()
#         )

#         sentiment_counts.columns = [
#             'Sentiment',
#             'Count'
#         ]

#         fig = px.bar(
#             sentiment_counts,
#             x='Sentiment',
#             y='Count',
#             color='Sentiment',
#             color_discrete_map={
#                 'Positive': '#2ecc71',
#                 'Negative': '#e74c3c',
#                 'Neutral': '#f1c40f'
#             }
#         )

#         st.plotly_chart(
#             fig,
#             use_container_width=True
#         )

#     # ========================================================
#     # TAB 4
#     # ========================================================

#     with tab4:

#         st.dataframe(
#             df,
#             use_container_width=True
#         )

#         if is_admin:

#             csv = df.to_csv(
#                 index=False
#             ).encode('utf-8')

#             st.download_button(
#                 "⬇️ Download CSV",
#                 csv,
#                 "feedback.csv",
#                 "text/csv"
#             )



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

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Student Voice Feedback System",
    page_icon="🎤",
    layout="wide"
)

if os.path.exists("pragyan_ai_school_cover.jpg"):
    st.image("pragyan_ai_school_cover.jpg", use_container_width=True)

# ============================================================
# OPTIONAL: OPENCV (FACE DETECTION)
# Wrapped safely so a broken / missing OpenCV build never
# crashes the whole app — it just disables face verification.
# ============================================================

HAS_CV2 = False
FACE_CASCADE = None

try:
    import cv2

    # Some broken OpenCV builds import fine but are missing
    # large chunks of the API (this is exactly what caused the
    # AttributeError on Streamlit Cloud when it fell back to an
    # incompatible wheel under Python 3.14).
    if hasattr(cv2, "CascadeClassifier") and hasattr(cv2, "data"):
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        if os.path.exists(cascade_path):
            FACE_CASCADE = cv2.CascadeClassifier(cascade_path)
            if not FACE_CASCADE.empty():
                HAS_CV2 = True
except Exception:
    HAS_CV2 = False

# ============================================================
# OPTIONAL SPEECH RECOGNITION
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

COLUMNS = [
    'Timestamp',
    'Student_Name',
    'Roll_Number',
    'College_Name',
    'Department_name',
    'E_mail',
    'Phone_number',
    'Event_Name',
    'Face_Detected',
    'Transcript',
    'Sentiment',
    'Polarity'
]

# ============================================================
# CUSTOM CSS — WHITE BACKGROUND / BLACK BUTTONS / WHITE TEXT
# ============================================================

st.markdown("""
<style>

.stApp {
    background-color: #ffffff;
}

h1, h2, h3, h4, h5, h6, p, label, span, div {
    color: #000000;
}

/* Buttons: black background, white text */
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
div.stFormSubmitButton > button * {
    color: #ffffff !important;
}

div.stButton > button:hover,
div.stDownloadButton > button:hover,
div.stFormSubmitButton > button:hover {
    background-color: #333333 !important;
}

/* Inputs */
input, textarea {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    background-color: #ffffff !important;
}

.stTextInput > div > div > input,
.stTextArea textarea {
    border: 1px solid #000000 !important;
    border-radius: 6px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #f5f5f5;
    border-right: 1px solid #ddd;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background-color: #f9f9f9;
    border: 1px solid #eee;
    border-radius: 10px;
    padding: 10px;
}

/* Tabs */
button[data-baseweb="tab"] {
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# EXCEL FUNCTIONS
# ============================================================

def create_excel_if_not_exists():

    if not os.path.exists(EXCEL_FILE):

        wb = Workbook()
        ws = wb.active
        ws.title = "Feedback Data"

        header_fill = PatternFill(
            start_color="1F4E79",
            end_color="1F4E79",
            fill_type="solid"
        )

        header_font = Font(
            bold=True,
            color="FFFFFF"
        )

        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        for col_idx, header in enumerate(COLUMNS, 1):

            cell = ws.cell(row=1, column=col_idx, value=header)

            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")
            cell.border = thin_border

        wb.save(EXCEL_FILE)

# ============================================================

def append_to_excel(record):

    create_excel_if_not_exists()

    try:

        wb = load_workbook(EXCEL_FILE)
        ws = wb.active

        row_data = [record.get(col, '') for col in COLUMNS]

        ws.append(row_data)

        wb.save(EXCEL_FILE)

        return True

    except Exception as e:

        st.error(f"Excel Save Error: {e}")

        return False

# ============================================================

def load_from_excel():

    create_excel_if_not_exists()

    try:

        df = pd.read_excel(
            EXCEL_FILE,
            engine='openpyxl',
            header=0
        )

        if df.empty:
            return pd.DataFrame(columns=COLUMNS)

        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(
                df['Timestamp'],
                errors='coerce'
            )

        if 'Polarity' in df.columns:
            df['Polarity'] = pd.to_numeric(
                df['Polarity'],
                errors='coerce'
            )

        return df

    except Exception as e:

        st.error(f"Excel Load Error: {e}")

        return pd.DataFrame(columns=COLUMNS)

# ============================================================

def get_excel_download():

    if os.path.exists(EXCEL_FILE):

        with open(EXCEL_FILE, "rb") as f:
            return f.read()

    return None

# ============================================================
# LOGIC FUNCTIONS
# ============================================================

def analyze_sentiment(text):

    if not text:
        return "Neutral", 0.0

    polarity = TextBlob(text).sentiment.polarity

    if polarity > 0.1:
        return "Positive", polarity

    elif polarity < -0.1:
        return "Negative", polarity

    else:
        return "Neutral", polarity

# ============================================================

def detect_faces(image_bytes):
    """
    Returns (PIL_image_or_None, face_count, face_verified_bool).
    Never raises — if OpenCV is unavailable or broken, it degrades
    gracefully instead of crashing the app.
    """

    if not HAS_CV2 or FACE_CASCADE is None:
        # No working face detector available — just decode the
        # image so it can still be shown/stored, but skip detection.
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

        faces = FACE_CASCADE.detectMultiScale(
            gray,
            1.1,
            5,
            minSize=(60, 60)
        )

        pil_img = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))

        return pil_img, len(faces), len(faces) > 0

    except Exception:
        # Any unexpected OpenCV failure at runtime — fail safe.
        return None, 0, False

# ============================================================

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

if not HAS_CV2:
    st.sidebar.warning(
        "⚠️ Face verification is disabled (OpenCV face detector "
        "unavailable on this server). Feedback submission still works."
    )

page = st.sidebar.radio(
    "Navigate",
    ["Record Feedback", "Analysis Dashboard"]
)

# ============================================================
# SIDEBAR — ADMIN
# ============================================================

st.sidebar.markdown("---")

st.sidebar.subheader("🔒 Admin Access")

pwd_input = st.sidebar.text_input(
    "Enter Password",
    type="password"
)

is_admin = (pwd_input == ADMIN_PASSWORD)

if is_admin:

    st.sidebar.success("Access Granted")

    excel_data = get_excel_download()

    if excel_data:

        st.sidebar.download_button(
            "📥 Download Excel",
            excel_data,
            "feedback_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

elif pwd_input != "":

    st.sidebar.error("Incorrect Password")

# ============================================================
# PAGE 1 - RECORD FEEDBACK
# ============================================================

if page == "Record Feedback":

    st.header("Submit Your Feedback")

    col1, col2 = st.columns(2)

    with col1:

        s_name = st.text_input("Full Name *")

        s_roll = st.text_input("Roll Number *")

        s_college = st.text_input("College Name")

    with col2:

        s_event = st.selectbox(
            "Event",
            [
                "Hackathon 2026",
                "Science Fair",
                "Sports Meet",
                "Other"
            ]
        )

        s_email = st.text_input("Email")

        s_phone = st.text_input("Phone Number")

    st.subheader("📸 Capture Photo")

    img_file = st.camera_input("Take Photo")

    st.subheader("🎙️ Feedback")

    with st.form("feedback_form"):

        audio_data = st.audio_input("Record Voice")

        text_data = st.text_area("Or Type Feedback")

        submitted = st.form_submit_button(
            "Submit Feedback"
        )

    # ========================================================

    if submitted:

        if not s_name or not s_roll:

            st.error("Name and Roll Number required!")

        else:

            transcript = (
                transcribe_audio(audio_data.getvalue())
                if audio_data else text_data
            )

            sentiment, score = analyze_sentiment(
                transcript
            )

            face_verified = False

            if img_file:

                _, _, face_verified = detect_faces(
                    img_file.getvalue()
                )

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

                'Polarity': score
            }

            if append_to_excel(record):

                st.success(
                    f"✅ Feedback Saved! Sentiment: {sentiment}"
                )

                st.balloons()

# ============================================================
# PAGE 2 - ANALYTICS DASHBOARD
# ============================================================

elif page == "Analysis Dashboard":

    st.header("📊 Feedback Analysis Dashboard")

    df = load_from_excel()

    required_cols = [
        'Timestamp',
        'Student_Name',
        'Roll_Number',
        'Event_Name',
        'Sentiment',
        'Polarity'
    ]

    missing_cols = [
        col for col in required_cols
        if col not in df.columns
    ]

    if missing_cols:

        st.error(
            f"❌ Missing columns in Excel: {missing_cols}"
        )

        st.stop()

    if df.empty:

        st.warning(
            "⚠️ No data available yet. Submit feedback first."
        )

        st.stop()

    # ========================================================
    # TOP METRICS
    # ========================================================

    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        "Total Feedbacks",
        len(df)
    )

    m2.metric(
        "Unique Students",
        df['Roll_Number'].nunique()
    )

    positive_percent = round(
        (df['Sentiment'] == "Positive").mean() * 100,
        2
    )

    m3.metric(
        "Positive %",
        f"{positive_percent}%"
    )

    m4.metric(
        "Avg Polarity",
        round(df['Polarity'].mean(), 2)
    )

    st.markdown("---")

    # ========================================================
    # TABS
    # ========================================================

    tab1, tab2, tab3, tab4 = st.tabs([
        "📌 Event Analysis",
        "👨‍🎓 Student Analysis",
        "😊 Sentiment Analysis",
        "📂 Raw Data"
    ])

    with tab1:

        st.subheader("Event-wise Analysis")

        event = st.selectbox(
            "Select Event",
            df['Event_Name'].unique()
        )

        edf = df[df['Event_Name'] == event]

        fig = px.pie(
            edf,
            names='Sentiment',
            color='Sentiment',
            color_discrete_map={
                'Positive': '#2ecc71',
                'Negative': '#e74c3c',
                'Neutral': '#f1c40f'
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            edf,
            use_container_width=True
        )

    with tab2:

        student_list = sorted(
            df['Student_Name'].dropna().unique()
        )

        student = st.selectbox(
            "Select Student",
            student_list
        )

        sdf = df[df['Student_Name'] == student]

        st.dataframe(
            sdf,
            use_container_width=True
        )

    with tab3:

        sentiment_counts = (
            df['Sentiment']
            .value_counts()
            .reset_index()
        )

        sentiment_counts.columns = [
            'Sentiment',
            'Count'
        ]

        fig = px.bar(
            sentiment_counts,
            x='Sentiment',
            y='Count',
            color='Sentiment',
            color_discrete_map={
                'Positive': '#2ecc71',
                'Negative': '#e74c3c',
                'Neutral': '#f1c40f'
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with tab4:

        st.dataframe(
            df,
            use_container_width=True
        )

        if is_admin:

            csv = df.to_csv(
                index=False
            ).encode('utf-8')

            st.download_button(
                "⬇️ Download CSV",
                csv,
                "feedback.csv",
                "text/csv"
            )
