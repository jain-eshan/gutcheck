import functools
import html
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import quote
from xml.etree import ElementTree

import requests
from google_play_scraper import Sort, reviews as gp_reviews, search as gp_search
from mcp.server.fastmcp import FastMCP
from pytrends.request import TrendReq

mcp = FastMCP("gutcheck")

# Lazy singleton - TrendReq()'s constructor makes a real network call (fetching a
# Google cookie) on instantiation. Eagerly constructing it at import time means
# every test run (and every MCP server boot) makes an uncounted, unrecordable
# network call before any test/tool even runs - the exact flakiness issue #8's
# recorded-fixture testing is meant to eliminate. Deferring construction to first
# use means that call happens inside whichever test's cassette scope needs it.
_pytrends = None


def get_pytrends():
    global _pytrends
    if _pytrends is None:
        _pytrends = TrendReq(hl="en-US", tz=0)
    return _pytrends

RESPONSE_FORMATS = ("concise", "full")

# Wikimedia requires a descriptive User-Agent identifying the app and a contact
# URL, or it returns 403 - https://meta.wikimedia.org/wiki/User-Agent_policy
USER_AGENT = "gutcheck/1.0 (https://github.com/jain-eshan/gutcheck)"
WIKI_USER_AGENT = USER_AGENT

# Optional API keys live in one file the /gutcheck setup flow writes, so users
# never have to export env vars before launching their editor. Read on every
# call (it's tiny) so a key saved mid-session works without a restart.
CONFIG_DIR = os.path.expanduser(os.environ.get("GUTCHECK_HOME", "~/.config/gutcheck"))


def get_key(name: str) -> str | None:
    """An API key from the environment, else from CONFIG_DIR/.env (KEY=value lines)."""
    if os.environ.get(name):
        return os.environ[name]
    try:
        with open(os.path.join(CONFIG_DIR, ".env")) as f:
            for line in f:
                k, sep, v = line.strip().partition("=")
                if sep and k.strip() == name and v.strip():
                    return v.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return None


