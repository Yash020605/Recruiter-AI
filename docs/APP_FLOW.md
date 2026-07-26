# Application Flow Document

This document outlines the user journeys and data flows within the Recruiter AI platform.

## 1. Authentication & Role Selection Flow
1. **User lands on application.**
2. **Role Selection:** User is prompted to select their role (`Recruiter`, `Hiring Manager`, or `Admin`).
3. **Dashboard Initialization:** Based on the selected role, the React frontend renders the appropriate view and UI components (e.g., Hiring Managers cannot upload resumes or access the chat widget).

## 2. Candidate Onboarding Flow (Recruiter Only)
1. **Resume Upload:** Recruiter navigates to the "Candidates" tab and uploads a PDF resume.
2. **Backend Processing:**
   - The file is sent via multipart/form-data to the FastAPI backend.
   - `PyPDF2` extracts the text content.
   - A new `Candidate` record is created in the database.
3. **UI Update:** The new candidate instantly appears in the Candidate Roster list.

## 3. Multi-Agent Evaluation Flow
1. **Initiate Match:** Recruiter selects a candidate and inputs a target Job Description (JD) in the "Job Matching" tab.
2. **Trigger Analysis:** User clicks "Analyze Match".
3. **WebSocket Connection:** The frontend establishes a WS connection to listen for live updates.
4. **LangGraph Pipeline (Background Task):**
   - **Extraction Node:** Identifies skills and experiences from the candidate's resume text.
   - **Comparison Node:** Maps extracted skills against JD requirements.
   - **Scoring Node:** Computes a 0-100 Match Score and generates a summary.
5. **Real-time Updates:** As each node completes, a WS message is sent to the frontend, updating the loading UI.
6. **Completion:** The final `JobMatch` object is saved to the database. The UI displays the score, AI summary, and matched/missing skills.

## 4. Interview Scheduling Flow
1. **Schedule Setup:** User navigates to the "Interviews" section and clicks "Schedule Interview".
2. **Form Submission:** User selects a Candidate, Interview Type (Technical, HR, Culture Fit), Date, and Time.
3. **Backend Integration:**
   - The API receives the request and formats a Google Calendar payload.
   - The Google Calendar API is invoked to create an event with a Jitsi Meet link.
   - The `Interview` record is saved in the database.
4. **Confirmation:** The UI updates the Interview Table with the newly scheduled event and displays the meeting link.

## 5. Review & Feedback Flow (Hiring Manager)
1. **View Profiles:** Hiring Manager logs in and views the Candidate Roster and Match Scores.
2. **Provide Feedback:** Manager adds qualitative comments to a specific candidate profile.
3. **Status Update:** Manager marks the candidate as "Approved", "Rejected", or "Needs Interview".

## 6. AI Assistant Interaction Flow
1. **Open Chat:** Recruiter opens the floating chat widget.
2. **Submit Query:** User asks a question (e.g., "Why did Candidate X get a low score?").
3. **Contextual Retrieval:** The backend LLM retrieves relevant candidate and JD data.
4. **Response:** The LLM streams the explanation back to the chat widget, providing actionable insights.
