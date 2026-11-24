"""The terminal replay: lines from the real run in raw/run2.jsonl (see raw/run2-dump.txt), condensed the way
Claude Code shows them. Every value below is copied from that run's tool results or its final report."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT = (ROOT / "raw/report-excerpt.txt")

def esc(s): return html.escape(s, quote=False)
def span(c, s): return f'<span class="{c}">{esc(s)}</span>'

CMD = "/gutcheck --deep is there demand for a simple app that splits rent and bills between flatmates?"

def build(words, marks, steps):
    L = []  # [html, at, typed]
    add = lambda h, at: L.append([h, round(at, 3), None])
    d0 = marks["demo"]
    IW = 51
    box = lambda inner_html, n: span("boxl", "│ ") + inner_html + " " * (IW - 1 - n) + span("boxl", "│")
    add(span("boxl", "╭" + "─" * IW + "╮"), d0)
    add(box(span("c-or", "✻") + " Welcome to " + span("c-hi", "Claude Code") + "!", len("✻ Welcome to Claude Code!")), d0)
    add(box("", 0), d0)
    add(box("  " + span("c-dim", "/help for help, /status for your current setup"), 2 + len("/help for help, /status for your current setup")), d0)
    add(span("boxl", "╰" + "─" * IW + "╯"), d0)
    add("", d0)
    t_cmd = d0 + 0.9
    L.append(["", round(t_cmd, 3), {"pre": span("c-dim", "&gt; ").replace("&amp;", "&"), "text": CMD, "dur": 2.4, "hideCursor": round(t_cmd + 2.9, 3)}])
    t = t_cmd + 3.0
    add("", t)
    # step 2: it plans the study
    s2 = steps[1][0] + 0.25
    plan = [
        (span("c-or", "⏺ ") + "I'll load the gutcheck tools and the design and research playbooks.", 0),
        (span("c-or", "⏺ ") + span("c-hi", "Read") + "(~/.claude/skills/gutcheck/design.md)", 0.45),
        ("  " + span("c-dim", "⎿  Read 111 lines"), 0.6),
        (span("c-or", "⏺ ") + span("c-hi", "Read") + "(~/.claude/skills/gutcheck/research.md)", 0.95),
        (span("c-or", "⏺ ") + span("c-hi", "Read") + "(~/.claude/skills/gutcheck/references/study-types.md)", 1.3),
        (span("c-or", "⏺ ") + span("c-hi", "Read") + "(~/.claude/skills/gutcheck/references/playbooks.md)", 1.6),
        ("", 1.9),
        (span("c-or", "⏺ ") + "This is an " + span("c-y", "IDEA") + " question, and " + span("c-y", "--deep") + " maps to the deep-study", 2.1),
        ("  archetype. I'll go straight to gathering, batching every relevant tool call.", 2.25),
        ("", 2.6),
    ]
    for h, dt in plan: add(h, s2 + dt)
    # step 3: live evidence (values from run2 tool results)
    s3 = steps[2][0] + 0.3
    calls = [
        ("interest_over_time", 'keywords: ["splitwise", "split rent app", "bill splitting app"…]', "splitwise: 17 in 2021 → 42 now, peak 68 · \"split rent app\": 0 to 15", "Google Trends"),
        ("related_queries", 'keyword: "splitwise"', "\"splitwise free\" 42 · \"splitwise pro\" 29 · \"splitwise alternative\" 21", None),
        ("news_coverage", 'query: "bill splitting app", recent: "1y"', "32 stories · \"Venmo Finally Launches An In-App Bill Splitting Feature\"", "Google News"),
        ("app_store_apps", 'query: "split rent bills roommates", country: "US"', "Splitwise 4.0★ 29,827 · Livble 4.6★ 3,491 · Split 4.7★ 856", "App Store"),
        ("play_store_search", 'query: "split bills flatmates", country: "IN"', "Splitwise 10,000,000+ installs · Splid 1,000,000+ · Split Bills 100,000+", "Google Play"),
        ("builder_activity", 'query: "rent bill splitting app"', "HN: 4 stories · \"Launch HN: YSplit (YC W19)\" 77 points · GitHub: 14 repos", "Hacker News + GitHub"),
        ("reddit_signal", 'query: "splitwise alternative"', None, None),
    ]
    chips = []
    k = 0
    for i, (tool, args, res, chip) in enumerate(calls):
        at = s3 + i * 0.85
        add(span("c-or", "⏺ ") + span("c-hi", f"gutcheck - {tool}") + span("c-dim", f" (MCP)({args})"), at)
        if res: add("  " + span("c-dim", "⎿  ") + span("c-ok", res), at + 0.3)
        else: add("  " + span("c-dim", "⎿  ") + span("c-err", "Reddit's search feed returned an error. Carrying on without it."), at + 0.3)
        if chip: chips.append([chip, round(at + 0.3, 3)])
    at = s3 + len(calls) * 0.85
    add(span("c-or", "⏺ ") + span("c-hi", "Web Search") + span("c-dim", '("Splitwise alternative reddit complaints 2026 free plan limit")'), at)
    add("  " + span("c-dim", "⎿  Did 1 search"), at + 0.3)
    chips.append(["Web search", round(at + 0.3, 3)])
    add("", at + 0.5)
    # step 4: the report, copied from the run's final message (raw/report-excerpt.txt)
    s4 = steps[3][0] + 0.25
    add(span("c-or", "⏺ ") + span("c-hi", "Nobody's missing a bill-splitter here — they're actively fleeing the one they have."), s4)
    add("", s4 + 0.1)
    s4 += 0.35
    rep = REPORT.read_text().rstrip("\n").split("\n")
    first_report = len(L)
    verdict = bottom = None
    for j, line in enumerate(rep):
        h = esc(line)
        if line.startswith(("GUTCHECK REPORT", "THE READ", "THE CASE AGAINST", "Next steps", "Bottom line")): h = span("c-hi", line)
        elif line.startswith("Verdict:"):
            h = span("c-hi", "Verdict:") + " " * 9 + span("c-y", line.split(":", 1)[1].strip()); verdict = [len(L), round(s4 + 2.75, 3)]
        elif line.startswith("Confidence:"): h = span("c-hi", "Confidence:") + esc(line[11:])
        elif line.startswith("═"): h = span("c-dim", line)
        if line.startswith("Bottom line"): bottom = len(L)
        add(h, s4 + min(j * 0.07, 1.6))
    # after the report is in, scroll back so the verdict and the read sit on screen
    LH, VIEW = 28, 828 - 52
    top = (first_report) * LH
    scrolls = [[max(0, top - 2 * LH), s4 + 2.4, 0.9]]
    total = len(L) * LH
    scrolls.append([max(0, total - VIEW), steps[3][1] - 4.6, 2.8])
    # camera (scale, x, y, at, duration): push in on the header + verdict, out, then in on the bottom line
    v_at = verdict[1]
    cam = [[1.45, -20, -110, v_at - 0.3, 0.8], [1.0, 0, 0, steps[3][1] - 4.9, 0.7]]
    how = "Google Trends, the news, the App Store and Google Play, Hacker News, GitHub and the web, all at once."
    return {"lines": L, "chips": chips, "how": how, "scrolls": scrolls, "verdict": verdict, "cam": cam, "hls": [[verdict[0], 1, 470, verdict[1]], [bottom, 2, 1090, steps[3][1] - 2.4]]}