def handle_trends_errors(func):
    """Catch pytrends/network failures and return them as a plain error string
    instead of crashing the server (Google Trends is a scraped, rate-limited endpoint)."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return f"Google Trends request failed: {e}"
    return wrapper


def df_to_records(df):
    """Convert a pytrends DataFrame (or None) to plain JSON-safe records. Only
    folds the index into the output when it's meaningfully named (e.g. "date",
    "geoName") — related_queries' DataFrame carries a bare ranking index with
    no name, and unconditionally reset_index()-ing it leaks a stray "index"
    field into the API contract (caught by test_related_queries_shape_and_truncation
    once that test asserted an exact key set instead of just membership)."""
    if df is None or df.empty:
        return []
    if df.index.name is not None:
        df = df.reset_index()
    return json.loads(df.to_json(orient="records", date_format="iso"))


CONCISE_TIMESERIES_POINTS = 26


def thin_timeseries(records, max_points=CONCISE_TIMESERIES_POINTS):
    """Evenly sample a time series down to max_points, always keeping the first and
    last record.

    Concise mode used to keep only the last 90 days, which quietly destroyed any
    longer request: asking for 5 years returned 13 weekly points with nothing saying
    the rest had been dropped, so a reader could conclude interest was zero until
    this year. Thinning instead of truncating keeps the real shape of the window that
    was actually asked for, at a similar token cost."""
    if len(records) <= max_points:
        return records
    step = (len(records) - 1) / (max_points - 1)
    picked = {round(i * step) for i in range(max_points)}
    picked.add(len(records) - 1)
    return [r for i, r in enumerate(records) if i in picked]


def apply_format(records, response_format, *, sort_key=None, limit=None, timeseries=False):
    """Shrink a list of dict records for response_format="concise". No-op for "full"
    or an empty/non-list input. timeseries thins a date-keyed series to a readable
    number of points spanning the whole window; sort_key + limit implement top-N
    truncation (used for ranked lists like related queries/topics/regions). Concise
    mode also rounds floats to whole numbers and drops isPartial when False (it's the
    common case - only worth stating when True)."""
    if response_format != "concise" or not records:
        return records
    if timeseries:
        records = thin_timeseries(records)
    if sort_key is not None:
        records = sorted(records, key=lambda r: r.get(sort_key) or 0, reverse=True)
    if limit is not None:
        records = records[:limit]
    for r in records:
        for k, v in list(r.items()):
            if isinstance(v, float):
                r[k] = round(v)
        if r.get("isPartial") is False:
            del r["isPartial"]
    return records


@mcp.tool()
@handle_trends_errors
def interest_over_time(
    keywords: list[str], timeframe: str = "today 12-m", geo: str = "", response_format: str = "concise"
) -> list:
    """Relative Google search interest (0-100) over time for up to 5 keywords, compared side by side.

    Args:
        keywords: 1-5 search terms to compare. Only the first 5 are used; additional keywords are silently dropped.
        timeframe: pytrends timeframe string, e.g. "today 12-m", "today 5-y", "now 7-d", or "YYYY-MM-DD YYYY-MM-DD".
        geo: ISO country code (e.g. "US", "IN", "GB"), or "" for worldwide (default).
        response_format: "concise" (default) covers the whole requested timeframe, thinned to
            about 26 evenly spaced points (first and last always kept) and rounded to whole
            numbers, so the shape of the window is intact at a low token cost. "full" returns
            every point unrounded - use it when you need week-by-week detail.

    Returns:
        A list of records, one per date, each containing:
        - "date": ISO date string
        - "isPartial": present and true only when the period is incomplete (most recent point) -
          omitted when false in "concise" mode, since false is the common case.
        - One numeric key per keyword (0-100 relative interest value)
    """
    get_pytrends().build_payload(keywords[:5], timeframe=timeframe, geo=geo)
    df = get_pytrends().interest_over_time()
    records = df_to_records(df)
    return apply_format(records, response_format, timeseries=True)


@mcp.tool()
@handle_trends_errors
def related_queries(
    keyword: str, timeframe: str = "today 12-m", geo: str = "", response_format: str = "concise"
) -> dict:
    """Top and rising related search queries for a single keyword.

    Args:
        keyword: a single search term.
        timeframe: pytrends timeframe string, e.g. "today 12-m".
        geo: ISO country code (e.g. "US", "IN"), or "" for worldwide (default).
        response_format: "concise" (default) returns only the top 10 of each list, sorted by
            "value" descending, rounded to whole numbers. "full" returns every row Google Trends
            provides (often 25), unrounded.

    Returns:
        A dict with two keys, each containing a list of query records:
        - "top": most-searched related queries. Each record has "query" and "value"
          (0-100 relative interest on Google Trends scale).
        - "rising": fastest-growing related queries. Each record has "query" and "value"
          (percent increase in search interest). IMPORTANT: a value of 5000% is Google's
          "Breakout" marker, indicating explosive new growth from near-zero baseline,
          NOT a literal 5000% increase. This is Google's way of saying the data cannot
          be assigned a meaningful numeric value.
    """
    get_pytrends().build_payload([keyword], timeframe=timeframe, geo=geo)
    # Patch pytrends to handle empty rankedList (IndexError when Google has no related queries data)
    try:
        result = get_pytrends().related_queries()[keyword]
    except IndexError:
        # Google Trends doesn't have related queries data for this keyword/geo combination
        result = {"top": None, "rising": None}
    return {
        "top": apply_format(df_to_records(result.get("top")), response_format, sort_key="value", limit=10),
        "rising": apply_format(df_to_records(result.get("rising")), response_format, sort_key="value", limit=10),
    }


@mcp.tool()
@handle_trends_errors
def related_topics(
    keyword: str, timeframe: str = "today 12-m", geo: str = "", response_format: str = "concise"
) -> dict:
    """Top and rising related topics (Google's topic clusters, not raw query strings) for a single keyword.

    Args:
        keyword: a single search term.
        timeframe: pytrends timeframe string, e.g. "today 12-m".
        geo: ISO country code (e.g. "US", "IN"), or "" for worldwide (default).
        response_format: "concise" (default) returns only the top 10 of each list, sorted by
            "value" descending, rounded to whole numbers. "full" returns every row, unrounded.

    Returns:
        A dict with two keys, each containing a list of topic records:
        - "top": most-searched related topics. Each record has "topic_title", "topic_type", "value"
          (0-100 relative interest on Google Trends scale).
        - "rising": fastest-growing related topics. Each record has "topic_title", "topic_type", "value".
          IMPORTANT: a value of 5000% is Google's "Breakout" marker, indicating explosive new growth
          from near-zero baseline, NOT a literal 5000% increase. This is the same convention as "rising"
          queries.
    """
    get_pytrends().build_payload([keyword], timeframe=timeframe, geo=geo)
    # Patch pytrends to handle empty rankedList (IndexError when Google has no related topics data)
    try:
        result = get_pytrends().related_topics()[keyword]
    except IndexError:
        # Google Trends doesn't have related topics data for this keyword/geo combination
        result = {"top": None, "rising": None}
    return {
        "top": apply_format(df_to_records(result.get("top")), response_format, sort_key="value", limit=10),
        "rising": apply_format(df_to_records(result.get("rising")), response_format, sort_key="value", limit=10),
    }


@mcp.tool()
@handle_trends_errors
def interest_by_region(
    keyword: str, timeframe: str = "today 12-m", geo: str = "", response_format: str = "concise"
) -> list:
    """Search interest for a keyword broken down by state/region within a country, or by
    country when geo is "" (worldwide).

    Args:
        keyword: a single search term.
        timeframe: pytrends timeframe string, e.g. "today 12-m".
        geo: ISO country code (e.g. "US", "IN"), or "" for worldwide (default).
        response_format: "concise" (default) returns only the top 10 regions by interest,
            rounded to whole numbers. "full" returns every region, unrounded.

    Returns:
        A list of records, one per state/region within the specified geo, each containing:
        - "geoName": the state/region name (e.g. "California"), or the country name when worldwide
        - A column with the keyword name as the key: relative search interest (0-100 scale) for that
          region. Higher values indicate higher relative interest in that region compared to others
          in the same country. This is Google Trends' standard region-relative scale.
    """
    get_pytrends().build_payload([keyword], timeframe=timeframe, geo=geo)
    # inc_low_vol=True includes regions Google would otherwise omit for low search volume
    # Google only accepts REGION inside a country; worldwide it has to be COUNTRY.
    df = get_pytrends().interest_by_region(resolution="REGION" if geo else "COUNTRY", inc_low_vol=True)
    records = df_to_records(df)
    return apply_format(records, response_format, sort_key=keyword, limit=10)


def handle_http_errors(func):
    """Catch HTTP/network failures (used by tools that call plain REST APIs, not
    pytrends) and return them as a plain error string instead of crashing."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.HTTPError as e:
            status = e.response.status_code if e.response is not None else None
            if status == 404:
                return f"Not found: {e.request.url}"
            if status in (403, 429):
                return (
                    f"Rate-limited or blocked ({status}) by {e.request.url.split('/')[2]}. Wait a minute and "
                    "try again. If it keeps happening, `/gutcheck setup` lists optional keys that raise limits."
                )
            return f"Request failed: {e}"
        except Exception as e:
            return f"Request failed: {e}"
    return wrapper


def _parse_duration_days(duration: str) -> int:
    """Parse a simple ISO-8601-style duration like "P1Y", "P6M", "P90D" into a day
    count. Only whole-number Y/M/D forms are supported (no weeks, no combined
    P1Y6M) - this tool only needs "roughly how far back", not a full ISO-8601
    duration parser."""
    match = re.fullmatch(r"P(\d+)([YMD])", duration.upper())
    if not match:
        raise ValueError(f'Unrecognized timeframe "{duration}" - expected a form like "P1Y", "P6M", or "P90D"')
    n, unit = int(match.group(1)), match.group(2)
    return {"Y": 365, "M": 30, "D": 1}[unit] * n


@mcp.tool()
@handle_http_errors
def wikipedia_pageviews(article: str, timeframe: str = "P1Y", response_format: str = "concise") -> list:
    """Monthly Wikipedia pageview counts for an article - a free, no-auth reference/reading
    interest signal that complements Google Trends' search-interest signal. The two diverging
    (e.g. a term trending in search but flat on Wikipedia) can itself be a signal worth flagging.

    Args:
        article: an English Wikipedia article title, e.g. "Artificial_intelligence" or
            "Machine learning" (spaces are handled automatically).
        timeframe: how far back to request, as a simple duration - "P1Y" (1 year, default),
            "P6M" (6 months), "P90D" (90 days). Only whole Y/M/D forms are supported.
        response_format: "concise" (default) returns only the most recent 12 months.
            "full" returns the entire requested timeframe.

    Returns:
        A list of records, one per month, each containing:
        - "month": "YYYY-MM"
        - "views": total pageviews that month (all access methods, human traffic only -
          bot traffic is excluded by Wikimedia's "user" agent filter)
    """
    days = _parse_duration_days(timeframe)
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=days)
    encoded_article = quote(article.strip().replace(" ", "_"), safe="")
    url = (
        "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
        f"en.wikipedia/all-access/user/{encoded_article}/monthly/"
        f"{start.strftime('%Y%m%d')}/{end.strftime('%Y%m%d')}"
    )
    resp = requests.get(url, headers={"User-Agent": WIKI_USER_AGENT}, timeout=15)
    resp.raise_for_status()
    items = resp.json().get("items", [])
    records = [{"month": f"{item['timestamp'][:4]}-{item['timestamp'][4:6]}", "views": item["views"]} for item in items]
    if response_format == "concise":
        records = records[-12:]
    return records


