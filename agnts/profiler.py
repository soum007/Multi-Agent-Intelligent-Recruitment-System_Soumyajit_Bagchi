from __future__ import annotations
from typing import Dict, List, Any
import math, json, datetime as dt
from collections import Counter

def _months_between(start: str, end: str|None) -> int:
    s = dt.datetime.strptime(start, "%Y-%m")
    e = dt.datetime.now() if end is None else dt.datetime.strptime(end, "%Y-%m")
    return max(1, (e.year - s.year) * 12 + (e.month - s.month))

def _confidence_from_sources(skill_freq: int, recency_boost: float, repo_signal: float) -> float:
    # 0-1 confidence based on frequency, recency, and github repos
    base = min(1.0, 0.4 + 0.15*skill_freq)
    score = base + 0.25*recency_boost + 0.2*repo_signal
    return max(0.1, min(1.0, score))

def extract_skills(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    li_skills = profile.get("linkedin", {}).get("skills", [])
    gh_langs = profile.get("github", {}).get("languages", [])
    gh_topics = [t for r in profile.get("github", {}).get("repos", []) for t in r.get("topics", [])]
    all_terms = [*li_skills, *gh_langs, *gh_topics]
    freq = Counter([t.lower() for t in all_terms])
    # recency: weight current role
    recency_map = {}
    for exp in profile.get("linkedin", {}).get("experience", []):
        months = _months_between(exp["start"], exp["end"])
        for k in li_skills:
            recency_map[k.lower()] = max(recency_map.get(k.lower(), 0), min(1.0, months/48))
    items = []
    for term, f in freq.items():
        rec = recency_map.get(term, 0.2)
        repo_signal = 1.0 if any(term in [t.lower() for t in r.get("topics", [])] for r in profile.get("github", {}).get("repos", [])) else 0.0
        conf = round(_confidence_from_sources(f, rec, repo_signal), 2)
        items.append({"skill": term, "confidence": conf})
    # sorted by confidence desc
    return sorted(items, key=lambda x: (-x["confidence"], x["skill"]))

def summarize_career(profile: Dict[str, Any]) -> str:
    exps = profile.get("linkedin", {}).get("experience", [])
    if not exps: return "No work history available."
    exps_sorted = sorted(exps, key=lambda e: e["start"])
    total_months = sum(_months_between(e["start"], e["end"]) for e in exps_sorted)
    current = exps_sorted[-1]
    curr_dur = _months_between(current["start"], current["end"])
    headline = profile.get("headline","")
    name = profile.get("name","")
    return (
        f"{name} has ~{round(total_months/12,1)} years across {len(exps_sorted)} roles. "
        f"Currently at {current['company']} as {current['title']} (~{curr_dur//12}y {curr_dur%12}m). "
        f"Focus areas inferred from headline: {headline.split('|')[1].strip() if '|' in headline else headline}."
    )

def talent_intelligence_report(profile: Dict[str, Any]) -> Dict[str, Any]:
    skills = extract_skills(profile)
    summary = summarize_career(profile)
    gh = profile.get("github",{})
    repo_highlights = sorted(gh.get("repos", []), key=lambda r: (-r.get("stars",0), r["name"]))[:3]
    return {
        "id": profile.get("id"),
        "name": profile.get("name"),
        "summary": summary,
        "top_skills": skills[:10],
        "github_summary": {
            "contrib_last12mo": gh.get("contrib_last12mo", 0),
            "top_repos": repo_highlights
        }
    }
