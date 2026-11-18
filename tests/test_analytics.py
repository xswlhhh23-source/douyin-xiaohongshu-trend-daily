import unittest
import pandas as pd

from src.analytics import add_metrics, load_posts, build_daily_digest, build_idea_prompt


class TrendAnalyticsTests(unittest.TestCase):
    def sample(self):
        return pd.DataFrame([{
            "platform": "Douyin", "post_date": "2026-11-10", "title": "Demo post",
            "niche": "education", "views": 1000, "likes": 100, "comments": 10,
            "shares": 20, "saves": 30,
        }])

    def test_load_posts_requires_columns(self):
        data, errors = load_posts(pd.DataFrame({"title": ["x"]}))
        self.assertTrue(errors)
        self.assertTrue(data.empty)

    def test_metrics_are_calculated(self):
        data, errors = load_posts(self.sample())
        self.assertFalse(errors)
        result = add_metrics(data)
        self.assertAlmostEqual(result.iloc[0]["engagement_rate"], 16.0)
        self.assertAlmostEqual(result.iloc[0]["save_share_rate"], 5.0)

    def test_digest_and_prompt(self):
        data, _ = load_posts(self.sample())
        result = add_metrics(data)
        self.assertIn("Daily Content Research Digest", build_daily_digest(result))
        self.assertIn("Do not copy", build_idea_prompt(result.iloc[0].to_dict()))


if __name__ == "__main__":
    unittest.main()
