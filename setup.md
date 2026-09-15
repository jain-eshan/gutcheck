# /gutcheck setup

A friendly walkthrough that confirms gutcheck works and optionally connects extra data sources. Assume the user may not be technical: explain each step in one plain sentence, never dump a wall of instructions, and do one thing at a time.

## 1. Make sure it's installed

```bash
ls ~/.claude/skills/gutcheck/server.py ~/.config/gutcheck/.env 2>&1
claude mcp get gutcheck 2>&1 | head -5
```

- If `server.py` is missing, gutcheck isn't installed where Claude Code looks for it. Offer to run: `git clone --depth 1 https://github.com/jain-eshan/gutcheck.git ~/.claude/skills/gutcheck && ~/.claude/skills/gutcheck/setup`.
- If `.env` is missing or `claude mcp get gutcheck` says it isn't found, run `~/.claude/skills/gutcheck/setup` and show the output.
- If the gutcheck tools (like `interest_over_time`) aren't available in this conversation but the server is registered, the user needs to restart Claude Code once. Tell them so plainly. You can still continue with steps 2-4, since they use the terminal, not the tools.

## 2. Check every source

Tell the user: "Checking each data source live. This takes up to a minute."

```bash
cd ~/.claude/skills/gutcheck && uv run server.py doctor 2>/dev/null
```

Show the result as a short table: source, status, and what it's used for. Explain the statuses:
- `ok`: working now.
- `optional`: needs a free key. gutcheck works without it.
- `error`: read the message. A rate limit (403/429) is usually temporary, so suggest trying again in a minute. For anything else, run `~/.claude/skills/gutcheck/setup` again, then re-check.

Then say what already works with no keys: Google Trends, Reddit, Google News, Wikipedia, Hacker News, GitHub, and the App Store.

## 3. Offer the optional keys

Ask with AskUserQuestion (multiSelect) which extras they want. Only list keys that aren't saved yet. Recommend YouTube first, since it's the most useful and quick to get.

| Option | What it adds | Effort |
|---|---|---|
| YouTube | View and comment counts on videos about the topic | Free, about 3 minutes |
| GitHub | Raises GitHub searches from 10 to 30 a minute | Free, about 1 minute, or instant if they use the `gh` command |
| OpenCorporates | Checks whether a named company is officially registered, and since when | Free account |
| Reddit API | Upvote and comment counts, and no one-search-a-minute limit | Free, but Reddit reviews new apps by hand, which can take days. Only worth it for heavy use |
| Skip | Use gutcheck as is | none |

If they skip, jump to step 5.

## 4. Get and save each chosen key

Handle one key at a time: give the steps, wait for the key, save it, verify it.

### Getting the key

**YouTube (`YOUTUBE_API_KEY`)**
1. Open https://console.cloud.google.com/ and sign in with any Google account.
2. At the top, click the project picker, then **New project**. Name it "gutcheck" and create it.
3. Open https://console.cloud.google.com/apis/library/youtube.googleapis.com and click **Enable**.
4. Go to **APIs & Services → Credentials → Create credentials → API key**.
5. Copy the key. It starts with `AIza`.
The free quota is 10,000 units a day, which is about 90 YouTube lookups.

**GitHub (`GITHUB_TOKEN`)**
- First run `gh auth token 2>/dev/null | head -c 4`. If that prints something, ask: "You're already logged in to GitHub's command-line tool. Want me to use that login for gutcheck?" If yes, save it without showing it: `gh auth token` piped into the save command below (replace the value argument with `"$(gh auth token)"`).
- Otherwise: open https://github.com/settings/personal-access-tokens/new, name it "gutcheck", set an expiry, leave **Repository access** on "Public repositories", click **Generate token**, and copy it.

**OpenCorporates (`OPENCORPORATES_API_TOKEN`)**
1. Open https://opencorporates.com/api_accounts/new and create a free account.
2. Once approved, copy the API token from your account page.

**Reddit (`REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET`)**
1. Open https://www.reddit.com/prefs/apps while logged in and click **create another app**.
2. Pick **script**, name it "gutcheck", set the redirect URI to `http://localhost:8080`, and create it.
3. The client ID is the short string under the app name. The secret is labeled **secret**.
4. If Reddit asks you to apply for API access, submit the form. Until you're approved, gutcheck keeps using the keyless Reddit feed, so nothing breaks.

### Saving the key

Offer two ways and let the user choose:

1. **Paste it here.** Mention that it will be in this chat's history. Save it with the command below. Never repeat the key back; confirm with the last 4 characters only.
2. **Edit the file yourself** (keeps the key out of the chat). Run `open -e ~/.config/gutcheck/.env` on macOS, or tell them to open that file in any text editor. They paste the value after the matching `=` and save. Then they tell you they're done.

Save command (adds the key, or replaces it if one is already saved, and keeps the file private):

```bash
python3 - "YOUTUBE_API_KEY" "<value>" <<'PY'
import os, sys
key, value = sys.argv[1], sys.argv[2].strip()
path = os.path.expanduser("~/.config/gutcheck/.env")
os.makedirs(os.path.dirname(path), exist_ok=True)
lines = open(path).read().splitlines() if os.path.exists(path) else []
lines = [l for l in lines if not l.strip().startswith(key + "=")] + [f"{key}={value}"]
with open(path, "w") as f:
    f.write("\n".join(lines) + "\n")
os.chmod(path, 0o600)
print(f"saved {key} (ending ...{value[-4:]})")
PY
```

### Verifying

Re-run the doctor (step 2) and confirm that source now shows `ok`. If it shows an error:
- YouTube `403`: the API usually isn't enabled on that project yet (step 3 of the YouTube instructions), or it was enabled less than a few minutes ago.
- GitHub `401`: the token was copied incompletely or has expired.
- OpenCorporates "rejected": the account isn't approved yet or the token is wrong.

Keys are read fresh on every call, so there's no need to restart after saving one.

## 5. Finish

Say it's ready, in one line, then suggest three first checks tailored to anything you know about the user (fall back to these):

- `/gutcheck is there demand for a simpler meal-planning app for busy parents?`
- `/gutcheck freelancers keep getting paid late, how common is this and what actually works?`
- `/gutcheck should I learn Rust or Go in 2026?`

Mention that `--deep` pulls in more sources (YouTube, GitHub, App Store, Product Hunt) and that `/gutcheck upgrade` updates gutcheck.
