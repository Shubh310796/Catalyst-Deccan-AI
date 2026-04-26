# Khoj — AI-Powered Talent Scouting & Engagement Agent

> **Catalyst Hackathon · Deccan AI · April 2026**

---

## What it does

**Khoj** is an end-to-end AI agent that takes a Job Description as input and returns a ranked candidate shortlist scored across two dimensions: **Match Score** and **Interest Score**.

The agent runs a 3-stage pipeline:

| Stage | What happens |
|---|---|
| **JD Parsing** | LLM extracts role title, required skills, experience, location, and role type from raw JD text |
| **Candidate Matching** | 50 candidates are scored against the parsed JD across skills (40%), experience (30%), and role alignment (30%) |
| **Conversational Outreach** | LLM simulates a 4-turn recruiter ↔ candidate conversation for the top 5 matches; interest level is scored 0–100 |
| **Ranked Shortlist** | Combined score = 60% Match + 40% Interest, full list returned with explanations |

---

## Demo

🌐 **Live Site:** `[add your deployed URL here]`

---

## Architecture

```
                    ┌─────────────────────────────────┐
                    │          KHOJ AGENT              │
                    │                                  │
  JD Text Input ──▶ │  ┌─────────────────────────┐   │
                    │  │    FastAPI Backend        │   │
                    │  │                          │   │
                    │  │  [1] JD Parser (LLM)     │   │
                    │  │        │                 │   │
                    │  │  [2] Candidate Matcher   │   │  ◀── candidates.json (50 profiles)
                    │  │       (rule-based)       │   │
                    │  │        │                 │   │
                    │  │  [3] Outreach Simulator  │   │
                    │  │       (LLM, Top 5)       │   │
                    │  │        │                 │   │
                    │  │  [4] Ranker & Response   │   │
                    │  └────────┼────────────────┘   │
                    └───────────┼─────────────────────┘
                                │
                    ┌───────────▼──────────────────────┐
                    │     React Frontend (Vite)         │
                    │  - JD Input textarea              │
                    │  - Ranked cards with scores       │
                    │  - Expandable conversation view   │
                    └──────────────────────────────────┘
```

### Scoring Formula

```
Combined Score = (Match Score × 0.6) + (Interest Score × 0.4)
```

**Match Score components:**
- Skills overlap: `matched_skills / required_skills × 100` → weight 40%
- Experience fit: `candidate_exp / required_exp × 100` (capped at 100) → weight 30%
- Role alignment: exact/partial title match → weight 30%

**Interest Score:** Derived from the LLM outreach simulation. The model plays both recruiter and candidate, then returns a 0–100 score based on enthusiasm, curiosity, counter-questions, and willingness to proceed.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python · FastAPI · Uvicorn |
| LLM | Ollama (llama3.1) locally · Anthropic Claude (cloud) |
| Frontend | React 19 · Vite · Tailwind CSS v4 · Framer Motion |
| Data | Static JSON (50 synthetic candidates) |

---

## Local Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- [Ollama](https://ollama.ai) installed with `llama3.1` pulled **OR** an Anthropic API key

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/khoj
cd khoj
```

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
```

**Option A — Ollama (local, default):**
```bash
ollama pull llama3.1
# Make sure Ollama is running: ollama serve
uvicorn main:app --reload --port 8000
```

**Option B — Anthropic Claude (cloud, recommended for deployment):**
```bash
# In backend/.env, set:
# LLM_PROVIDER=anthropic
# ANTHROPIC_API_KEY=sk-ant-...
uvicorn main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

### 4. Use it

Open `http://localhost:5173`, paste any job description, and click **Find Candidates**.

---

## Deployment

### Backend (Railway / Render)
```bash
# Set these environment variables on your hosting platform:
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

### Frontend (Vercel / Netlify)
```bash
cd frontend
npm run build
# Deploy the dist/ folder
# Set VITE_API_BASE to your backend URL
```

---

## Sample Input

```
Senior Full-Stack Engineer — FinTech Startup (Remote)

Requirements:
- 4+ years of full-stack experience (Node.js + React)
- PostgreSQL, Redis, TypeScript
- Payments / PCI-DSS experience
- AWS (Lambda, RDS, SQS)
- Team lead experience (2–5 people)

Compensation: ₹35–55 LPA + equity
```

## Sample Output (truncated)

```json
{
  "parsed_jd": {
    "role_title": "Senior Full-Stack Engineer",
    "required_skills": ["Node.js", "React", "TypeScript", "PostgreSQL", "Redis", "AWS"],
    "experience_years_required": 4,
    "role_type": "Full-time",
    "location_preference": "Remote"
  },
  "shortlist": [
    {
      "name": "Priya Sharma",
      "current_role": "Full Stack Engineer",
      "experience_years": 6,
      "match_score": 93.33,
      "interest_score": 85,
      "match_explanation": "Matched 6/6 required skills. Experience (6 yrs) meets requirement (4 yrs). Current role aligns well.",
      "interest_summary": "Highly engaged — asked about equity, team structure, and technical challenges. Clear intent to proceed.",
      "conversation": [
        { "speaker": "Recruiter", "text": "Hi Priya, we have an exciting Senior Full-Stack opportunity at a fintech startup..." },
        { "speaker": "Priya Sharma", "text": "Hi! Yes, I'm currently exploring options. What's the equity structure like?" }
      ]
    }
  ]
}
```

---

## Repo Structure

```
khoj/
├── backend/
│   ├── main.py                  # FastAPI app, pipeline logic
│   ├── requirements.txt
│   ├── .env                     # LLM config
│   ├── data/
│   │   └── candidates.json      # 50 synthetic candidate profiles
│   ├── scripts/
│   │   └── generate_candidates.py
│   └── services/
│       └── llm_service.py       # LLM abstraction (Ollama + Anthropic)
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   └── components/
    │       ├── JDInput.jsx
    │       └── ShortlistTable.jsx
    └── package.json
```

---

## Author

**Shubham Choudhary**
Submitted to: Catalyst Hackathon · Deccan AI · April 2026
E-mail ID: shubham310796@gmail.com
Deccan ID : blbirhw0y2debffcif@getdeccan.ai
Repo access shared with: hackathon@deccan.ai

---

## License

MIT
