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

Say which one you picked and why, in one line. If it's a quick check, don't announce a methodology, just start.

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

Then ask exactly one question: anything to add or cut? Take the answer, adjust, and start. Don't wait for enthusiasm; a plan they don't object to is approved.

If you can't get an answer (a headless or scripted run with nobody there), don't stall and don't skip the question. State it, assume the most reasonable answer, label the assumption in one line, and carry on. Flag it again in the report's caveats, since a different answer may change the verdict.

Skip this display entirely for a quick check. Showing a plan for a ten-minute question is the kind of ceremony that makes people stop using a tool.

## 5. Run it in phases

Work through the plan question by question, batching tool calls within each phase. After each phase of a multi-phase study, say in two or three sentences what you now know and what it changes. Those checkpoints are what make a long study feel like working with someone instead of waiting on a machine.

**Adapt out loud.** Evidence redirects a study all the time. When it does, say so and say why: "Question 2 is answered and it's a dead end. Nobody is switching from spreadsheets, so I'm dropping the pricing question and looking at why switching fails instead." A researcher who runs an obsolete plan to completion is following a script, not thinking.

**Stop when you have the answer.** If question 1 settles the decision, say so and skip the rest. Finishing a plan is not the goal; answering the decision is.

## 6. Hand it over in the right shape

`references/study-types.md` gives the output format per archetype. The GUTCHECK REPORT in `research.md` is the default and the core of every output; larger studies wrap sections around it rather than replacing it. A case competition needs numbers a jury can cite; a dissertation needs method and limitations; a business plan needs risks and what to do next. Same evidence, different packaging, and the packaging is part of the job.

## What you can and cannot study

Know your instrument. Say this plainly when it matters, rather than quietly producing a weaker answer.

**You can:** measure search interest and its direction, read what people say in public in their own words, see who already serves a need and how their users rate them, track press attention and its angle, see what builders are shipping, check whether a company legally exists, and pull anything public on the web (pricing pages, reviews, published surveys, job ads, regulator pages).

**You cannot:** run a survey or an interview, reach private or paid data (revenue, funding detail, industry-panel reports), see inside anyone's product analytics, or produce a credible market-size number from scratch. Market sizes come from published sources you cite, or from a bottom-up estimate whose assumptions you show. Never present either as a measurement.

**They can, and often should:** talk to ten people who have the problem, post the question in a community and count answers, put up a landing page, or ask their own customers. When the honest answer is "no public data can settle this", say that early and design the smallest primary-research step that would.