@mcp.tool()
@handle_http_errors
def company_registration(name: str, jurisdiction: str | None = None) -> list:
    """Company registration lookup via OpenCorporates - registration facts only
    (incorporation date, status, company number). Does NOT cover funding, valuation,
    or traction data - no free API exists for that (see README for why).

    Requires a free OpenCorporates API token: as of 2026 OpenCorporates requires a
    token on every request, even on the free tier (roughly 50 requests/day, 200/month).
    Register at https://opencorporates.com/api_accounts/new and save it as
    OPENCORPORATES_API_TOKEN via `/gutcheck setup`.

    Args:
        name: company name to search for.
        jurisdiction: optional OpenCorporates jurisdiction code (e.g. "in", "us_de") to narrow results.

    Returns:
        A list of up to 5 matches, each containing "company_name", "jurisdiction_code",
        "incorporation_date", "company_number", "current_status", "opencorporates_url".
        Empty list if no matches. A setup-instructions string if OPENCORPORATES_API_TOKEN
        is unset, or OpenCorporates' own rejection message if the token is invalid/expired.
    """
    token = get_key("OPENCORPORATES_API_TOKEN")
    if not token:
        return (
            "company_registration requires a free OpenCorporates API token. Register at "
            "https://opencorporates.com/api_accounts/new, then run `/gutcheck setup` "
            "to save it."
        )
    params = {"q": name, "api_token": token}
    if jurisdiction:
        params["jurisdiction_code"] = jurisdiction
    resp = requests.get("https://api.opencorporates.com/v0.4/companies/search", params=params, timeout=15)
    if resp.status_code == 401:
        message = resp.json().get("error", {}).get("message", "invalid token")
        return f"OpenCorporates rejected the API token: {message}"
    resp.raise_for_status()
    companies = resp.json().get("results", {}).get("companies", [])[:5]
    return [
        {
            "company_name": c.get("company", {}).get("name"),
            "jurisdiction_code": c.get("company", {}).get("jurisdiction_code"),
            "incorporation_date": c.get("company", {}).get("incorporation_date"),
            "company_number": c.get("company", {}).get("company_number"),
            "current_status": c.get("company", {}).get("current_status"),
            "opencorporates_url": c.get("company", {}).get("opencorporates_url"),
        }
        for c in companies
    ]


