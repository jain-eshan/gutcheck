# Design the study before you run it

A researcher doesn't open six tabs and start typing. They work out what decision is being made, what would answer it, what kind of study that implies, and what they'll do with each finding. Then they run it.

This file is that step. It ends with a plan. `research.md` executes the plan.

## 1. Scope the job

Answer these from what they said and from `~/.config/gutcheck/profile.json`. Ask only what you genuinely can't infer, two questions maximum.

- **The decision.** What will they do differently depending on the answer? "Whether to spend the next three months building it" is a decision. "Learning about the market" is not, and if that's all there is, ask what would make it worth their time.
- **The stakes and the clock.** A weekend project and a career change deserve different studies. A case competition due Friday deserves a different one again.
- **The audience.** Themselves, a jury, an investor, a professor, a boss. This decides the output format, how much sourcing is needed, and whether "I don't know" is acceptable.
- **Their priors.** What do they already believe, and what would change their mind? Aim the study at that, since evidence that can't move them is wasted.
- **What they already know.** They may have talked to customers or worked in the industry for a decade. Ask before spending a tool call re-establishing what they could tell you in a sentence.

## 2. Choose the study

Read `references/study-types.md` and pick one. Nine archetypes, each with its own questions, sources, output, and quality bar.

**Check for sides first.** If the question names two or more distinct groups who have to say yes (a marketplace's buyers and sellers, an insurer's patients and clinics, a tool's admins and end users), research each side separately and give each its own verdict. Cap at 3. This usually decides the answer: one side is easy and one is hard, and naming the hard one is the most useful thing you can hand back. Averaging the sides into one verdict destroys exactly that.

**Default to the quick check.** Most questions deserve ten minutes and a straight answer, and turning a simple question into a research program is its own failure. Design a bigger study when one of these is true:

- They named a deliverable: a case competition, business plan, investor memo, board paper, dissertation, market report.
- The stakes are high: quitting a job, spending real money, a company-level bet.
- The question contains several genuinely separate questions.
- They asked for depth: "properly", "deep dive", "full research", `--deep`.

**Let them pick the depth.** Unless it's obviously a quick check, put the choice in front of them with AskUserQuestion before you research anything. Name the cost of each, because that's what they're actually choosing between:

- Header: `Depth`
- Question: "How far do you want me to take this?"
- Options, recommended one first, drawn from what the question deserves:
  - **"Quick check (~5 min)"** — one claim, search and community evidence, straight answer.
  - **"Full validation (~20 min)"** — demand, who already serves it, the narrow group with the problem worst, what would kill it.
  - **"Case-comp brief (~40 min)"** — industry structure, named players with figures, the recommendation and the rebuttals a jury will throw.
  - **"Deep study (~45 min+)"** — research questions, method, findings, limitations, references.

Swap in whichever four fit: a business plan, a landscape scan, a decision matrix, a trend watch. Mark the one you'd pick as `(Recommended)` and say in half a line why, so choosing is quick rather than homework.

If they go quick, don't announce a methodology, just start.

## 3. Write the plan

For anything beyond a quick check, write 3-5 **research questions**. Each is answerable, and each has evidence attached. A question nothing could answer is a question to cut.

For each, name:
- **What would answer it.** Be specific: "at least three apps with 10k+ ratings" or "complaint threads from the last 12 months".
- **Which source.** From the tools, from web search, or from them (their customers, their data, their industry knowledge).
- **What "answered" looks like**, so you know when to stop digging.

Then set the boundaries:
- **Out of scope.** Name what this study won't cover, so nobody expects it later.
- **What this toolkit can't do.** Be honest and early: no surveys, no interviews, no paid industry databases (Nielsen, Euromonitor, Gartner, Crunchbase), no private financials, no accurate market-size figures. Anything needing those is a job for them, and you should say what to go and get.
- **Effort.** Roughly how long, and how many phases.

## 4. Show it, briefly, then go

Show the plan in at most twelve lines. Compact and readable, not a document:

```
STUDY PLAN — <study type>
Decision it serves:  <what they'll do with the answer>
Questions:
  1. <question> → <source> → answered when <bar>
  2. ...
Out of scope:        <what you're not doing>
You'll need to get:  <anything only they can find, if any>
Effort:              <rough time, phases>
```

Then hand them the plan as a choice, with AskUserQuestion:

- Header: `Plan`
- Question: "Here's what I'd run. Good to go, or want it pointed somewhere else?"
- Options:
  - **"Run it (Recommended)"**
  - **"Focus on <the question you'd cut first>"** — drop the rest and go deeper on one thing.
  - **"Add something"** — they name what's missing, and you fold it in.
  - **"Go quicker"** — collapse to a quick check and one answer.

Take the answer, adjust, start. If you can't get one (a headless or scripted run with nobody there), take the recommendation, say in one line which you took and why, and flag it in the report's caveats, since a different choice may change the verdict.

Skip this display entirely for a quick check. Showing a plan for a ten-minute question is the kind of ceremony that makes people stop using a tool.

## 5. Run it in phases

Work through the plan question by question, batching tool calls within each phase. After each phase of a multi-phase study, say in two or three sentences what you now know and what it changes. Those checkpoints are what make a long study feel like working with someone instead of waiting on a machine.

**Adapt out loud, and let them call it.** Evidence redirects a study all the time. When it does, say what you found and put the turn to them rather than quietly rewriting the plan:

> Question 2 is answered and it's a dead end: nobody is switching from spreadsheets. I'd drop the pricing question and dig into why switching fails instead. Want me to, or stick to the plan?

Offer it as a choice (follow the new thread / finish the original plan), take the recommendation if nobody answers, and never burn a turn asking about a change that doesn't cost them anything.

**Stop when you have the answer.** If question 1 settles the decision, say so and skip the rest. Finishing a plan is not the goal; answering the decision is.

## 6. Hand it over in the right shape

`references/study-types.md` gives the output format per archetype. The GUTCHECK REPORT in `research.md` is the default and the core of every output; larger studies wrap sections around it rather than replacing it. A case competition needs numbers a jury can cite; a dissertation needs method and limitations; a business plan needs risks and what to do next. Same evidence, different packaging, and the packaging is part of the job.

## What you can and cannot study

Know your instrument. Say this plainly when it matters, rather than quietly producing a weaker answer.

**You can:** measure search interest and its direction, read what people say in public in their own words, see who already serves a need and how their users rate them, track press attention and its angle, see what builders are shipping, check whether a company legally exists, and pull anything public on the web (pricing pages, reviews, published surveys, job ads, regulator pages).

**You cannot:** run a survey or an interview, reach private or paid data (revenue, funding detail, industry-panel reports), see inside anyone's product analytics, or produce a credible market-size number from scratch. Market sizes come from published sources you cite, or from a bottom-up estimate whose assumptions you show. Never present either as a measurement.

**They can, and often should:** talk to ten people who have the problem, post the question in a community and count answers, put up a landing page, or ask their own customers. When the honest answer is "no public data can settle this", say that early and design the smallest primary-research step that would.
