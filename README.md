# gutcheck

**Check your gut against the internet before you commit.**

gutcheck is a market researcher for [Claude Code](https://claude.com/claude-code). Give it an idea you want to build, a problem you keep hitting, a topic you're curious about, or a decision you're stuck on. It works out what would actually answer the question, designs a study to match, pulls live evidence from Google Trends, Reddit, Google News, Wikipedia, Hacker News, GitHub, the App Store, YouTube and the web, then tells you what it thinks and why.

It scales with the stakes. A hunch gets ten minutes and a straight answer. A case competition, business plan, market landscape, or dissertation gets a research plan first, run in phases, in the shape that audience expects.

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

Run this once after installing. It's a conversation, not a config file hunt:

1. It asks what's actually on your mind first, and checks every data source in the background while you answer.
2. It asks the little it can't infer (which country, what you do), so later runs know whether to check India or the US and which communities to search.
3. It offers an optional key only when one would help *your* question, described by what it gets you rather than by its name, and saves it for you.
4. It finishes by researching the thing you named, for real, so setup ends with an answer instead of instructions.

You can skip the keys. Seven sources work with zero setup, and step 4 works immediately, even before you restart Claude Code.

## What you get

A point of view, not a pile of search results. Every run leads with what gutcheck
thinks is true, backs it with the evidence, argues the other side, and ends with
something you can do this week. Here's a real one:

```
GUTCHECK REPORT
════════════════════════════════════════════════════
Question:        freelancers keep getting paid late by clients - how common is this and what actually works?
Type:            PROBLEM
Checking:        Late payment is a widespread freelancer problem with no settled fix.
Verdict:         MODERATE_SIGNAL
Confidence:      MEDIUM (6 sources, 5-year window, worldwide)

THE READ
It's not you, and it's not rare: across the surveys, most freelancers get paid
late at least sometimes, and roughly a third of all invoices land after the due
date. But the second half of your question has an uncomfortable answer. The fixes
are known and boring, and they work: a deposit up front, a late fee written into
the contract, an invoice sent the day the work ends, and automatic reminders after.
Almost nobody is short of tools here, because every invoicing app already sends
reminders. What people are short of is the nerve to enforce terms with a client
they're afraid of losing. The threads aren't asking how to chase an invoice; they're
asking whether they're allowed to. That's a confidence problem wearing a process
problem's clothes, and it's why the pain persists even though the playbook is settled.

WHAT'S GOING ON
- What you're up against today is a polite reminder email and hoping. That's the
  status quo, and it mostly works slowly: most late invoices arrive within two
  weeks, so this reads as a cash-flow and dignity problem, not a bad-debt one.
- Desire, not demand. Search interest for the problem is climbing, but searches
  for tools that solve it sit near zero. People are looking for reassurance and
  scripts, not software.
- The sources disagree in a useful way: news coverage is about freelancer finance
  in general, while the actual complaints are about specific relationships with
  bigger clients. The power imbalance is the real subject.
- The sharpest thing anyone said: "these bigger companies are acting like Net 30
  means Net 60." Nobody in those threads is confused about what to do. They're
  weighing whether enforcing it costs them the account.

THE CASE AGAINST
The strongest counter is that this was checked worldwide and in English, and late
payment is heavily shaped by local law: the EU and UK have statutory interest rules
that change what "what works" even means. A second is that the survey numbers all
come from companies selling invoicing or payroll products, which have an interest in
the problem looking big. Checking one country properly, with its own rules, would
sharpen this a lot.

What would change this:
- Evidence that deposits and late fees get refused in practice would move this to
  STRONG_SIGNAL for "no settled fix", since the known playbook would then not work.
- A survey showing most late invoices go unpaid entirely, rather than arriving late,
  would change this from a cash-flow problem to a much more serious one.

Next steps:
- Put a 50% deposit and a late-fee line in your next two contracts and see whether
  either client actually pushes back. Most don't, and that's the fastest way to learn it.
- Check whether your current invoicing tool already sends automatic reminders before
  you pay for anything new. It probably does.
- Ask in r/freelance what finally got someone's worst payer to pay on time, and count
  how many answers are about process versus about firing the client.

Caveats:
- "late payment" on Google Trends also covers loans and credit cards, so part of that
  rise has nothing to do with freelancing.
- All survey figures come from vendors selling invoicing or payroll tools.
- Reddit without an API key returns posts without upvote counts, so popularity is unknown.
- Wikipedia had no usable article here (under 25 views a month), so it was dropped.

── Evidence ──
Google Trends, 5 years, worldwide: "late payment" rose from ~26 (2021) to a 55-86
range through 2026. "unpaid invoice" and "invoice reminder" stayed at 1-5 throughout.

Reddit, r/smallbusiness + r/graphic_design, 2026: "Do you guys actually enforce late
fees on Net 30 invoices or is it an empty threat?", "I'm constantly chasing money
I've already earned."

App Store, US: Invoice Simple (122k ratings), Invoice Fly (105k), Invoice2go (56k),
all updated within the month. Standalone late-payment chasers: 0 ratings.

[surveys, news and advice blocks trimmed for this README]

Sources used:    interest_over_time, related_queries, reddit_signal, news_coverage, app_store_apps, wikipedia_pageviews, web search
════════════════════════════════════════════════════
Bottom line: "Most freelancers get paid late, the fixes are known and boring (deposit,
late fee, instant invoice, auto-reminders), and the real blocker is enforcing terms
with clients you're afraid to lose."
```

The raw numbers sit at the bottom on purpose, so you can check the work without
wading through it first. After the report, gutcheck asks you something specific
about what it found. Say "save this" and it writes the report to `~/gutcheck-reports/`.

### How it works

**It designs the study before running it.** It works out what decision you're making, what would change your mind, and who the output is for, then picks from nine study types and writes a short plan: the research questions, what evidence would answer each, what's out of scope, and what only you can find out (nobody's public data can replace ten customer conversations, and it will say so).

| Study | What you get |
|---|---|
| Quick check | The default. One claim, ten minutes, a straight answer. |
| Opportunity validation | Demand, incumbents, the narrow group with the problem worst, what would kill it |
| Case competition | Industry structure, players, what's changing, customer evidence, recommendation, and the rebuttals a jury will throw |
| Business plan / investment memo | Bottom-up market size with the arithmetic shown, competition, go-to-market, ranked assumptions |
| Market landscape | Players grouped by approach, pricing picture, underserved segments |
| Problem diagnosis | How common, in whose words, what actually works |
| Decision analysis | The axis that really decides it, options compared on one scale |
| Deep study | Research questions, method, findings, limitations, references |
| Trend watch | Five-year shape, what's rising underneath, fad or trend, what to watch |

For a small question it skips the ceremony entirely and just answers. For a big one it shows the plan, asks what to cut, then runs it in phases and tells you what changed after each.

### How it thinks

- **It forms a view.** The analysis comes from crossing sources, which no single tool can do: flat search plus a crowded App Store means a settled market; loud Reddit plus flat search means an intense problem for a small group; busy builders plus silent users means a solution chasing a problem.
- **Desire versus demand.** Saying you want something is not downloading, paying, or switching. gutcheck says which one the evidence actually shows.
- **It names the status quo.** Every idea competes with a spreadsheet, an incumbent, or people deciding to live with it. "Nothing" is the hardest competitor there is.
- **Four kinds of question.** An **idea** (is there room), a **problem** (is it just me, what works), a **topic** (growing or fading), a **decision** (which one, and on what axis). Each gathers different evidence.
- **One claim, one verdict.** Your question becomes a single testable sentence, rated `STRONG_SIGNAL`, `MODERATE_SIGNAL`, `WEAK_SIGNAL`, `MIXED_SIGNAL` or `INSUFFICIENT_DATA`. "Not enough data" is an allowed answer, and it will say what would settle it.
- **It argues against itself.** Every report includes the strongest case that its own read is wrong.
- **Receipts, never invented numbers.** Every figure traces to a tool result or a cited page.
- **It remembers.** What you check is saved locally, so a similar question later opens with what you found last time and what moved.
- **`--deep`** pulls in more sources (regional breakdowns, GitHub, App Store, YouTube, Product Hunt launches, review sites) when the decision is expensive.

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
SKILL.md                  router, voice, and what to do before researching
design.md                 scope the job, pick the study, write the plan
research.md               run it: gather, form a view, write the report
setup.md                  the /gutcheck setup conversation
references/
  study-types.md          nine study archetypes, their questions and output shapes
  research-craft.md       desire vs demand, the status quo, triangulation, source tilt
  reading-signals.md      what each source's numbers mean, and the traps
  playbooks.md            how to aim an idea, problem, topic, or decision question
server.py                 MCP server: 11 tools that fetch raw data, no interpretation
setup                     installer (uv, dependencies, MCP registration, settings file)
tests/                    contract tests (mocked or recorded, no network)
tests/eval/               report-structure checks plus evals that run through `claude -p`
```

The tools also run from a terminal, which is how setup can research something in the
session you installed it in:

```bash
cd ~/.claude/skills/gutcheck && uv run server.py call reddit_signal '{"query":"meal prep app"}'
cd ~/.claude/skills/gutcheck && uv run server.py doctor   # health-check every source
```

The split is deliberate. The server only fetches data. Every judgment lives in the
markdown, in plain English, so you can read exactly how a verdict gets decided and
change it. If you think a verdict was wrong, the fix is usually one paragraph in
`references/research-craft.md`.

Run the tests:

```bash
uv sync --group dev && uv run pytest
```

## Contributing

Issues and PRs are welcome, especially new keyless data sources, sharper interpretation rules in `SKILL.md`, and reports where gutcheck got the verdict wrong (paste the report and say why).

gutcheck started as `market-signal-mcp`, a Google Trends wrapper for startup-idea checks. The install flow borrows from Garry Tan's [gstack](https://github.com/garrytan/gstack).

## License

MIT. See [LICENSE](LICENSE).
