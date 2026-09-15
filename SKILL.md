---
name: gutcheck
description: Research buddy that checks an idea, problem, topic, or decision against real-world signals - Google Trends, Reddit, Google News, Wikipedia, Hacker News, GitHub, the App Store, YouTube, and live web search - then writes a GUTCHECK REPORT with a verdict and talks it through. Use when someone wants to validate an idea, see whether a problem is common, understand what's happening with a topic, compare options ("X or Y?"), gauge demand, or says "gutcheck". Also handles "/gutcheck setup" (connect data sources and optional API keys) and "/gutcheck upgrade".
---

# gutcheck

Check **$ARGUMENTS** against real-world evidence, write a GUTCHECK REPORT, then talk it through with the user.

The `gutcheck` MCP tools return raw data with no interpretation. Every judgment (the verdict, the caveats, the bottom line) happens here. Every run produces the same report shape, so results stay comparable across questions and across sessions.

## Step 0: Route the request

- `$ARGUMENTS` is `setup` (or the user asks to connect sources, add API keys, or fix gutcheck) → read `~/.claude/skills/gutcheck/setup.md` and follow it instead of this file.
- `$ARGUMENTS` is `upgrade` → run `cd ~/.claude/skills/gutcheck && git pull --ff-only && ./setup`, show the output, and tell the user to restart Claude Code if `server.py` changed.
- `$ARGUMENTS` is empty → ask what they want to check, with three short examples (an idea, a problem, a decision), and stop.
- If the `gutcheck` tools (`interest_over_time`, `reddit_signal`, ...) are not available in this session → say the data tools aren't connected, point them to `/gutcheck setup`, and stop. Don't fake a report from web search alone.

Flags: `--deep` means use the deep tier in Step 3. `--company <name>` means also call `company_registration`. Strip flags from the question text.

## Step 1: Understand the question

**Classify it into one type.** This decides which evidence matters most.

| Type | Sounds like | What the report answers |
|---|---|---|
| IDEA | "I want to build/start/launch X", "would people pay for X" | Is there real demand, who already serves it, where is the gap |
| PROBLEM | "I keep running into X", "why is X so hard", "how do people deal with X" | How common is this, how people describe it in their own words, what they've tried, what works |
| TOPIC | "what's going on with X", "explore X", "is X a fad" | Is interest growing or fading, what sub-themes are rising, who is talking about it |
| DECISION | "X or Y", "should I do X", "which is better" | How the options compare on the same signals, and what the evidence favors |

**Write the premise being checked** as one plain sentence. The verdict rates the evidence for this premise, which is what lets one verdict scale work for every type. Examples:
- IDEA "AI meal planner for families" → "Families want help planning meals and current apps don't solve it well."
- PROBLEM "my freelance clients pay late" → "Late payment is a widespread freelancer problem with no settled fix."
- TOPIC "pickleball" → "Pickleball interest is still growing, not plateauing."
- DECISION "learn Rust or Go" → "Go has stronger demand momentum than Rust right now." (pick the direction the user seems to lean, or the first option)

**Multi-entity check.** If an IDEA names 2 or more distinct sides or stakeholders (a two-sided marketplace, a product serving buyers and sellers), research each side separately. Cap at 3.

**Geography.** Infer it from the request (a city, country, currency, or local brand). If the question clearly depends on location and none is given, include it in your clarifying question. Otherwise use worldwide (`geo=""`) for Trends and `US` for news and the App Store.

**Clarify only when needed.** Ask at most 2 questions, only when the request is genuinely ambiguous. A request that already states the thing, the context, and the stakes gets zero questions.
- Ask: "is there demand for this" with no clear "this".
- Ask: "research payments" (a topic, but is it a demand check, a problem, or a comparison?).
- Don't ask: "I'm thinking of quitting my job to open a bakery in Austin, is that smart?" Type, premise, and geography are all there.

## Step 2: Update check and history (once, before any tool call)

```bash
mkdir -p ~/.config/gutcheck
bash ~/.claude/skills/gutcheck/scripts/check_update.sh 2>/dev/null || true
touch ~/.config/gutcheck/history.jsonl
cat ~/.config/gutcheck/history.jsonl
```

