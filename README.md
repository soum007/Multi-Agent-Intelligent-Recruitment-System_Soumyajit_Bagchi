# Multi-Agent Intelligent Recruitment System (Free & Local)

An AI-powered, **multi-agent recruitment assistant** that automates key parts of the hiring workflow — candidate profiling, personalized assessment design, behavioral & culture-fit analysis, and market intelligence.  
Designed to run **entirely on local, free tools** (e.g., Ollama or small open Hugging Face models), with a **Streamlit UI** and a **CLI**. Synthetic data is included and reproducible.

## ✨ Core Agents

1. **Intelligent Candidate Profiler Agent**
   - Parses synthetic LinkedIn/GitHub-style profiles.
   - Extracts skills & experiences with **confidence scores**.
   - Produces a structured **Talent Intelligence Report** (JSON & Markdown).

2. **Adaptive Technical Assessment Designer Agent**
   - Generates **personalized technical assessments** based on candidate profile + role.
   - Includes **Problems**, **Scoring Rubric**, and a **Bias Mitigation Protocol**.

3. **Behavioral & Cultural Fit Analyzer Agent**
   - Analyzes qualitative interview transcripts to extract themes: collaboration, communication, problem-solving.
   - Provides **high-level insights** with **explicit demographic-bias avoidance**.

4. **Market Intelligence & Sourcing Optimizer Agent**
   - Analyzes static market data to compute **compensation benchmarks** and **talent trends**.
   - Recommends **optimal sourcing channels**.

## 🧱 Architecture

- Lightweight, modular **agents** under `agents/` (stateless, composable).
- Optional LLM use via **Ollama** (recommended: `llama3.1:8b`) or small free HF models (e.g., `google/flan-t5-base`).  
  The system **works without an LLM** using rule-based heuristics + templates.
- **Streamlit app** for interactive demo and **CLI** for batch generation to `outputs/`.

```
multi_agent_recruitment_system/
├─ agents/
│  ├─ profiler.py
│  ├─ assessment_designer.py
│  ├─ behavioral.py
│  └─ market_intel.py
├─ data/
│  ├─ synthetic_profiles.json
│  ├─ market_compensation.csv
│  └─ transcripts.json
├─ app.py
├─ cli.py
├─ README.md
├─ requirements.txt
└─ outputs/
```

## 🛠️ Local Setup (Free-Only)

1. **Python**
   ```bash
   python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   python -m nltk.downloader punkt stopwords
   ```

2. **(Optional) Ollama for better LLM generation**
   - Install from https://ollama.com
   - Pull a free local model:
     ```bash
     ollama pull llama3.1:8b
     ```
   - The app auto-detects Ollama; if unavailable, it uses heuristic templates / small HF models where feasible.

3. **Run Streamlit UI**
   ```bash
   streamlit run app.py
   ```

4. **Run Headless (CLI)**
   ```bash
   python cli.py --candidate-id CAND-001 --role "AI Engineer"
   ```

Outputs are written to `outputs/` as JSON and Markdown.

## 📦 Data Simulation Methodology

- **Candidate Profiles**: Generated via seeded templates blending GitHub/LinkedIn-like fields (repos, languages, roles, durations, education). Frequencies, recency, and cross-source agreement produce **confidence scores**.
- **Transcripts**: Synthetic panel-style Q&A emphasizing collaboration, communication, ownership, conflict resolution. No demographic attributes are stored or inferred.
- **Market Data**: Seeded distribution per role, level, and region; bins for p25/median/p75, growth trend %, and inferred sourcing channels.

Reproducible with `--seed` flags used in the data generator functions inside agents.

## 🔍 Bias Mitigation & Compliance

- Blind to demographic/family/affinity attributes — they are neither input nor inferred.
- Standardized rubrics with **weighted criteria**; consistent across candidates for the same role/level.
- Language audits to avoid value-laden adjectives; focuses on **observable behaviors and outputs**.
- Transparent scoring + rater guidelines included in each Assessment Package.
- All models used are local/free; no PII leaves your machine.

## 🧪 Tests

Minimal smoke tests under `tests/` illustrate agent contracts and validate JSON schema shapes.

## 📹 Demo Video Script (10–12 mins)

See `demo_script.md` for a ready-to-record outline.

## 📧 Submission

- Push this repo to GitHub (public).
- Email the link to **hr@metaupspace.com** with subject:  
  `AI Intern Hiring Task: Multi-Agent Intelligent Recruitment System`.
- Include a brief feature summary (template below).

### Email Template

Subject: AI Intern Hiring Task: Multi-Agent Intelligent Recruitment System

Body (short):
- Built a local, free, multi-agent recruiting assistant with Streamlit + CLI.
- Features: Talent Intelligence Reports, personalized assessments + bias protocol, behavioral insights, market benchmarks & sourcing recs.
- Stack: Python, heuristics + optional Ollama, scikit-learn / NLP, reproducible synthetic data.
- Repo: <your GitHub URL>
- Demo video: <your video URL>

---

**Author:** Your Name • Date: 2025-08-20
