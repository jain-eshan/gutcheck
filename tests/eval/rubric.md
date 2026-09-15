# GUTCHECK REPORT quality rubric

Used by `run_report_quality_judge.py`. Score each dimension 1-5 against the report produced for a query in `gold_answers.jsonl`, comparing with that entry's `gold_verdict` and `gold_rationale`.

## 1. Verdict correctness (weight 3x)

- **5**: Verdict matches `gold_verdict`, and the reasoning matches the gold rationale's logic rather than landing on the same label by luck.
- **3**: Verdict is defensible given the data pulled, even if it differs from `gold_verdict`. Trends data is noisy and two careful readers can land on adjacent verdicts. Score 3, not 1, for a defensible near-miss.
- **1**: Verdict contradicts what the report's own evidence shows, e.g. STRONG_SIGNAL while every source describes flat interest.

## 2. Synthesis, not summary (weight 3x)

The difference between a researcher and a search wrapper.

- **5**: THE READ states a view about the world that no single source contains, built by crossing sources (e.g. flat search plus a crowded App Store read as a settled market). It names the status quo people use today, says whether the evidence shows desire or demand, and narrows the question to the group the evidence actually supports.
- **3**: Some interpretation beyond restating the data, but mostly source-by-source observations placed under a heading. Cross-source reasoning is thin or asserted without support.
- **1**: A summary of what each tool returned. The reader could have produced this by reading the Evidence section themselves.

## 3. Hallucination absence (weight 2x)

- **5**: No invented numbers, and no misread conventions: a `5000` rising value is treated as the Breakout marker and not a literal percentage, `isPartial: true` is treated as provisional and not a decline, Trends values are described as relative rather than as search counts.
- **3**: Minor imprecision (an odd rounding, a loose date) but no invented facts.
- **1**: States a number, trend direction, or finding that appears nowhere in the tool output it claims to summarize.

## 4. Honesty and self-criticism (weight 1x)

- **5**: THE CASE AGAINST makes a real argument against the report's own read. Caveats name the actual limits present here, including source tilt (vendor-run surveys, Reddit's skew, an ambiguous keyword, a partial month).
- **3**: Caveats exist and name at least one real limit, but the case against is token or generic.
- **1**: No self-criticism, boilerplate caveats, or caveats contradicted by the report's own claims.

## 5. Actionability (weight 1x)

- **5**: Next steps are things this person could do this week, specific enough to start today (a named subreddit to post in, a specific contract change to try, five people to ask). "What would change this" names a concrete finding that would flip the verdict.
- **3**: Next steps are reasonable but generic ("talk to customers", "do more research").
- **1**: Missing, or advice unrelated to what the evidence showed.

## Pass threshold

A report passes if the weighted average `(3×verdict + 3×synthesis + 2×hallucination + 1×honesty + 1×actionability) / 10` is **≥ 4.0**. Below that, the judge names which dimensions failed and why, not just the number.

A report that scores 5 on verdict and 1 on synthesis fails, by design. Getting the right answer while handing the reader a pile of search results is the failure mode this tool exists to avoid.
