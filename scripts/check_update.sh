#!/usr/bin/env bash
# check_update.sh - is the installed copy behind GitHub?
#
# Run once per /gutcheck invocation. Throttled, quiet, and never fatal: a
# research question must not fail because GitHub is slow or the machine is
# offline.
#
# Output (nothing, or one line each):
#   UPDATE_AVAILABLE <n> <short-sha> <subject of the newest commit>
#   LOCAL_CHANGES                 - the install has uncommitted edits, so a
#                                   pull would clobber them. Never auto-update.
#   DETACHED <branch>             - not on main; leave it alone.
#
# Env overrides (testing):
#   GUTCHECK_STATE_DIR        - state dir, default ~/.config/gutcheck
#   GUTCHECK_UPDATE_INTERVAL  - throttle seconds, default 86400. 0 = always check.
set -uo pipefail

STATE_DIR="${GUTCHECK_STATE_DIR:-$HOME/.config/gutcheck}"
CACHE_FILE="$STATE_DIR/last-update-check"
INTERVAL="${GUTCHECK_UPDATE_INTERVAL:-86400}"
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"

mkdir -p "$STATE_DIR" 2>/dev/null || exit 0

NOW=$(date +%s)
if [ "$INTERVAL" -gt 0 ] && [ -f "$CACHE_FILE" ]; then
  LAST=$(cat "$CACHE_FILE" 2>/dev/null || echo 0)
  [ $(( NOW - LAST )) -lt "$INTERVAL" ] && exit 0
fi
# Record the attempt before the network call, so a hang or failure still
# throttles the next run instead of retrying on every invocation.
echo "$NOW" > "$CACHE_FILE" 2>/dev/null || true

# A git install (the normal one) compares commits. A zip download has no git
# metadata, so fall back to the VERSION file.
if ! git -C "$REPO_DIR" rev-parse --git-dir >/dev/null 2>&1; then
  LOCAL_VERSION=$(tr -d '[:space:]' < "$REPO_DIR/VERSION" 2>/dev/null)
  REMOTE_VERSION=$(curl -fsSL --max-time 5 \
    "https://raw.githubusercontent.com/jain-eshan/gutcheck/main/VERSION" 2>/dev/null | tr -d '[:space:]')
  [ -n "$LOCAL_VERSION" ] && [ -n "$REMOTE_VERSION" ] && [ "$LOCAL_VERSION" != "$REMOTE_VERSION" ] &&
    echo "UPDATE_AVAILABLE ? $REMOTE_VERSION version $REMOTE_VERSION is out (you have $LOCAL_VERSION)"
  exit 0
fi

BRANCH=$(git -C "$REPO_DIR" branch --show-current 2>/dev/null)
if [ "$BRANCH" != "main" ]; then
  echo "DETACHED ${BRANCH:-unknown}"
  exit 0
fi

# Bound the fetch: abort a transfer stalled under 1KB/s for 5s rather than
# leaving someone staring at a frozen prompt.
git -C "$REPO_DIR" -c http.lowSpeedLimit=1000 -c http.lowSpeedTime=5 \
  fetch --quiet origin main 2>/dev/null || exit 0

BEHIND=$(git -C "$REPO_DIR" rev-list --count HEAD..FETCH_HEAD 2>/dev/null || echo 0)
[ "${BEHIND:-0}" -gt 0 ] 2>/dev/null || exit 0

SHA=$(git -C "$REPO_DIR" rev-parse --short FETCH_HEAD 2>/dev/null)
SUBJECT=$(git -C "$REPO_DIR" log -1 --format=%s FETCH_HEAD 2>/dev/null)
echo "UPDATE_AVAILABLE $BEHIND $SHA $SUBJECT"

[ -n "$(git -C "$REPO_DIR" status --porcelain 2>/dev/null)" ] && echo "LOCAL_CHANGES"
exit 0
