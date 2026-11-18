"""Metrics and reporting for manually collected public content observations."""

from typing import Tuple
import pandas as pd

REQUIRED_COLUMNS = [
    "platform", "post_date", "title", "niche",
    "views", "likes", "comments", "shares", "saves",
]
OPTIONAL_COLUMNS = ["creator", "url", "hook", "format", "topic", "notes"]
NUMERIC_COLUMNS = ["views", "likes", "comments", "shares", "saves"]


def load_posts(frame: pd.DataFrame) -> Tuple[pd.DataFrame, list]:
    """Validate and normalize a post-observation dataframe."""
    missing = [col for col in REQUIRED_COLUMNS if col not in frame.columns]
    if missing:
        return pd.DataFrame(), [f"Missing required columns: {', '.join(missing)}"]

    data = frame.copy()
    for col in OPTIONAL_COLUMNS:
        if col not in data.columns:
            data[col] = ""

    data["platform"] = data["platform"].fillna("").astype(str).str.strip()
    data["title"] = data["title"].fillna("").astype(str).str.strip()
    data["niche"] = data["niche"].fillna("Uncategorized").astype(str).str.strip()
    data["post_date"] = pd.to_datetime(data["post_date"], errors="coerce")
    for col in NUMERIC_COLUMNS:
        data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0).clip(lower=0)

    errors = []
    if data["post_date"].isna().any():
        errors.append("Some post_date values could not be parsed; correct them using YYYY-MM-DD.")
    if (data["title"] == "").any():
        errors.append("Post title cannot be blank.")
    if (data["platform"] == "").any():
        errors.append("Platform cannot be blank.")
    if errors:
        return pd.DataFrame(), errors

    data["post_date"] = data["post_date"].dt.strftime("%Y-%m-%d")
    return data, []


def _percentile(series: pd.Series) -> pd.Series:
    if len(series) <= 1:
        return pd.Series([100.0] * len(series), index=series.index)
    return series.rank(pct=True, method="average") * 100


def add_metrics(data: pd.DataFrame) -> pd.DataFrame:
    """Add engagement and within-dataset relative trend metrics."""
    result = data.copy()
    denominator = result["views"].replace(0, pd.NA)
    interactions = result["likes"] + result["comments"] + result["shares"] + result["saves"]
    result["engagement_rate"] = (interactions / denominator * 100).fillna(0)
    result["save_share_rate"] = ((result["saves"] + result["shares"]) / denominator * 100).fillna(0)
    score = (
        _percentile(result["views"]) * 0.45
        + _percentile(result["engagement_rate"]) * 0.35
        + _percentile(result["save_share_rate"]) * 0.20
    )
    result["trend_score"] = score.round(1)
    return result


def build_daily_digest(data: pd.DataFrame) -> str:
    if data.empty:
        return "# Daily Content Research Digest\n\nNo observations available."
    ranked = data.sort_values("trend_score", ascending=False).head(5)
    lines = [
        "# Daily Content Research Digest",
        "",
        f"Posts reviewed: {len(data)}",
        f"Platforms: {', '.join(sorted(data['platform'].unique()))}",
        "",
        "## Posts to review",
    ]
    for _, row in ranked.iterrows():
        lines.append(
            f"- **{row['title']}** ({row['platform']}, {row['niche']}) — "
            f"{int(row['views']):,} views; engagement {row['engagement_rate']:.2f}%; "
            f"trend score {row['trend_score']:.1f}/100"
        )
        if str(row.get("hook", "")).strip():
            lines.append(f"  - Hook observation: {row['hook']}")
        if str(row.get("notes", "")).strip():
            lines.append(f"  - Research note: {row['notes']}")
    lines.extend([
        "",
        "## Research reminder",
        "Scores are relative to this filtered dataset. Validate context, post age, account size, and platform differences before drawing conclusions.",
    ])
    return "\n".join(lines)


def build_idea_prompt(row: dict) -> str:
    return f"""Act as a short-form content strategist. Use this post only as a reference for audience need and broad creative structure. Do not copy its wording, footage, or distinctive expression.

Reference observation:
- Platform: {row.get('platform', '')}
- Topic/niche: {row.get('topic', row.get('niche', ''))}
- Title: {row.get('title', '')}
- Opening hook: {row.get('hook', '')}
- Format: {row.get('format', '')}
- Research notes: {row.get('notes', '')}

Create 3 original content concepts for the same broad audience:
1. Audience pain point and insight
2. New angle that makes the concept distinct
3. Original 3-second hook
4. Suggested structure (opening, value, ending)
5. Visual shots or scenes
6. A save/share reason and a non-pushy call to action

Avoid unverified trend claims. Clearly label assumptions.
"""
