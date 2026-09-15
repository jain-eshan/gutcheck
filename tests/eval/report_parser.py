"""Parses a GUTCHECK REPORT (the fixed output format from
SKILL.md Step 5) into a dict, and raises
ValueError with a specific message for each way it can be malformed. This is
the shared structural checker used by both the eval and, potentially, by the
skill itself in the future to self-check before presenting a report."""
import re

VERDICT_ENUM = {"STRONG_SIGNAL", "MODERATE_SIGNAL", "WEAK_SIGNAL", "MIXED_SIGNAL", "INSUFFICIENT_DATA"}

TYPE_ENUM = {"IDEA", "PROBLEM", "TOPIC", "DECISION"}

REQUIRED_FIELDS = {
    "question": re.compile(r"^Question:\s*(.+)$", re.MULTILINE),
    "type": re.compile(r"^Type:\s*(\S+)", re.MULTILINE),
    "checking": re.compile(r"^Checking:\s*(.+)$", re.MULTILINE),
    "verdict": re.compile(r"^Verdict:\s*(\S+)", re.MULTILINE),
    "confidence": re.compile(r"^Confidence:\s*(.+)$", re.MULTILINE),
    "sources_used": re.compile(r"^Sources used:\s*(.+)$", re.MULTILINE),
}
BOTTOM_LINE_RE = re.compile(r'^Bottom line:\s*"(.+)"', re.MULTILINE)
NEXT_STEPS_RE = re.compile(r"^Next steps:\s*$", re.MULTILINE)
CAVEATS_RE = re.compile(r"^Caveats:\s*$", re.MULTILINE)


def parse_report(text: str) -> dict:
    """Returns a dict with keys: question, type, checking, verdict, confidence,
    sources_used, bottom_line, approx_tokens.
    Raises ValueError naming the specific missing/invalid field."""
    if "GUTCHECK REPORT" not in text:
        raise ValueError("missing GUTCHECK REPORT header")

    result = {}
    for field, pattern in REQUIRED_FIELDS.items():
        match = pattern.search(text)
        if not match:
            raise ValueError(f"missing required field: {field}")
        result[field] = match.group(1).strip()

    if result["verdict"] not in VERDICT_ENUM:
        raise ValueError(f"verdict '{result['verdict']}' is not one of {sorted(VERDICT_ENUM)}")

    if result["type"] not in TYPE_ENUM:
        raise ValueError(f"type '{result['type']}' is not one of {sorted(TYPE_ENUM)}")

    if not NEXT_STEPS_RE.search(text):
        raise ValueError("missing required Next steps: section")

    if not CAVEATS_RE.search(text):
        raise ValueError("missing required Caveats: section")

    bottom_match = BOTTOM_LINE_RE.search(text)
    if not bottom_match:
        raise ValueError("missing required Bottom line: (must be quoted)")
    result["bottom_line"] = bottom_match.group(1)

    result["approx_tokens"] = len(text) // 4
    return result
