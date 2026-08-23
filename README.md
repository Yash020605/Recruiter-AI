# Recruiter AI — Autonomous Agentic HR Platform

![Status](https://img.shields.io/badge/Status-Live-brightgreen) ![Python](https://img.shields.io/badge/Python-3.11%2B-blue) ![React](https://img.shields.io/badge/React-18-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.110-teal) ![LangGraph](https://img.shields.io/badge/LangGraph-0.1-orange)

Recruiter AI is a full-stack, multi-agent hiring platform that automates the entire recruitment lifecycle. It uses LangGraph-orchestrated AI agents to parse resumes, score candidates against job descriptions, generate communications, and provide hiring analytics — all in a real-time React dashboard.

---

## 🌍 Live Deployment

| Service | URL |
|---------|-----|
| **Frontend (Vercel)** | https://recruiter-jet.vercel.app |
| **Backend API (Railway)** | https://recruiter-ai-backend-production-1c27.up.railway.app |
| **API Docs (Swagger)** | https://recruiter-ai-backend-production-1c27.up.railway.app/docs |

### Demo Credentials (one-click login, no password required)
| Role | Button | Access |
|------|--------|--------|
| Admin | Login as Admin | Full access + admin panel + analytics |
| Recruiter | Login as Recruiter | Upload, analyze, email, export |
| Hiring Manager | Login as Manager | View candidates, approve, comment |

---

## ✅ Features

### Candidate Pipeline Dashboard
- Kanban-style pipeline board with stages: New → Screening → Shortlisted → Interview Scheduled → Offer Sent → Hired / Rejected
- Real-time status updates with journey timeline per candidate
- Filter by name, score, skills, notice period, recommendation

### Resume Upload & Processing
- Upload PDF, DOCX, or TXT resumes
- LangGraph multi-agent pipeline extracts: skills, experience, education, projects, certifications, CTC, notice period, location
- Background processing — non-blocking, polls for completion

### Job Requirement Matching
- Paste any Job Description to analyze a candidate
- AI returns match score (0–100), matched skills, missing skills, extra skills, and a fit summary
- Full E2E screening workflow available per candidate

### Interview Scheduling
- Schedule interviews with date, time, mode (Online/In-person), and meeting link
- Edit, update status, and delete interviews
- Interview stats dashboard (Scheduled / Completed / Cancelled)

### Candidate Communication
- Generate AI-drafted emails: Interview Invitation, Rejection, Job Offer, Status Update
- Editable in-modal before sending
- One-click copy to clipboard

### Export Functionality
- **Export all candidates** as CSV (name, score, recommendation, CTC, skills, integrations)
- **Export hiring analytics** as CSV (selection rate, rejection rate, avg scores)
- **Export individual candidate report** as CSV from their expanded card

### Input Validation
- Inline error messages for: missing JD before analysis, upload failures (wrong format/empty file), missing candidate selection for job matching
- No more `alert()` popups — errors display inline next to the relevant field

### D&I Analytics
- Gender, education, experience, and location distribution charts
- Hiring funnel visualization
- Selection rate and rejection rate metrics

### Admin Panel
- User management (create, delete recruiters/hiring managers)
- System performance metrics (parse time, AI response time, API latency)
- Job matching statistics and skill gap analysis
- Live system logs viewer

### AI Chat Assistant
- Floating chat widget (recruiter/admin only)
- Ask natural language questions about candidates and hiring insights

### Third-Party Integrations (mocked)
- Zoho Recruit ATS sync
- HackerEarth technical assessment invite
- AuthBridge background verification
- Keka HRMS onboarding

---

## 🏗️ Architecture

```
react-frontend/          # React + Vite + TypeScript + Tailwind CSS
backend/
  api/routes.py          # All FastAPI endpoints
  agents/                # LangGraph agent nodes
    screening_agent.py   # Resume parsing (skills, experience, education)
    communication_agent.py  # Email generation
  workflows/
    recruiter_graph.py   # Main LangGraph pipeline
    recruitment_workflow.py  # E2E screening workflow
  tools/
    keyword_extractor.py # JD keyword extraction
  database/              # SQLAlchemy models + migrations
  config/settings.py     # Environment config (Pydantic Settings)
```

---

## 🛠️ Local Setup

### Prerequisites
- Node.js 18+
- Python 3.11+
- Git

### 1. Clone
```bash
git clone https://github.com/yashlimbhore-afk/Recruiter.git
cd Recruiter
```

### 2. Backend
```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory:
```ini
# Required
GEMINI_API_KEY=your_google_gemini_api_key

# Database (defaults to SQLite for local dev)
DATABASE_URL=sqlite:///./recruiter.db

# JWT
SECRET_KEY=your_secret_key_here

# Optional integrations (mocked if not set)
ZOHO_CLIENT_ID=
KEKA_API_KEY=
HACKEREARTH_CLIENT_SECRET=
AUTHBRIDGE_TOKEN=
```

Run database migrations:
```bash
cd backend
alembic upgrade head
```

Start the backend:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at: http://localhost:8000/docs

### 3. Frontend
```bash
cd react-frontend
npm install
```

Create a `.env` file in `react-frontend/`:
```ini
VITE_API_URL=http://localhost:8000
```

Start the frontend:
```bash
npm run dev
```

App available at: http://localhost:5173

---

## 🚀 Deployment

### Backend → Railway
1. Connect your GitHub repo to Railway
2. Set the root directory to `/` (Railway auto-detects the `Procfile` or `main.py`)
3. Add environment variables in Railway dashboard:
   - `GEMINI_API_KEY`
   - `DATABASE_URL` (Railway provides a PostgreSQL URL)
   - `SECRET_KEY`
4. Railway auto-deploys on every push to `main`

### Frontend → Vercel
1. Connect your GitHub repo to Vercel
2. Set **Root Directory** to `react-frontend`
3. Add environment variable in Vercel dashboard:
   - `VITE_API_URL` = your Railway backend URL
4. Vercel auto-deploys on every push to `main`

---

## 🔑 Getting a Free Gemini API Key

1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Click **Get API key** → **Create API key**
3. Copy and add to Railway environment variables as `GEMINI_API_KEY`

Free tier: 15 requests/minute, 1500 requests/day — sufficient for demos and development.

---

## 👥 Role-Based Access Control

| Feature | Admin | Recruiter | Hiring Manager |
|---------|-------|-----------|----------------|
| Upload resumes | ✅ | ✅ | ❌ |
| Analyze candidates | ✅ | ✅ | ❌ |
| View candidates | ✅ | ✅ | ✅ |
| Edit candidate details | ✅ | ✅ | ❌ |
| Approve candidates | ✅ | ❌ | ✅ |
| Delete candidates | ✅ | ❌ | ❌ |
| Export CSV | ✅ | ✅ | ✅ (report only) |
| Schedule interviews | ✅ | ✅ | ❌ |
| Generate emails | ✅ | ✅ | ✅ |
| Admin panel | ✅ | ❌ | ❌ |
| AI chat | ✅ | ✅ | ❌ |

---

## 🧠 AI Pipeline (LangGraph)

```
Upload Resume
     │
     ▼
Resume Parser Node (text extraction)
     │
     ▼
Parallel Agent Nodes:
  ├── Skills Extractor
  ├── Experience Extractor
  ├── Education Extractor
  ├── Projects & Certifications Extractor
  └── Recruitment Details Extractor (CTC, notice, location)
     │
     ▼
JD Analysis Node (keyword extraction)
     │
     ▼
Evaluation Node (match scoring)
     │
     ▼
Recommendation Node (hire/reject reasoning)
     │
     ▼
Save to Database + Update Status
```

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, TypeScript, Tailwind CSS, Lucide Icons |
| Backend | FastAPI, SQLAlchemy, Alembic, Pydantic |
| AI / LLM | LangGraph, LangChain, Google Gemini (gemini-1.5-flash) |
| Database | PostgreSQL (Railway) / SQLite (local) |
| Auth | JWT (PyJWT + passlib bcrypt) |
| Deployment | Vercel (frontend) + Railway (backend) |

---

## 🤝 Contributing

Built during an Agentic AI Internship to demonstrate autonomous AI workflows in enterprise HR. PRs welcome for improvements to agent reasoning, UI enhancements, or new integrations.
