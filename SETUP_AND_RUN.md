
# 🎓 Exam Coach AI — Complete Setup & Run Guide

## 📁 Your Project File Structure

```
your_project/
│
├── 📄 database.py              ← DB connection (SQLite, no setup needed)
├── 📄 models_enhanced.py       ← Original DB tables + new relationships
├── 📄 models_new_features.py   ← NEW: 6 new DB tables
├── 📄 schemas_enhanced.py      ← Pydantic validation schemas
├── 📄 main_enhanced.py         ← FastAPI backend (original + new router)
├── 📄 routes_new_features.py   ← NEW: All new API endpoints
├── 📄 llm_enhanced.py          ← Original Gemini AI functions
├── 📄 llm_new_features.py      ← NEW: AI for error patterns + discussions
├── 📄 whatsapp_notifier.py     ← NEW: WhatsApp via PyWhatKit
├── 📄 app_enhanced.py          ← Streamlit frontend (all 9 pages)
└── 🗄️  app.db                  ← SQLite database file (auto-created)
```

---

## 🗄️ Database — Everything You Need to Know

### What database does this use?
**SQLite** — a single file called `app.db` that lives in your project folder.
- ✅ Zero installation required
- ✅ No server to start
- ✅ No password or configuration
- ✅ The file is created automatically when you first run the backend

### Where is the database file?
```
your_project/app.db     ← this file IS your entire database
```

### All Tables (auto-created on first run)

#### Original Tables (from your existing code):
| Table | What it stores |
|---|---|
| `student_profiles` | Exam type, target rank |
| `mock_tests` | Uploaded test results + weak topics |
| `revision_plans` | Generated 7-day study plans |
| `progress_tracking` | Topic-wise progress per student |
| `free_resources` | Learning resources (videos, articles) |
| `chat_history` | AI Q&A conversations |

#### New Tables (from models_new_features.py):
| Table | What it stores |
|---|---|
| `uploaded_sheets` | Each uploaded mock test file + extracted text |
| `error_patterns` | AI-identified recurring mistakes across sheets |
| `reminder_settings` | Student's WhatsApp number + preferences |
| `reminder_logs` | Log of every WhatsApp message sent |
| `discussion_posts` | Student forum questions/posts |
| `discussion_replies` | Replies (human + AI) to each post |

### Do I need to create tables manually?
**No.** The line in `main_enhanced.py`:
```python
Base.metadata.create_all(bind=engine)
```
...automatically creates ALL tables the first time the backend starts.

### How to view the database (optional)
Install **DB Browser for SQLite** (free): https://sqlitebrowser.org
Then open `app.db` to browse/edit data visually.

Or use the command line:
```bash
# Install sqlite3 CLI (usually pre-installed on Mac/Linux)
sqlite3 app.db

# Inside sqlite3 shell:
.tables                        # list all tables
SELECT * FROM student_profiles;
SELECT * FROM discussion_posts;
.quit
```

### Reset the database (start fresh)
```bash
# Just delete the file — it will be recreated on next backend start
rm app.db
```

---

## 📦 Step 1 — Install All Dependencies

Run this once in your project folder:

```bash
pip install fastapi uvicorn sqlalchemy pydantic python-dotenv \
            streamlit requests pandas google-generativeai \
            pywhatkit python-multipart
```

Or create a `requirements.txt`:
```
fastapi
uvicorn
sqlalchemy
pydantic
python-dotenv
streamlit
requests
pandas
google-generativeai
pywhatkit
python-multipart
```
Then run:
```bash
pip install -r requirements.txt
```

---

## 🔑 Step 2 — Set Your API Key

Create a `.env` file in your project folder:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

Then update the top of `llm_enhanced.py` and `llm_new_features.py`:
```python
# Replace the hardcoded key with:
import os
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
```

---

## 🚀 Step 3 — Run the App

You need **two terminal windows** open at the same time.

