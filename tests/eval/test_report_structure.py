"""Structural half of the output eval: does a GUTCHECK REPORT follow the format
in research.md - pure string structure, no LLM judge. The substantive "is the
verdict right" half is run_report_quality_judge.py."""
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
    assert "Reddit" in result["sources_used"]
    assert result["bottom_line"].startswith("Most freelancers get paid late")


def test_analysis_outweighs_raw_evidence():
    """The whole point of the format: the report leads with a view and demotes
    the source data to exhaust. If Evidence outgrows the analysis, the report has
    slid back into being a data dump with a headline."""
    result = parse_report(FIXTURE)
    assert result["analysis_chars"] > result["evidence_chars"]


def test_report_stays_readable_length():
    assert parse_report(FIXTURE)["approx_tokens"] < 2500


@pytest.mark.parametrize(
    "mutation,expected_error_substring",
    [
        (lambda t: t.replace("Verdict:         MODERATE_SIGNAL", ""), "missing required field: verdict"),
        (lambda t: t.replace("MODERATE_SIGNAL", "PROBABLY_GOOD"), "is not one of"),
        (lambda t: t.replace("Type:            PROBLEM", "Type:            RANT"), "type 'RANT' is not one of"),
        (lambda t: t.replace("Checking:", "Premise:"), "missing required field: checking"),
        (lambda t: t.replace("THE READ", "SUMMARY"), "missing required section: read"),
        (lambda t: t.replace("THE CASE AGAINST", "OTHER NOTES"), "missing required section: case_against"),
        (lambda t: t.replace("── Evidence ──", "── Appendix ──"), "missing required section: evidence"),
        (lambda t: t.replace("Caveats:", "Notes:"), "missing required section: caveats"),
        (lambda t: t.replace("Next steps:", "Ideas:"), "missing required section: next_steps"),
        (lambda t: t.replace('Bottom line: "', "Bottom line: "), "missing required Bottom line"),
        (lambda t: t.replace("GUTCHECK REPORT", "Here's what I found:"), "missing GUTCHECK REPORT header"),
    ],
)
def test_each_required_element_is_actually_enforced(mutation, expected_error_substring):
    """Mutation testing: prove the parser doesn't pass well-formed input by
    accident - removing each required element must raise a specific, correctly
    attributed error."""
    broken = mutation(FIXTURE)
    with pytest.raises(ValueError, match=expected_error_substring):
        parse_report(broken)


def test_sections_must_be_in_order():
    read_start = FIXTURE.index("THE READ")
    evidence_start = FIXTURE.index("── Evidence ──")
    swapped = (
        FIXTURE[:read_start]
        + FIXTURE[evidence_start:]
        + FIXTURE[read_start:evidence_start]
    )
    with pytest.raises(ValueError, match="out of order|missing required section"):
        parse_report(swapped)
