"""Contract tests for the 4 Google Trends tools. Fixtures are recorded
HTTP cassettes (see tests/cassettes/) so these run against a fixed snapshot of
Trends data, not live network - live Trends is scraped, rate-limited, and its
response shape has drifted before (a retired endpoint once broke a whole tool)."""
import pytest

import server


@pytest.mark.vcr
def test_interest_over_time_shape_concise():
    records = server.interest_over_time(keywords=["lab grown diamonds"], response_format="concise")
    assert isinstance(records, list)
    assert len(records) > 0
    for r in records:
        assert "date" in r
        assert "lab grown diamonds" in r
        assert isinstance(r["lab grown diamonds"], int)
    # concise mode: isPartial should be omitted when false, present (and true) on at most the last record
    partial_flags = [r.get("isPartial") for r in records if "isPartial" in r]
    assert all(flag is True for flag in partial_flags), "concise mode must drop isPartial when false"


@pytest.mark.vcr
def test_interest_over_time_full_keeps_ispartial_false():
    records = server.interest_over_time(keywords=["lab grown diamonds"], response_format="full")
    assert isinstance(records, list)
    assert any(r.get("isPartial") is False for r in records), "full mode must NOT drop isPartial: false"


@pytest.mark.vcr
def test_related_queries_shape_and_truncation():
    result = server.related_queries(keyword="lab grown diamonds", response_format="concise")
    assert set(result.keys()) == {"top", "rising"}
    assert len(result["top"]) <= 10
    assert len(result["rising"]) <= 10
    for record in result["top"]:
        assert "query" in record and "value" in record
        assert set(record.keys()) == {"query", "value"}, f"unexpected extra field(s) leaked in: {record}"


@pytest.mark.vcr
def test_related_topics_shape():
    result = server.related_topics(keyword="lab grown diamonds", response_format="concise")
    assert set(result.keys()) == {"top", "rising"}
    for record in result["top"]:
        assert "topic_title" in record and "topic_type" in record and "value" in record
        assert set(record.keys()) == {"topic_title", "topic_type", "value"}, (
            f"unexpected extra field(s) leaked in: {record}"
        )


@pytest.mark.vcr
def test_interest_by_region_shape_and_sort():
    # geo="IN" exercises the state-level breakdown; worldwide is covered below.
    records = server.interest_by_region(keyword="lab grown diamonds", geo="IN", response_format="concise")
    assert isinstance(records, list)
    assert len(records) <= 10
    assert all("geoName" in r for r in records)
    values = [r["lab grown diamonds"] for r in records]
    assert values == sorted(values, reverse=True), "concise mode must sort regions by value descending"



def test_interest_by_region_worldwide_asks_for_countries(monkeypatch):
    """Google only accepts resolution="COUNTRY" for a worldwide region breakdown;
    "REGION" returns HTTP 500, so the default geo="" always failed when checked live."""
    calls = {}

    class FakeTrends:
        def build_payload(self, *args, **kwargs):
            pass

        def interest_by_region(self, resolution, inc_low_vol):
            calls["resolution"] = resolution
            return None

    monkeypatch.setattr(server, "get_pytrends", lambda: FakeTrends())
    server.interest_by_region(keyword="lab grown diamonds")
    assert calls["resolution"] == "COUNTRY"


def test_concise_timeseries_spans_the_whole_window_not_just_the_end():
    """Concise mode used to keep only the last 90 days, so a 5-year request came
    back as 13 weekly points with nothing saying the rest was dropped - a reader
    could conclude interest was zero until this year. Thinning must keep the first
    and last points and sample across everything between."""
    records = [{"date": f"2021-{m:02d}-01T00:00:00.000", "x": m} for m in range(1, 13)]
    records += [{"date": f"2026-{m:02d}-01T00:00:00.000", "x": 100 + m} for m in range(1, 13)]
    thinned = server.apply_format(list(records), "concise", timeseries=True)
    assert thinned[0] == records[0]
    assert thinned[-1] == records[-1]
    assert len(thinned) <= server.CONCISE_TIMESERIES_POINTS


def test_concise_timeseries_thins_a_long_series():
    records = [{"date": f"2020-01-{d:02d}T00:00:00.000", "x": d} for d in range(1, 29)] * 10
    thinned = server.apply_format(list(records), "concise", timeseries=True)
    assert len(thinned) == server.CONCISE_TIMESERIES_POINTS
    assert server.apply_format(list(records), "full", timeseries=True) == records