### Terminal 1 — Start the Backend (FastAPI)
```bash
cd your_project
uvicorn main_enhanced:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

The database file `app.db` is created here automatically.

### Terminal 2 — Start the Frontend (Streamlit)
```bash
cd your_project
streamlit run app_enhanced.py
```

You should see:
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

### Open in Browser
Go to: **http://localhost:8501**

---

## ✅ Verify Everything is Working

### Check backend is alive:
Open in browser: http://127.0.0.1:8000
You should see: `{"message": "Welcome to Exam Coach API"}`

### Check all API endpoints:
Open in browser: http://127.0.0.1:8000/docs
This shows the full interactive API documentation (Swagger UI).

### Check database was created:
```bash
ls -la app.db     # should exist and be > 0 bytes after first backend start
```

---

## 🔔 WhatsApp Setup (for Reminders page)

1. Install pywhatkit:
   ```bash
   pip install pywhatkit
   ```
2. Open **Chrome** and go to https://web.whatsapp.com
3. Scan the QR code with your phone
4. Keep this tab open while using the Reminders page
5. In the app, go to 🔔 Reminders → enter your phone number → Save → Send Test

---

## 🗂️ Multi-Sheet Upload — Supported Formats

| Format | How it works |
|---|---|
| `.txt` | Raw text, read directly |
| `.csv` | Read as text, columns detected |
| `.pdf` | Text extracted from PDF content |

---

## ❗ Common Issues & Fixes

### "Connection refused" on frontend
→ Backend is not running. Start `uvicorn` in Terminal 1 first.

### "Module not found: models_new_features"
→ Make sure `models_new_features.py` is in the same folder as `main_enhanced.py`.

### "Table already exists" error
→ Safe to ignore — SQLAlchemy skips existing tables automatically.

### WhatsApp message not sending
→ Make sure WhatsApp Web is open and logged in Chrome before clicking Send.
→ Increase `wait_time` in `whatsapp_notifier.py` from 12 to 20 if your internet is slow.

### Gemini API error
→ Check your API key is correct in `.env`
→ Free tier has rate limits — wait 60 seconds and retry.

### Frontend shows blank page
→ Refresh the browser (Ctrl+R / Cmd+R)
→ Check Terminal 2 for any Python errors.

---

## 📋 Quick Reference — All Pages & What They Need

| Page | Requires Profile | Requires Mock Test |
|---|---|---|
| 🏠 Home | No | No |
| 📊 Analyze | Yes | No |
| 📅 7-Day Plan | Yes | Yes (for topics) |
| 📚 Resources | Yes | Yes (for topics) |
| 📈 Dashboard | Yes | No |
| 💬 Ask AI | Yes | No |
| 🗂️ Multi-Sheet | Yes | No |
| 🔔 Reminders | Yes | No |
| 👥 Discussions | Yes | No |

**Recommended flow for first use:**
1. Open app → Create profile (exam + target)
2. Go to Analyze → paste some test results
3. Go to 7-Day Plan → generate timetable
4. Explore Multi-Sheet, Reminders, Discussions

---

## 🧪 Test the New Features with Sample Data

### Test Multi-Sheet Upload
Create a file `sample_test.txt` with this content:
```
Mock Test Results - JEE Mock 1
Score: 145/300

Wrong answers:
Q5: Thermodynamics - confused isothermal and adiabatic processes
Q12: Integration - wrong formula for integration by parts
Q18: Organic Chemistry - wrong product in SN2 reaction
Q24: Thermodynamics - incorrect sign for work done
Q31: Vectors - wrong cross product calculation
Q37: Integration - forgot +C constant
```
Upload this file (and a few more like it) in the Multi-Sheet page, then click Analyse.

### Test Discussions
Go to 👥 Discussions → Post a Question → write anything → then click "Get AI Answer" on your post.

### Test WhatsApp
Configure your number in 🔔 Reminders → click "Send Test Message".
