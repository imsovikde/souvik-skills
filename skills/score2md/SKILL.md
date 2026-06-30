---
name: score2md
description: Deterministically convert music sources into one playable Markdown ABC file. Use when Codex needs to convert MusicXML, MXL, XML, ABC, MIDI, PDF sheet music, score images, audio, video, or YouTube links into Markdown-safe ABC notation while preserving symbolic notes, rests, chords, RH/LH piano voices, tempo, key, meter, ties, grace notes, repeats, and verification reports.
---

# score2md

Convert supported music sources into a single Markdown file containing one playable ABC fenced code block. Always prefer deterministic conversion from symbolic source files over manual note writing.

## Source Policy

1. Never invent notes when a symbolic source is available.
2. Convert exact copyrighted music only from user-provided or otherwise authorized source material.
3. Treat PDF/image output as OMR-derived and audio/YouTube output as transcription-derived.
4. Use original composition mode only when the user explicitly asks for new music rather than conversion.

## Primary Command

Run from the repository root or from any project with the skill installed:

```bash
python skills/score2md/scripts/score2md.py convert INPUT --out OUTPUT.md --verify strict
```

Useful subcommands:

```bash
python skills/score2md/scripts/score2md.py inspect INPUT
python skills/score2md/scripts/score2md.py to-musicxml INPUT --out score.musicxml
python skills/score2md/scripts/score2md.py musicxml-to-md score.musicxml --out score.md
python skills/score2md/scripts/score2md.py verify score.musicxml score.md
```

The converter writes:

- `OUTPUT.md`: the final Markdown ABC file.
- `OUTPUT.abc`: the raw ABC body.
- `OUTPUT.md.verify.json`: conversion counts, status, warnings, and limitations.

## Routing

Use the built-in converter for:

- `.mxl`, `.musicxml`, `.xml`: parse directly and verify symbolically.
- `.abc`: normalize/wrap into the Markdown house style.
- `.mid`, `.midi`, `.kar`: convert through MuseScore CLI when available, then parse MusicXML.

Use adapters for:

- `.pdf`: render pages to images, run an installed OMR backend, join MusicXML, then convert.
- `.png`, `.jpg`, `.jpeg`, `.tiff`, `.webp`: run an installed OMR backend, then convert.
- YouTube/audio/video: call a configured oh-sheet service and download its MusicXML artifact; local video is extracted to WAV first.

Read `references/source-routing.md` before working on PDF/image/audio/YouTube paths.
Read `references/abc-markdown.md` before debugging ABC rendering or manually inspecting output.

## Required Markdown Shape

The final `.md` file must contain only one ABC fenced block:

````markdown
```abc
X:1
T:Song Title
C:Composer Or Arranger
M:4/4
Q:1/4=120
L:1/16
%%score {RH LH}
V:RH clef=treble name="Piano RH"
V:LH clef=bass name="Piano LH"
K:Em
[V:RH] note tokens here |
[V:LH] note tokens here |]
```
````

Never insert a blank line after `K:`. Do not wrap the actual output file in another Markdown code block.

## Reliability Labels

Report conversion status honestly:

- `verified symbolic conversion`: MusicXML/MXL/XML/ABC note/rest counts match the source model.
- `MIDI-derived conversion; pitch/timing preserved, notation inferred`: MIDI required notation inference.
- `OMR-derived conversion; recognition may require correction`: PDF/image required recognition.
- `audio-transcription-derived conversion; approximate score reconstruction`: audio/YouTube required transcription.

Never call OMR or audio output exact.

## Verification

After converting, inspect the verification summary. For symbolic files, strict verification must compare source model counts against the rendered model counts. If strict verification fails, fix the conversion or report the mismatch.

When the skill itself changes, run:

```bash
python skills/score2md/scripts/run_tests.py
npm run validate:skills
npm run build
node bin/souvik-skills.cjs install score2md --force
```

After installing locally, remind the user to restart Codex.
