
"""
Student Voice Feedback System - with OpenCV Face Detection + Excel Persistence
Every submission is appended to feedback_data.xlsx with timestamp
"""

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

# Optional: Speech recognition
try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Student Voice Feedback System", page_icon="🎤", layout="wide")

# Company logo
st.image("pragyan_ai_school_cover.jpg", width=1150)

# --- EXCEL FILE PATH ---
EXCEL_FILE = "feedback_data.xlsx"

COLUMNS = [
    'Timestamp', 'Student_Name', 'Roll_Number', 'College_Name', 'Department_name', 'E_mail', 'Phone_number', 'Event_Name',
    'Face_Detected', 'Transcript', 'Sentiment', 'Polarity'
]

# ============================================================
# EXCEL FUNCTIONS
# ============================================================

def create_excel_if_not_exists():
    """Create Excel file with styled header if it doesn't exist."""
    if not os.path.exists(EXCEL_FILE):
        wb = Workbook()
        ws = wb.active
        ws.title = "Feedback Data"

        headers = COLUMNS
        header_fill = PatternFill("solid", start_color="1F4E79")
        header_font = Font(bold=True, color="FFFFFF", name="Arial", size=11)
        thin_border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )

        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border

        # Column widths
        col_widths = {
            'Timestamp': 22, 'Student_Name': 20, 'Roll_Number': 15, 'College_Name': 22, 'Department_name': 20, 'E_mail':20, 'Phone_number':20,
            'Event_Name': 22, 'Face_Detected': 15, 'Transcript': 50,
            'Sentiment': 12, 'Polarity': 12
        }
        for col_idx, col_name in enumerate(headers, 1):
            ws.column_dimensions[get_column_letter(col_idx)].width = col_widths.get(col_name, 15)

        ws.row_dimensions[1].height = 22
        ws.freeze_panes = "A2"
        wb.save(EXCEL_FILE)


def append_to_excel(record: dict):
    """Append one row to the Excel file. Creates file if missing."""
    create_excel_if_not_exists()
    try:
        wb = load_workbook(EXCEL_FILE)
        ws = wb.active

        next_row = ws.max_row + 1
        thin_border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )

        # Alternate row fill for readability
        row_fill = PatternFill("solid", start_color="D6E4F0") if next_row % 2 == 0 else PatternFill("solid", start_color="FFFFFF")

        # Sentiment color
        sentiment_colors = {"Positive": "C6EFCE", "Negative": "FFC7CE", "Neutral": "FFEB9C"}
        sentiment_fill = PatternFill("solid", start_color=sentiment_colors.get(record.get('Sentiment', 'Neutral'), "FFFFFF"))

        row_data = [
            record.get('Timestamp', ''),
            record.get('Student_Name', ''),
            record.get('Roll_Number', ''),
            record.get('College_Name', ''),
            record.get('Department_name', ''),
            record.get('E_mail', ''),
            record.get('Phone_number', ''),
            record.get('Event_Name', ''),
            str(record.get('Face_Detected', False)),
            record.get('Transcript', ''),
            record.get('Sentiment', ''),
            round(float(record.get('Polarity', 0.0)), 4),
        ]

        for col_idx, value in enumerate(row_data, 1):
            cell = ws.cell(row=next_row, column=col_idx, value=value)
            cell.font = Font(name="Arial", size=10)
            cell.border = thin_border
            cell.alignment = Alignment(vertical="center", wrap_text=(col_idx == 10))  # wrap Transcript

            # Sentiment column gets color
            if col_idx == 11:
                cell.fill = sentiment_fill
            else:
                cell.fill = row_fill

        ws.row_dimensions[next_row].height = 18
        wb.save(EXCEL_FILE)
        return True
    except Exception as e:
        st.error(f"⚠️ Could not save to Excel: {e}")
        return False


def load_from_excel():
    """Load all data from Excel into a DataFrame."""
    create_excel_if_not_exists()
    try:
        df = pd.read_excel(EXCEL_FILE, engine='openpyxl')
        if df.empty:
            return pd.DataFrame(columns=COLUMNS + ['Photo'])
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df['Polarity'] = pd.to_numeric(df['Polarity'], errors='coerce').fillna(0.0)
        df['Face_Detected'] = df['Face_Detected'].map(
            {'True': True, 'False': False, True: True, False: False}
        ).fillna(False)
        df['Photo'] = None  # Photos not stored in Excel
        return df
    except Exception as e:
        st.error(f"⚠️ Could not load from Excel: {e}")
        return pd.DataFrame(columns=COLUMNS + ['Photo'])


