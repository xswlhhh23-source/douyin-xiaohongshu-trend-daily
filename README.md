# Social Content Trend & Idea Tracker

A practical content-research workspace for tracking public Douyin and Xiaohongshu posts, comparing content performance, identifying recurring creative patterns, and turning observations into an actionable idea backlog.

> **MVP 1.0** — CSV/manual-input workflow with transparent metrics. It does not scrape platforms, bypass logins, or claim to provide live trend feeds. You supply links and observations from content you are allowed to review.

## Features

- Import a CSV of public-post observations or enter a post manually.
- Track platform, niche, post date, creator, post URL, hook, format, topic, and content notes.
- Compare views, likes, comments, shares, and saves.
- Calculate engagement rate and a transparent relative trend score.
- Filter by platform, niche, and date.
- Build a daily digest and a content-idea backlog.
- Export filtered research and the digest as CSV/Markdown.

## Run locally

```bash
git clone https://github.com/xswlhhh23-source/douyin-xiaohongshu-trend-daily.git
cd douyin-xiaohongshu-trend-daily
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## CSV format

Required columns: `platform, post_date, title, niche, views, likes, comments, shares, saves`.

Optional columns: `creator, url, hook, format, topic, notes`.

A fictional example dataset is included at `data/sample_posts.csv`. It is synthetic and must not be described as actual platform trend data.

## Metric definitions

- Engagement rate = (likes + comments + shares + saves) / views × 100.
- Save/share rate = (saves + shares) / views × 100.
- Relative trend score = a weighted percentile score within the currently filtered dataset: views 45%, engagement rate 35%, save/share rate 20%.

Scores are useful for prioritizing items inside the same dataset only. They are not comparable across accounts, niches, time windows, or platforms without normalization and context. A high score does not prove a post is organically viral.

## Responsible research

- Record only publicly accessible information you are permitted to use.
- Respect platform terms, creators' rights, and privacy.
- Do not copy full creator scripts or republish their work. Record short observations and create original adaptations.
- Metrics can be incomplete, self-reported, or time-sensitive. Add capture date and source URL when possible.
- This project does not automatically collect platform data.

## Project structure

```text
├── app.py
├── src/analytics.py
├── data/sample_posts.csv
├── prompts/content_idea_prompt.md
├── docs/metric_definitions.md
├── tests/test_analytics.py
└── requirements.txt
```

## Author

Personal portfolio project by **Xudong Sun**. Demonstrates content research, social media operations, structured observation, and data-informed creative planning.


## Deploy a public demo (Streamlit Community Cloud)

1. Sign in at https://share.streamlit.io/ with GitHub.
2. Connect/authorize your GitHub account if prompted.
3. Select **Create app**.
4. Choose repository `xswlhhh23-source/douyin-xiaohongshu-trend-daily`, branch `main`, and entrypoint file `app.py`.
5. Choose an available subdomain and click **Deploy**.

The app has no API keys or secrets. After deployment, commits to the connected GitHub branch are reflected in the app. See the [official deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).