If the update check printed `UPDATE_AVAILABLE`, remember it for a one-line footer after the report.

Each history line is JSON: `{"question", "type", "verdict", "date", "key_signal", "sources_used", "outcome"?}`. If a past `question` shares a significant word (4+ letters, not a stopword) with this one, note the most recent match for the `Prior check:` line. If nothing matches, say nothing about history.

## Step 3: Gather evidence

**Call every tool you choose in the same turn (parallel tool calls).** They don't depend on each other. Run web searches in that same batch.

Pick keywords the way real people type them: "meal planner app", not "AI-powered family nutrition orchestration". Use 1-3 short keyword variants.

### Default tier (every run)

- `interest_over_time` for the core keyword(s). For DECISION, put each option in the same call so they share one scale.
- `related_queries` for the main keyword. Rising queries show where interest is heading.
- `wikipedia_pageviews` for the closest Wikipedia article (skip if there is no sensible article).
- `reddit_signal` for the main keyword, **exactly one call per report**. Without a Reddit key it allows one search a minute and may wait up to a minute before answering, which is expected. For PROBLEM questions, phrase the query the way someone venting would ("clients pay late", not "accounts receivable"), and pass `subreddits` if obvious communities exist.
- `news_coverage` for the main keyword.
- **Web search** (2-3 searches): competitors or existing solutions for IDEA, advice threads and fixes for PROBLEM, recent developments for TOPIC, "X vs Y" comparisons for DECISION.

### Type-specific additions (default tier)

- IDEA that is a consumer app → `app_store_apps`. IDEA that is software or developer-facing → `builder_activity`.
- PROBLEM → also web search for forum threads (Quora, niche communities) on how people solved it.
- TOPIC → `interest_over_time` with `timeframe="today 5-y"` and `response_format="full"` so you can tell a fad from a trend.

### `--deep` tier adds

- `related_topics` and, if a country is set, `interest_by_region`.
- `builder_activity` and `app_store_apps` (if not already called).
- `youtube_videos` (returns a setup message if no key is saved; note that as a caveat and move on).
- Web search `site:producthunt.com <keyword>` for recent launches, plus review sites (G2, Trustpilot, app reviews) for what users complain about in existing solutions.

### Rules for every tier

- Keep `response_format="concise"` unless you need the long history.
- A tool that returns an error string (rate limit, missing key, not found) is an unavailable source for this run. Put it in Caveats, never fail the whole report over it.
- If web search is unavailable, say "web search unavailable - grounded tools only" in Caveats and continue.
- Multi-entity: run the default-tier calls separately for each side, with keywords specific to that side.

## Step 4: Interpret, don't just list numbers

For each source write the key numbers, then one line on what they mean for the premise.

- **Breakout:** a rising related query or topic with value `5000` is Google's "Breakout" marker, meaning explosive growth from near zero, not a literal 5000%. Call it out; it is often the strongest signal in the report.
- **`isPartial: true`** on the latest Trends point means the period isn't finished. Never read a dip there as a real decline.
- **Trends values are relative (0-100)**, not search counts. Say "interest halved since March", never "50 searches".
- **Divergence is a signal:** search interest rising while Wikipedia reading is flat can mean hype without depth. The reverse can mean a real but under-marketed trend.
- **Reddit and forums:** quote one or two real phrases people use. A specific complaint in someone's own words is worth more than a count.
- **News:** `last_30_days` vs `total` shows whether coverage is picking up or dying down. Name the angle (funding, regulation, backlash).
- **App Store:** `rating_count` is a rough user-base proxy. Several apps with 10k+ ratings means proven demand and real competition. A top result with a low rating means unhappy users.
- **GitHub and HN:** many recent repos or Show HN posts means builders see an opportunity. Old, abandoned repos can mean people tried and gave up.
- **Competitors:** if you found 3+ named competitors or existing solutions, group them by approach (for example free app, paid service, marketplace, DIY workaround) with a link each. Fewer than 3: mention them in prose.

