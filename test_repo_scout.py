"""Tests for repo_scout pure logic. Run: python3 -m unittest test_repo_scout -v"""

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

import repo_scout


def make_repo(**overrides):
    repo = {
        "full_name": "owner/tool",
        "url": "https://github.com/owner/tool",
        "description": "A useful tool",
        "topics": ["pdf"],
        "language": "Python",
        "stars": 1234,
        "pushed_at": "2026-06-01T00:00:00Z",
        "profile_id": "pdf-extraction",
        "profile_goal": "Better PDF extraction",
    }
    repo.update(overrides)
    return repo


class TestLoadEnv(unittest.TestCase):
    def test_parses_basic_and_ignores_comments(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / ".env"
            p.write_text('A=1\n# comment\nB="quoted"\nbroken line\nC = spaced \n',
                         encoding="utf-8")
            env = repo_scout.load_env(p)
        self.assertEqual(env, {"A": "1", "B": "quoted", "C": "spaced"})

    def test_missing_file_returns_empty(self):
        self.assertEqual(repo_scout.load_env(Path("/nonexistent/.env")), {})


class TestIsSeen(unittest.TestCase):
    def test_recent_entry_is_seen(self):
        now = datetime.now(timezone.utc)
        state = {"o/r": {"seen_at": (now - timedelta(days=10)).isoformat(), "score": 5}}
        self.assertTrue(repo_scout.is_seen(state, "o/r", now))

    def test_old_entry_can_be_rescanned(self):
        now = datetime.now(timezone.utc)
        state = {"o/r": {"seen_at": (now - timedelta(days=200)).isoformat(), "score": 5}}
        self.assertFalse(repo_scout.is_seen(state, "o/r", now))

    def test_unknown_repo_not_seen(self):
        self.assertFalse(repo_scout.is_seen({}, "o/r", datetime.now(timezone.utc)))


class TestScoreRepo(unittest.TestCase):
    def _ollama_response(self, payload):
        resp = mock.Mock()
        resp.json.return_value = {"response": json.dumps(payload)}
        resp.raise_for_status.return_value = None
        return resp

    @mock.patch("repo_scout.requests.post")
    def test_valid_verdict_parsed_and_clamped(self, post):
        post.return_value = self._ollama_response(
            {"score": 15, "project": "ExampleBid", "reason": "Hyvä työkalu"})
        verdict = repo_scout.score_repo(make_repo(), "http://x", "m", "ctx")
        self.assertEqual(verdict["score"], 10)  # clamped
        self.assertEqual(verdict["project"], "ExampleBid")

    @mock.patch("repo_scout.requests.post")
    def test_urls_stripped_from_reason(self, post):
        post.return_value = self._ollama_response(
            {"score": 8, "project": "X", "reason": "Katso https://evil.example/phish nyt"})
        verdict = repo_scout.score_repo(make_repo(), "http://x", "m", "ctx")
        self.assertNotIn("evil.example", verdict["reason"])
        self.assertIn("[url poistettu]", verdict["reason"])

    @mock.patch("repo_scout.requests.post")
    def test_invalid_json_returns_none(self, post):
        resp = mock.Mock()
        resp.json.return_value = {"response": "not json"}
        resp.raise_for_status.return_value = None
        post.return_value = resp
        self.assertIsNone(repo_scout.score_repo(make_repo(), "http://x", "m", "ctx"))

    @mock.patch("repo_scout.requests.post",
                side_effect=repo_scout.requests.ConnectionError("boom"))
    def test_network_error_returns_none(self, _post):
        self.assertIsNone(repo_scout.score_repo(make_repo(), "http://x", "m", "ctx"))


class TestBuildReport(unittest.TestCase):
    def test_escapes_html_in_fields(self):
        find = {**make_repo(description="<b>bold</b> & stuff", language="C++"),
                "verdict": {"score": 8, "project": "<X>", "reason": "syy <i>"}}
        report = repo_scout.build_report([find], scanned=3)
        self.assertIn("&lt;b&gt;bold&lt;/b&gt; &amp; stuff", report)
        self.assertIn("&lt;X&gt;", report)
        self.assertNotIn("<i>", report)
        self.assertIn("owner/tool", report)


class TestSendTelegramRedaction(unittest.TestCase):
    @mock.patch("repo_scout.requests.post",
                side_effect=repo_scout.requests.ConnectionError(
                    "url: /botSECRET123/sendMessage"))
    def test_token_redacted_in_error_log(self, _post):
        with self.assertLogs("repo_scout", level="ERROR") as captured:
            ok = repo_scout.send_telegram("SECRET123", "42", "hello")
        self.assertFalse(ok)
        joined = "\n".join(captured.output)
        self.assertNotIn("SECRET123", joined)
        self.assertIn("***", joined)


if __name__ == "__main__":
    unittest.main()