def _reddit_oauth_token(client_id: str, client_secret: str) -> str:
    """Reddit's app-only OAuth flow (client_credentials) - no user login needed,
    just the app's own id/secret."""
    resp = requests.post(
        "https://www.reddit.com/api/v1/access_token",
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
        headers={"User-Agent": USER_AGENT},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


_STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "what", "which", "should", "would",
    "have", "has", "are", "was", "were", "you", "your", "about", "into", "than", "then",
    "how", "why", "when", "does", "did", "can", "could", "there", "their", "them", "not",
    "any", "all", "get", "got", "just", "like", "one", "two", "vs", "versus", "best", "good",
}


def _relevance(query: str, text: str) -> int:
    """How many distinct meaningful query words appear in a result. Reddit's keyless
    search matches loosely, so a long natural-language query ("rust vs go which should
    I learn") comes back with unrelated posts that happen to share a common word.
    Scoring lets the caller drop the noise instead of quoting a Destiny 2 thread as
    community signal."""
    words = {w for w in re.findall(r"[a-z0-9]+", query.lower()) if len(w) > 2 and w not in _STOPWORDS}
    if not words:
        return 1
    found = set(re.findall(r"[a-z0-9]+", text.lower()))
    return len(words & found)


def _by_relevance(records: list, query: str) -> list:
    """Drop results matching no query word, then sort by how many they match.
    Ties keep the source's own ranking (Python's sort is stable)."""
    scored = [(r, _relevance(query, f"{r.get('title', '')} {r.get('snippet', '')}")) for r in records]
    keep = [(r, score) for r, score in scored if score > 0]
    return [r for r, _ in sorted(keep, key=lambda pair: pair[1], reverse=True)]


def _strip_html(text: str, limit: int = 300) -> str:
    text = re.sub(r"<[^>]+>", " ", html.unescape(text or ""))
    return re.sub(r"\s+", " ", text).strip()[:limit]


