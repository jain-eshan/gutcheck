"""Contract tests for the plain-REST tools (company_registration, reddit_signal,
builder_activity, news_coverage, app_store_apps, youtube_videos) and the key
lookup they share.

Almost everything here fakes requests.get/post with canned responses instead of
recording cassettes: the parsing and fallback logic is what can regress, and the
live endpoints (Reddit's feed especially) rate-limit hard enough that recording
them is flaky. The one cassette left covers OpenCorporates' real 401 body."""
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from types import SimpleNamespace

import pytest
import requests

import server

KEY_NAMES = ("OPENCORPORATES_API_TOKEN", "YOUTUBE_API_KEY", "REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "GITHUB_TOKEN")


@pytest.fixture(autouse=True)
def isolated_keys(monkeypatch, tmp_path):
    """Keys on the machine running the tests (env vars or a real
    ~/.config/gutcheck/.env) must not change which code path runs. CONFIG_DIR is
    resolved from GUTCHECK_HOME at import time, so patch the resolved value too."""
    for name in KEY_NAMES:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("GUTCHECK_HOME", str(tmp_path))
    monkeypatch.setattr(server, "CONFIG_DIR", str(tmp_path))
    return tmp_path


class FakeResponse:
    def __init__(self, url, status_code=200, content=b"", json_data=None, headers=None):
        self.url = url
        self.status_code = status_code
        self.content = content
        self.headers = headers or {}
        self._json = json_data

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(
                f"{self.status_code} error", response=self, request=SimpleNamespace(url=self.url)
            )


def no_network(*args, **kwargs):
    raise AssertionError("this code path should not make a request")


# --- get_key ---------------------------------------------------------------


def test_get_key_env_beats_file(monkeypatch, isolated_keys):
    (isolated_keys / ".env").write_text("YOUTUBE_API_KEY=from-file\n")
    monkeypatch.setenv("YOUTUBE_API_KEY", "from-env")
    assert server.get_key("YOUTUBE_API_KEY") == "from-env"


def test_get_key_file_parsing_handles_quotes_and_blank_lines(isolated_keys):
    """/gutcheck setup writes this file, but users hand-edit it too - quoted
    values, blank lines, and empty assignments all show up in practice."""
    (isolated_keys / ".env").write_text(
        '\nGITHUB_TOKEN="ghp_quoted"\n\nREDDIT_CLIENT_ID=\'single\'\n  YOUTUBE_API_KEY = spaced  \nOPENCORPORATES_API_TOKEN=\n'
    )
    assert server.get_key("GITHUB_TOKEN") == "ghp_quoted"
    assert server.get_key("REDDIT_CLIENT_ID") == "single"
    assert server.get_key("YOUTUBE_API_KEY") == "spaced"
    assert server.get_key("OPENCORPORATES_API_TOKEN") is None
    assert server.get_key("REDDIT_CLIENT_SECRET") is None


def test_get_key_missing_file_returns_none():
    assert server.get_key("YOUTUBE_API_KEY") is None


# --- missing-key setup messages -------------------------------------------


def test_company_registration_missing_token_returns_setup_instructions(monkeypatch):
    monkeypatch.setattr(server.requests, "get", no_network)
    result = server.company_registration("Stripe")
    assert isinstance(result, str)
    assert "opencorporates.com/api_accounts/new" in result
    assert "/gutcheck setup" in result


@pytest.mark.vcr
def test_company_registration_invalid_token_returns_clean_message(monkeypatch):
    monkeypatch.setenv("OPENCORPORATES_API_TOKEN", "obviously-fake-token")
    result = server.company_registration("Stripe")
    assert isinstance(result, str)
    assert "rejected" in result.lower()


def test_youtube_videos_missing_key_returns_setup_instructions(monkeypatch):
    monkeypatch.setattr(server.requests, "get", no_network)
    result = server.youtube_videos("coffee")
    assert isinstance(result, str)
    assert "/gutcheck setup" in result


# --- reddit_signal (keyless RSS) -------------------------------------------

REDDIT_FEED = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>r/habittracking</title>
    <link href="https://www.reddit.com/r/habittracking/"/>
  </entry>
  <entry>
    <category term="productivity" label="r/productivity"/>
    <title>Every habit app nags me</title>
    <link href="https://www.reddit.com/r/productivity/comments/abc/every_habit_app/"/>
    <content type="html">&lt;div&gt;&lt;p&gt;Tried five apps &amp;amp;   quit all of them.&lt;/p&gt;&lt;/div&gt;</content>
    <published>2026-08-01T12:34:56+00:00</published>
  </entry>
</feed>"""


def test_reddit_signal_keyless_parses_rss_and_skips_subreddit_entries(monkeypatch):
    """Reddit's search feed mixes subreddit matches (no <category>) in with posts;
    only posts belong in the result."""
    calls = []

    def fake_get(url, **kwargs):
        calls.append(url)
        return FakeResponse(url, content=REDDIT_FEED)

    monkeypatch.setattr(server.requests, "get", fake_get)
    monkeypatch.setattr(server.requests, "post", no_network)
    result = server.reddit_signal("habit tracker")
    assert calls == ["https://www.reddit.com/search.rss"]
    assert result == [
        {
            "title": "Every habit app nags me",
            "subreddit": "productivity",
            "snippet": "Tried five apps & quit all of them.",
            "url": "https://www.reddit.com/r/productivity/comments/abc/every_habit_app/",
            "created": "2026-08-01",
        }
    ]


def test_reddit_signal_waits_out_one_429_then_retries(monkeypatch):
    responses = [
        FakeResponse("https://www.reddit.com/search.rss", status_code=429, headers={"x-ratelimit-reset": "5"}),
        FakeResponse("https://www.reddit.com/search.rss", content=REDDIT_FEED),
    ]
    sleeps = []
    monkeypatch.setattr(server.requests, "get", lambda url, **kwargs: responses.pop(0))
    monkeypatch.setattr(server.time, "sleep", sleeps.append)
    result = server.reddit_signal("habit tracker")
    assert sleeps == [6]
    assert responses == []
    assert [r["subreddit"] for r in result] == ["productivity"]


# --- builder_activity ------------------------------------------------------


def test_builder_activity_shape(monkeypatch):
    def fake_get(url, **kwargs):
        if "hn.algolia.com" in url:
            return FakeResponse(url, json_data={
                "nbHits": 42,
                "hits": [
                    {"title": "Show HN: Habitly", "points": 120, "num_comments": 30,
                     "url": "https://habitly.app", "created_at": "2026-07-01T10:00:00Z", "objectID": "1"},
                    {"title": "Ask HN: habit apps?", "points": 5, "num_comments": 2,
                     "url": None, "created_at": "2026-06-01T10:00:00Z", "objectID": "999"},
                ],
            })
        return FakeResponse(url, json_data={
            "total_count": 7,
            "items": [{"full_name": "me/habits", "description": None, "stargazers_count": 300,
                       "pushed_at": "2026-09-01T00:00:00Z", "html_url": "https://github.com/me/habits"}],
        })

    monkeypatch.setattr(server.requests, "get", fake_get)
    result = server.builder_activity("habit tracker")
    assert set(result) == {"hn", "github"}
    assert result["hn"]["total"] == 42
    assert result["hn"]["stories"][0] == {
        "title": "Show HN: Habitly", "points": 120, "num_comments": 30,
        "url": "https://habitly.app", "created_at": "2026-07-01",
    }
    # Ask HN posts have no external url - fall back to the HN thread itself.
    assert result["hn"]["stories"][1]["url"] == "https://news.ycombinator.com/item?id=999"
    assert result["github"] == {
        "total": 7,
        "repos": [{"name": "me/habits", "description": "", "stars": 300,
                   "last_push": "2026-09-01", "url": "https://github.com/me/habits"}],
    }


# --- news_coverage ---------------------------------------------------------


def _news_item(title, published):
    pub = f"<pubDate>{format_datetime(published)}</pubDate>" if published else ""
    return (
        f"<item><title>{title}</title><link>https://news.example/{title}</link>"
        f"<source url=\"https://pub.example\">Pub</source>{pub}</item>"
    )


def test_news_coverage_counts_recent_and_sorts_newest_first(monkeypatch):
    now = datetime.now(timezone.utc)
    feed = (
        "<rss><channel>"
        + _news_item("old", now - timedelta(days=90))
        + _news_item("newest", now - timedelta(days=1))
        + _news_item("undated", None)
        + _news_item("recent", now - timedelta(days=10))
        + "</channel></rss>"
    ).encode()
    monkeypatch.setattr(server.requests, "get", lambda url, **kwargs: FakeResponse(url, content=feed))
    result = server.news_coverage("habit tracker", limit=2)
    assert set(result) == {"total", "last_30_days", "headlines"}
    assert result["total"] == 3  # the undated item is dropped, and limit doesn't shrink the count
    assert result["last_30_days"] == 2
    assert [h["title"] for h in result["headlines"]] == ["newest", "recent"]
    assert result["headlines"][0] == {
        "title": "newest",
        "source": "Pub",
        "published": (now - timedelta(days=1)).date().isoformat(),
        "url": "https://news.example/newest",
    }


# --- app_store_apps --------------------------------------------------------


def test_app_store_apps_field_mapping(monkeypatch):
    seen = {}

    def fake_get(url, params=None, **kwargs):
        seen.update(params)
        return FakeResponse(url, json_data={"results": [
            {"trackName": "Habitly", "sellerName": "Habitly Inc", "averageUserRating": 4.678,
             "userRatingCount": 1234, "formattedPrice": "Free", "primaryGenreName": "Productivity",
             "releaseDate": "2020-01-02T08:00:00Z", "currentVersionReleaseDate": "2026-08-03T07:00:00Z",
             "trackViewUrl": "https://apps.apple.com/app/id1"},
            {"trackName": "Unrated"},
        ]})

    monkeypatch.setattr(server.requests, "get", fake_get)
    result = server.app_store_apps("habit tracker", country="IN", limit=999)
    assert seen["country"] == "in" and seen["limit"] == 50
    assert result[0] == {
        "name": "Habitly", "developer": "Habitly Inc", "rating": 4.7, "rating_count": 1234,
        "price": "Free", "genre": "Productivity", "released": "2020-01-02",
        "last_updated": "2026-08-03", "url": "https://apps.apple.com/app/id1",
    }
    assert result[1]["rating"] is None and result[1]["released"] == ""


# --- handle_http_errors ----------------------------------------------------


def test_http_429_returns_rate_limited_message(monkeypatch):
    monkeypatch.setattr(
        server.requests, "get", lambda url, **kwargs: FakeResponse("https://itunes.apple.com/search", status_code=429)
    )
    result = server.app_store_apps("habit tracker")
    assert isinstance(result, str)
    assert result.startswith("Rate-limited or blocked (429) by itunes.apple.com")


def _rss(entries):
    """Minimal Reddit search feed. Each entry is (title, subreddit, body)."""
    items = "".join(
        f"""<entry><title>{t}</title><category term="{sub}"/>
        <content type="html">&lt;div&gt;{body}&lt;/div&gt;</content>
        <link href="https://www.reddit.com/r/{sub}/comments/x/"/>
        <published>2026-08-25T05:38:51+00:00</published></entry>"""
        for t, sub, body in entries
    )
    return f'<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom">{items}</feed>'.encode()


def test_reddit_drops_results_sharing_no_query_word(monkeypatch):
    """Reddit's keyless search matches loosely, so a long question comes back with
    posts that happen to share a common word - live-observed: a Destiny 2 patch
    thread for "rust vs go which should I learn". Those must not reach a report as
    community signal."""
    feed = _rss([
        ("Why choose Go over Rust today?", "golang", "both are fast"),
        ("This Week In Destiny", "DestinyTheGame", "Monument of Triumph update"),
        ("Tips for a smoother league start", "PathOfExileBuilds", "stuff I learnt"),
    ])
    monkeypatch.setattr(server.requests, "get", lambda url, **kwargs: FakeResponse(url, content=feed))
    titles = [r["title"] for r in server.reddit_signal("rust or go")]
    assert titles == ["Why choose Go over Rust today?"]


def test_reddit_ranks_by_how_many_query_words_match(monkeypatch):
    feed = _rss([
        ("Meal ideas", "cooking", "nothing much"),
        ("Simple meal prep app wanted", "mealprep", "every app is bloated"),
    ])
    monkeypatch.setattr(server.requests, "get", lambda url, **kwargs: FakeResponse(url, content=feed))
    titles = [r["title"] for r in server.reddit_signal("meal prep app")]
    assert titles == ["Simple meal prep app wanted", "Meal ideas"]


def test_relevance_matches_whole_words_only():
    """"I learnt" must not count as a match for "learn", or near-miss posts survive
    the filter and get quoted as evidence."""
    assert server._relevance("learn rust", "stuff I learnt in poe") == 0
    assert server._relevance("learn rust", "how I learn rust") == 2


def test_call_tool_runs_a_tool_from_the_terminal(monkeypatch, capsys):
    """`server.py call <tool>` is what lets /gutcheck setup demo a real check in the
    session where someone just installed gutcheck, before Claude Code has loaded the
    MCP tools."""
    monkeypatch.setattr(server, "app_store_apps", lambda **kw: [{"name": "Mealime", **kw}])
    server.call_tool("app_store_apps", {"query": "meal prep", "limit": 1})
    assert '"name": "Mealime"' in capsys.readouterr().out


def test_call_tool_rejects_an_unknown_tool_with_the_list():
    with pytest.raises(SystemExit) as excinfo:
        server.call_tool("definitely_not_a_tool", {})
    assert "reddit_signal" in str(excinfo.value)
