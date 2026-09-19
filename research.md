# Running the study

`design.md` gave you a study type and a plan. This file executes it: gather, form a view, write it up.

## 1. Aim the questions

Work out which kind of question this is. Read `references/playbooks.md` for the one that fits, since each kind needs different evidence and has a different failure mode. The playbooks' ordering is about **what matters most**, not a sequence to run in: gather in one batch (step 2), then weigh the evidence in the playbook's order when forming your view.

| Kind | Sounds like | The real question |
|---|---|---|
| IDEA | "I want to build X", "would people pay for X" | Is there demand, who already serves it, where's the opening |
| PROBLEM | "X keeps happening to me", "why is X so hard" | How common is it, how people describe it, what they've tried |
| TOPIC | "what's going on with X", "is X a fad" | Growing or fading, what's rising underneath, who cares |
| DECISION | "X or Y", "should I do X" | How the options compare on the same evidence |

**Multi-sided ideas:** decided in `design.md`. Each side gets its own keywords, its own evidence, and its own verdict.

**Where:** take the country from their profile or their words. A local question ("bakery in Austin") is US; a global one is worldwide. If location decides the answer and you can't tell, that's one of your two questions.

**The claim.** One testable statement, not two joined by "and". "Late payment is widespread **and** has no settled fix" is two claims, and a single verdict on it is an average of a yes and a no. Pick the one the decision rests on, and let the other one show up in the analysis.

**Keywords:** what a real person would type. "meal planner app", not "AI-driven nutrition orchestration". Get 1-3 variants. `references/reading-signals.md` has the keyword traps (brand names, ambiguous words like "late payment" that also mean something else).

## 2. Gather, in one batch

**Web-only mode?** If you have no gutcheck tools and no terminal (`SKILL.md`, "Check your instruments"), gather with web search using `references/web-only.md` instead of the tool list below, and follow its report changes.

Call every tool you need **in the same turn**, web searches included. They don't depend on each other, and one batch keeps this fast.

**Always:**
- `interest_over_time` for the core keywords. For a DECISION, put both options in one call so they share a scale.
- `related_queries` for the main keyword. What's rising tells you where this is heading.
- `reddit_signal`, **once per report**. Two to five words, in the words people with the problem would use rather than industry terms ("claim rejected physiotherapy", not "outpatient claims adjudication"). Not a whole sentence: it matches loosely, so a question returns noise. Phrase it how a frustrated person would type it, and pass `subreddits` when obvious communities exist. Without a key it allows one search a minute and may take that long to answer.
- `news_coverage` for the main keyword.
- **Web search**, 2-3 queries. This is where competitors, surveys, and forum threads live.

**Add, depending:**
- Consumer app idea → `app_store_apps`. Developer or software idea → `builder_activity` (Hacker News + GitHub).
- A question about a concept people read up on → `wikipedia_pageviews`.
- TOPIC → `interest_over_time` with `timeframe="today 5-y"`, `response_format="full"`, so you can tell a fad from a trend.
- A named company → `company_registration`.
- `--deep` → add `related_topics`, `interest_by_region` (needs a country), `builder_activity`, `app_store_apps`, `youtube_videos`, plus web searches on `site:producthunt.com` and review sites (G2, Trustpilot, app reviews) for what people complain about in existing tools.

**Prune what didn't earn its place.** A source that came back empty, irrelevant, or simply dull does not get a paragraph in the report just because you called it. Drop it, and say in Caveats that it had nothing. Length is not thoroughness.

**When a source fails** (rate limit, no key, nothing found), it's one unavailable source, not a dead report. Note it in Caveats and carry on. A missing key is worth one line at the end: "YouTube would have added watch data here; `/gutcheck setup` takes three minutes."

## 3. Say the first interesting thing before the report

This is the difference between a research partner and a vending machine. As soon as the results land, react to the sharpest one or two findings in plain conversation. Two or three sentences, no headers, no template.

> Okay, this is interesting. Nobody on Reddit is asking for a better meal planner, but there are a dozen threads about giving up on the ones they tried. That's a retention problem, not a discovery problem.

Then, if their own knowledge would change how you read it, ask **one** question through AskUserQuestion (not as prose, which would strand them mid-study) and keep researching while they answer:

- Header: `Your read`
- Question: "Have you talked to anyone who quit one of these apps? The data shows me they churn, not why."
- Options: **"Yes, and here's what they said"** (they fill in the detail), **"No, going on instinct"**, **"Skip, just keep researching"**

Skip it entirely when the evidence is clear or they've already told you. Never block on the answer: keep gathering while it sits there.

