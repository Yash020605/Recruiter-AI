# Recruiter AI: Autonomous Agentic HR Platform

![Recruiter AI](https://img.shields.io/badge/Status-MVP-brightgreen) ![Python](https://img.shields.io/badge/Python-3.11%2B-blue) ![React](https://img.shields.io/badge/React-18-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.104-teal)

Recruiter AI is a cutting-edge, stateful multi-agent recruitment platform designed to automate and augment the entire hiring lifecycle. By orchestrating a swarm of specialized AI agents (using LangGraph and LangChain), this platform parses resumes, evaluates candidate skills against job descriptions, and triggers automated integrations with industry-standard HR tools.

## 🚀 Features

- **Multi-Agent Evaluation:** Utilizes stateful LangGraph workflows to score candidate profiles autonomously. Agents extract skills, compare them to the Job Description, and assign a match score.
- **Background Processing:** AI evaluations are pushed to background tasks, enabling non-blocking, asynchronous analysis of hundreds of candidates at once.
- **Interactive HR Dashboard:** A highly dynamic React dashboard with real-time websocket integration, enabling recruiters to view status updates live.
- **Third-Party Integrations:** API-ready endpoints for initiating background checks (AuthBridge), triggering technical assessments (HackerEarth), syncing ATS records (Zoho Recruit), and onboarding (Keka HRMS).
- **AI Chat Assistant:** A built-in LLM-powered mentor/assistant restricted to retrieving only HR and candidate-related insights.

## 👥 Role-Based Access Control (RBAC)

The platform is designed with three distinct user roles, each with specific permissions:

### 🎯 Recruiter
The primary operator of the platform.
- **Upload:** Upload and parse candidate resumes.
- **Analyze:** Trigger the multi-agent evaluation pipeline.
- **Chat:** Ask the AI assistant questions about candidate matching.

### 👔 Hiring Manager
The decision-maker reviewing the recruiter's shortlisted candidates.
- **View:** Access the dashboard to view candidate profiles, match scores, and parsed skills.
- **Comment:** Leave feedback on specific candidate profiles.
- **Approve:** Finalize decisions based on AI recommendations.

### 🛡️ Admin
The system overseer.
- **Manage Users:** Create, edit, and delete user accounts (Recruiters, Hiring Managers).
- **System Monitoring:** View platform analytics (total candidates, processed resumes, average scores).
- **Logs:** Access system and agent execution logs for debugging.

## 🏗️ System Architecture

The repository is split into two primary components:

### 1. Backend (`/backend`)
- **Framework:** FastAPI
- **Database:** PostgreSQL/SQLite via SQLAlchemy ORM
- **Agent Orchestration:** LangGraph & LangChain (OpenAI/Nemotron models)
- **File Processing:** PyPDF2 for resume parsing
- **Concurrency:** FastAPI BackgroundTasks and Websockets

### 2. Frontend (`/react-frontend`)
- **Framework:** React + Vite
- **Styling:** Tailwind CSS + Lucide Icons
- **State Management:** React Hooks
- **Communication:** Axios REST calls & native WebSocket connections

## 🛠️ Setup & Installation

### Prerequisites
- Node.js (v18+)
- Python (3.10+)

### Backend Initialization
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
```
*Configure your `.env` file in the backend root with your API keys (OpenAI, Zoho, Keka, etc.).*

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Initialization
```bash
cd react-frontend
npm install
npm run dev
```

## 🔐 Environment Variables (.env)
To enable the "Action" integrations and LLM reasoning, a `.env` file is required in the `/backend` directory:
```ini
OPENAI_API_KEY="sk-..."
NVIDIA_API_KEY="nvapi-..."
ZOHO_CLIENT_ID="..."
HACKEREARTH_CLIENT_SECRET="..."
AUTHBRIDGE_TOKEN="..."
KEKA_API_KEY="..."
DATABASE_URL="sqlite:///./recruiter.db"
```

## 🤝 Contributing
Built during an Agentic AI Internship to demonstrate the power of autonomous AI workflows in enterprise environments. Contributions and improvements to the agentic reasoning loops are welcome.
