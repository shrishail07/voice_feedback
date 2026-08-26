# 🎤 Student Voice Feedback System

**PragyanAI · Grow with Gyan**

A Streamlit app for collecting student feedback on events (with optional photo capture, voice recording, and automatic sentiment analysis), backed by Supabase for authentication and event management, with an admin analytics dashboard.

---

## 1. What this system does

| Capability | Details |
|---|---|
| Student signup/login | Roll number + password, stored in Supabase (`students` table). Signed-up students never see the signup form again — they just log in. |
| Feedback submission | Name/roll/email/phone/college auto-filled from the logged-in profile. Student picks an event, optionally takes a photo and/or records voice, or types feedback directly. |
| Face detection | Best-effort face verification on the captured photo using OpenCV Haar cascades. Degrades gracefully (never crashes the app) if OpenCV is unavailable on the server. |
| Voice transcription | Recorded audio is transcribed via `SpeechRecognition` (Google Web Speech API) before sentiment scoring. |
| Sentiment analysis | `TextBlob` scores every transcript as Positive / Neutral / Negative with a numeric polarity (-1 to +1). |
| File storage | Captured photos and audio recordings are saved to a local `uploads/` folder and their paths logged alongside the feedback row. |
| Admin dashboard | Password-gated. Event-wise sentiment breakdown, per-student history, per-student event-attendance + sentiment breakdown, raw data table, CSV/Excel export, and a media viewer for uploaded photos/audio. |
| Event management | Events are stored in Supabase (`events` table), not hardcoded. Only admins can add new events, from a sidebar panel. |

---

## 2. Architecture

```
┌─────────────────────────────┐
│        Streamlit UI         │   app.py
│  (login/signup, feedback    │
│   form, admin dashboard)    │
└──────────┬───────────────┬──┘
           │               │
           ▼               ▼
┌────────────────┐  ┌──────────────────┐
│  Supabase       │  │  Local filesystem │
│  (Postgres)     │  │  (ephemeral on    │
│                 │  │   Streamlit Cloud)│
│ - students      │  │                    │
│   (auth)        │  │ - feedback_data.   │
│ - events        │  │   xlsx (all        │
│   (event list)  │  │   feedback rows)   │
│                 │  │ - uploads/ (photos │
│                 │  │   & audio files)   │
└────────────────┘  └──────────────────┘
```