## 4. Think it through before you write anything

This is the actual job. You are not summarizing six searches; you are forming a view and using the searches as evidence. A researcher who hands over "here's what Reddit said, here's what Trends said" has done the gathering and skipped the work.

Before writing, answer these for yourself. `references/research-craft.md` is the reference for how.

1. **What is actually true here?** One or two sentences you'd defend. Not a summary of sources, a claim about the world.
2. **What do these people do today?** Every idea competes with the current workaround, usually a spreadsheet, a friend, or nothing. Name it.
3. **Is this desire or demand?** Wanting it is not paying, downloading, or switching. Say which one the evidence actually shows.
4. **Who exactly has this problem worst?** The evidence usually points at a narrower group than the question assumed. Name that group.
5. **Where do the sources disagree, and why?** Disagreement is information. Press coverage running ahead of community chatter means something specific.
6. **What's the strongest case against your read?** If you can't argue the other side, you haven't looked hard enough.
7. **So what should they do differently on Monday?** If nothing changes, the research didn't matter.
8. **What's the one number or fact that decides this?** Find it, and if it exists, commit to a view on it. Handing back "if X is above 80, this doesn't work" without saying whether X is plausibly above 80 is passing the decision back as homework. If you genuinely can't know it, say who can and how they'd get it in a day.

Cross the sources against each other rather than reading them in a line. Trends flat but App Store crowded means a settled market, not a dead one. Reddit loud but search flat means an intense problem for a small group. Builders active but users silent means a solution chasing a problem. That crossing is the analysis, and no single tool can give it to you.

`references/reading-signals.md` is the reference for what each number means and the traps that make people misread it. The ones worth memorizing:

- A rising query at value `5000` is Google's Breakout marker, meaning growth from near zero, not 5000%.
- `isPartial: true` on the last Trends point means the period isn't over. Never call that a decline.
- Trends is relative, 0-100. "Interest halved since March", never "50 searches".
- Search interest up while Wikipedia reading is flat suggests hype without depth. The reverse suggests something real that nobody markets well.
- App Store `rating_count` is a rough user count. Several apps past 10k ratings means demand exists and competition is real.
- Old, abandoned GitHub repos in a space mean people tried this and stopped. Ask why.

When the sources disagree, that's the finding. Say what the disagreement implies instead of averaging it into mush.

## 5. The report

Your view comes first. The raw numbers go at the bottom as evidence, where someone can check your work. Never open with "here's what each source said".

Same shape every time, so runs stay comparable. `Verdict` is exactly one of the five values.

```
GUTCHECK REPORT
════════════════════════════════════════════════════
Question:        <their question, as they asked it>
Type:            <IDEA | PROBLEM | TOPIC | DECISION>
Checking:        <the one-sentence claim you tested>
Verdict:         <STRONG_SIGNAL | MODERATE_SIGNAL | WEAK_SIGNAL | MIXED_SIGNAL | INSUFFICIENT_DATA>
Confidence:      <LOW | MEDIUM | HIGH> (<N> sources, <window>, <where>)
                 [N counts independent bodies of evidence that produced something
                 usable, not tool calls. Every Trends tool together is one. Web
                 search is one per distinct kind of source you actually cite (a
                 regulator page and a pricing survey are two; six queries against
                 the same blog are one). The count must match the Evidence blocks.]
[Prior check:    You checked "<past question>" on <date>. Verdict then: <verdict>.]

THE READ
<3-6 sentences. What you believe is true and why, written as one argument that
moves: what's happening, what's driving it, what it means for them. Name the
specific group the evidence points at. Reference evidence inline the way a person
would ("two apps past 100k ratings"), never as "Source X shows". This is the part
they'll actually read, so it carries the thinking.>

WHAT'S GOING ON
- <What they're really up against today: the current workaround, the incumbent,
  or nothing at all. Every idea competes with something.>
- <Desire or demand: what the evidence shows people actually do, not what they say.>
- <The sharpest specific finding, ideally a real quote in someone's words.>
- <Where the sources disagree and what that tension means - only when they
  genuinely disagree. Never manufacture a tension to fill the slot.>

[3-5 bullets. These four are the ones that usually matter; swap one out when the
study type calls for something sharper (a pricing pattern, a regulatory clock).]

[── Competitors ── when you found 3+ named players: group by approach
(free app, paid service, marketplace, DIY workaround), one line and a link each.
Say what's missing from all of them, not just who they are.]

THE CASE AGAINST
<2-3 sentences arguing the other side honestly. The strongest reason your read
could be wrong, and what it would take to find out.>

What would change this:
- <the finding that would flip the verdict, so they know what to watch>

Next steps:
- <2-3 cheap things they could do this week to test it themselves, specific
  enough to act on today: a subreddit to post in, a page to put up, five people to ask>

Caveats:
- <at least one: a source that failed, a small sample, an ambiguous keyword,
  a partial month, a survey run by someone selling the solution>

── Evidence ──
<The exhaust, compact. One short block per source: the numbers, dates, quotes,
and links behind the read. Two or three lines each, no interpretation here since
it's already above. This is where they check your work.>

Sources used:    <the tools and searches you actually used>
════════════════════════════════════════════════════
Bottom line: "<one sentence they could paste into a message>"
```

