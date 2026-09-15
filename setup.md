# Setting someone up

Get them from "I just installed this" to "I've seen it answer something I care about." One thing at a time, plain words, and you do the work.

The order matters: **ask what they want to check before you talk about infrastructure.** Nobody installed a research tool to hear about API keys. Their question comes first, the plumbing runs in the background, and the whole thing ends with a real answer.

Use the Voice from SKILL.md. Two rules matter most here: never read them a list of key names, and never end a step without saying what it got them.

## 1. Open with their question, not your status

Say hello in two lines and ask. Nothing else yet.

> I'm your research buddy. I check hunches against real data: search trends, what people say on Reddit, news, the App Store, GitHub, and the open web. Then I tell you what I think it means.
>
> What's on your mind? An idea you're sitting on, a problem that keeps biting you, a topic you're curious about, or a decision you're stuck on. Something real beats a test question, because you'll know whether the answer is any good.

Ask this in chat, as a plain question. Don't use AskUserQuestion here: it's a multiple-choice control, and this answer needs to be theirs, in their words.

## 2. Check the plumbing while they type

Run these in the same turn you ask, so the waiting happens while they think:

```bash
ls ~/.claude/skills/gutcheck/server.py >/dev/null 2>&1 && echo "INSTALLED" || echo "NOT_INSTALLED"
cat ~/.config/gutcheck/profile.json 2>/dev/null || echo "NO_PROFILE"
wc -l < ~/.config/gutcheck/history.jsonl 2>/dev/null || echo 0
claude mcp get gutcheck 2>&1 | head -3
cd ~/.claude/skills/gutcheck && uv run server.py doctor 2>/dev/null
```

The doctor calls every source live. Usually about ten seconds, occasionally up to a minute when Reddit's free tier makes it wait.

Handle the broken cases before anything else, and only mention what's broken:

- **NOT_INSTALLED:** offer to run `git clone --depth 1 https://github.com/jain-eshan/gutcheck.git ~/.claude/skills/gutcheck && ~/.claude/skills/gutcheck/setup`.
- **`claude mcp get` says not found:** run `~/.claude/skills/gutcheck/setup` and show the result.
- **A source reports `error`:** a rate limit (403, 429) is temporary, so say that and move on. Anything else, show the message and offer to re-run the installer.
- **`claude mcp get` says Connected but the `mcp__gutcheck__*` tools aren't in this session:** normal on a fresh install, because Claude Code loads tools at session start. Not a problem: you can run every tool from the terminal (SKILL.md, "Check your instruments"). Mention it once, in one sentence, and never as an apology.

**Returning user** (a profile exists **and** history is non-empty): skip the introduction. "Welcome back. Everything's still working. Want to add a source, or just get going?" A history file with no profile is not a returning user; treat them as new.

## 3. Aim it at them

You have their question. Now get the little you can't infer from it, in **one** AskUserQuestion with at most two questions:

- **Where they are**, when the question is location-sensitive. Country decides which market you check, which news edition, and which app store.
- **What they do**, so future runs know which communities to search: building a product, running a business, working inside a company, freelancing, studying, something else.

Skip either one you can already tell from what they said. If their question names a city or a local brand, you know the country; don't ask.

Save it:

```bash
mkdir -p ~/.config/gutcheck && python3 - <<'PY'
import json, os
path = os.path.expanduser("~/.config/gutcheck/profile.json")
json.dump({
    "role": "<what they do, their words>",
    "country": "<ISO code, e.g. US, IN, GB>",
    "working_on": "<what they're building or dealing with>",
    "first_question": "<their answer from step 1>",
}, open(path, "w"), indent=1)
PY
```

One line, no explanation of the explanation: "Saved locally so I don't ask again."

## 4. Offer a key only if it would help their question

Look at what they actually asked. A consumer app question wants YouTube. A B2B question doesn't. A question about a specific company wants company records. If nothing fits, say so and move on: "Nothing here needs an extra key. Let's just run it."

When something does fit, offer it as what it gets them, never as a key name. One AskUserQuestion, multi-select, listing **only** what's relevant plus a skip:

| Offer it as | Actually | Cost |
|---|---|---|
| "See how many people watch videos about this. Good for anything consumer." | `YOUTUBE_API_KEY` | free, ~3 min |
| "Check whether a company is really registered, and since when." | `OPENCORPORATES_API_TOKEN` | free account |
| "Search GitHub 30 times a minute instead of 10. Only matters if you run a lot of checks." | `GITHUB_TOKEN` | free, ~1 min, instant if they use `gh` |
| "Reddit upvote counts and no one-a-minute wait. Reddit approves these by hand, so it can take days." | `REDDIT_CLIENT_ID` + `SECRET` | slow, rarely worth it |

