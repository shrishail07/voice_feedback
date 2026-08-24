# 🎤 Student Voice Feedback System

A Streamlit app where students log in, submit voice/text feedback (with optional
face-verification photo), and admins view sentiment analytics — all backed by
a Supabase (Postgres) database instead of a local Excel file.

## Project Structure

```
student-feedback-system/
├── app.py                          # Entry point: Login / Signup page
├── requirements.txt
├── .streamlit/
│   ├── config.toml                 # Theme
│   └── secrets.toml.example        # Template — copy values into Streamlit Cloud Secrets
├── assets/
│   └── pragyan_ai_school_cover.jpg # (add your own cover image here)
├── database/
│   ├── db_client.py                # Supabase client (cached)
│   ├── queries.py                  # All CRUD functions
│   └── schema.sql                  # Run once in Supabase SQL Editor
├── auth/
│   └── auth_utils.py                # Signup/login/logout, password hashing (bcrypt)
├── utils/
│   ├── sentiment.py                 # TextBlob sentiment scoring
│   ├── face_detection.py            # OpenCV Haar cascade face detection
│   └── transcription.py             # Google Speech-to-Text via SpeechRecognition
└── pages/
    ├── 1_🎤_Record_Feedback.py      # Protected: feedback form
    └── 2_📊_Analysis_Dashboard.py   # Protected by admin password: analytics + CSV export
```

## 1. Set up Supabase (free tier is enough)

1. Create a project at https://supabase.com
2. Go to **SQL Editor** → paste the contents of `database/schema.sql` → Run
3. Go to **Project Settings → API** → copy your **Project URL** and **anon public key**

## 2. Configure secrets

Locally, create `.streamlit/secrets.toml` (already gitignored) using
`secrets.toml.example` as a template, and fill in your real Supabase URL/key.

## 3. Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 4. Deploy to Streamlit Community Cloud

1. Push this folder to a GitHub repo (secrets.toml stays out of git — it's in `.gitignore`)
2. Go to https://share.streamlit.io → New app → point to your repo, branch, and `app.py`
3. In **App settings → Secrets**, paste the contents of `secrets.toml.example`
   with your real Supabase URL/key and admin password
4. Deploy 🎉

## How data flows

- **Students** sign up once (Roll Number + Password) → stored in the `students` table
- **Login** re-uses that Roll Number + Password (bcrypt-hashed, never stored in plain text)
- **Feedback** submitted by a logged-in student is written straight to the `feedback` table
- **Admins** enter the admin password on the Analysis Dashboard page to view charts and
  download a full CSV export pulled live from Supabase — no more manually managing an
  Excel file on disk

## Notes

- Add your own `pragyan_ai_school_cover.jpg` into `assets/` — the app runs fine without it too.
- To manage/browse raw data directly, you can always use the Supabase Table Editor
  in your project dashboard.