**Why the split?** Auth and the event list need to persist reliably and be shared across every app restart, so they live in Supabase (a real Postgres database reachable over HTTPS). Feedback submissions and uploaded media currently live on local disk as an Excel file — simple for a POC, but **it resets every time Streamlit Cloud restarts or redeploys the app** (see [Section 8: Known Limitations](#8-known-limitations--whats-next)).

---

## 3. File structure

```
voice_feedback/
├── app.py                      # Main Streamlit application (single entry point)
├── supabase_auth.py             # Signup / login / logout / session-check logic
├── events_db.py                 # Get / add events, backed by Supabase
├── requirements.txt              # Python dependencies
├── runtime.txt                   # Pins Python version (see caveat in Section 7)
├── feedback_data.xlsx            # Seed/dummy feedback data (1,500 rows) — committed
│                                  # so the dashboard has data from first launch
├── create_students_table.sql     # Run once in Supabase SQL Editor
├── create_events_table.sql       # Run once in Supabase SQL Editor
├── pragyan_ai_school_cover.jpg   # Optional cover banner (app runs fine without it)
└── uploads/                      # Auto-created at runtime; stores captured photos/audio
```

---

## 4. Data model

### Supabase: `students` table (authentication)

| Column | Type | Notes |
|---|---|---|
| `roll_number` | text (PK) | Unique login identifier |
| `full_name` | text | |
| `email` | text | |
| `phone` | text | |
| `college` | text | |
| `department` | text | |
| `password_hash` | text | PBKDF2-SHA256, 100,000 iterations, hex-encoded |
| `password_salt` | text | 16 random bytes, hex-encoded, unique per user |
| `created_at` | timestamptz | Defaults to `now()` |

Passwords are **never stored in plaintext**. Each password is hashed with a unique random salt using `hashlib.pbkdf2_hmac`.

### Supabase: `events` table

| Column | Type | Notes |
|---|---|---|
| `id` | bigint (PK, identity) | |
| `name` | text (unique) | Event name shown in the dropdown |
| `created_at` | timestamptz | Defaults to `now()` |

Seeded on first run with: `Hackathon 2026`, `Science Fair`, `Sports Meet`, `Other`.

### Local Excel: `feedback_data.xlsx` (feedback records)

| Column | Description |
|---|---|
| `Timestamp` | Submission time |
| `Student_Name`, `Roll_Number`, `College_Name`, `Department_name`, `E_mail`, `Phone_number` | Copied from the student's profile at submission time |
| `Event_Name` | Selected from the live Supabase event list |
| `Face_Detected` | `True`/`False` — result of OpenCV face detection on the captured photo |
| `Transcript` | Transcribed audio, or typed text |
| `Sentiment` | `Positive` / `Neutral` / `Negative` |
| `Polarity` | Numeric score, -1.0 to +1.0 |
| `Photo_Path`, `Audio_Path` | Relative paths into `uploads/`, blank if not provided |

---

## 5. Setup — from zero to running locally

```bash
git clone <your-repo-url>
cd voice_feedback
pip install -r requirements.txt
```

Create `.streamlit/secrets.toml` in the project root (this file should **never** be committed to git):

```toml
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "your-anon-or-service-role-key"
```

Get both values from **Supabase Dashboard → Project Settings → API**.

Run the two SQL scripts once against your Supabase project (**SQL Editor** tab):
1. `create_students_table.sql`
2. `create_events_table.sql`

Both scripts are idempotent — safe to re-run even if the tables already exist with a different schema; they add any missing columns rather than failing.

Then launch:

```bash
streamlit run app.py
```

---

## 6. Deploying to Streamlit Community Cloud

1. Push the repo root exactly as structured in [Section 3](#3-file-structure) to GitHub.
2. On [share.streamlit.io](https://share.streamlit.io), create a new app pointing at `app.py`.
3. Go to **App → Settings → Secrets** and paste the same `SUPABASE_URL` / `SUPABASE_KEY` pair shown above.
4. Go to **App → Settings → General** and explicitly set the **Python version to 3.11** (see the caveat in Section 7 — don't rely on `runtime.txt` alone).
5. Deploy. First launch will auto-seed the `events` table if it's empty.
6. Because `feedback_data.xlsx` is committed with 1,500 dummy rows, the dashboard shows **"Total Active Users: 1500"** immediately; every real submission increments this for the life of that running instance.

**Admin password** (hardcoded in `app.py`, change it before going anywhere near production): `PRAGYANAI`

---

## 7. Problems we hit building this, and how they were fixed

This project went through a few rounds of real deployment failures — documenting them here so future-you (or whoever inherits this) doesn't re-solve them from scratch.

| Symptom | Root cause | Fix |
|---|---|---|
| `AttributeError: module 'cv2' has no attribute 'CascadeClassifier'` | Streamlit Cloud was running **Python 3.14**, for which OpenCV has no compatible wheel yet — pip silently installed a broken/partial build. | Pinned `opencv-python-headless` in `requirements.txt`, and wrapped all OpenCV usage in `try/except` so a broken build disables face detection instead of crashing the app. |
| `use_container_width will be removed after 2025-12-31` warnings | Streamlit deprecated the parameter. | Replaced every `use_container_width=True` with `width='stretch'`. |
| `ModuleNotFoundError: No module named 'db_auth'` | Linux (which Streamlit Cloud runs on) is case-sensitive; the repo file was named with different casing than the `import` statement expected. | Renamed the file to match the import exactly, all lowercase. |
| MongoDB Atlas: `SSL: TLSV1_ALERT_INTERNAL_ERROR` on every shard, even with `certifi`'s CA bundle passed explicitly | Combination of Streamlit Cloud still running Python 3.14 (OpenSSL 3.x TLS-negotiation quirks) and/or an Atlas free-tier cluster auto-pausing from inactivity. | **Abandoned MongoDB Atlas entirely** in favor of **Supabase** (Postgres over plain HTTPS/REST — no raw TLS socket handshake to fail). This is the current, working setup. |
| `runtime.txt` pinning `python-3.11` didn't actually change the running Python version | Streamlit Community Cloud has become inconsistent about honoring `runtime.txt`; version selection moved into the dashboard UI. | Explicitly set the Python version in **App → Settings → General** in the Streamlit Cloud dashboard, in addition to keeping `runtime.txt` for other platforms. |
| Signup failing: `Could not find the 'college' column of 'students' in the schema cache` | A `students` table already existed from earlier work, with a different (older) schema. `CREATE TABLE IF NOT EXISTS` silently no-ops against an existing table, so the new columns were never added. | Rewrote the SQL as a series of `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` statements (safe against both a fresh and a pre-existing table), plus `NOTIFY pgrst, 'reload schema';` to force Supabase's PostgREST layer to pick up the change immediately. |

---

## 8. Known limitations & what's next

- **Feedback data is not yet persistent across restarts.** `feedback_data.xlsx` and `uploads/` live on Streamlit Cloud's local, ephemeral filesystem. Every redeploy or container restart resets them back to whatever was last committed to git (i.e., the 1,500-row seed file). Auth (`students`) and the event list (`events`) *are* persistent because they live in Supabase — only feedback submissions and uploaded media are at risk.
  - **Fix, if/when needed:** move feedback storage from local Excel into a Supabase table (e.g., `feedback`), and uploaded photos/audio into Supabase Storage instead of local disk. This mirrors exactly what was already done for auth and events, so it's a well-trodden pattern in this codebase — just needs to be applied to the last remaining local-disk dependency.
- **Admin password is a single hardcoded string** (`PRAGYANAI`) checked client-side in `app.py`. Fine for an internal demo; not meant to gate anything sensitive.
- **Speech transcription depends on Google's Web Speech API** via `SpeechRecognition`, which requires outbound internet access from wherever the app runs and has no official uptime guarantee — treat transcription failures as expected/handled (falls back to an error string) rather than exceptional.
- **Face detection is best-effort**, not proof of identity — it flags whether *a* face was found in frame, not that it's the *right* face.

---

## 9. Quick reference: where to change things

| To change... | Edit... |
|---|---|
| Admin password | `ADMIN_PASSWORD` constant in `app.py` |
| Which events are offered | Use the "➕ Add New Event" panel in the sidebar while logged in as admin (no code change needed) |
| CSS / color theme | The `st.markdown("""<style>...""")` block near the top of `app.py` |
| Password hashing strength | `_hash_password()` in `supabase_auth.py` (iteration count, currently 100,000) |
| Sentiment thresholds | `analyze_sentiment()` in `app.py` (currently ±0.1 polarity for Positive/Negative cutoffs) |
| Excel column schema | `COLUMNS` list in `app.py` — if you change this, existing `feedback_data.xlsx` files with the old schema will need to be regenerated or migrated |
