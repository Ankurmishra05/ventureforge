# VentureForge

VentureForge is an AI-powered platform designed to help early-stage founders turn raw startup ideas into structured, actionable business plans.

Instead of relying on generic text generation, VentureForge uses multiple specialized AI agents to evaluate an idea from different business angles—market demand, branding, monetization, and strategic viability.

The goal is simple: help founders move faster from idea to decision.

---

# What It Does

A user enters:

* Startup idea
* Target audience

The platform then generates:

* Market research summary
* Target audience insights
* Pain points analysis
* Startup name and tagline
* Brand tone suggestions
* Revenue model and projections
* AI strategic verdict (Build / Pivot / Avoid)
* Risk score
* Revenue chart
* Exportable reports
* Saved generation history

---

# Why I Built It

A lot of startup tools can generate content, but very few help with actual decision-making.

I wanted to build something that feels closer to a founder’s co-pilot—something that doesn’t just write outputs, but helps evaluate whether an idea is worth pursuing and how it could be improved.

---

# How It Works

VentureForge uses a multi-agent architecture where each component has a focused role.

### Research Agent

Looks at market need, user pain points, and opportunity potential.

### Branding Agent

Generates names, taglines, and positioning ideas.

### Finance Agent

Creates monetization strategy, pricing, and early revenue estimates.

### Decision Agent

Provides a final recommendation:

* Build
* Pivot
* Avoid

Along with reasoning and a risk score.

---

# Tech Stack

## Frontend

* Next.js
* TypeScript
* Tailwind CSS
* Framer Motion

## Backend

* FastAPI
* Python
* SQLAlchemy
* Alembic
* PostgreSQL

## AI & Infrastructure

* Groq
* OpenRouter
* Ollama
* JWT Authentication
* GitHub

---

# Key Features

* Secure signup/login system
* Protected dashboard
* Real-time startup generation
* Confidence scoring normalization
* Saved history in PostgreSQL
* PDF export
* Pitch deck export
* Evaluation script for benchmarking
* Ready for CI/CD and cloud deployment

---

# Example Use Case

### Input

Idea: AI Resume Coach
Audience: Job Seekers

### Output

* Startup Name: ResumeGenie
* Verdict: Build
* Risk Score: 30%
* Freemium Revenue Model
* Strategic expansion suggestions

---

# Local Setup

## Clone the repository

```bash id="1yajlo"
git clone https://github.com/Ankurmishra05/ventureforge.git
cd ventureforge
```

## Backend

```bash id="pb53vd"
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Frontend

```bash id="e3hy4s"
cd frontend
npm install
npm run dev
```

---

# Environment Variables

Create a `.env` file inside the backend folder:

```env id="ncz4v0"
GROQ_API_KEY=your_key
OPENROUTER_API_KEY=your_key
OLLAMA_URL=http://localhost:11434
DATABASE_URL=your_postgresql_url
SECRET_KEY=your_secret
```

---

# What I Learned Building This

This project involved much more than model APIs. It required solving real product problems:

* authentication flows
* database persistence
* frontend/backend integration
* schema validation
* output consistency
* evaluation metrics
* user experience design

It was a strong exercise in building an end-to-end AI product instead of just a model demo.

---

# Roadmap

* Live deployment
* CI/CD automation
* Real-time market signals
* Team workspaces
* Advanced analytics
* A/B testing across models

---

# Author

Ankur Mishra

If you’d like to connect, collaborate, or discuss the project, feel free to reach out.
