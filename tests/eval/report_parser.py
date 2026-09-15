"""Parses a GUTCHECK REPORT (the fixed output format from research.md step 5)
into a dict, and raises ValueError with a specific message for each way it can
be malformed. Shared by the structural eval and the quality judge."""
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

# The analysis sections, in the order they must appear. Each maps to the marker
# that opens it; the section runs until the next marker.
SECTION_MARKERS = [
    ("read", re.compile(r"^THE READ\s*$", re.MULTILINE)),
    ("whats_going_on", re.compile(r"^WHAT'S GOING ON\s*$", re.MULTILINE)),
    ("case_against", re.compile(r"^THE CASE AGAINST\s*$", re.MULTILINE)),
    ("next_steps", re.compile(r"^Next steps:\s*$", re.MULTILINE)),
    ("caveats", re.compile(r"^Caveats:\s*$", re.MULTILINE)),
    ("evidence", re.compile(r"^── Evidence ──\s*$", re.MULTILINE)),
]
BOTTOM_LINE_RE = re.compile(r'^Bottom line:\s*"(.+)"', re.MULTILINE | re.DOTALL)


def parse_report(text: str) -> dict:
    """Returns question, type, checking, verdict, confidence, sources_used,
    bottom_line, the analysis sections, and approx_tokens. Raises ValueError
    naming the specific missing or invalid element."""
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

    starts = []
    for name, pattern in SECTION_MARKERS:
        match = pattern.search(text)
        if not match:
            raise ValueError(f"missing required section: {name}")
        starts.append((name, match.start(), match.end()))

    order = [name for name, _, _ in starts]
    if sorted(order, key=lambda n: dict((s[0], s[1]) for s in starts)[n]) != order:
        raise ValueError(f"sections are out of order: {order}")

    for i, (name, _, body_start) in enumerate(starts):
        body_end = starts[i + 1][1] if i + 1 < len(starts) else len(text)
        body = text[body_start:body_end].strip()
        if not body:
            raise ValueError(f"section '{name}' is empty")
        result[name] = body

    bottom_match = BOTTOM_LINE_RE.search(text)
    if not bottom_match:
        raise ValueError("missing required Bottom line: (must be quoted)")
    result["bottom_line"] = bottom_match.group(1).strip()

    # The point of the format: the analysis carries the report and the raw data
    # is the exhaust. A report whose Evidence dwarfs its analysis is a data dump
    # with a headline on top, which is exactly what this format exists to prevent.
    result["analysis_chars"] = sum(len(result[k]) for k in ("read", "whats_going_on", "case_against"))
    result["evidence_chars"] = len(result["evidence"])
    result["approx_tokens"] = len(text) // 4
    return result
