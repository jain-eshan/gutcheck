"""Eval layer 3, structural half (issue #10): does a GUTCHECK REPORT follow the
fixed format from SKILL.md - no LLM judge needed for this part, it's pure
string structure. The substantive "is the verdict actually right" half is
run_report_quality_judge.py."""
from pathlib import Path

import pytest

from report_parser import parse_report

FIXTURE = (Path(__file__).parent / "fixtures" / "sample_report_default.txt").read_text()


def test_valid_report_parses_cleanly():
    result = parse_report(FIXTURE)
    assert result["question"].startswith("freelancers keep getting paid late")
    assert result["type"] == "PROBLEM"
    assert result["verdict"] == "MODERATE_SIGNAL"
    assert result["confidence"].startswith("MEDIUM")
    assert "reddit_signal" in result["sources_used"]
    assert result["bottom_line"].startswith("Most freelancers get paid late")


def test_valid_report_stays_readable_length():
    # A report someone will actually read end to end - generous ceiling for a
    # six-source default-tier run.
    assert parse_report(FIXTURE)["approx_tokens"] < 2000


@pytest.mark.parametrize(
    "mutation,expected_error_substring",
    [
        (lambda t: t.replace("Verdict:         MODERATE_SIGNAL", ""), "missing required field: verdict"),
        (lambda t: t.replace("MODERATE_SIGNAL", "PROBABLY_GOOD"), "is not one of"),
        (lambda t: t.replace("Type:            PROBLEM", "Type:            RANT"), "type 'RANT' is not one of"),
        (lambda t: t.replace("Checking:", "Premise:"), "missing required field: checking"),
        (lambda t: t.replace("Caveats:", "Notes:"), "missing required Caveats"),
        (lambda t: t.replace("Next steps:", "Ideas:"), "missing required Next steps"),
        (lambda t: t.replace('Bottom line: "', 'Bottom line: '), "missing required Bottom line"),
        (lambda t: t.replace("GUTCHECK REPORT", "Here's what I found:"), "missing GUTCHECK REPORT header"),
    ],
)
def test_each_required_element_is_actually_enforced(mutation, expected_error_substring):
    """Mutation testing: prove the parser doesn't just pass on well-formed input
    by accident - each required element's removal must produce a specific,
    correctly-attributed error."""
    broken = mutation(FIXTURE)
    with pytest.raises(ValueError, match=expected_error_substring):
        parse_report(broken)
