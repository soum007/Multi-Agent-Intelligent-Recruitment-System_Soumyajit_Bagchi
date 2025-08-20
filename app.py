# app.py
import json
import re
from datetime import datetime, timezone
from pathlib import Path
import streamlit as st
import pandas as pd

# try to import agent functions (fail gracefully)
try:
    from agents.profiler import talent_intelligence_report
except Exception:
    talent_intelligence_report = None

try:
    from agents.assessment_designer import generate_assessment
except Exception:
    generate_assessment = None

try:
    from agents.behavioral import analyze_transcript
except Exception:
    analyze_transcript = None

try:
    from agents.market_intel import load_market, summarize
except Exception:
    load_market = None
    summarize = None

# -------------------- CONFIG & DATA PATHS --------------------
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
PROFILES_PATH = DATA_DIR / "synthetic_profiles.json"
TRANSCRIPTS_PATH = DATA_DIR / "transcripts.json"
MARKET_PATH = DATA_DIR / "market_compensation.csv"
ASSESS_PATH = DATA_DIR / "assessments.json"
BEHAV_PATH = DATA_DIR / "behavioral_analysis.json"

# ensure output files exist (create empty arrays if missing)
for p in [ASSESS_PATH, BEHAV_PATH]:
    if not p.exists():
        p.write_text("[]", encoding="utf-8")

# -------------------- HELPERS --------------------
def safe_load_json(path_or_file):
    """Load JSON from file path or file-like object. Returns None on error."""
    try:
        if hasattr(path_or_file, "read"):
            return json.load(path_or_file)
        else:
            with open(path_or_file, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        st.sidebar.error(f"Failed to load JSON ({path_or_file}): {e}")
        return None

def safe_read_json_file(path: Path):
    try:
        if not path.exists():
            return []
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []

def safe_write_json_file(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def append_to_json_array(path: Path, entry: dict):
    arr = safe_read_json_file(path)
    arr.append(entry)
    safe_write_json_file(path, arr)

def infer_role(profile):
    if not isinstance(profile, dict):
        return "Unknown"
    headline = profile.get("headline")
    if isinstance(headline, str) and headline.strip():
        return headline.split("|")[0].strip()
    linkedin = profile.get("linkedin", {}) or {}
    exp = linkedin.get("experience") or []
    if isinstance(exp, list) and exp:
        title = exp[0].get("title")
        if title:
            return title
    summary = linkedin.get("summary", "")
    if isinstance(summary, str) and summary:
        m = re.search(r"is (an|a)\s+([A-Za-z0-9\-\s/]+?)(?:\s+with|\.\s|$)", summary, flags=re.IGNORECASE)
        if m:
            return m.group(2).strip()
    skills = linkedin.get("skills", []) or []
    if skills:
        return skills[0]
    return "Unknown"

def parse_years_from_summary(summary):
    if not summary or not isinstance(summary, str):
        return None
    m = re.search(r"(\d+)\s*-\s*(\d+)\s*years", summary, flags=re.IGNORECASE)
    if m:
        try:
            return float(int(m.group(1)))
        except Exception:
            pass
    m2 = re.search(r"(\d+)\s*years", summary, flags=re.IGNORECASE)
    if m2:
        try:
            return float(int(m2.group(1)))
        except Exception:
            pass
    return None

def compute_experience_years(profile, as_of_date=None):
    if as_of_date is None:
        as_of_date = datetime.now()
    linkedin = profile.get("linkedin", {}) or {}
    exp = linkedin.get("experience") or []
    starts = []
    ends = []
    for e in exp:
        s = e.get("start")
        t = e.get("end")
        if isinstance(s, str):
            try:
                if re.match(r"^\d{4}-\d{2}$", s):
                    starts.append(datetime.strptime(s, "%Y-%m"))
                elif re.match(r"^\d{4}$", s):
                    starts.append(datetime.strptime(s, "%Y"))
            except Exception:
                pass
        if isinstance(t, str):
            try:
                if re.match(r"^\d{4}-\d{2}$", t):
                    ends.append(datetime.strptime(t, "%Y-%m"))
                elif re.match(r"^\d{4}$", t):
                    ends.append(datetime.strptime(t, "%Y"))
            except Exception:
                pass
        else:
            ends.append(as_of_date)
    if not starts:
        return None
    start_dt = min(starts)
    end_dt = max(ends) if ends else as_of_date
    months = (end_dt.year - start_dt.year) * 12 + (end_dt.month - start_dt.month)
    years = months / 12.0
    return round(years, 1)

def infer_level(profile):
    linkedin = profile.get("linkedin", {}) or {}
    summary = linkedin.get("summary", "")
    y = parse_years_from_summary(summary)
    if y is None:
        y = compute_experience_years(profile)
    if y is None:
        return "Mid"
    try:
        y = float(y)
        if y < 2:
            return "Junior"
        if 2 <= y < 5:
            return "Mid"
        return "Senior"
    except Exception:
        return "Mid"

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="Recruitment Assistant", layout="wide")
st.title("🤖 Multi-Agent Intelligent Recruitment System")

# -------------------- SIDEBAR: Data & candidate selector --------------------
with st.sidebar:
    st.header("📂 Data Sources")

    profiles_file = st.file_uploader("Upload Candidate Profiles JSON", type=["json"], accept_multiple_files=False)
    if not profiles_file and PROFILES_PATH.exists():
        profiles_file = str(PROFILES_PATH)

    profiles = safe_load_json(profiles_file) or []
    if not isinstance(profiles, list):
        st.sidebar.error("Profiles JSON must be a list/array of profile objects.")
        profiles = []

    # transcripts
    transcripts = safe_load_json(TRANSCRIPTS_PATH) or {}

    # market data
    try:
        if load_market:
            market_df = load_market(MARKET_PATH)
        else:
            market_df = pd.read_csv(MARKET_PATH) if Path(MARKET_PATH).exists() else pd.DataFrame()
    except Exception:
        market_df = pd.DataFrame()

    st.markdown("---")
    st.subheader("Candidate Selection")
    if profiles:
        ids = [p.get("id", f"no-id-{i}") for i, p in enumerate(profiles)]
        selected_cid = st.selectbox("Choose candidate", ids)
    else:
        selected_cid = None

# ensure selected_cid exists
if not selected_cid and profiles:
    selected_cid = profiles[0].get("id")
# safe profile object
profile = next((p for p in profiles if p.get("id") == selected_cid), profiles[0] if profiles else {})

# load saved lists
saved_assessments = safe_read_json_file(ASSESS_PATH)
saved_behaviorals = safe_read_json_file(BEHAV_PATH)

# -------------------- TABS --------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Candidate Profiler",
    "Assessment Designer",
    "Behavioral Analyzer",
    "Market Intelligence"
])

