# 🎤 Student Voice Feedback System

An AI-powered web application built with Streamlit that collects, transcribes, and analyzes student feedback for college events using voice recording, face detection, and sentiment analysis.

![Python](https://img.shields.io/badge/Python-3.9+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-red) ![OpenCV](https://img.shields.io/badge/OpenCV-green) ![TextBlob](https://img.shields.io/badge/NLP-TextBlob-purple) ![License](https://img.shields.io/badge/License-Proprietary-lightgrey)

---

## 📌 Overview

Traditional feedback forms get ignored and produce low-quality responses. This system removes friction by letting students **speak their feedback naturally**, verifies their identity via camera, and automatically processes everything into structured sentiment data — all in one seamless workflow.

Built as a module within **PragyanAI** — the AI-powered EdTech platform by Pragyan Smart AI Technology LLP.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎙️ Voice Recording | Record live audio feedback directly in the browser |
| 📝 Auto Transcription | Speech-to-text via Google Speech Recognition API |
| 📸 Face Detection | OpenCV Haar Cascade detects and verifies student identity in real-time |
| 🧠 Sentiment Analysis | TextBlob NLP classifies feedback as Positive / Negative / Neutral |
| 📊 Analytics Dashboard | Event-wise and student-wise breakdown with Plotly charts |
| 💾 Excel Persistence | All submissions saved to `feedback_data.xlsx` with full timestamp |
| 📥 Data Export | Download all feedback as `.xlsx` or `.csv` |
| 🔤 Text Fallback | Manual text input if audio is unavailable |
| ☁️ Cloud Ready | Fully compatible with Streamlit Community Cloud |

---

## 🛠️ Tech Stack

- **Frontend** — Streamlit
- **Face Detection** — OpenCV (Haar Cascade Classifier)
- **NLP / Sentiment** — TextBlob
- **Speech-to-Text** — SpeechRecognition + Google Web Speech API
- **Data Visualization** — Plotly Express
- **Data Manipulation** — Pandas
- **Excel Storage** — openpyxl
- **Image Processing** — Pillow (PIL)
- **Language** — Python 3.9+

---

## 🚀 Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/student-voice-feedback.git
cd student-voice-feedback
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

App opens at **http://localhost:8501**

---

## 📦 requirements.txt

```
streamlit
pandas
textblob
plotly
opencv-python-headless
numpy
Pillow
SpeechRecognition
openpyxl
```

> ⚠️ Use `opencv-python-headless` (not `opencv-python`) for Streamlit Cloud deployment.

---

## 📁 Project Structure

```
student-voice-feedback/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── feedback_data.xlsx      # Auto-created on first submission
├── .streamlit/
│   └── secrets.toml        # Local credentials (never commit!)
├── .gitignore
└── README.md
```

---

## 🗂️ Data Storage

Every submission appends one row to `feedback_data.xlsx` with these columns:

| Column | Description |
|---|---|
| Timestamp | Exact date & time of submission (`YYYY-MM-DD HH:MM:SS`) |
| Student_Name | Full name entered by the student |
| Roll_Number | Student ID / roll number |
| Event_Name | Event the feedback was submitted for |
| Face_Detected | `True` / `False` — face verification result |
| Transcript | Auto-transcribed or manually typed feedback |
| Sentiment | `Positive` / `Negative` / `Neutral` |
| Polarity | Score from `-1.0` (very negative) to `+1.0` (very positive) |

---

## 📖 Usage

### Student Flow
1. Open the app → go to **Record Feedback**
2. Enter your **Name**, **Roll Number**, and select your **Event**
3. Take a live photo or upload an image — face detection runs automatically
4. Record your voice feedback or type it manually
5. Click **🚀 Submit Feedback** — transcript, sentiment, and data are saved instantly

### Admin Flow
1. Go to **Analysis Dashboard**
2. **Event-Wise** tab — sentiment breakdown per event
3. **Student-Wise** tab — individual feedback history with photo
4. **Face Detection Stats** — identity verification rates
5. **Raw Data** tab — download full `.xlsx` or `.csv`

---

## ☁️ Deploying to Streamlit Cloud

1. Push your code to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select your repo, branch, and set main file to `app.py`
4. Click **Deploy** — Streamlit installs `requirements.txt` automatically

> ⚠️ The `feedback_data.xlsx` file resets on every redeploy since Streamlit Cloud has an ephemeral filesystem. For permanent storage, integrate Google Sheets (see below).

---

## 🔗 Optional: Google Sheets Integration

To sync data live to a Google Sheet, add credentials to `.streamlit/secrets.toml`:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key = "-----BEGIN RSA PRIVATE KEY-----\n..."
client_email = "your-service-account@project.iam.gserviceaccount.com"
```

> 🔒 Never commit `secrets.toml` to GitHub. Add it to `.gitignore`.

---

## 🐛 Troubleshooting

| Error | Fix |
|---|---|
| `ModuleNotFoundError: cv2` | Use `opencv-python-headless` in `requirements.txt` |
| `ModuleNotFoundError: openpyxl` | Add `openpyxl` to `requirements.txt` and redeploy |
| Camera input not working | `st.camera_input` must be outside `st.form()` — already fixed in this version |
| Audio not transcribing | Google Speech API needs internet. Use text fallback offline |
| Face not detected | Ensure good lighting and face is clearly visible |
| Excel lost after redeploy | Expected on Streamlit Cloud — use Google Sheets for persistence |

---

## 🔮 Roadmap

- [ ] Student login / authentication
- [ ] Multi-language transcription (Kannada, Hindi, Telugu)
- [ ] Auto email PDF report to admin after each event
- [ ] Google Drive photo storage
- [ ] QR code per event for quick access
- [ ] Advanced NLP — topic extraction from transcripts
- [ ] Mobile-responsive UI improvements

---

## 🤝 Contributing

1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature`
3. Commit your changes
4. Push and open a Pull Request

---

## 🏢 About

Built by **Pragyan Smart AI Technology LLP**
Part of **PragyanAI** — *Grow with Gyan* 🌱

---

*For questions or support, open an issue on GitHub.*