@mcp.tool()
@handle_http_errors
def reddit_signal(query: str, subreddits: list[str] | None = None, limit: int = 25, time_filter: str = "year") -> list:
    """What real people on Reddit are saying, asking, or complaining about - qualitative
    community signal, as opposed to Trends/Wikipedia's passive search/reading numbers.

    Works with no setup via Reddit's public search feed (which returns post text but not
    scores, and rate-limits after a burst of requests). If REDDIT_CLIENT_ID and
    REDDIT_CLIENT_SECRET are saved via `/gutcheck setup`, uses the official API instead,
    which adds score and comment counts.

    Args:
        query: search terms.
        subreddits: optional subreddit names to restrict the search to (e.g. ["startups", "SaaS"]).
        limit: max results, capped at 100.
        time_filter: "week", "month", "year" (default), or "all".

    Keep the query short (2-4 words) and pass `subreddits` when obvious communities exist.
    Reddit's keyless search matches loosely on long questions, so results that share no
    meaningful word with the query are dropped and the rest are ranked by how many query
    words they match.

    Returns:
        A list of records with "title", "subreddit", "snippet" (first ~300 chars of the post
        body), "url", "created". "score" and "num_comments" are included only in API mode.
    """
    limit = max(1, min(limit, 100))
    scope = "+".join(subreddits) if subreddits else "all"
    client_id, client_secret = get_key("REDDIT_CLIENT_ID"), get_key("REDDIT_CLIENT_SECRET")
    if client_id and client_secret:
        token = _reddit_oauth_token(client_id, client_secret)
        resp = requests.get(
            f"https://oauth.reddit.com/r/{scope}/search",
            params={"q": query, "sort": "relevance", "t": time_filter, "limit": limit, "restrict_sr": bool(subreddits)},
            headers={"Authorization": f"Bearer {token}", "User-Agent": USER_AGENT},
            timeout=15,
        )
        resp.raise_for_status()
        return _by_relevance([
            {
                "title": c["data"].get("title"),
                "subreddit": c["data"].get("subreddit"),
                "snippet": _strip_html(c["data"].get("selftext", "")),
                "score": c["data"].get("score"),
                "num_comments": c["data"].get("num_comments"),
                "url": f"https://reddit.com{c['data'].get('permalink', '')}",
                "created": datetime.fromtimestamp(c["data"].get("created_utc", 0), timezone.utc).date().isoformat(),
            }
            for c in resp.json().get("data", {}).get("children", [])
        ], query)

    base = f"https://www.reddit.com/r/{scope}/search.rss" if subreddits else "https://www.reddit.com/search.rss"
    params = {"q": query, "sort": "relevance", "t": time_filter, "limit": limit}
    if subreddits:
        params["restrict_sr"] = "on"
    resp = requests.get(base, params=params, headers={"User-Agent": USER_AGENT}, timeout=15)
    # The keyless feed allows ~1 search a minute and says when the window resets -
    # waiting it out once beats failing the source for the whole report.
    reset = resp.headers.get("x-ratelimit-reset", "")
    if resp.status_code == 429 and reset.isdigit() and int(reset) <= 60:
        time.sleep(int(reset) + 1)
        resp = requests.get(base, params=params, headers={"User-Agent": USER_AGENT}, timeout=15)
    resp.raise_for_status()
    atom = "{http://www.w3.org/2005/Atom}"
    records = []
    for entry in ElementTree.fromstring(resp.content).findall(f"{atom}entry"):
        category = entry.find(f"{atom}category")
        if category is None:  # subreddit matches, not posts
            continue
        link = entry.find(f"{atom}link")
        records.append({
            "title": entry.findtext(f"{atom}title"),
            "subreddit": category.get("term"),
            "snippet": _strip_html(entry.findtext(f"{atom}content", "")),
            "url": link.get("href") if link is not None else None,
            "created": (entry.findtext(f"{atom}published") or "")[:10],
        })
    return _by_relevance(records, query)


