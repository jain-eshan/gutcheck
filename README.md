# gutcheck

**Check your gut against the internet before you commit.**

gutcheck is a research buddy for [Claude Code](https://claude.com/claude-code). Give it an idea you want to build, a problem you keep hitting, a topic you're curious about, or a decision you're stuck on. It pulls live evidence from Google Trends, Reddit, Google News, Wikipedia, Hacker News, GitHub, the App Store, YouTube, and the web, then gives you a straight verdict with the receipts, and talks it through with you.

```
/gutcheck is there demand for a simpler meal-planning app for busy parents?
/gutcheck freelancers keep getting paid late, how common is this and what actually works?
/gutcheck is pickleball still growing or has it peaked?
/gutcheck should I learn Rust or Go in 2026?
```

Free and open source. Works with no API keys. Everything runs on your machine.

## Install (30 seconds)

Open Claude Code and paste this. Claude does the rest.

> Install gutcheck: run **`git clone --single-branch --depth 1 https://github.com/jain-eshan/gutcheck.git ~/.claude/skills/gutcheck && ~/.claude/skills/gutcheck/setup`**, then tell me to restart Claude Code and run `/gutcheck setup`.

Or run it yourself in a terminal:

```bash
git clone --single-branch --depth 1 https://github.com/jain-eshan/gutcheck.git ~/.claude/skills/gutcheck && ~/.claude/skills/gutcheck/setup
```

The setup script installs [uv](https://docs.astral.sh/uv/) if you don't have it, installs the Python dependencies, registers the data tools with Claude Code, and creates a private settings file at `~/.config/gutcheck/.env`. Restart Claude Code once afterwards.

**Requirements:** macOS or Linux, [Claude Code](https://claude.com/claude-code), and `git`. Windows hasn't been tested yet; WSL is the likely route.

## Setup: `/gutcheck setup`

Run this once after installing. It's a short conversation, not a config file hunt:

1. Checks every data source live and shows you what's working.
2. Asks which optional extras you want, explains what each adds, and gives click-by-click steps to get a free key.
3. Saves the key for you (or lets you paste it into the settings file yourself, if you'd rather keep it out of the chat) and confirms it works.

You can skip all of it. Seven sources work with zero keys.

## What you get

Every run ends in the same report shape, so you can compare checks over time. Here's a real one:

```
GUTCHECK REPORT
════════════════════════════════════════════════════
Question:        freelancers keep getting paid late by clients - how common is this and what actually works?
Type:            PROBLEM
Checking:        Late payment is a widespread freelancer problem with no settled fix.
Verdict:         MODERATE_SIGNAL
Confidence:      MEDIUM (6 sources, 5-year window, worldwide)

── Google Trends (5 years, worldwide) ──
"late payment" roughly doubled, from ~26 in 2021 to a 55-86 range through 2026.
"unpaid invoice" and "invoice reminder" stay near the floor (1-5).
Top rising query is a meme ("universal unpaid invoice viking ship"), which is noise.
Means: the pain is growing, but people search for the problem, not a tool for it.

── Web search: surveys ──
Remote's State of Freelance Work 2025: 85% of freelancers get paid late at least
sometimes, and 21% are paid late or not at all more than half the time. Bonsai's
invoice data (100k+ freelancers): 29% of invoices are late, but 75% of those
arrive within 14 days.
Means: very common, yet most late invoices are days late, not unpaid.

── Reddit (r/smallbusiness, r/graphic_design, r/freelance) ──
Several 2026 threads, in people's own words: "these bigger companies are acting like
Net 30 means Net 60", "I'm constantly chasing money I've already earned", and a client
answering a reminder with "a little professional courtesy would be appreciated".
Means: the pain is as much the awkwardness of chasing as the money.

── App Store (US) ──
General invoice apps are large and mature (Invoice Simple 122k ratings, Invoice Fly
105k, Invoice2go 56k). Apps that only chase late payments have 0 ratings.
Means: reminders already come bundled with invoicing tools, so a standalone fix is a hard sell.

[Google News and "what works" blocks trimmed for this README]

What would change this:
- Evidence that deposits and late fees fail in practice would push this to STRONG_SIGNAL.

Next steps:
- Add a 50% deposit and a late-fee line to your next two contracts and track pushback.
- Post in r/freelance asking "what finally got your worst client to pay on time?"

Caveats:
- "late payment" on Google Trends also covers loans and credit cards.
- Survey figures come from companies that sell invoicing or payroll tools.

Sources used:    interest_over_time, related_queries, reddit_signal, news_coverage, app_store_apps, web search
════════════════════════════════════════════════════
Bottom line: "Most freelancers get paid late, but the fixes are well known (deposits,
late fees, auto-reminders); the real gap is using them, not a missing tool."
```

After the report, gutcheck asks what surprised you and whether it changes your plan. Say "save this" and it writes the report to `~/gutcheck-reports/`.

### How it thinks

- **Four kinds of question.** It works out whether you're checking an **idea** (is there demand, who already serves it), a **problem** (how common, what people have tried), a **topic** (growing or fading), or a **decision** (how the options compare on the same data), and gathers different evidence for each.
- **One premise, one verdict.** It restates your question as a single claim it can test, then rates the evidence: `STRONG_SIGNAL`, `MODERATE_SIGNAL`, `WEAK_SIGNAL`, `MIXED_SIGNAL`, or `INSUFFICIENT_DATA`. "Not enough data" is an allowed answer, and it will say so.
- **Receipts, not vibes.** Every number comes from a tool result or a cited page. Real quotes from real people beat comment counts.
- **Asks before it guesses.** At most two clarifying questions, and only when your request is genuinely unclear.
- **Remembers.** Each check is saved to `~/.config/gutcheck/history.jsonl`. Check something similar later and the report opens with what you found last time.
- **`--deep`** adds more sources (regional breakdowns, related topics, GitHub, App Store, YouTube, Product Hunt launches, review sites) for when the decision is a big one.

## Sources

| Source | What it tells you | Key needed? |
|---|---|---|
| Google Trends | Is search interest rising or falling, what related searches are breaking out, where | No |
| Reddit | What people actually say, ask, and complain about, in their own words | No (1 search a minute). Optional key removes the limit |
| Google News | Is the press covering it, and what angle it takes | No |
| Wikipedia pageviews | Reading interest, a check on search hype | No |
| Hacker News + GitHub | Are builders shipping in this space | No. Optional token raises GitHub's limit |
| App Store | Who already serves this need, and how many people rate them | No |
| Web search | Competitors, surveys, forum threads, Product Hunt launches | No (built into Claude Code) |
| YouTube | How much people watch content about it | Free key, about 3 minutes |
| OpenCorporates | Is a named company officially registered, and since when | Free account |

## Using the data tools outside Claude Code

The `/gutcheck` playbook is a Claude Code skill, but the data tools are a standard [MCP](https://modelcontextprotocol.io) server that any MCP client can use (Cursor, Codex, Claude Desktop, and others). After cloning and running `setup`, add this to your client's MCP config:

```json
{
  "mcpServers": {
    "gutcheck": {
      "command": "/Users/YOU/.local/bin/uv",
      "args": ["run", "--directory", "/Users/YOU/.claude/skills/gutcheck", "server.py"]
    }
  }
}
```

Use the full path to `uv` (run `which uv` to find it), since desktop apps often can't see your terminal's PATH. You'll get the 11 tools. Ask your assistant to use them, or point it at `SKILL.md` for the full method.

## Update and uninstall

Update from inside Claude Code with `/gutcheck upgrade`. gutcheck also checks for a new version at most once a day and mentions it under a report.

Uninstall:

```bash
claude mcp remove gutcheck --scope user && rm -rf ~/.claude/skills/gutcheck ~/.config/gutcheck
```

## Privacy

gutcheck has no server, account, or analytics. Your questions go only to the sources listed above, straight from your machine. API keys stay in `~/.config/gutcheck/.env` (readable only by you). Your history stays in `~/.config/gutcheck/history.jsonl`.

## Known limits

- **Google Trends has no official API.** gutcheck uses [pytrends](https://github.com/GeneralMills/pytrends), which reads the public site. If you run many checks back to back, Google may block you for a few minutes. The report marks that source as unavailable and carries on.
- **Keyless Reddit allows one search a minute.** gutcheck waits it out, so a report can take about a minute. A Reddit API key removes the limit, but Reddit reviews new API apps by hand, which can take days.
- **Trends numbers are relative (0-100), not search counts.** The report treats them that way.
- **OpenCorporates covers registration facts only**, never funding or revenue. No free source for that exists.

## How it's built

```
SKILL.md       the /gutcheck playbook: classify, research, interpret, report
setup.md       the /gutcheck setup conversation
server.py      MCP server: 11 tools that fetch raw data and do no interpretation
setup          installer (uv, dependencies, MCP registration, settings file)
scripts/       once-a-day update check
tests/         contract tests (recorded or mocked, no network) + report-structure checks
tests/eval/    tool-selection and report-quality evals that run through `claude -p`
```

The split is deliberate. The server only fetches data. All judgment lives in `SKILL.md`, in plain English, so you can read exactly how a verdict gets decided, and change it.

Run the tests:

```bash
uv sync --group dev && uv run pytest
```

## Contributing

Issues and PRs are welcome, especially new keyless data sources, sharper interpretation rules in `SKILL.md`, and reports where gutcheck got the verdict wrong (paste the report and say why).

gutcheck started as `market-signal-mcp`, a Google Trends wrapper for startup-idea checks. The install flow borrows from Garry Tan's [gstack](https://github.com/garrytan/gstack).

## License

MIT. See [LICENSE](LICENSE).
