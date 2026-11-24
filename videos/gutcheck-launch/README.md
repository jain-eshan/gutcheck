# gutcheck launch video

A 61-second, 1920×1080 demo for the Product Hunt and LinkedIn launch in November 2026, built with [HyperFrames](https://hyperframes.heygen.com). The terminal part replays a real gutcheck run (`raw/run2.jsonl`), condensed the way Claude Code shows it.

Published at [youtu.be/Nb1n2udLX9w](https://youtu.be/Nb1n2udLX9w), used on the Product Hunt launch (25 November 2026), and on eshanjain.com's Work card and case study.

## The story

| Time | On screen | What it says |
|---|---|---|
| 0-15 s | An idea on a sticky note, then a pile of tabs (Trends, Reddit, news, App Store, GitHub) and a clock running to 3h 42m | Checking demand by hand takes hours and ends in a hunch |
| 15-20 s | The gutcheck mark | Check your gut against the internet, inside Claude Code |
| 20-49 s | Step panel + terminal: the command, the plan, the tool calls, the report | Ask in plain words, it plans the study, pulls live evidence, gives a straight answer |
| 49-54 s | Free · No API keys · Runs on your machine | |
| 54-61 s | End card: github.com/jain-eshan/gutcheck, "Designed and built by Eshan Jain" | |

## The real run

`claude -p "/gutcheck --deep is there demand for a simple app that splits rent and bills between flatmates? Run it now without asking me anything." --model sonnet --output-format stream-json --verbose`, 24 November 2026, about 4 minutes. Verdict: **MODERATE_SIGNAL**, confidence MEDIUM. Every value in `tools/term.py` and `raw/report-excerpt.txt` is copied from that run's tool results or final report (`raw/run2-dump.txt` is a readable dump). Reddit's search feed failed in the run and the film shows that error rather than hiding it. The cause turned out to be Reddit closing its keyless feeds (fixed to say so in PR #19); Reddit now needs your own API keys. `raw/run1.jsonl` is an earlier quick-check run, not used.

## Narration

Voice: Kokoro `af_heart` (local, free) at 0.88 speed, one file per line in `assets/vo/`, word times from `hyperframes transcribe --model small.en`.

> You've got an idea. Before you spend three months building it, you want to know if anyone actually wants it. So you open Google Trends. Then Reddit. Then the news, the App Store, GitHub. Hours later, all you have is a hunch. Meet gutcheck. It checks your gut against the internet, right inside Claude Code. Type /gutcheck, and your idea, in plain words. It works out what would actually answer the question, and plans the study. Then it pulls live evidence from Google Trends, the news, both app stores, Hacker News, GitHub and the web. And you get a straight answer. A verdict, how sure it is, the case against it, and what to do this week. It's free. No API keys. And it all runs on your machine. gutcheck is open source. Check your gut, before you commit.

"gutcheck" is written as "gut check" in the text sent to the voice, so it is said as two words; captions show it as one.

## Files

Not in git: `raw/`, the narration audio (`assets/vo/*.wav`), the mix, the music and `renders/` (see `.gitignore`). The word timings in `assets/vo/*.json` are kept.


- `index.html`: the composition. `tools/build.py` writes the narration word times, the terminal script and the section timings into it.
- `tools/build.py`: mixes narration, music and sound effects (music ducked under the voice, -14 LUFS) and injects the timeline.
- `tools/term.py`: the terminal lines, chips, highlights and camera moves, from the real run.
- `raw/`: the run's stream, its dump, its final report and the excerpt shown on screen.
- `renders/gutcheck-launch.mp4` (1280×720, for the web), `gutcheck-launch-master.mp4` (1920×1080), `gutcheck-launch-poster.webp`, `gutcheck-loop.mp4` (silent 12 s card loop, 540×290).

## Rebuild

```bash
python3 tools/build.py
```

```bash
HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1 HYPERFRAMES_SKIP_SKILLS=1 npx --yes hyperframes@0.8.164 render -f 30 -o renders/gutcheck-launch-master.mp4
```

The web copy, loop and poster are cut from the master with ffmpeg (1280×720 at CRF 27; loop from 21.2-24.6 s, 30.2-35.2 s and 40.4-44.2 s, cropped to the demo and scaled to 540×290 at 20 fps; poster at 43.9 s).

## Credits

- Music: `startup.mp3` from the Lumen film's candidates, Pixabay Content License.
- Sound effects: Pixabay Content License, bundled with HyperFrames.
- Fonts: Instrument Serif and Archivo, SIL Open Font License 1.1 (`assets/fonts/LICENSE.txt`). Terminal text uses the Mac's Menlo.
