from __future__ import annotations
from typing import Dict, List, Any
from collections import Counter
import re, json

THEMES = {
    "collaboration": ["pair", "mentor", "consensus", "handoff", "async", "review", "huddle", "team"],
    "communication": ["clarify", "document", "notes", "public", "proposal", "explain", "write", "structure"],
    "problem_solving": ["experiment", "trade", "metric", "precision", "recall", "debug", "test", "hypothesis"]
}

def analyze_transcript(lines: List[str]) -> Dict[str, Any]:
    text = "\n".join(lines).lower()
    theme_hits = {k:0 for k in THEMES}
    keywords = []
    for theme, kws in THEMES.items():
        count = sum(len(re.findall(r"\b"+re.escape(kw)+r"\b", text)) for kw in kws)
        theme_hits[theme] = count
        keywords.extend([kw for kw in kws if re.search(r"\b"+re.escape(kw)+r"\b", text)])
    strengths = sorted(theme_hits.items(), key=lambda x: -x[1])
    insights = []
    if theme_hits["problem_solving"]>0:
        insights.append("Evidence of data-driven problem solving and experimentation.")
    if theme_hits["communication"]>0:
        insights.append("Emphasis on clear, structured communication and documentation.")
    if theme_hits["collaboration"]>0:
        insights.append("Signals healthy collaboration practices (reviews, mentoring, coordination).")
    if not insights:
        insights.append("Insufficient evidence to assess soft skills from provided transcript.")
    return {
        "themes": theme_hits,
        "keywords": sorted(set(keywords)),
        "insights": insights,
        "bias_notice": "No demographic or affinity attributes were considered; conclusions are evidence-based and limited to job-relevant behaviors."
    }
