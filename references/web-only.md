# Web-only mode

You're here because the gutcheck data tools and a terminal aren't available: claude.ai chat, ChatGPT, or another host with only its own search and browsing. The study still works. It's lighter, and it has to say so.

## What changes

The design step (`design.md`) is unchanged. So are the playbooks, the craft rules, and the report shape. Only the evidence source changes: you search the web instead of calling tools. Nothing in `references/reading-signals.md` about tool output applies to numbers you didn't get.

## Stand-ins for each tool

Run these in one batch of searches, the way you'd batch tool calls.

| Full gutcheck uses | Web-only does |
|---|---|
| `reddit_signal` | Search `site:reddit.com <how a frustrated person would phrase it>`. Quote what people say. You will not have upvote counts. |
| `interest_over_time`, `related_queries` | Search for published trend reports and news on the topic. **Do not** state search-volume numbers or "interest rose X%" unless a page you cite says it. If the host can open trends.google.com, read a chart there and cite it. Otherwise say direction is unmeasured. |
| `news_coverage` | Search news, restricted to the last year. Note the angle, not just the count. |
| `app_store_apps` | Search the App Store and Google Play listing pages for the category. Rating counts on the page are fine to cite. |
| `builder_activity` | Search `site:news.ycombinator.com`, `site:github.com`, `site:producthunt.com`. |
| `wikipedia_pageviews` | Skip it. Say so in Caveats. |
| `company_registration` | Search the official registry for the country, or skip and say so. |
| `youtube_videos` | Skip unless the host can search YouTube. |

## Report changes

- Add a line under the header: `Mode: WEB-ONLY (no Trends, Reddit, or App Store tools; web search only)`.
- `Confidence` is `LOW` or `MEDIUM`, never `HIGH`. Count sources the usual way: one per distinct kind of source you actually cite.
- `STRONG_SIGNAL` needs several independent sources agreeing and sustained interest. Without measured trends you can't show sustained, so use `MODERATE_SIGNAL` at most unless a cited report gives the trend.
- Caveats must name what web-only couldn't measure (usually: trend direction, community upvotes, app ranks).
- End with one line: full data is available in Claude Code with gutcheck installed (`github.com/jain-eshan/gutcheck`).

## Saving

No shell means no history file. If they want to keep the report, put it in your reply as one block they can copy. Don't offer a file path.