@mcp.tool()
@handle_http_errors
def builder_activity(query: str) -> dict:
    """Are people actually building and shipping in this space? Hacker News stories
    (launches, Show HNs, debates) plus GitHub repositories - a builder signal, as opposed
    to search interest or community chatter. Works with no setup; a GITHUB_TOKEN saved via
    `/gutcheck setup` raises GitHub's limit from 10 to 30 searches a minute.

    For Product Hunt launches, use web search restricted to producthunt.com instead -
    Product Hunt's API has no search endpoint.

    Args:
        query: search terms, e.g. a product category ("habit tracker") or problem.

    Returns:
        {"hn": {"total": int, "stories": [...]}, "github": {"total": int, "repos": [...]}}.
        Each story: title, points, num_comments, url, created_at.
        Each repo (top 10 by stars): name, description, stars, last_push, url.
    """
    hn_resp = requests.get("https://hn.algolia.com/api/v1/search", params={"query": query, "tags": "story"}, timeout=15)
    hn_resp.raise_for_status()
    hn = hn_resp.json()

    gh_headers = {"Accept": "application/vnd.github+json", "User-Agent": USER_AGENT}
    if get_key("GITHUB_TOKEN"):
        gh_headers["Authorization"] = f"Bearer {get_key('GITHUB_TOKEN')}"
    gh_resp = requests.get(
        "https://api.github.com/search/repositories",
        params={"q": query, "sort": "stars", "per_page": 10},
        headers=gh_headers,
        timeout=15,
    )
    gh_resp.raise_for_status()
    gh = gh_resp.json()

    return {
        "hn": {
            "total": hn.get("nbHits"),
            "stories": [
                {
                    "title": h.get("title"),
                    "points": h.get("points"),
                    "num_comments": h.get("num_comments"),
                    "url": h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}",
                    "created_at": (h.get("created_at") or "")[:10],
                }
                for h in hn.get("hits", [])[:10]
            ],
        },
        "github": {
            "total": gh.get("total_count"),
            "repos": [
                {
                    "name": r.get("full_name"),
                    "description": (r.get("description") or "")[:200],
                    "stars": r.get("stargazers_count"),
                    "last_push": (r.get("pushed_at") or "")[:10],
                    "url": r.get("html_url"),
                }
                for r in gh.get("items", [])
            ],
        },
    }


@mcp.tool()
@handle_http_errors
def news_coverage(query: str, geo: str = "US", recent: str = "1y", limit: int = 15) -> dict:
    """Recent news coverage from Google News - is the press writing about this, and what
    angle are they taking? Useful for spotting funding rounds, regulation, launches, and
    whether a topic is getting more or less attention. No setup needed.

    Args:
        query: search terms.
        geo: ISO country code for the news edition, e.g. "US" (default), "IN", "GB".
        recent: how far back - "7d", "1m", "1y" (default). Uses Google News' own `when:` filter.
        limit: max headlines to return (Google returns up to ~100; "total" counts all of them).

    Returns:
        {"total": int, "last_30_days": int, "headlines": [{"title", "source", "published", "url"}]},
        newest first. "total" and "last_30_days" are counts within Google's capped result set,
        so treat them as a rough attention gauge, not an exact article count.
    """
    geo = (geo or "US").upper()
    resp = requests.get(
        "https://news.google.com/rss/search",
        params={"q": f"{query} when:{recent}", "hl": "en", "gl": geo, "ceid": f"{geo}:en"},
        headers={"User-Agent": USER_AGENT},
        timeout=15,
    )
    resp.raise_for_status()
    items = []
    for item in ElementTree.fromstring(resp.content).findall("./channel/item"):
        try:
            published = parsedate_to_datetime(item.findtext("pubDate"))
        except (TypeError, ValueError):
            continue
        items.append({
            "title": item.findtext("title"),
            "source": item.findtext("source"),
            "published": published,
            "url": item.findtext("link"),
        })
    items.sort(key=lambda i: i["published"], reverse=True)
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    return {
        "total": len(items),
        "last_30_days": sum(1 for i in items if i["published"] >= cutoff),
        "headlines": [{**i, "published": i["published"].date().isoformat()} for i in items[:limit]],
    }


@mcp.tool()
@handle_http_errors
def app_store_apps(query: str, country: str = "US", limit: int = 10) -> list:
    """Existing iPhone/iPad apps matching a query, from Apple's public iTunes Search API -
    who already serves this need, and how many people rate them (rating count is a rough
    proxy for user base). No setup needed.

    Args:
        query: search terms, e.g. "meal planner" or "invoice".
        country: ISO country code for the store, e.g. "US" (default), "IN", "GB".
        limit: max apps, capped at 50.

    Returns:
        A list in App Store relevance order, each with "name", "developer", "rating",
        "rating_count", "price", "genre", "released", "last_updated", "url".
    """
    resp = requests.get(
        "https://itunes.apple.com/search",
        params={"term": query, "entity": "software", "country": (country or "US").lower(), "limit": max(1, min(limit, 50))},
        timeout=15,
    )
    resp.raise_for_status()
    return [
        {
            "name": a.get("trackName"),
            "developer": a.get("sellerName"),
            "rating": round(a["averageUserRating"], 1) if a.get("averageUserRating") else None,
            "rating_count": a.get("userRatingCount"),
            "price": a.get("formattedPrice"),
            "genre": a.get("primaryGenreName"),
            "released": (a.get("releaseDate") or "")[:10],
            "last_updated": (a.get("currentVersionReleaseDate") or "")[:10],
            "url": a.get("trackViewUrl"),
        }
        for a in resp.json().get("results", [])
    ]


