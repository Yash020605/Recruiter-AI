# Technical Requirements Document (TRD)

## 1. System Architecture Overview
The Recruiter AI platform is designed as a modular, decoupled application featuring a robust API backend and a responsive single-page application (SPA) frontend.

### 1.1. High-Level Components
- **Frontend Client:** React 18, Vite, Tailwind CSS.
- **Backend API:** FastAPI (Python 3.11+).
- **Database:** PostgreSQL (production via psycopg2) / SQLite (local development) with SQLAlchemy ORM.
- **AI Orchestration Layer:** LangChain and LangGraph for managing stateful multi-agent workflows.

## 2. Backend Specifications
### 2.1. Framework & Core Libraries
- **FastAPI:** Handles RESTful routing, background tasks, and Websocket connections for real-time client updates.
- **SQLAlchemy:** Manages database models and migrations. Models include `Candidate`, `JobMatch`, and `Interview`.
- **PyPDF2:** For extracting raw text from uploaded resume PDF files.
- **Pydantic:** Validates incoming and outgoing API schemas.

### 2.2. AI Orchestration (LangGraph)
- **State Definition:** Maintains candidate data, JD text, extracted skills, and intermediate reasoning paths.
- **Nodes/Agents:**
  - `Extraction Agent`: Parses resumes to identify hard skills, soft skills, and experiences.
  - `Comparison Agent`: Checks extracted profile against the JD.
  - `Scoring Agent`: Generates the final composite match score.
- **LLM Integrations:** Uses OpenAI/Nemotron models for natural language understanding and synthesis.

### 2.3. Integrations & API Clients
- **Google Calendar API:** Used for scheduling `Interview` entities. Authenticated via `credentials.json`.
- **WebSockets:** Endpoints at `/ws/{client_id}` push analysis statuses (e.g., "Extracting Skills...", "Computing Score...") to the frontend.

## 3. Frontend Specifications
### 3.1. Core Tech Stack
- **React & Vite:** Fast HMR and optimized production builds.
- **Styling:** Tailwind CSS for a modern, glassmorphic UI design system. Lucide-React for consistent iconography.
- **State Management:** React hooks (`useState`, `useEffect`, `useCallback`) handle local state.

### 3.2. Key UI Components
- **HR Dashboard (`HRDashboard.tsx`):** The primary view orchestrating tabbed navigation between Candidates, Job Matching, and Interview Scheduling.
- **Interview Section (`InterviewSection.tsx`, `InterviewForm.tsx`, `InterviewTable.tsx`):** Components dedicated to listing upcoming interviews, scheduling new ones, and managing statuses.
- **Floating Chat Widget:** A persistent bottom-right modal allowing context-aware conversations with the AI Assistant.

## 4. Deployment Architecture
- **Frontend Hosting:** Vercel (Auto-deploy on push to `main`).
- **Backend Hosting:** Railway/Render. Uses `render.yaml` or Docker-based build pipelines.
- **Environment Management:** Strict separation of `.env` configurations. Secrets (like Google credentials, API keys) are managed via native platform secret stores and excluded from version control via `.gitignore`.

## 5. Security & Access Control
- **Authentication:** Role-based access control (RBAC). Roles include `recruiter`, `hiring_manager`, and `admin`. UI features are toggled conditionally based on the active role.
- **Data Privacy:** PII and resumes are processed in memory and stored securely. Secret scanning and push protection are enforced on the GitHub repository to prevent credential leaks.