# -------------------- TAB 1: Candidate Profiler --------------------
with tab1:
    st.subheader("🧑 Candidate Profiler")
    if not profile:
        st.warning("No profile selected or profile is empty.")
    else:
        report = {}
        if talent_intelligence_report:
            try:
                report = talent_intelligence_report(profile) or {}
            except Exception as e:
                st.warning(f"talent_intelligence_report() failed: {e}")
                report = {}

        # fallback values
        report.setdefault("role", infer_role(profile))
        report.setdefault("level", infer_level(profile))
        report.setdefault("skills", (profile.get("linkedin", {}) or {}).get("skills", []))
        if "experience_years" not in report:
            exp_y = compute_experience_years(profile)
            if exp_y is not None:
                report["experience_years"] = exp_y

        col1, col2, col3 = st.columns(3)
        col1.metric("Role", report.get("role", "-"))
        col2.metric("Region", report.get("region", "-"))
        col3.metric("Level", report.get("level", "-"))

        st.markdown(f"### {profile.get('name','Unknown')}")
        if profile.get("headline"):
            st.write(profile.get("headline"))
        summary = (profile.get("linkedin", {}) or {}).get("summary")
        if summary:
            st.write(summary)

        # Skills
        skills = report.get("skills", [])
        if skills:
            st.markdown("#### 🛠 Skills")
            st.write(", ".join(skills))

        # Experience list
        exp_list = (profile.get("linkedin", {}) or {}).get("experience", [])
        if isinstance(exp_list, list) and exp_list:
            st.markdown("#### 💼 Experience")
            for exp in exp_list:
                title = exp.get("title", "N/A")
                comp = exp.get("company", "N/A")
                start = exp.get("start", "N/A")
                end = exp.get("end", None)
                end_display = end if end else "Present"
                st.write(f"**{title}** @ {comp} ({start} – {end_display})")
                for h in exp.get("highlights", []) or []:
                    st.write(f"- {h}")

        # Education
        edu_list = (profile.get("linkedin", {}) or {}).get("education", [])
        if isinstance(edu_list, list) and edu_list:
            st.markdown("#### 🎓 Education")
            for edu in edu_list:
                st.write(f"{edu.get('degree','')} from {edu.get('school','')} ({edu.get('grad_year','')})")

        # GitHub overview
        gh = profile.get("github", {}) or {}
        if gh:
            st.markdown("#### 🐙 GitHub Overview")
            st.write(f"Contributions (last 12mo): {gh.get('contrib_last12mo', 0)}")
            repos = gh.get("repos", [])
            if isinstance(repos, list) and repos:
                for repo in repos:
                    st.write(f"- {repo.get('name','unknown')} ⭐ {repo.get('stars',0)} | Topics: {', '.join(repo.get('topics',[]) or [])}")

        # Experience years metric
        if "experience_years" in report and report["experience_years"] is not None:
            st.metric("Experience (Years)", report["experience_years"])