Length discipline: THE READ, WHAT'S GOING ON and THE CASE AGAINST together must outweigh the Evidence section, and Evidence gets at most three lines per source. Cite the two or three numbers that carry the argument, not every value the tool returned. If the exhaust is bigger than the thinking, you wrote a data dump with a headline on it. On a `--deep` run that means pruning evidence blocks, not expanding the analysis to compensate.

Bigger studies (case competition, business plan, deep study) wrap extra sections around this core rather than replacing it. `references/study-types.md` gives the shape for each.

**What the verdicts mean:**

- `STRONG_SIGNAL` — several independent sources agree, and at least one shows sustained interest, not a spike.
- `MODERATE_SIGNAL` — real evidence, but narrower than their claim. Name the narrower version that holds.
- `WEAK_SIGNAL` — flat, thin, or pointing the other way.
- `MIXED_SIGNAL` — sources genuinely disagree. Say what that tension means.
- `INSUFFICIENT_DATA` — too little came back to call it. An honest answer, not a failure.

For a DECISION, the Bottom line names the option the evidence favors, or says plainly it's a wash.

For multi-sided ideas, repeat `Checking:` through `Caveats:` per side, each headed `SIDE: <name>` with its own verdict, then `Strongest side: <name> - <verdict>, because <one sentence>` before the Bottom line. Never score sides numerically.

If an update was flagged, put one line **below the Bottom line**, as the last thing in the message: `A newer gutcheck is available (<old> -> <new>). Run /gutcheck upgrade.`

## 6. Then actually talk about it

The report is the middle of the conversation, not the end. Two things happen here, in this order.

**First, offer where to take it next**, with AskUserQuestion, built from what you actually found rather than a standing menu:

- Header: `Next`
- Question: "Where do you want to take this?"
- Options, the most useful first:
  - **"Dig into <the specific open thread>"** — the one thing that would move the verdict.
  - **"Check <the adjacent question the evidence raised>"** — often the sharper question they didn't ask.
  - **"Save the report"** — writes it to `~/gutcheck-reports/`.
  - **"That's enough"** — stop cleanly.

**Then ask the human question**, specific to what you found, never a generic "thoughts?":

- Verdict weaker than they hoped: "Does the flat search interest match what you're seeing, or do you have signals I can't see from here?"
- Verdict strong: "The opening looks like the people who already tried and quit. Is that who you'd build for?"
- Mixed: "News says this is hot, Reddit says nobody cares. My read is the press is early. What's your read?"

Two exchanges at most, then wrap up. If they push into pricing, business models, or strategy, answer briefly from the evidence you have, say where the data stops, and name what they'd have to find out.

If they ask to save or share it and you have a shell, write to `~/gutcheck-reports/<YYYY-MM-DD>-<slug>.md` (create the folder) and give them the path.

## 7. Save what happened

Terminal only. With no shell, skip this section.

After the conversation, append one line. Never rewrite the file.

```bash
python3 -c "
import json, sys
entry = {'question': sys.argv[1], 'type': sys.argv[2], 'verdict': sys.argv[3], 'date': sys.argv[4],
         'key_signal': sys.argv[5], 'sources_used': sys.argv[6].split(',')}
if sys.argv[8]:
    entry['outcome'] = sys.argv[8]
with open(sys.argv[7], 'a') as f:
    f.write(json.dumps(entry) + '\n')
" "<question>" "<TYPE>" "<VERDICT>" "$(date -u +%Y-%m-%d)" "<one-line key signal>" "<tool1,tool2>" ~/.config/gutcheck/history.jsonl "<what they said it changes, or empty>"
```

Last argument stays empty unless they actually said what this changes for them.

If they mentioned something durable about themselves that isn't in their profile yet (what they're building, their field, their market), update `~/.config/gutcheck/profile.json` so the next run starts warmer. Keep it to the fields setup.md defines.
