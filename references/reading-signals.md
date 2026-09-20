# Reading each source

What the numbers mean, and the traps that make smart people wrong.

## Google Trends (`interest_over_time`, `related_queries`, `related_topics`, `interest_by_region`)

**What it is:** relative search interest, scaled 0-100 against the peak in the window you asked for. Not search counts. Nobody can get search counts for free.

**Reading it:**
- Say "interest halved since March", never "50 searches".
- 100 means the busiest point in that window, nothing more. Re-run with a longer window and the shape changes.
- Comparing keywords in one call shares one scale, which is the only way to compare them. Separate calls are not comparable.
- A flat line at 0-2 usually means volume too low for Google to report, not zero interest. For niche and B2B terms that's the norm, not a finding.

**Traps:**
- **`isPartial: true`** on the last point means the period isn't finished. The dip is the calendar, not the market. Never call it a decline.
- **Breakout (`5000`)** in rising queries means growth from near zero, not 5000%. It's Google saying "this is new", and it's often the most useful thing in the report.
- **Ambiguous keywords.** "late payment" covers credit cards and loans. "Mercury" is a planet, a bank, and a car. Check `related_topics` to see which meaning Google thinks you mean.
- **Brand names beat categories.** People search "Notion", not "note taking app". If the category is flat, check the leading brand before concluding the space is dead.
- **Seasonality.** Tax tools spike in spring, fitness in January. Compare year over year, not month to month.
- **Worldwide hides everything.** A term can be flat globally and tripling in one country. If geography matters, check `interest_by_region`.

## Reddit (`reddit_signal`)

**What it is:** actual sentences from people with the problem. The single richest source here, and the reason a report feels human.

**Reading it:**
- Quote them. One real line beats any count.
- Look for the workaround they describe, not just the complaint. "I keep a spreadsheet" tells you what you're replacing.
- Note the subreddit. The same complaint in r/smallbusiness and r/personalfinance are different markets.
- Dates matter. Three threads this quarter is live; three from 2019 is history.

**Traps:**
- Without a key there are no scores, so you can't tell a popular post from an ignored one. Say so.
- Reddit rewards complaining. Absence of praise is not evidence of a problem.
- Heavy skew: young, Western, English, technical. A silent Reddit means little for a market of accountants or people over 60.
- Search matches text, so an unrelated post can match your words. Read before you quote.

## Google News (`news_coverage`)

**What it is:** headline counts and sources over a window. `last_30_days` against `total` shows whether attention is rising or fading.

**Reading it:** name the angle, not the volume. Funding rounds, regulation, a backlash, and a product launch mean different things. Trade press covering it while consumer press ignores it is a B2B signal.

**Traps:** the `url` is a Google News redirect, not the publisher's address. It opens correctly in a browser but looks opaque in a report, so cite the outlet and date by name alongside it. Press releases and SEO farms inflate counts. A single event can produce fifty near-identical headlines. Google News editions are country-specific, so check the right one.

## App Store (`app_store_apps`)

**What it is:** who already serves this need on iPhone, with `rating_count` as a rough proxy for user base.

**Reading it:**
- Several apps past 10k ratings means demand is proven and competition is real.
- `last_updated` within a month means an active, funded competitor. A year stale means a dying one, and an opening.
- A leader with a low rating and lots of ratings is the best setup there is: proven demand, unhappy users.
- `released` dates cluster around when the category opened up.

**Traps:** ratings accumulate over years, so old apps look bigger than they are now. iOS only, US store by default, which skews against markets where Android dominates. Free apps collect more ratings than paid ones, so never read rating count as revenue.

## Play Store (`play_store_search`, `play_store_reviews`)

**What it is:** `play_store_search` lists who serves this need on Android, with `installs` as a bucketed user count. `play_store_reviews` returns recent reviews of one app, the closest thing to a live complaint box for a competitor.

**Reading it:**
- Tally themes across the sample: "~15 of 100 mention refunds" beats a cherry-picked quote. Sort by `newest` for what is broken now, `helpful` for what bothers the most people.
- Low-star reviews (1-2) name the gaps an entrant could fill. High-star reviews name what to match, not beat.
- A strong app with the same complaint repeated in dozens of reviews is an opening.

**Traps:** `installs` is a bucket ("1,000,000+"), not a count. Reviews skew to the delighted and the furious, and a single sample of 100-200 is one app's recent users. Reviews are per store country and language, so a US sample says little about India. Reviewers who left rating-only reviews have empty `text`. The scraper reads Play Store pages, so it can break if Google changes them; a failure comes back as a message, so carry on.

## Hacker News + GitHub (`builder_activity`)

**What it is:** whether builders are moving here. HN stories with points and comments; repositories with stars and last push.

**Reading it:**
- Recent Show HN posts and fresh repos mean builders smell an opportunity. Early, and crowded soon.
- Lots of stars but last push two years ago means people tried and moved on. Find out why.
- High comment counts with low points means an argument, which is usually where the interesting truth is.

**Traps:** GitHub stars measure developer attention, not usage or money. HN is not the market for anything consumer. Both are close to useless for questions about non-technical buyers, so say so rather than reading noise as signal.

## Wikipedia (`wikipedia_pageviews`)

**What it is:** monthly reads of an article. Reference interest, which moves differently from search interest.

**Reading it:** rising search plus flat Wikipedia suggests hype without depth. Flat search plus rising Wikipedia suggests something real that isn't marketed. Under a few hundred views a month means the article is too obscure to use; drop it rather than reading noise.

**Traps:** pick the right article title or you get a 404. The article is about a concept, so it tracks the concept, not your product idea.

## YouTube (`youtube_videos`)

**What it is:** view and comment counts on videos about the topic. Strong for consumer questions, where people watch before they buy.

**Reading it:** high views on "how to" or "I tried" videos means real, active interest. Comments are a second Reddit; read them. Recent uploads with fast view counts beat old videos with big totals.

**Traps:** needs a key. Views accumulate forever, so check dates. Creator-driven spikes (one big channel covered it) can look like a trend and aren't.

## Company registration (`company_registration`)

**What it is:** incorporation facts. Name, jurisdiction, number, status, date.

**Traps:** this is not funding, revenue, or traction data, and no free source for those exists. Never present it as such. An active registration means the paperwork is filed, nothing more.

## Web search

**What it is:** everything the tools can't reach. Competitors, surveys, pricing pages, forum threads, Product Hunt launches, review sites.

**Reading it:** pricing pages are the fastest read on a market, since they tell you who pays and how much. Review sites (G2, Trustpilot, app reviews) tell you what people hate about existing options, which is where openings live.

**Traps:** cite what you use. "Best X of 2026" listicles are affiliate marketing, not research. Check who ran a survey before quoting its number.
