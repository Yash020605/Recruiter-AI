# UI/UX Design Guidelines

## 1. Design Philosophy
The Recruiter AI platform adopts a modern, "glassmorphic", dark-themed design language. The UI is built to feel responsive, premium, and highly interactive, reflecting the advanced AI capabilities running beneath the hood.

## 2. Color Palette & Typography
- **Primary Colors:** Deep blues and vibrant purples to signify AI and technology.
  - Primary Accent: `#3B82F6` (Tailwind `blue-500`)
  - Secondary Accent: `#8B5CF6` (Tailwind `purple-500`)
- **Background:** Dark grey/black shades (`gray-900` to `black`) to reduce eye strain for recruiters working long hours.
- **Success/Warning/Error:**
  - Success: `green-500` (e.g., Match Score > 80, Completed Interviews)
  - Warning: `yellow-500` (e.g., Match Score 50-79, Pending Interviews)
  - Error: `red-500` (e.g., Match Score < 50, Cancelled Interviews)
- **Typography:** Sans-serif (Inter or Roboto) for clean, highly legible data presentation.

## 3. Core UI Components

### 3.1. Glass Cards
Containers use a glassmorphism effect (semi-transparent backgrounds with backdrop blur and subtle white borders) to create depth and hierarchy without cluttering the screen.
- **Implementation:** `bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl`

### 3.2. Tab Navigation
A horizontal, sticky tab bar allows users to switch contexts (Candidates, Job Matching, Interviews) instantly. Active tabs are highlighted with a glowing bottom border and bold text.

### 3.3. Candidate Roster & Badges
- Candidates are displayed in interactive list items.
- **Badges:** Skill pills and status indicators use solid or outlined badge styles. High-scoring candidates get a distinct visual indicator (e.g., a glowing border or crown icon).

### 3.4. Match Analysis Visualization
- **Score Ring/Bar:** The AI Match Score is presented prominently using a large, bold typographic treatment accompanied by a colored progress bar.
- **Skill Chips:** Matched skills are green pills with checkmarks; missing skills are red pills with 'X' marks, providing immediate visual scannability.

### 3.5. Interactive Floating Chat
- A fixed, bottom-right widget.
- When collapsed, it shows a pulsing message icon.
- When expanded, it reveals a chat interface with distinct chat bubbles (User vs. AI) and smooth slide-in animations.

## 4. Animations & Micro-interactions
- **Hover States:** Buttons and interactive cards slightly scale up (`active:scale-[0.98]`) and increase their shadow or border opacity on hover to encourage interaction.
- **Loading States:** Uses pulsing skeleton loaders or smooth spinners during background AI processing to reassure the user that the system is working.
- **Transitions:** Tab switching and modal toggling use fade-in and slide-in animations (`animate-in fade-in duration-300`).

## 5. Accessibility & Responsiveness
- **Contrast:** High contrast between text (white/light grey) and backgrounds.
- **Grid Layouts:** CSS Grid and Flexbox are used to ensure the dashboard seamlessly reflows from a 3-column desktop layout to a single-column mobile/tablet layout.
- **Focus States:** Distinct focus rings on inputs and textareas for keyboard navigability.
