# score2md Source Routing

Use this reference when converting anything other than direct MusicXML/MXL/XML.

## Reliability Tiers

- Tier A symbolic: `.mxl`, `.musicxml`, `.xml`, `.abc`.
  Report `verified symbolic conversion` when strict counts match.
- Tier B inferred symbolic: `.mid`, `.midi`, `.kar`.
  Report `MIDI-derived conversion; pitch/timing preserved, notation inferred`.
- Tier C OMR: `.pdf`, `.png`, `.jpg`, `.jpeg`, `.tiff`, `.webp`.
  Report `OMR-derived conversion; recognition may require correction`.
- Tier D transcription: YouTube, audio, video.
  Report `audio-transcription-derived conversion; approximate score reconstruction`.

## PDF And Image

The skill adapter follows the PDF2Muse/oemer pattern:

1. Render PDF pages at roughly 300 DPI with `pypdfium2`.
2. Run oemer as a subprocess with `python -m oemer.ete`.
3. Limit OMR workers conservatively because model inference is memory-heavy.
4. Join page-level MusicXML files by appending measures.
5. Re-parse the combined MusicXML through the deterministic score2md renderer.

Do not vendor oemer checkpoints, media, UI code, or demos into this skill. Depend on installed oemer or tell the user which dependency is missing.

## MIDI

Prefer MuseScore CLI for MIDI-to-MusicXML:

```bash
MuseScore4.exe -o output.musicxml input.mid
```

Try `MuseScore4`, `MuseScore3`, `mscore`, `mscore3`, and `musescore` on PATH, plus common Windows installation paths. If MuseScore is unavailable, try `music21`. If both are unavailable, fail with a clear dependency message.

## YouTube And Audio

Use a configured oh-sheet service. Set:

```text
SCORE2MD_OHSHEET_URL=http://localhost:8000
```

For audio files:

1. Upload to `/v1/uploads/audio`.
2. Submit `/v1/jobs` with the returned audio object.
3. Poll `/v1/jobs/{job_id}`.
4. Download `/v1/artifacts/{job_id}/musicxml`.

For YouTube URLs:

1. Submit `/v1/jobs` with `title` set to the URL.
2. Poll the job.
3. Download the MusicXML artifact.

This path is transcription-derived. Never claim exact notation for audio or YouTube.