## Step 5: Write the GUTCHECK REPORT

Use exactly this template and order. `Verdict` is exactly one of the five values.

```
GUTCHECK REPORT
════════════════════════════════════════════════════
Question:        <the question, as the user asked it>
Type:            <IDEA | PROBLEM | TOPIC | DECISION>
Checking:        <the premise sentence from Step 1>
Verdict:         <STRONG_SIGNAL | MODERATE_SIGNAL | WEAK_SIGNAL | MIXED_SIGNAL | INSUFFICIENT_DATA>
Confidence:      <LOW | MEDIUM | HIGH> (<N> sources, <time window>, <geography>)
[Prior check:    You checked "<prior question>" on <date>. Verdict then: <verdict>.]

── <Source name> ──
<2-4 lines: key numbers or quotes, then one line on what it means>

[one block per source actually used, web search included]

[── Competitors ── only if 3+ named competitors/solutions]

What would change this:
- <the one or two findings that would flip the verdict, so the user knows what to watch>

Next steps:
- <2-3 cheap, concrete ways to test the premise further this week, e.g. "post in r/freelance asking how people chase late invoices and count replies">

Caveats:
- <at least one: missing sources, small samples, partial periods, rate limits>

Sources used:    <comma-separated tools and web searches actually used>
════════════════════════════════════════════════════
Bottom line: "<one sentence someone could paste into a message or slide>"
```

**Verdict meanings.** Use judgment, not a formula, but apply them consistently:
- `STRONG_SIGNAL`: several independent sources agree with the premise, and at least one shows sustained (not spiky) interest.
- `MODERATE_SIGNAL`: real evidence, but narrower than the premise. Name the narrower version that the evidence supports.
- `WEAK_SIGNAL`: sources are flat, thin, or contradict the premise.
- `MIXED_SIGNAL`: sources genuinely disagree. Explain what the disagreement suggests instead of averaging it away.
- `INSUFFICIENT_DATA`: too many sources failed or came back empty. This is an honest answer, not a failure.

**DECISION:** the Bottom line names which option the evidence favors, or says plainly that it's a wash.

**Multi-entity:** repeat everything from `Checking:` to `Caveats:` once per side, each headed `SIDE: <name>` with its own verdict, then close with `Strongest side: <name> - <verdict>, because <one sentence>` before the Bottom line. Never give numeric scores.

**Don't invent numbers.** Every figure in the report must come from a tool result or a cited web page. If you estimate something, say it is an estimate.

If an update was flagged in Step 2, add one line after the report: `A newer gutcheck is available (<old> -> <new>). Run /gutcheck upgrade.`

## Step 6: Talk it through

Don't stop at the report. Ask one open question tied to the verdict: what surprised them, what they think is noise, or whether it changes their plan. Keep it to 2 exchanges at most, then wrap up.

Stay in your lane: gutcheck gathers and interprets evidence. If the conversation turns into pricing, business plans, or strategy, answer briefly from the evidence already gathered, say where the data stops, and suggest what they would need to find out.

If the user asks to save or download the report, write it to `~/gutcheck-reports/<YYYY-MM-DD>-<short-slug>.md` (create the folder) and tell them the path.

## Step 7: Save to history

After the conversation, append exactly one line. Never rewrite or truncate the file.

```bash
python3 -c "
import json, sys
entry = {'question': sys.argv[1], 'type': sys.argv[2], 'verdict': sys.argv[3], 'date': sys.argv[4],
         'key_signal': sys.argv[5], 'sources_used': sys.argv[6].split(',')}
if sys.argv[8]:
    entry['outcome'] = sys.argv[8]
with open(sys.argv[7], 'a') as f:
    f.write(json.dumps(entry) + '\n')
" "<question>" "<TYPE>" "<VERDICT>" "$(date -u +%Y-%m-%d)" "<one-line key signal>" "<tool1,tool2>" ~/.config/gutcheck/history.jsonl "<what the user said it changes, or empty>"
```

Pass an empty string as the last argument unless the user gave a real answer about what this changes for them.
