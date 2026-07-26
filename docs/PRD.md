# Product Requirements Document (PRD)

## 1. Product Overview
**Recruiter AI** is an autonomous, multi-agent recruitment platform designed to automate and augment the entire hiring lifecycle. By orchestrating a swarm of specialized AI agents, this platform streamlines repetitive HR tasks, parses resumes, evaluates candidate skills against job descriptions, and triggers automated integrations with industry-standard HR tools.

## 2. Target Audience
- **Recruiters:** Primary operators who upload candidate data, trigger analyses, and schedule interviews.
- **Hiring Managers:** Decision-makers who review shortlisted candidates, provide feedback, and make final hiring decisions.
- **System Administrators:** IT/Admin staff overseeing the platform, managing users, and monitoring analytics.

## 3. Key Objectives
- **Efficiency:** Reduce the time-to-hire by automating initial resume screening and candidate evaluation.
- **Objectivity:** Eliminate human bias in the early stages of recruitment by standardizing evaluation criteria through AI scoring.
- **Seamless Integration:** Connect disparate HR tools (ATS, Assessment, Background checks, Calendars) into a single unified workflow.
- **Autonomy:** Leverage multi-agent systems to perform complex reasoning, extraction, and synthesis tasks without blocking user interactions.

## 4. Core Features
### 4.1. Multi-Agent Evaluation & Ranking
- Agents parse uploaded resumes and extract key skills, experiences, and qualifications.
- Agents compare extracted candidate profiles against provided Job Descriptions (JDs).
- System assigns a composite "Match Score" based on AI evaluation and third-party technical assessments.
- Real-time ranking and color-coded badges to surface top candidates instantly.

### 4.2. Automated Interview Scheduling
- Provide an interface to schedule Technical and HR interviews.
- Automatically integrate with Google Calendar to dispatch meeting invites.
- Generate Jitsi Meet links for seamless video conferencing.
- Track interview status (Scheduled, Completed, Cancelled).

### 4.3. Interactive HR Dashboard
- Provide role-specific views (Recruiter, Hiring Manager, Admin).
- Real-time updates via WebSockets so users see evaluation progress live without refreshing.
- Detailed candidate profiles containing AI summaries, matched/missing skills, and historical comments.

### 4.4. AI Chat Assistant
- An LLM-powered mentor accessible via a floating chat widget.
- Restricted explicitly to HR and candidate-related inquiries to ensure data security and relevance.
- Can assist recruiters in understanding why a candidate received a specific match score.

### 4.5. Third-Party Integrations
- **Assessments:** HackerEarth API for triggering coding challenges.
- **Background Checks:** AuthBridge API integration.
- **ATS & HRMS:** Zoho Recruit and Keka HRMS sync.
- **Workspace:** Google Workspace (Sheets for export, Calendar for scheduling).

## 5. Success Metrics
- **Time Savings:** >50% reduction in resume screening time.
- **Candidate Quality:** Higher retention rate and positive feedback from Hiring Managers.
- **System Stability:** >99% uptime with robust background processing capabilities.
- **User Adoption:** High daily active usage among the recruiting team.