def get_excel_download():
    """Read Excel file as bytes for download button."""
    if os.path.exists(EXCEL_FILE):
        with open(EXCEL_FILE, "rb") as f:
            return f.read()
    return None


# ============================================================
# INITIALIZE SESSION STATE
# ============================================================

if 'feedbacks' not in st.session_state:
    st.session_state['feedbacks'] = load_from_excel()

if 'captured_photo' not in st.session_state:
    st.session_state['captured_photo'] = None

# Ensure Excel file exists on startup
create_excel_if_not_exists()


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

# def load_sample_data():
#     samples = [
#         {'Timestamp': datetime.datetime.now(), 'Student_Name': 'Alice Smith', 'Roll_Number': '101', 'Event_Name': 'Hackathon 2026', 'Photo': None, 'Face_Detected': True, 'Transcript': 'The event was absolutely amazing and I learned so much about AI.', 'Sentiment': 'Positive', 'Polarity': 0.8},
#         {'Timestamp': datetime.datetime.now(), 'Student_Name': 'Bob Jones', 'Roll_Number': '102', 'Event_Name': 'Hackathon 2026', 'Photo': None, 'Face_Detected': True, 'Transcript': 'It was poorly organized and the internet kept dropping. Very frustrating.', 'Sentiment': 'Negative', 'Polarity': -0.6},
#         {'Timestamp': datetime.datetime.now(), 'Student_Name': 'Charlie Brown', 'Roll_Number': '103', 'Event_Name': 'Science Fair', 'Photo': None, 'Face_Detected': False, 'Transcript': 'It was okay, nothing special but decent overall.', 'Sentiment': 'Neutral', 'Polarity': 0.05},
#         {'Timestamp': datetime.datetime.now(), 'Student_Name': 'Alice Smith', 'Roll_Number': '101', 'Event_Name': 'Science Fair', 'Photo': None, 'Face_Detected': True, 'Transcript': 'Great presentations, really enjoyed the chemistry experiments!', 'Sentiment': 'Positive', 'Polarity': 0.6},
#     ]
#     for s in samples:
#         append_to_excel(s)
#     st.session_state['feedbacks'] = load_from_excel()

def load_sample_data():
    samples = [
        {
            'Timestamp': datetime.datetime.now(),
            'Student_Name': 'Alice Smith',
            'Roll_Number': '101',
            'College_Name': 'ABC College',
            'Department_name': 'CSE',
            'E_mail': 'alice@example.com',
            'Phone_number': '9876543210',
            'Event_Name': 'Hackathon 2026',
            'Face_Detected': True,
            'Transcript': 'The event was absolutely amazing and I learned so much about AI.',
            'Sentiment': 'Positive',
            'Polarity': 0.8
        },
        {
            'Timestamp': datetime.datetime.now(),
            'Student_Name': 'Bob Jones',
            'Roll_Number': '102',
            'College_Name': 'XYZ College',
            'Department_name': 'ECE',
            'E_mail': 'bob@example.com',
            'Phone_number': '9123456780',
            'Event_Name': 'Hackathon 2026',
            'Face_Detected': True,
            'Transcript': 'It was poorly organized and the internet kept dropping. Very frustrating.',
            'Sentiment': 'Negative',
            'Polarity': -0.6
        },
        {
            'Timestamp': datetime.datetime.now(),
            'Student_Name': 'Charlie Brown',
            'Roll_Number': '103',
            'College_Name': 'LMN College',
            'Department_name': 'MECH',
            'E_mail': 'charlie@example.com',
            'Phone_number': '9988776655',
            'Event_Name': 'Science Fair',
            'Face_Detected': False,
            'Transcript': 'It was okay, nothing special but decent overall.',
            'Sentiment': 'Neutral',
            'Polarity': 0.05
        }
    ]

    for s in samples:
        append_to_excel(s)

    st.session_state['feedbacks'] = load_from_excel()

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


def transcribe_audio(audio_bytes):
    if not HAS_SR:
        return "SpeechRecognition library not installed."
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        return "Audio could not be understood. Please try speaking clearer."
    except Exception as e:
        return f"Could not transcribe audio. Error: {str(e)}"


