#!/usr/bin/env python3
"""Build the portable packages into dist/.

  dist/gutcheck-knowledge.md   every instruction file merged, for hosts that can't
                               open sibling files (ChatGPT knowledge, a Claude Project)
  dist/chatgpt-instructions.txt  short prompt for a Custom GPT (limit 8000 chars)
  dist/gutcheck-skill.zip      for claude.ai: Settings > Capabilities > Skills > Upload

Run: python3 scripts/bundle.py
"""
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
GPT_LIMIT = 8000
ORDER = ["SKILL.md", "design.md", "research.md",
         "references/study-types.md", "references/research-craft.md",
         "references/reading-signals.md", "references/playbooks.md",
         "references/web-only.md"]
SKILL_FILES = ORDER + ["setup.md", "server.py", "pyproject.toml", "VERSION", "LICENSE",
                       "scripts/check_update.sh"]


def main():
    DIST.mkdir(exist_ok=True)

    parts = ["# gutcheck knowledge file\n\nEach section below is one file of the gutcheck skill. "
             "Where an instruction says to read a file by name, read that section.\n"]
    for name in ORDER:
        body = (ROOT / name).read_text()
        body = re.sub(r"\A---\n.*?\n---\n", "", body, flags=re.S)  # drop frontmatter
        parts.append(f"\n\n{'=' * 60}\n# FILE: {name}\n{'=' * 60}\n\n{body.strip()}\n")
    (DIST / "gutcheck-knowledge.md").write_text("".join(parts))

    instructions = (ROOT / "chatgpt" / "instructions.txt").read_text()
    if len(instructions) > GPT_LIMIT:
        sys.exit(f"chatgpt/instructions.txt is {len(instructions)} chars; Custom GPT limit is {GPT_LIMIT}")
    (DIST / "chatgpt-instructions.txt").write_text(instructions)

    with zipfile.ZipFile(DIST / "gutcheck-skill.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for name in SKILL_FILES:
            if (ROOT / name).exists():
                z.write(ROOT / name, f"gutcheck/{name}")

    for f in sorted(DIST.iterdir()):
        print(f"{f.name}: {f.stat().st_size:,} bytes")
    print(f"instructions: {len(instructions)}/{GPT_LIMIT} chars")


if __name__ == "__main__":
    main()