# -------------------- TAB 2: Assessment Designer --------------------
with tab2:
    st.subheader("📝 Assessment Designer")
    available_roles = sorted({infer_role(p) for p in profiles}) if profiles else ["General"]
    role_choice = st.selectbox("Role", available_roles, index=0 if infer_role(profile) in available_roles else 0)
    inferred_level = infer_level(profile)
    level_choice = st.selectbox("Level", ["Junior", "Mid", "Senior"], index=["Junior","Mid","Senior"].index(inferred_level) if inferred_level in ["Junior","Mid","Senior"] else 1)

    package = {}
    if generate_assessment:
        try:
            package = generate_assessment(profile, role=role_choice, level=level_choice) or {}
        except Exception as e:
            st.warning(f"generate_assessment() failed: {e}")
            package = {}
    else:
        package = {
            "format": "Mixed (MCQ + Coding)",
            "difficulty": "Medium",
            "sections": ["Core Knowledge", "System Design", "Practical Task"],
            "sample_questions": [
                "Describe a RAG architecture and its failure modes.",
                "Implement a function to merge two sorted arrays (30 min)."
            ]
        }

    st.markdown("### 📦 Assessment Package")
    st.write("**Format:**", package.get("format", "N/A"))
    st.write("**Difficulty:**", package.get("difficulty", "N/A"))

    if "sections" in package:
        st.markdown("#### Sections")
        for section in package["sections"]:
            st.write(f"- {section}")

    if "sample_questions" in package:
        with st.expander("💡 Sample Questions"):
            for q in package["sample_questions"]:
                st.write(f"- {q}")

    # Save assessment button
    st.markdown("---")
    if st.button("Save Assessment Package"):
        entry = {
            "profile_id": selected_cid,
            "role": role_choice,
            "level": level_choice,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "package": package,
            "seed": None
        }
        append_to_json_array(ASSESS_PATH, entry)
        st.success(f"Saved assessment for {selected_cid} to {ASSESS_PATH}")
        # refresh saved_assessments in-memory
        saved_assessments = safe_read_json_file(ASSESS_PATH)

    # Show saved assessments for this candidate
    st.markdown("#### Saved Assessments")
    my_assess = [a for a in saved_assessments if a.get("profile_id") == selected_cid]
    if my_assess:
        for a in my_assess[::-1]:
            ga = a.get("generated_at", "unknown")
            diff = a.get("package", {}).get("difficulty", "N/A")
            st.write(f"- {ga} — Difficulty: {diff}")
            st.download_button(
                label="Download package (JSON)",
                data=json.dumps(a, indent=2, ensure_ascii=False),
                file_name=f"{selected_cid}_assessment_{ga.replace(':','-')}.json",
                mime="application/json"
            )
    else:
        st.info("No saved assessments for this candidate (click 'Save Assessment Package' to store one).")

