from datetime import date

import pandas as pd
import streamlit as st

from src.analytics import REQUIRED_COLUMNS, add_metrics, build_daily_digest, build_idea_prompt, load_posts

st.set_page_config(page_title="Social Content Trend Tracker", page_icon="📈", layout="wide")
st.title("📈 Social Content Trend & Idea Tracker")
st.caption("A structured research desk for public Douyin and Xiaohongshu content observations.")
st.info("This MVP does not scrape platforms or fetch live trends. Import observations you have collected manually from public content you are allowed to review.")

uploaded = st.file_uploader("Upload research CSV", type=["csv"])
try:
    raw = pd.read_csv(uploaded) if uploaded is not None else pd.read_csv("data/sample_posts.csv")
    data, errors = load_posts(raw)
except Exception as exc:
    st.error(f"Could not read the dataset: {exc}")
    st.stop()

if errors:
    st.error("CSV validation issues: " + "; ".join(errors))
    st.stop()

with st.expander("Add a post observation manually"):
    with st.form("manual_post"):
        c1, c2 = st.columns(2)
        platform = c1.selectbox("Platform", ["Xiaohongshu", "Douyin"])
        post_date = c2.date_input("Post date", value=date.today())
        title = st.text_input("Post title")
        niche = st.text_input("Niche / audience", placeholder="e.g. student lifestyle")
        hook = st.text_input("Opening hook")
        fmt = st.selectbox("Format", ["Tutorial", "Talking-head", "Vlog", "Carousel", "Review", "Other"])
        c1, c2, c3 = st.columns(3)
        views = c1.number_input("Views", min_value=0, step=100)
        likes = c2.number_input("Likes", min_value=0, step=10)
        comments = c3.number_input("Comments", min_value=0, step=1)
        c1, c2 = st.columns(2)
        shares = c1.number_input("Shares", min_value=0, step=1)
        saves = c2.number_input("Saves", min_value=0, step=1)
        url = st.text_input("Public post URL (optional)")
        notes = st.text_area("What is worth learning from this post?")
        submitted = st.form_submit_button("Add observation")
        if submitted:
            new_row = pd.DataFrame([{
                "platform": platform, "post_date": str(post_date), "title": title,
                "niche": niche, "views": views, "likes": likes, "comments": comments,
                "shares": shares, "saves": saves, "creator": "", "url": url,
                "hook": hook, "format": fmt, "topic": niche, "notes": notes,
            }])
            raw = pd.concat([raw, new_row], ignore_index=True)
            data, errors = load_posts(raw)
            if errors:
                st.error("; ".join(errors))
            else:
                st.success("Observation added to this session. Export the data to keep it.")

if data.empty:
    st.warning("No valid observations yet. Upload a CSV or add a post above.")
    st.stop()

metrics = add_metrics(data)
st.sidebar.header("Filters")
platforms = st.sidebar.multiselect("Platform", sorted(metrics["platform"].dropna().unique()), default=sorted(metrics["platform"].dropna().unique()))
niches = st.sidebar.multiselect("Niche", sorted(metrics["niche"].dropna().unique()), default=sorted(metrics["niche"].dropna().unique()))
filtered = metrics[metrics["platform"].isin(platforms) & metrics["niche"].isin(niches)].copy()

if filtered.empty:
    st.warning("No posts match the selected filters.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Posts tracked", len(filtered))
c2.metric("Total views", f"{int(filtered['views'].sum()):,}")
c3.metric("Average engagement", f"{filtered['engagement_rate'].mean():.2f}%")
c4.metric("Average save/share", f"{filtered['save_share_rate'].mean():.2f}%")

st.subheader("Posts to review")
display_cols = ["platform", "post_date", "title", "niche", "views", "likes", "comments", "shares", "saves", "engagement_rate", "trend_score", "url"]
st.dataframe(filtered.sort_values("trend_score", ascending=False)[display_cols], use_container_width=True, hide_index=True)

left, right = st.columns(2)
with left:
    st.subheader("Views by post")
    st.bar_chart(filtered.set_index("title")["views"])
with right:
    st.subheader("Engagement rate by format")
    by_format = filtered.groupby("format", dropna=False)["engagement_rate"].mean().sort_values(ascending=False)
    st.bar_chart(by_format)

digest = build_daily_digest(filtered)
st.subheader("Daily research digest")
st.text_area("Digest preview", digest, height=240)
st.download_button("Download digest (.md)", digest, file_name="daily-content-research-digest.md", mime="text/markdown")
st.download_button("Download filtered observations (.csv)", filtered.to_csv(index=False), file_name="content-observations.csv", mime="text/csv")

selected_title = st.selectbox("Choose a post to turn into an original content idea", filtered["title"].tolist())
selected = filtered[filtered["title"] == selected_title].iloc[0].to_dict()
st.subheader("Original idea brief")
st.text_area("Prompt for an AI writing assistant", build_idea_prompt(selected), height=220)
st.caption("Use the selected post as a learning reference only. Create a new angle, script, and visual execution; do not copy the creator's wording or footage.")