@mcp.tool()
@handle_http_errors
def play_store_search(query: str, country: str = "IN", lang: str = "en", limit: int = 5) -> list:
    """Existing Android apps on Google Play matching a query - the Android counterpart to
    app_store_apps, and the way to find an app_id for play_store_reviews. No setup needed.

    Args:
        query: what the app does, e.g. "physiotherapy at home".
        country: ISO country code for the store, e.g. "IN" (default), "US".
        lang: language code, e.g. "en".
        limit: max apps, capped at 30.

    Returns:
        A list in Play Store relevance order, each with "app_id", "title", "developer",
        "rating", "installs" (a bucket like "1,000,000+"), "url".
    """
    results = gp_search(query, n_hits=max(1, min(limit, 30)), lang=lang, country=(country or "IN").lower())
    return [
        {
            "app_id": r.get("appId"),
            "title": r.get("title"),
            "developer": r.get("developer"),
            "rating": round(r["score"], 1) if r.get("score") else None,
            "installs": r.get("installs"),
            "url": f"https://play.google.com/store/apps/details?id={r.get('appId')}",
        }
        for r in results
    ]


@mcp.tool()
@handle_http_errors
def play_store_reviews(app_id: str, country: str = "IN", lang: str = "en", count: int = 100, sort: str = "newest") -> list | str:
    """Recent user reviews for one Google Play app - raw complaints and praise from people
    already using something like the idea being researched. Returns reviews only; spotting
    themes and judging sentiment is the caller's job. Optional: offer it, don't run it
    unprompted. No setup needed.

    Args:
        app_id: package name from play_store_search, e.g. "com.example.app".
        country: ISO country code for the store, e.g. "IN" (default), "US".
        lang: language code, e.g. "en".
        count: number of reviews, capped at 200.
        sort: "newest" (default), "helpful" (most thumbs-up), or "relevant".

    Returns:
        A list of {"rating" (1-5), "text", "thumbs_up", "date", "app_version"}. Reviewer
        names are dropped. Only the requested store and language are sampled.
    """
    sorts = {"newest": Sort.NEWEST, "helpful": Sort.RATING, "relevant": Sort.MOST_RELEVANT}
    if sort not in sorts:
        return f"sort must be one of {', '.join(sorts)}, got '{sort}'"
    result, _ = gp_reviews(
        app_id, lang=lang, country=(country or "IN").lower(), sort=sorts[sort], count=max(1, min(count, 200))
    )
    return [
        {
            "rating": r.get("score"),
            "text": r.get("content"),
            "thumbs_up": r.get("thumbsUpCount"),
            "date": r["at"].date().isoformat() if r.get("at") else None,
            "app_version": r.get("reviewCreatedVersion"),
        }
        for r in result
    ]


@mcp.tool()
@handle_http_errors
def youtube_videos(query: str, limit: int = 10, published_after_days: int | None = None) -> list | str:
    """YouTube videos matching a query, with view and comment counts - shows how much
    people watch content about a topic (tutorials, reviews, "I tried X" videos), which is
    often a stronger consumer-interest signal than search volume.

    Requires a free YOUTUBE_API_KEY (Google Cloud, YouTube Data API v3), saved via
    `/gutcheck setup`. Each call uses about 101 of the free 10,000 daily quota units.

    Args:
        query: search terms.
        limit: max videos, capped at 25.
        published_after_days: only videos from the last N days; omit for any time.

    Returns:
        A list in YouTube relevance order, each with "title", "channel", "published",
        "views", "likes", "comments", "url". A setup-instructions string if no key is saved.
    """
    key = get_key("YOUTUBE_API_KEY")
    if not key:
        return (
            "youtube_videos needs a free YouTube Data API key. Get one at "
            "https://console.cloud.google.com/apis/library/youtube.googleapis.com, then run "
            "`/gutcheck setup` to save it."
        )
    params = {"part": "snippet", "type": "video", "q": query, "maxResults": max(1, min(limit, 25)), "key": key}
    if published_after_days:
        after = datetime.now(timezone.utc) - timedelta(days=published_after_days)
        params["publishedAfter"] = after.strftime("%Y-%m-%dT%H:%M:%SZ")
    search = requests.get("https://www.googleapis.com/youtube/v3/search", params=params, timeout=15)
    search.raise_for_status()
    ids = [i["id"]["videoId"] for i in search.json().get("items", []) if i.get("id", {}).get("videoId")]
    if not ids:
        return []
    stats = requests.get(
        "https://www.googleapis.com/youtube/v3/videos",
        params={"part": "snippet,statistics", "id": ",".join(ids), "key": key},
        timeout=15,
    )
    stats.raise_for_status()
    by_id = {v["id"]: v for v in stats.json().get("items", [])}
    return [
        {
            "title": by_id[i]["snippet"].get("title"),
            "channel": by_id[i]["snippet"].get("channelTitle"),
            "published": by_id[i]["snippet"].get("publishedAt", "")[:10],
            "views": int(by_id[i]["statistics"].get("viewCount", 0)),
            "likes": int(by_id[i]["statistics"]["likeCount"]) if "likeCount" in by_id[i]["statistics"] else None,
            "comments": int(by_id[i]["statistics"]["commentCount"]) if "commentCount" in by_id[i]["statistics"] else None,
            "url": f"https://www.youtube.com/watch?v={i}",
        }
        for i in ids
        if i in by_id
    ]