Skipping is normal. Don't editorialize about it, just carry on.

### Getting one key

One at a time. Numbered steps, one screen.

**YouTube:**
1. Open https://console.cloud.google.com and sign in with any Google account.
2. Project picker at the top, then **New project**. Name it anything.
3. Open https://console.cloud.google.com/apis/library/youtube.googleapis.com and hit **Enable**.
4. **APIs & Services → Credentials → Create credentials → API key**.
5. Copy it. Starts with `AIza`. Free quota covers about 90 lookups a day.

**GitHub:** first try `gh auth token >/dev/null 2>&1 && echo HAS_GH`. If they're logged in, offer to reuse it (nothing to copy, nothing on screen) by passing `"$(gh auth token)"` as the value. Otherwise https://github.com/settings/personal-access-tokens/new, name it gutcheck, leave repository access on "Public repositories", generate.

**OpenCorporates:** https://opencorporates.com/api_accounts/new, free account, token on the account page.

**Reddit:** https://www.reddit.com/prefs/apps while logged in → **create another app** → type **script** → redirect URI `http://localhost:8080`. The client ID is the short string under the app name. If Reddit makes you apply for access, submit it; gutcheck keeps using the free feed meanwhile, so nothing breaks.

### Saving it

Offer both routes in one line:

> Paste it here and I'll save it, or if you'd rather keep it out of the chat, I'll open the file and you paste it there.

File route: `open -e ~/.config/gutcheck/.env` on macOS, otherwise name the path. They paste after the matching `=`, save, tell you they're done.

Paste route, never repeating the key back:

```bash
python3 - "YOUTUBE_API_KEY" "<value>" <<'PY'
import os, sys
key, value = sys.argv[1], sys.argv[2].strip()
path = os.path.expanduser("~/.config/gutcheck/.env")
os.makedirs(os.path.dirname(path), exist_ok=True)
lines = open(path).read().splitlines() if os.path.exists(path) else []
lines = [l for l in lines if not l.strip().startswith(key + "=")] + [f"{key}={value}"]
open(path, "w").write("\n".join(lines) + "\n")
os.chmod(path, 0o600)
print(f"saved {key} (ending ...{value[-4:]})")
PY
```

Confirm with the last four characters only, then prove it:

```bash
cd ~/.claude/skills/gutcheck && uv run server.py doctor 2>/dev/null | grep -i "<source>"
```

If it errors: YouTube 403 usually means the API isn't enabled yet (step 3), or was enabled seconds ago. GitHub 401 means a truncated or expired token. OpenCorporates "rejected" means the account isn't approved yet. Keys are read on every call, so nothing needs restarting.

## 5. Now answer their question for real

The point of the whole walkthrough. Take what they said in step 1 and research it properly: `design.md`, then `research.md`, with the thinking out loud and a real report.

If the `mcp__gutcheck__*` tools aren't in this session, **use the terminal** rather than stopping:

```bash
cd ~/.claude/skills/gutcheck && uv run server.py call reddit_signal '{"query":"meal prep app","limit":10}'
```

One call per command, same data. Say once that restarting Claude Code makes them native and quicker, then get on with it. Never end setup on "restart and try again": they installed a research tool, so they should leave having had something researched.

## 6. Leave them knowing what they have

After the report, three short lines:

> That's the whole thing. Next time just type `/gutcheck` and your question, the same way you asked this one.
>
> Add `--deep` when the decision is expensive and you want everything. For something bigger, say so and I'll design a proper study first: a case competition brief, a business plan, a market landscape, or a full write-up with method and sources.
>
> Everything stays on your machine. I keep what you check in `~/.config/gutcheck/history.jsonl`, so when you come back to a question I'll tell you what you found last time and what changed.

## If they ask

- **"Does this send my data anywhere?"** Your questions go from your machine to the sources being searched (Google, Reddit, Apple, and the sites in a web search), the same as typing them into a browser. No gutcheck server, no account, no analytics. Keys and history stay in `~/.config/gutcheck/`, readable only by you.
- **"What does it cost?"** Nothing. Every default source is free and needs no key. The optional keys have free tiers.
- **"How do I delete what it saved?"** `rm -rf ~/.config/gutcheck` removes the profile, history, and keys. Uninstall entirely with `claude mcp remove gutcheck --scope user && rm -rf ~/.claude/skills/gutcheck ~/.config/gutcheck`.
- **"Why did the health check print a source twice?"** It lists the eight sources first, then the two optional keys that raise limits rather than adding a source.
- **"Can I use this outside Claude Code?"** Yes, it's a standard MCP server; the README covers connecting Cursor, Codex, or Claude Desktop, though the research method itself is the Claude Code skill.
