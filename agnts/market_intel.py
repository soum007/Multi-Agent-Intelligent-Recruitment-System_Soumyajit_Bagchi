from __future__ import annotations
from typing import Dict, Any
import pandas as pd

def load_market(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

def summarize(df: pd.DataFrame, role: str, region: str, level: str) -> Dict[str, Any]:
    subset = df[(df['role']==role) & (df['region']==region) & (df['level']==level)]
    if subset.empty:
        return {"error":"No market data for selection."}
    row = subset.iloc[0].to_dict()
    rec_channels = sorted(df[df['role']==role]['channel_hint'].value_counts().index[:3].tolist())
    return {
        "role": role, "region": region, "level": level,
        "compensation_LPA": {
            "p25": row["p25_LPA"],
            "median": row["median_LPA"],
            "p75": row["p75_LPA"]
        },
        "trend_yoy_pct": row["trend_yoy_pct"],
        "recommended_channels": rec_channels
    }