def call_tool(name: str, params: dict):
    """`uv run server.py call <tool> '<json params>'` - run one tool from the terminal.

    Exists so the `/gutcheck setup` walkthrough can run a real check in the session
    where someone just installed gutcheck. Claude Code loads MCP tools at session
    start, so a first-time installer cannot call them until they restart; without
    this, setup always ends on "restart and try again" instead of showing the thing
    working."""
    tool = globals().get(name)
    if not callable(tool) or not any(name == t for t in TOOL_NAMES):
        raise SystemExit(f"unknown tool '{name}'. Available: {', '.join(TOOL_NAMES)}")
    print(json.dumps(tool(**params), indent=1, default=str))


def doctor():
    """`uv run server.py doctor` - live-check every source and print one line each, so
    `/gutcheck setup` (and users) can see what works on this machine right now."""
    checks = [
        ("Google Trends", lambda: interest_over_time(["coffee"]), None),
        ("Wikipedia", lambda: wikipedia_pageviews("Coffee"), None),
        ("Reddit", lambda: reddit_signal("coffee", limit=3), None),
        ("Hacker News + GitHub", lambda: builder_activity("coffee"), None),
        ("Google News", lambda: news_coverage("coffee", limit=3), None),
        ("App Store", lambda: app_store_apps("coffee", limit=3), None),
        ("Google Play", lambda: play_store_search("coffee", limit=3), None),
        ("YouTube", lambda: youtube_videos("coffee", limit=1), "YOUTUBE_API_KEY"),
        ("OpenCorporates", lambda: company_registration("Starbucks"), "OPENCORPORATES_API_TOKEN"),
    ]
    for name, check, needed_key in checks:
        if needed_key and not get_key(needed_key):
            print(f"[optional] {name}: no key saved ({needed_key})")
            continue
        result = check()
        if isinstance(result, str):
            print(f"[error]    {name}: {result[:160]}")
        else:
            print(f"[ok]       {name}")
    for label, key, adds in (
        ("GitHub token", "GITHUB_TOKEN", "raises GitHub search to 30/min"),
        ("Reddit API", "REDDIT_CLIENT_ID", "adds scores, removes the 1/min wait"),
    ):
        status = "saved" if get_key(key) else "optional"
        print(f"[{status}]{' ' * (6 if status == 'saved' else 4)}{label}: {adds} ({key})")


TOOL_NAMES = (
    "interest_over_time", "related_queries", "related_topics", "interest_by_region",
    "wikipedia_pageviews", "reddit_signal", "builder_activity", "news_coverage",
    "app_store_apps", "play_store_search", "play_store_reviews", "youtube_videos", "company_registration",
)


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["doctor"]:
        doctor()
    elif args and args[0] == "call":
        if len(args) < 2:
            raise SystemExit(f"usage: server.py call <tool> '<json params>'\ntools: {', '.join(TOOL_NAMES)}")
        call_tool(args[1], json.loads(args[2]) if len(args) > 2 else {})
    elif args and args[0] == "serve":
        # `serve [port]` - run as a web service so hosts that can't launch a local
        # program (claude.ai, ChatGPT) can add it as a remote connector by URL.
        mcp.settings.host = os.environ.get("HOST", "127.0.0.1")
        mcp.settings.port = int(args[1]) if len(args) > 1 else int(os.environ.get("PORT", 8000))
        mcp.run(transport="streamable-http")
    elif args:
        raise SystemExit(f"usage: server.py [doctor | call <tool> '<json params>' | serve [port]]")
    else:
        mcp.run()
