<div align="center">

<img src="https://img.shields.io/badge/AI%20Powered-Gemini%202.5%20Flash-blue?style=for-the-badge&logo=google" />
<img src="https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi" />
<img src="https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit" />
<img src="https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite" />
<img src="https://img.shields.io/badge/Notifications-WhatsApp-25D366?style=for-the-badge&logo=whatsapp" />

<br /><br />

# 🎓 Exam Coach AI

### *The smart study companion that turns mock test data into exam success*

> **The only exam prep tool that combines AI-powered weak topic analysis, personalized revision planning, multi-sheet error pattern detection, and peer collaboration — all in one platform, completely free.**

<br />

[🚀 Quick Start](#-quick-start) · [🧠 How It Works](#-how-it-works) · [✨ Features](#-key-features) · [🛠️ Tech Stack](#️-tech-stack) · [🌍 Impact](#-real-world-impact)

</div>

---

## 🚨 The Problem

**Students preparing for competitive entrance exams lack personalized guidance** — generic study plans ignore individual weak areas, target scores, and available study hours, leading to inefficient preparation and missed exam goals.

### Pain Points We Solve

| ❌ Before Exam Coach AI | ✅ After Exam Coach AI |
|---|---|
| Manually reviewing mock tests to spot mistakes | AI identifies weak topics in seconds |
| One-size-fits-all study plans | Personalized 7-day plan based on your hours & target |
| No idea which errors keep repeating | Cross-sheet error pattern analysis across all tests |
| Searching the internet for resources alone | Curated free resources matched to your weak topics |
| Studying in isolation | Peer discussion forum with AI assistance |
| Forgetting study schedules | WhatsApp reminders delivered to your phone daily |

---

## 💡 Our Solution

**Exam Coach AI** is a full-stack, AI-powered study companion that:

1. 📊 **Analyzes** mock test results and pinpoints weak topics using Gemini AI
2. 📅 **Generates** a personalized 7-day revision timetable calibrated to study hours and target rank
3. 🗂️ **Cross-analyzes** multiple test sheets to detect recurring error patterns
4. 📚 **Recommends** free learning resources for every weak topic
5. 💬 **Answers** subject questions via an AI-powered chatbot tutor
6. 👥 **Connects** students through an open peer discussion forum with AI reply support
7. 🔔 **Reminds** students via WhatsApp — daily tasks, plan alerts, discussion replies
8. 📈 **Tracks** progress on a live dashboard with scores and topic completion

---

## ✨ Key Features

### 🔍 Mock Test Analysis
Paste or upload test results. Gemini AI extracts weak topics instantly and recommends targeted resources with one click.

### 📅 7-Day Personalized Revision Plan
Enter your weekday and weekend study hours. The AI generates a day-by-day timetable that prioritizes your weakest topics and perfectly fits your schedule.

### 🗂️ Multi-Sheet Error Pattern Analysis ⭐ *Unique*
Upload **multiple mock tests at once**. The AI reads all of them together and identifies **recurring error patterns** — categorized into:
- 🧠 **Conceptual** — gaps in understanding
- 🔢 **Calculation** — arithmetic and formula errors
- 🤦 **Silly/Careless** — avoidable mistakes under pressure
- ⏱️ **Time-based** — errors caused by rushing

Each pattern shows severity (🔴High / 🟠Medium / 🟢Low), frequency count, what you're doing wrong, and exactly how to fix it. Exportable as CSV.

### 📚 Smart Resource Recommendations
For every weak topic the system fetches free resources grouped by type — videos, articles, PDFs, problem sets, and practice tests — with direct links.

### 💬 AI Chatbot Tutor
Ask any exam-related question. The AI responds with exam-specific context, formulas, worked examples, common mistakes, and time-saving tips.

### 👥 Open Discussion Forum ⭐ *Unique*
A peer-to-peer discussion board where students can:
- Post questions tagged by topic and exam
- Reply to each other's doubts
- Get **instant AI answers** on any post
- Upvote helpful replies and mark questions as resolved
- Receive WhatsApp notifications when someone replies

### 🔔 WhatsApp Reminders ⭐ *No API Key Required*
Get daily study task reminders, plan-ready alerts, and discussion reply notifications directly on WhatsApp — using your existing WhatsApp Web session. Completely free, zero signup.

### 📈 Progress Dashboard
Track topic-wise completion, study hours logged, performance scores, and recent AI Q&A history — all in one clean view.

---

## 🧠 How It Works

```
Student submits mock test results
              │
              ▼
     ┌─────────────────┐
     │  Gemini AI      │  ← Analyzes errors, identifies weak topics
     └────────┬────────┘
              │
     ┌────────┴──────────────────────────┐
     ▼                                   ▼
7-Day Revision Plan              Free Resource Recommendations
(personalized timetable)         (matched to each weak topic)
     │
     ▼
Multi-Sheet Upload (multiple test files)
     │
     ▼
Cross-Sheet Error Pattern Analysis
(conceptual / calculation / silly / time-based)
     │
     ▼
┌─────────────────────────────────────────────┐
│  Progress Dashboard  │  AI Chatbot Tutor    │
│  Discussion Forum    │  WhatsApp Reminders  │
└─────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **AI Engine** | Google Gemini 2.5 Flash | Weak topic analysis, revision plans, Q&A, error pattern detection, resource recommendations, discussion replies |
| **Backend** | FastAPI (Python) | REST API with 20+ endpoints |
| **Database ORM** | SQLAlchemy | All database models and queries |
| **Database** | SQLite | Zero-setup local database, auto-created on first run |
| **Data Validation** | Pydantic | Request/response schema validation |
| **Frontend** | Streamlit | 9-page interactive web app with top navigation |
| **Notifications** | PyWhatKit | Free WhatsApp messages via WhatsApp Web |
| **Data Processing** | Pandas | Tables, CSV export, data display |
| **Config** | python-dotenv | Secure API key management via `.env` |

---

## 📁 Project Structure

```
exam-coach-ai/
│
├── 📄 app_enhanced.py           # Streamlit frontend — all 9 pages + top nav
├── 📄 main_enhanced.py          # FastAPI app — original + new router registered
├── 📄 routes_new_features.py    # New API routes (sheets, reminders, discussions)
│
├── 📄 models_enhanced.py        # Original SQLAlchemy models (patched)
├── 📄 models_new_features.py    # New models: sheets, patterns, reminders, forum
├── 📄 schemas_enhanced.py       # Pydantic validation schemas
│
├── 📄 llm_enhanced.py           # Original Gemini AI functions
├── 📄 llm_new_features.py       # New AI: error patterns + discussion replies
├── 📄 whatsapp_notifier.py      # WhatsApp notification sender (PyWhatKit)
├── 📄 database.py               # SQLite connection and session management
│
├── 📄 requirements.txt          # All Python dependencies
├── 📄 start_windows.bat         # One-click startup for Windows
├── 📄 start_mac_linux.sh        # One-click startup for Mac/Linux
└── 🗄️  app.db                   # SQLite database file (auto-created)
```

---

## 🗄️ Database Schema

```
StudentProfile (1)
    ├── MockTest (n)           → test results + weak topics JSON
    ├── RevisionPlan (n)       → generated 7-day plans
    ├── ProgressTracking (n)   → topic-wise progress + scores
    ├── ChatHistory (n)        → AI Q&A conversations
    ├── UploadedSheet (n)      → uploaded mock test files + extracted text
    ├── ErrorPattern (n)       → recurring mistake patterns (AI-detected)
    ├── ReminderSetting (1)    → WhatsApp number + notification preferences
    ├── ReminderLog (n)        → log of every WhatsApp message sent
    ├── DiscussionPost (n)     → forum questions
    └── DiscussionReply (n)    → replies (human + AI)

FreeResource                   → learning resources per topic/exam
```

> ✅ All 12 tables are **auto-created** on first backend startup — no migrations, no manual setup.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Chrome browser (for WhatsApp reminders)

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/exam-coach-ai.git
cd exam-coach-ai
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure your API key
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
Get a **free** Gemini API key at: https://aistudio.google.com/app/apikey

### 4. Start the app

**Windows** — double-click `start_windows.bat`

**Mac / Linux:**
```bash
chmod +x start_mac_linux.sh
./start_mac_linux.sh
```

**Manual (two terminals):**
```bash
# Terminal 1 — Backend API
uvicorn main_enhanced:app --reload --port 8000

# Terminal 2 — Frontend
streamlit run app_enhanced.py
```

### 5. Open in browser
```
Frontend:  http://localhost:8501
API Docs:  http://127.0.0.1:8000/docs
```

---

## 📱 App Pages

| Page | Description |
|---|---|
| 🏠 **Home** | Overview and quick navigation |
| 📊 **Analyze** | Paste test results → get weak topics + resources |
| 📅 **7-Day Plan** | Generate personalized revision timetable |
| 📚 **Resources** | Browse free materials by topic |
| 📈 **Dashboard** | Track progress, scores, study hours |
| 💬 **Ask AI** | Chat with AI tutor on any topic |
| 🗂️ **Multi-Sheet** | Upload multiple tests → error pattern analysis |
| 🔔 **Reminders** | Set up WhatsApp study notifications |
| 👥 **Discussions** | Peer forum with AI reply support |

---

## 🌍 Real-World Impact

### Who benefits?
- Students preparing for **JEE, NEET, GATE, CAT, GRE, UPSC**, and any competitive exam
- **Self-studiers** who cannot afford expensive personalised coaching
- **Coaching centres** that want AI-powered analytics for their students

### Why it matters
- Over **2 million students** appear for JEE alone every year
- Most students waste **40–60% of study time** on topics they already know
- Personalised AI coaching was previously only accessible to students who could afford private tutors
- **Exam Coach AI makes data-driven, personalised exam prep free and accessible to everyone**

---

## 🔮 Roadmap

- [ ] Adaptive spaced repetition scheduling (Anki/SM-2 algorithm)
- [ ] PDF and image upload for handwritten answer sheets (OCR)
- [ ] Voice input for chatbot questions (Whisper API)
- [ ] Mobile PWA for studying on the go
- [ ] Teacher / coaching centre dashboard with batch analytics
- [ ] PostgreSQL support for production-scale deployment
- [ ] Automated scheduled WhatsApp reminders (APScheduler)
- [ ] Performance benchmarking against topper patterns

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

### 💬 *"Stop studying harder. Start studying smarter."*

⭐ **Star this repo if it helped you!** ⭐

<br />

Built with ❤️ for students who deserve better than generic study plans.

*Made for Hackathon 2025 · Powered by Google Gemini · Built with FastAPI + Streamlit*

</div>
