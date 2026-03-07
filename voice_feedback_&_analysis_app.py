# -*- coding: utf-8 -*-
"""
Student Voice Feedback System - with OpenCV Face Detection
"""

import streamlit as st
import pandas as pd
from textblob import TextBlob
import plotly.express as px
import datetime
import io
import cv2
import numpy as np
from PIL import Image

# Optional: Speech recognition
try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Student Voice Feedback System", page_icon="🎤", layout="wide")

# --- INITIALIZE SESSION STATE ---
if 'feedbacks' not in st.session_state:
    st.session_state['feedbacks'] = pd.DataFrame(columns=[
        'Timestamp', 'Student_Name', 'Roll_Number', 'Event_Name',
        'Photo', 'Face_Detected', 'Transcript', 'Sentiment', 'Polarity'
    ])

# --- SAMPLE DATA LOADER ---
def load_sample_data():
    sample_data = pd.DataFrame([
        {'Timestamp': datetime.datetime.now(), 'Student_Name': 'Alice Smith', 'Roll_Number': '101', 'Event_Name': 'Hackathon 2026', 'Photo': None, 'Face_Detected': True, 'Transcript': 'The event was absolutely amazing and I learned so much about AI.', 'Sentiment': 'Positive', 'Polarity': 0.8},
        {'Timestamp': datetime.datetime.now(), 'Student_Name': 'Bob Jones', 'Roll_Number': '102', 'Event_Name': 'Hackathon 2026', 'Photo': None, 'Face_Detected': True, 'Transcript': 'It was poorly organized and the internet kept dropping. Very frustrating.', 'Sentiment': 'Negative', 'Polarity': -0.6},
        {'Timestamp': datetime.datetime.now(), 'Student_Name': 'Charlie Brown', 'Roll_Number': '103', 'Event_Name': 'Science Fair', 'Photo': None, 'Face_Detected': False, 'Transcript': 'It was okay, nothing special but decent overall.', 'Sentiment': 'Neutral', 'Polarity': 0.05},
        {'Timestamp': datetime.datetime.now(), 'Student_Name': 'Alice Smith', 'Roll_Number': '101', 'Event_Name': 'Science Fair', 'Photo': None, 'Face_Detected': True, 'Transcript': 'Great presentations, really enjoyed the chemistry experiments!', 'Sentiment': 'Positive', 'Polarity': 0.6},
    ])
    st.session_state['feedbacks'] = pd.concat([st.session_state['feedbacks'], sample_data], ignore_index=True)

# --- UTILITY FUNCTIONS ---

def analyze_sentiment(text):
    """Analyze text sentiment using TextBlob"""
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
    """Transcribe audio using SpeechRecognition"""
    if not HAS_SR:
        return "SpeechRecognition library not installed."
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    except sr.UnknownValueError:
        return "Audio could not be understood. Please try speaking clearer."
    except Exception as e:
        return f"Could not transcribe audio. Error: {str(e)}"