# -------------------- TAB 3: Behavioral Analyzer --------------------
with tab3:
    st.subheader("🧠 Behavioral & Culture Fit")
    lines = transcripts.get(selected_cid, ["(no transcript provided)"]) if isinstance(transcripts, dict) else ["(no transcript provided)"]
    st.markdown("#### Transcript / Notes")
    for l in lines:
        st.write(l)

    analysis = {}
    if analyze_transcript:
        try:
            analysis = analyze_transcript(lines) or {}
        except Exception as e:
            st.warning(f"analyze_transcript() failed: {e}")
            analysis = {}
    else:
        text = "\n".join(lines) if isinstance(lines, list) else str(lines)
        traits = {}
        if re.search(r"\bteam\b|\bcollab(orate|oration)?\b", text, flags=re.I):
            traits["collaboration"] = "High"
        if re.search(r"\bexperiment\b|\bdata\b|\bmetric\b|\bprecision\b", text, flags=re.I):
            traits["data_driven"] = "Yes"
        if re.search(r"\blead(er|ing)?\b|\bmentor\b", text, flags=re.I):
            traits["leadership"] = "Possible"
        if traits:
            analysis["traits"] = traits
        # Add minimal follow-up suggestions
        analysis.setdefault("follow_up_questions", [
            "Tell me about a time you disagreed with a teammate — how did you resolve it?",
            "Describe a data-driven decision you made and how you validated it."
        ])
        analysis.setdefault("bias_check", "No demographic attributes were used or inferred.")

    if "traits" in analysis:
        st.markdown("### Personality Traits")
        for trait, score in analysis["traits"].items():
            st.write(f"- **{trait.capitalize()}**: {score}")
    else:
        st.info("No traits identified from transcript (or agent missing).")

    if "follow_up_questions" in analysis:
        with st.expander("Suggested Follow-up Questions"):
            for q in analysis["follow_up_questions"]:
                st.write(f"- {q}")

    if "bias_check" in analysis:
        st.markdown("#### Bias Check")
        st.write(analysis["bias_check"])

    # Save behavioral analysis
    st.markdown("---")
    if st.button("Save Behavioral Analysis"):
        entry = {
            "profile_id": selected_cid,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": str(TRANSCRIPTS_PATH),
            "analysis": analysis
        }
        append_to_json_array(BEHAV_PATH, entry)
        st.success(f"Saved behavioral analysis for {selected_cid} to {BEHAV_PATH}")
        saved_behaviorals = safe_read_json_file(BEHAV_PATH)

    # Show saved analyses
    st.markdown("#### Saved Behavioral Analyses")
    my_beh = [b for b in saved_behaviorals if b.get("profile_id") == selected_cid]
    if my_beh:
        for b in my_beh[::-1]:
            ga = b.get("generated_at", "unknown")
            st.write(f"- {ga}")
            st.download_button(
                label="Download analysis (JSON)",
                data=json.dumps(b, indent=2, ensure_ascii=False),
                file_name=f"{selected_cid}_behavior_{ga.replace(':','-')}.json",
                mime="application/json"
            )
    else:
        st.info("No saved behavioral analyses for this candidate (click 'Save Behavioral Analysis' to store one).")

# -------------------- TAB 4: Market Intelligence --------------------
with tab4:
    st.subheader("🌍 Market Intelligence & Sourcing")
    try:
        if isinstance(market_df, pd.DataFrame) and 'region' in market_df.columns:
            region_list = sorted(market_df['region'].dropna().unique().tolist())
        else:
            region_list = ["Global"]
        region_choice = st.selectbox("Region", region_list)

        if isinstance(market_df, pd.DataFrame) and 'role' in market_df.columns:
            market_roles = sorted(market_df['role'].dropna().unique().tolist())
        else:
            market_roles = available_roles if profiles else ["General"]
        mrole = st.selectbox("Role (Market)", market_roles)

        if isinstance(market_df, pd.DataFrame) and 'level' in market_df.columns:
            market_levels = sorted(market_df['level'].dropna().unique().tolist())
        else:
            market_levels = ["Junior", "Mid", "Senior"]
        mlevel = st.selectbox("Level (Market)", market_levels)

        if summarize:
            try:
                summary = summarize(market_df, role=mrole, region=region_choice, level=mlevel) or {}
            except Exception as e:
                st.warning(f"summarize() failed: {e}")
                summary = {}
        else:
            summary = {}
            if isinstance(market_df, pd.DataFrame) and not market_df.empty:
                subset = market_df.copy()
                if 'role' in subset.columns:
                    subset = subset[subset['role'] == mrole]
                if 'region' in subset.columns:
                    subset = subset[subset['region'] == region_choice]
                if 'level' in subset.columns:
                    subset = subset[subset['level'] == mlevel]
                if not subset.empty:
                    row = subset.iloc[0]
                    summary["trend_yoy_pct"] = row.get("trend_yoy_pct", 0)
                    summary["compensation_LPA"] = row.get("compensation_LPA", {})
                    channels = row.get("channels", "")
                    if isinstance(channels, str):
                        summary["channels"] = [c.strip() for c in channels.split(",") if c.strip()]
                    else:
                        summary["channels"] = channels or []
    except Exception as e:
        st.error(f"Market intelligence UI failed: {e}")
        summary = {}

    st.metric("YoY Growth (%)", f"{summary.get('trend_yoy_pct', 0)}%")
    st.markdown("### Compensation Range (LPA)")
    st.table(pd.DataFrame([summary.get("compensation_LPA", {})]))

    if "channels" in summary and summary["channels"]:
        with st.expander("📢 Recommended Sourcing Channels"):
            st.write(", ".join(summary["channels"]))
