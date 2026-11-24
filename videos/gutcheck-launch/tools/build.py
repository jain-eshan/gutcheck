#!/usr/bin/env python3
"""Builds the gutcheck launch video's soundtrack and the timeline injected into index.html.
Run from videos/gutcheck-launch: python3 tools/build.py
Inputs: assets/vo/s*.wav + s*.json (Kokoro af_heart narration and its word times), raw/run2.jsonl (the real gutcheck run,
replayed in the terminal via tools/term.py), assets/music/startup.mp3 (Pixabay)."""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import term

SFX = Path.home() / ".claude/video-kit/hyperframes/media-use/audio/assets/sfx"
END = 61.0
# narration line: (file, place at)
VO = [("s1", 0.30), ("s2", 6.85), ("s3", 12.35), ("s4", 15.05), ("s5", 21.0), ("s6", 25.2), ("s7", 30.0),
      ("s8", 38.0), ("s9", 49.3), ("s10", 54.2)]
SFXS = [("whoosh-short", 0.25, 20.45), ("pop", 0.25, 15.1), ("chime", 0.2, 54.15)]
FIX = {"gut": None}  # "gut check" is spoken as two words; shown as one

def run(*a):
    subprocess.run(a, check=True, cwd=ROOT)

def dur(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], cwd=ROOT))

def words():
    out = []
    for name, at in VO:
        ws = json.loads((ROOT / f"assets/vo/{name}.json").read_text())
        toks = []
        for w in ws:
            for part in re.split(r"(?<=—)", w["text"]):  # "answer—a" -> two words
                if part: toks.append([part.replace("—", "."), round(at + w["start"], 3)])
        i = 0
        while i < len(toks):
            t, s = toks[i]
            nx = toks[i + 1][0] if i + 1 < len(toks) else ""
            if t.lower() == "slash" and nx.lower() == "gut":
                toks[i:i + 3] = [["/gutcheck" + re.sub(r"[\w]", "", toks[i + 2][0]), s]]
            elif t.lower() == "gut" and re.sub(r"\W", "", nx).lower() == "check":
                toks[i:i + 2] = [["gutcheck" + re.sub(r"[\w]", "", nx), s]]
            i += 1
        fix = {"app": "App", "store,": "Store,", "store": "Store", "stores,": "stores,", "Trends.": "Trends,", "The": "the"}
        for j, (t, s) in enumerate(toks):
            prev = toks[j - 1][0] if j else ""
            if t in ("The",) and prev == "Trends,": t = "the"
            elif t == "Trends." and name == "s7": t = "Trends,"
            elif t.lower() == "app" and j + 1 < len(toks) and toks[j + 1][0].lower().startswith("store"): t = "App" if toks[j + 1][0].startswith("s") is False or True else t
            elif t.lower().startswith("store") and prev == "App": t = "Store" + t[5:]
            toks[j][0] = t
        if name == "s7":  # "both app stores" stays lower case
            for w in toks:
                if w[0] in ("App", "Stores,"): w[0] = w[0].lower()
        for j, w in enumerate(toks):  # sentence case after a full stop
            if (j == 0 or toks[j - 1][0].endswith(".")) and w[0][0].islower() and not w[0].startswith("gutcheck"):
                w[0] = w[0][0].upper() + w[0][1:]
        out += toks
    return out

def mix():
    ins, f, v = [], [], []
    for i, (name, at) in enumerate(VO):
        ins += ["-i", f"assets/vo/{name}.wav"]; ms = int(at * 1000)
        f.append(f"[{i}:a]aresample=48000,adelay={ms}|{ms}[v{i}]"); v.append(f"[v{i}]")
    n = len(VO)
    ins += ["-i", "assets/music/startup.mp3"]
    x = []
    for j, (name, vol, at) in enumerate(SFXS):
        ins += ["-i", str(SFX / f"{name}.mp3")]; ms = int(at * 1000)
        f.append(f"[{n+1+j}:a]aresample=48000,volume={vol},adelay={ms}|{ms}[x{j}]"); x.append(f"[x{j}]")
    # music: 39.4 s track, looped once with a crossfade so it covers the film, fade out on the end card
    f.append(f"[{n}:a]aresample=48000,asplit=2[m1][m2];[m1]atrim=0:39.0,asetpts=PTS-STARTPTS[ma];[m2]atrim=8.0,asetpts=PTS-STARTPTS[mb];"
             f"[ma][mb]acrossfade=d=1.5,atrim=0:{END},volume=0.24,afade=t=out:st={END-2.0}:d=2.0[mus]")
    f.append(f"{''.join(v)}amix=inputs={len(v)}:normalize=0,apad=whole_dur={END},asplit=2[sp][key]")
    f.append("[mus][key]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=400[duck]")
    f.append(f"{''.join(x)}amix=inputs={len(x)}:normalize=0[fx]")
    f.append(f"[sp][duck][fx]amix=inputs=3:normalize=0,atrim=0:{END},loudnorm=I=-14:TP=-1.5:LRA=11[out]")
    (ROOT / "assets/audio").mkdir(parents=True, exist_ok=True)
    run("ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(f), "-map", "[out]", "-ar", "48000", "-ac", "2", "assets/audio/mix.wav")
    print("mix done")

def inject():
    ws = words()
    at = dict(VO)
    ends = {name: round(at[name] + dur(f"assets/vo/{name}.wav"), 3) for name, _ in VO}
    marks = {"s2": at["s2"], "s2end": ends["s2"], "s3": at["s3"], "s3end": ends["s3"], "s4": at["s4"],
             "demo": 20.6, "demoEnd": 48.9, "s9": at["s9"], "s10": at["s10"]}
    steps = [[20.6, at["s6"] - 0.1], [at["s6"] - 0.1, at["s7"] - 0.2], [at["s7"] - 0.2, at["s8"] - 0.2], [at["s8"] - 0.2, 48.9]]
    tl = {"words": ws, "marks": marks, "steps": steps, "end": END}
    TERM = term.build(ws, marks, steps)
    html = (ROOT / "index.html").read_text()
    html = re.sub(r"const TL = .*?; // TL", lambda _: "const TL = " + json.dumps(tl, ensure_ascii=False) + "; // TL", html, flags=re.S)
    html = re.sub(r"const TERM = .*?; // TERM", lambda _: "const TERM = " + json.dumps(TERM, ensure_ascii=False) + "; // TERM", html, flags=re.S)
    html = re.sub(r'data-duration="[\d.]+"', f'data-duration="{END}"', html)
    (ROOT / "index.html").write_text(html)
    print("timeline injected:", len(ws), "words,", len(TERM["lines"]), "terminal lines")

if __name__ == "__main__":
    mix(); inject()