def detect_faces(image_bytes):
    """
    Detect faces in an image using OpenCV Haar Cascade.
    Returns:
        annotated_image (PIL Image): Image with rectangles drawn around faces
        face_count (int): Number of faces detected
        face_detected (bool): Whether at least one face was found
    """
    # Load image from bytes
    nparr = np.frombuffer(image_bytes, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img_bgr is None:
        return None, 0, False

    # Convert to grayscale for detection
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # Load OpenCV's built-in face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60)
    )

    face_count = len(faces)
    face_detected = face_count > 0

    # Draw rectangles around detected faces
    img_annotated = img_bgr.copy()
    for (x, y, w, h) in faces:
        # Draw green rectangle
        cv2.rectangle(img_annotated, (x, y), (x + w, y + h), (0, 200, 0), 3)
        # Add label above the box
        cv2.putText(img_annotated, f'Face Detected', (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 0), 2)

    # Convert back to RGB for display with PIL
    img_rgb = cv2.cvtColor(img_annotated, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(img_rgb)

    return pil_image, face_count, face_detected

# --- MAIN APP ---
st.title("🎤 Student Event Voice Feedback System")

# Sidebar Navigation
page = st.sidebar.radio("Navigate", ["Record Feedback", "Analysis Dashboard"])

if st.sidebar.button("Load Sample Data"):
    load_sample_data()
    st.sidebar.success("Sample data loaded!")

# ==========================================
# PAGE 1: RECORD FEEDBACK
# ==========================================
if page == "Record Feedback":
    st.header("Submit Your Feedback")

    with st.form("feedback_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("1. User Details")
            student_name = st.text_input("Full Name *")
            roll_number = st.text_input("Roll Number / ID *")

        with col2:
            st.subheader("2. Event Details")
            event_name = st.selectbox("Select Event *",
                                      ["Hackathon 2026", "Science Fair", "Annual Sports Meet", "Tech Symposium", "Other"])
            if event_name == "Other":
                event_name = st.text_input("Specify Event Name")

        # --- PHOTO + FACE DETECTION SECTION ---
        st.subheader("3. 📸 Photo Identity (with Face Detection)")
        st.info("📌 A face must be detected in your photo to verify identity.")

        photo_method = st.radio("Choose photo method", ["Upload Image", "Take Photo"], horizontal=True)
        photo_data = None

        if photo_method == "Upload Image":
            photo_data = st.file_uploader("Upload your photo", type=['jpg', 'jpeg', 'png'])
        else:
            photo_data = st.camera_input("Take a picture")

        st.subheader("4. Voice Feedback")
        st.info("**Please answer the following questions in your recording:**\n"
                "1. What did you enjoy most about this event?\n"
                "2. Were there any challenges or things you disliked?\n"
                "3. Would you recommend this event to others?")

        audio_value = st.audio_input("🎙️ Record your feedback here")
        fallback_text = st.text_area("Or type your feedback manually (if audio is unavailable)", height=100)

        submitted = st.form_submit_button("Submit Feedback", type="primary")

        if submitted:
            if not student_name or not roll_number or not event_name:
                st.error("Please fill in all mandatory fields (*).")
            elif not audio_value and not fallback_text:
                st.error("Please provide either voice feedback or text feedback.")
            else:
                with st.spinner("Processing feedback & running face detection..."):

                    # --- FACE DETECTION ---
                    face_detected = False
                    annotated_img = None
                    face_count = 0

                    if photo_data is not None:
                        image_bytes = photo_data.getvalue()
                        annotated_img, face_count, face_detected = detect_faces(image_bytes)

                    # --- TRANSCRIPTION ---
                    transcript = ""
                    if audio_value:
                        transcript = transcribe_audio(audio_value.getvalue())
                    else:
                        transcript = fallback_text

                    # --- SENTIMENT ---
                    sentiment_label, polarity_score = analyze_sentiment(transcript)

                    # --- SAVE RECORD ---
                    new_record = pd.DataFrame([{
                        'Timestamp': datetime.datetime.now(),
                        'Student_Name': student_name,
                        'Roll_Number': roll_number,
                        'Event_Name': event_name,
                        'Photo': photo_data,
                        'Face_Detected': face_detected,
                        'Transcript': transcript,
                        'Sentiment': sentiment_label,
                        'Polarity': polarity_score
                    }])
                    st.session_state['feedbacks'] = pd.concat(
                        [st.session_state['feedbacks'], new_record], ignore_index=True
                    )

                # --- RESULTS ---
                st.success(f"✅ Feedback submitted! Detected Sentiment: **{sentiment_label}**")

                result_col1, result_col2 = st.columns(2)

                with result_col1:
                    if annotated_img is not None:
                        st.image(annotated_img, caption=f"Face Detection Result", use_container_width=True)
                        if face_detected:
                            st.success(f"✅ {face_count} face(s) detected successfully!")
                        else:
                            st.warning("⚠️ No face detected. Please retake your photo with your face clearly visible.")
                    elif photo_data is None:
                        st.info("ℹ️ No photo provided — face detection skipped.")

                with result_col2:
                    with st.expander("📝 View Transcript", expanded=True):
                        st.write(transcript)
                    sentiment_color = "🟢" if sentiment_label == "Positive" else "🔴" if sentiment_label == "Negative" else "⚪"
                    st.metric("Sentiment", f"{sentiment_color} {sentiment_label}", f"Polarity: {polarity_score:.2f}")

# ==========================================
# PAGE 2: ANALYSIS DASHBOARD
# ==========================================
elif page == "Analysis Dashboard":
    st.header("📊 Feedback Analysis Dashboard")

    df = st.session_state['feedbacks']

    if df.empty:
        st.warning("No feedback data available yet. Please record some feedback or load sample data from the sidebar.")
    else:
        # --- OVERALL SUMMARY ---
        st.subheader("Overall Summary")
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Total Feedbacks", len(df))
        m2.metric("Unique Students", df['Roll_Number'].nunique())
        m3.metric("Total Events", df['Event_Name'].nunique())

        avg_polarity = df['Polarity'].mean()
        overall_sentiment = "Positive" if avg_polarity > 0.1 else ("Negative" if avg_polarity < -0.1 else "Neutral")
        m4.metric("Avg Sentiment", overall_sentiment, f"{avg_polarity:.2f}")

        # Face detection stat
        if 'Face_Detected' in df.columns:
            face_verified = df['Face_Detected'].sum()
            m5.metric("Face Verified", f"{face_verified}/{len(df)}")

        # --- TABS ---
        tab1, tab2, tab3, tab4 = st.tabs(["Event-Wise Analysis", "Student-Wise Analysis", "Face Detection Stats", "Raw Data"])

        # TAB 1: EVENT-WISE
        with tab1:
            col_e1, col_e2 = st.columns([1, 2])
            with col_e1:
                selected_event = st.selectbox("Select Event to Analyze", df['Event_Name'].unique())
                event_df = df[df['Event_Name'] == selected_event]
                st.write(f"**Total Feedbacks:** {len(event_df)}")
                st.write(f"**Avg Polarity:** {event_df['Polarity'].mean():.2f}")
                if 'Face_Detected' in event_df.columns:
                    verified = event_df['Face_Detected'].sum()
                    st.write(f"**Face Verified:** {verified}/{len(event_df)}")

            with col_e2:
                sentiment_counts = event_df['Sentiment'].value_counts().reset_index()
                sentiment_counts.columns = ['Sentiment', 'Count']
                fig_pie = px.pie(sentiment_counts, values='Count', names='Sentiment',
                                 title=f"Sentiment Distribution - {selected_event}",
                                 color='Sentiment',
                                 color_discrete_map={'Positive': 'green', 'Negative': 'red', 'Neutral': 'gray'})
                st.plotly_chart(fig_pie, use_container_width=True)

            st.write("#### Recent Feedback Highlights")
            for idx, row in event_df.head(5).iterrows():
                emoji = "🟢" if row['Sentiment'] == "Positive" else "🔴" if row['Sentiment'] == "Negative" else "⚪"
                face_icon = "✅" if row.get('Face_Detected', False) else "❌"
                st.info(f"{emoji} **{row['Student_Name']} ({row['Roll_Number']})** | Face: {face_icon}\n\n\"{row['Transcript']}\"")

        # TAB 2: STUDENT-WISE
        with tab2:
            student_list = df.apply(lambda x: f"{x['Student_Name']} ({x['Roll_Number']})", axis=1).unique()
            selected_student_str = st.selectbox("Search / Select Student", student_list)
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
                st.write("#### Feedback History")
                for idx, row in student_df.iterrows():
                    color = "green" if row['Sentiment'] == 'Positive' else "red" if row['Sentiment'] == 'Negative' else "gray"
                    face_icon = "✅ Verified" if row.get('Face_Detected', False) else "❌ Not Verified"
                    st.markdown(f"**Event:** {row['Event_Name']} | **Date:** {row['Timestamp'].strftime('%Y-%m-%d')} | **Face:** {face_icon}")
                    st.markdown(f"**Sentiment:** :{color}[{row['Sentiment']}]")
                    st.caption(f"\"{row['Transcript']}\"")
                    st.markdown("---")

        # TAB 3: FACE DETECTION STATS
        with tab3:
            st.subheader("🔍 Face Detection Overview")

            if 'Face_Detected' in df.columns:
                fd_col1, fd_col2 = st.columns(2)

                with fd_col1:
                    face_summary = df['Face_Detected'].value_counts().reset_index()
                    face_summary.columns = ['Status', 'Count']
                    face_summary['Status'] = face_summary['Status'].map({True: 'Face Detected ✅', False: 'No Face ❌'})
                    fig_face = px.pie(face_summary, values='Count', names='Status',
                                     title="Overall Face Detection Rate",
                                     color_discrete_sequence=['#00C49A', '#FF6B6B'])
                    st.plotly_chart(fig_face, use_container_width=True)

                with fd_col2:
                    # Per-event face detection bar chart
                    event_face = df.groupby('Event_Name')['Face_Detected'].agg(['sum', 'count']).reset_index()
                    event_face.columns = ['Event', 'Verified', 'Total']
                    event_face['Not Verified'] = event_face['Total'] - event_face['Verified']
                    fig_bar = px.bar(event_face, x='Event', y=['Verified', 'Not Verified'],
                                     title="Face Verification per Event",
                                     color_discrete_map={'Verified': '#00C49A', 'Not Verified': '#FF6B6B'},
                                     barmode='stack')
                    st.plotly_chart(fig_bar, use_container_width=True)

                # Students without face verification
                unverified = df[df['Face_Detected'] == False][['Student_Name', 'Roll_Number', 'Event_Name', 'Timestamp']]
                if not unverified.empty:
                    st.warning(f"⚠️ {len(unverified)} submission(s) without face verification:")
                    st.dataframe(unverified, use_container_width=True)
                else:
                    st.success("✅ All submissions have been face-verified!")

        # TAB 4: RAW DATA
        with tab4:
            st.subheader("Complete Data Log")
            display_df = df.drop(columns=['Photo']).copy()
            display_df['Timestamp'] = display_df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            st.dataframe(display_df, use_container_width=True)

            csv = display_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Data as CSV",
                data=csv,
                file_name='feedback_analysis_export.csv',
                mime='text/csv',
            )
