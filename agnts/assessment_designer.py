from __future__ import annotations
from typing import Dict, Any, List
import random, json

DEFAULT_RUBRIC = [
    {"name":"Problem-solving approach","weight":40,"criteria":["Decomposition","Trade-offs","Testing strategy"]},
    {"name":"Code quality","weight":30,"criteria":["Readability","Correctness","Efficiency"]},
    {"name":"Communication","weight":30,"criteria":["Clarity","Structure","Reasoning"]}
]

BIAS_PROTOCOL = [
    "Do not consider personal background beyond job-relevant evidence.",
    "Use the rubric and weights consistently across all candidates for this role/level.",
    "Ground feedback in observable actions (code, explanations, design diagrams). Avoid subjective adjectives.",
    "If uncertain, record 'insufficient evidence' rather than guessing.",
    "Double-score independently; resolve discrepancies via evidence-based discussion."
]

ROLE_BANK = {
  "AI Engineer": {
      "coding": [
          "Implement a retrieval-augmented QA function with BM25 + vector fallback; include tests.",
          "Write a streaming token-by-token generator with backpressure control."
      ],
      "system_design": [
          "Design a multi-tenant evaluation service to run model benchmarks at scale (cost, latency, safety)."
      ]
  },
  "ML Engineer": {
      "coding": [
          "Build a feature store loader with offline/online consistency guarantees.",
          "Implement a training loop with early stopping and model checkpointing."
      ],
      "system_design": [
          "Design an ML experimentation platform supporting versioning, lineage, and reproducibility."
      ]
  },
  "Full-Stack Developer": {
      "coding": [
          "Create a CRUD API with auth, rate-limits, and optimistic UI updates.",
          "Build a dashboard with pagination and accessibility (a11y) best practices."
      ],
      "system_design": [
          "Design a SaaS billing system with usage metering and invoice generation."
      ]
  }
}

def _pick(lst: List[str], k:int=1) -> List[str]:
    if k>=len(lst): return lst[:]
    return random.sample(lst, k)

def generate_assessment(profile: Dict[str, Any], role: str, level: str="Mid") -> Dict[str, Any]:
    bank = ROLE_BANK.get(role, ROLE_BANK["AI Engineer"]
    )
    coding = _pick(bank["coding"], 2 if level!="Junior" else 1)
    design = _pick(bank["system_design"], 1)
    # Slightly tailor prompts with top skills
    top_skills = [s["skill"] for s in profile.get("top_skills", [])][:5]
    tailored = [c + f" (prefer approaches leveraging: {', '.join(top_skills)})" for c in coding]
    return {
        "role": role,
        "level": level,
        "technical_challenges": tailored + design,
        "evaluation_rubric": DEFAULT_RUBRIC,
        "bias_mitigation_protocol": BIAS_PROTOCOL
    }