def detect_faces(image_bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img_bgr is None:
        return None, 0, False
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
    face_count = len(faces)
    img_annotated = img_bgr.copy()
    for (x, y, w, h) in faces:
        cv2.rectangle(img_annotated, (x, y), (x + w, y + h), (0, 200, 0), 3)
        cv2.putText(img_annotated, 'Face Detected', (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 0), 2)
    img_rgb = cv2.cvtColor(img_annotated, cv2.COLOR_BGR2RGB)
    return Image.fromarray(img_rgb), face_count, face_count > 0


# ============================================================
# MAIN APP
# ============================================================

st.title("🎤 Student Event Voice Feedback System")

page = st.sidebar.radio("Navigate", ["Record Feedback", "Analysis Dashboard"])

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Data Options")

if st.sidebar.button("Load Sample Data"):
    load_sample_data()
    st.sidebar.success("Sample data loaded & saved to Excel!")

# Excel download always available in sidebar
excel_bytes = get_excel_download()
if excel_bytes:
    st.sidebar.download_button(
        label="📥 Download Excel File",
        data=excel_bytes,
        file_name=f"feedback_data_{datetime.date.today()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if st.sidebar.button("🔄 Refresh Data from Excel"):
    st.session_state['feedbacks'] = load_from_excel()
    st.sidebar.success("Data refreshed!")

# Show Excel file info in sidebar
if os.path.exists(EXCEL_FILE):
    file_size = os.path.getsize(EXCEL_FILE) / 1024
    total_rows = len(st.session_state['feedbacks'])
    st.sidebar.info(f"📊 **Excel File**\n\n`{EXCEL_FILE}`\n\n{total_rows} record(s) | {file_size:.1f} KB")

# ==========================================
# PAGE 1: RECORD FEEDBACK
# ==========================================
if page == "Record Feedback":
    st.header("Submit Your Feedback")

    st.subheader("1️⃣ User & Event Details")
    col1, col2 = st.columns(2)
    with col1:
        student_name = st.text_input("Full Name *")
        roll_number = st.text_input("Roll Number / ID *")
        College_Name= st.text_input("College Name *")
        Phone_number = st.text_input("Phone Number *")  

        
    with col2:
        event_name = st.selectbox("Select Event *",
                                  ["Hackathon 2026", "Science Fair", "Annual Sports Meet", "Tech Symposium", "Other"])
        if event_name == "Other":
            event_name = st.text_input("Specify Event Name")
        E_mail=st.text_input("Please enter your Email ID")
        Department_name=st.text_input("Department Name *")


    st.markdown("---")

    st.subheader("2️⃣ 📸 Photo Identity (with Face Detection)")
    st.info("📌 Take or upload your photo below. Face detection runs automatically.")

    photo_method = st.radio("Choose photo method", ["📷 Take Photo", "📁 Upload Image"], horizontal=True)

    if photo_method == "📷 Take Photo":
        live_photo = st.camera_input("📸 Click the shutter button to capture your photo")
        if live_photo is not None:
            st.session_state['captured_photo'] = live_photo
    else:
        uploaded_photo = st.file_uploader("Upload your photo", type=['jpg', 'jpeg', 'png'])
        if uploaded_photo is not None:
            st.session_state['captured_photo'] = uploaded_photo

    if st.session_state['captured_photo'] is not None:
        with st.spinner("🔍 Running face detection..."):
            preview_img, preview_count, preview_detected = detect_faces(
                st.session_state['captured_photo'].getvalue()
            )
        if preview_img:
            col_p1, col_p2 = st.columns([1, 2])
            with col_p1:
                st.image(preview_img, caption="📸 Face Detection Preview", use_container_width=True)
            with col_p2:
                if preview_detected:
                    st.success(f"✅ {preview_count} face(s) detected! You're verified.")
                else:
                    st.warning("⚠️ No face detected. Please retake with your face clearly visible.")
                    if st.button("🔄 Retake Photo"):
                        st.session_state['captured_photo'] = None
                        st.rerun()
    else:
        st.caption("No photo taken yet.")

    st.markdown("---")

    st.subheader("3️⃣ 🎙️ Voice Feedback & Submit")

    with st.form("feedback_form", clear_on_submit=True):
        st.info("**Please answer these questions in your recording:**\n"
                "1. What did you enjoy most about this event?\n"
                "2. Were there any challenges or things you disliked?\n"
                "3. Would you recommend this event to others?")

        audio_value = st.audio_input("🎙️ Record your feedback here")
        fallback_text = st.text_area("Or type your feedback manually (if audio is unavailable)", height=100)

        submitted = st.form_submit_button("🚀 Submit Feedback", type="primary")

        if submitted:
            if not student_name or not roll_number or not event_name:
                st.error("❌ Please fill in Name, Roll Number, and Event above before submitting.")
            elif not audio_value and not fallback_text:
                st.error("❌ Please provide voice feedback or typed feedback.")
            else:
                with st.spinner("Processing and saving your submission..."):

                    final_photo = st.session_state.get('captured_photo', None)
                    face_detected = False
                    annotated_img = None
                    face_count = 0

                    if final_photo is not None:
                        annotated_img, face_count, face_detected = detect_faces(final_photo.getvalue())

                    transcript = transcribe_audio(audio_value.getvalue()) if audio_value else fallback_text
                    sentiment_label, polarity_score = analyze_sentiment(transcript)
                    submission_time = datetime.datetime.now()

                    record = {
                        'Timestamp': submission_time,
                        'Student_Name': student_name,
                        'Roll_Number': roll_number,
                        'College_Name': College_Name,        # ✅ add
                        'Department_name': Department_name,  # ✅ add
                        'E_mail': E_mail,                    # ✅ add
                        'Phone_number': Phone_number,
                        'Event_Name': event_name,
                        'Face_Detected': face_detected,
                        'Transcript': transcript,
                        'Sentiment': sentiment_label,
                        'Polarity': polarity_score
                    }

                    # ✅ Save to Excel (persistent)
                    excel_saved = append_to_excel(record)

                    # ✅ Update in-memory session state
                    new_record_df = pd.DataFrame([{**record, 'Photo': final_photo}])
                    st.session_state['feedbacks'] = pd.concat(
                        [st.session_state['feedbacks'], new_record_df], ignore_index=True
                    )

                    st.session_state['captured_photo'] = None

                if excel_saved:
                    st.success(f"✅ Feedback submitted & saved to Excel! Sentiment: **{sentiment_label}**")
                else:
                    st.warning(f"⚠️ Feedback processed but Excel save failed. Sentiment: **{sentiment_label}**")

                res_col1, res_col2 = st.columns(2)
                with res_col1:
                    if annotated_img:
                        st.image(annotated_img, caption="Face Detection Result", use_container_width=True)
                        if face_detected:
                            st.success(f"✅ {face_count} face(s) verified!")
                        else:
                            st.warning("⚠️ No face detected in the submitted photo.")
                with res_col2:
                    with st.expander("📝 View Transcript", expanded=True):
                        st.write(transcript)
                    emoji = "🟢" if sentiment_label == "Positive" else "🔴" if sentiment_label == "Negative" else "⚪"
                    st.metric("Sentiment", f"{emoji} {sentiment_label}", f"Score: {polarity_score:.2f}")
                    st.caption(f"🕐 Saved at: {submission_time.strftime('%Y-%m-%d %H:%M:%S')}")

# ==========================================
# PAGE 2: ANALYSIS DASHBOARD
# ==========================================
elif page == "Analysis Dashboard":
    st.header("📊 Feedback Analysis Dashboard")

    df = st.session_state['feedbacks']

    if df.empty:
        st.warning("No feedback data yet. Record feedback or load sample data from the sidebar.")
    else:
        st.subheader("Overall Summary")
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Total Feedbacks", len(df))
        m2.metric("Unique Students", df['Roll_Number'].nunique())
        m3.metric("Total Events", df['Event_Name'].nunique())
        avg_polarity = df['Polarity'].mean()
        overall_sentiment = "Positive" if avg_polarity > 0.1 else ("Negative" if avg_polarity < -0.1 else "Neutral")
        m4.metric("Avg Sentiment", overall_sentiment, f"{avg_polarity:.2f}")
        if 'Face_Detected' in df.columns:
            m5.metric("Face Verified", f"{df['Face_Detected'].sum()}/{len(df)}")

        tab1, tab2, tab3, tab4 = st.tabs(["Event-Wise", "Student-Wise", "Face Detection Stats", "Raw Data"])

        with tab1:
            col_e1, col_e2 = st.columns([1, 2])
            with col_e1:
                selected_event = st.selectbox("Select Event", df['Event_Name'].unique())
                event_df = df[df['Event_Name'] == selected_event]
                st.write(f"**Total Feedbacks:** {len(event_df)}")
                st.write(f"**Avg Polarity:** {event_df['Polarity'].mean():.2f}")
                if 'Face_Detected' in event_df.columns:
                    st.write(f"**Face Verified:** {event_df['Face_Detected'].sum()}/{len(event_df)}")
            with col_e2:
                sentiment_counts = event_df['Sentiment'].value_counts().reset_index()
                sentiment_counts.columns = ['Sentiment', 'Count']
                fig_pie = px.pie(sentiment_counts, values='Count', names='Sentiment',
                                 title=f"Sentiment - {selected_event}",
                                 color='Sentiment',
                                 color_discrete_map={'Positive': 'green', 'Negative': 'red', 'Neutral': 'gray'})
                st.plotly_chart(fig_pie, use_container_width=True)

            st.write("#### Recent Feedback Highlights")
            for idx, row in event_df.head(5).iterrows():
                emoji = "🟢" if row['Sentiment'] == "Positive" else "🔴" if row['Sentiment'] == "Negative" else "⚪"
                face_icon = "✅" if row.get('Face_Detected', False) else "❌"
                st.info(f"{emoji} **{row['Student_Name']} ({row['Roll_Number']})** | Face: {face_icon}\n\n\"{row['Transcript']}\"")

        with tab2:
            student_list = df.apply(lambda x: f"{x['Student_Name']} ({x['Roll_Number']})", axis=1).unique()
            selected_student_str = st.selectbox("Select Student", student_list)
            selected_roll = selected_student_str.split("(")[-1].replace(")", "")
            student_df = df[df['Roll_Number'] == selected_roll]

            st.markdown("---")
            col_s1, col_s2 = st.columns([1, 3])
            with col_s1:
                recent_photo = student_df.iloc[-1]['Photo']
                if recent_photo is not None:
                    st.image(recent_photo, caption="Student Photo", use_container_width=True)
                else:
                    st.image("https://api.dicebear.com/7.x/initials/svg?seed=" + student_df.iloc[-1]['Student_Name'], caption="No Photo")
            with col_s2:
                st.subheader(student_df.iloc[-1]['Student_Name'])
                st.write(f"**Roll Number:** {selected_roll}")
                st.write(f"**Total Events Reviewed:** {len(student_df)}")
                for idx, row in student_df.iterrows():
                    color = "green" if row['Sentiment'] == 'Positive' else "red" if row['Sentiment'] == 'Negative' else "gray"
                    face_icon = "✅ Verified" if row.get('Face_Detected', False) else "❌ Not Verified"
                    st.markdown(f"**Event:** {row['Event_Name']} | **Date:** {row['Timestamp'].strftime('%Y-%m-%d %H:%M:%S')} | **Face:** {face_icon}")
                    st.markdown(f"**Sentiment:** :{color}[{row['Sentiment']}]")
                    st.caption(f"\"{row['Transcript']}\"")
                    st.markdown("---")

        with tab3:
            st.subheader("🔍 Face Detection Overview")
            if 'Face_Detected' in df.columns:
                fd_col1, fd_col2 = st.columns(2)
                with fd_col1:
                    face_summary = df['Face_Detected'].value_counts().reset_index()
                    face_summary.columns = ['Status', 'Count']
                    face_summary['Status'] = face_summary['Status'].map({True: 'Detected ✅', False: 'Not Detected ❌'})
                    fig_face = px.pie(face_summary, values='Count', names='Status',
                                     title="Overall Face Detection Rate",
                                     color_discrete_sequence=['#00C49A', '#FF6B6B'])
                    st.plotly_chart(fig_face, use_container_width=True)
                with fd_col2:
                    event_face = df.groupby('Event_Name')['Face_Detected'].agg(['sum', 'count']).reset_index()
                    event_face.columns = ['Event', 'Verified', 'Total']
                    event_face['Not Verified'] = event_face['Total'] - event_face['Verified']
                    fig_bar = px.bar(event_face, x='Event', y=['Verified', 'Not Verified'],
                                     title="Face Verification per Event",
                                     color_discrete_map={'Verified': '#00C49A', 'Not Verified': '#FF6B6B'},
                                     barmode='stack')
                    st.plotly_chart(fig_bar, use_container_width=True)

                unverified = df[df['Face_Detected'] == False][['Student_Name', 'Roll_Number', 'Event_Name', 'Timestamp']]
                if not unverified.empty:
                    st.warning(f"⚠️ {len(unverified)} submission(s) without face verification:")
                    st.dataframe(unverified, use_container_width=True)
                else:
                    st.success("✅ All submissions have been face-verified!")

        with tab4:
            st.subheader("Complete Data Log")
            display_df = df.drop(columns=['Photo']).copy()
            display_df['Timestamp'] = display_df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            st.dataframe(display_df, use_container_width=True)

            col_d1, col_d2 = st.columns(2)
            with col_d1:
                csv = display_df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download CSV", data=csv,
                                   file_name=f'feedback_{datetime.date.today()}.csv', mime='text/csv')
            with col_d2:
                excel_bytes = get_excel_download()
                if excel_bytes:
                    st.download_button(
                        "📊 Download Excel (.xlsx)",
                        data=excel_bytes,
                        file_name=f"feedback_data_{datetime.date.today()}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
