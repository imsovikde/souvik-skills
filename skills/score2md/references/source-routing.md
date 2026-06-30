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
2. Run an installed OMR backend as a subprocess.
3. Limit OMR workers conservatively because model inference is memory-heavy.
4. Join page-level MusicXML files by appending measures.
5. Re-parse the combined MusicXML through the deterministic score2md renderer.

OMR backend discovery tries, in order:

```text
--omr-module
SCORE2MD_OMR_MODULE
oemer.ete
omr_parser.ete
oemer
omr_parser
```

Do not vendor oemer/omr_parser checkpoints, media, UI code, or demos into this skill. Depend on an installed OMR package or tell the user which dependency is missing.

## MIDI

Prefer MuseScore CLI for MIDI-to-MusicXML:

```bash
MuseScore4.exe -o output.musicxml input.mid
```

Try `MuseScore4`, `MuseScore3`, `mscore`, `mscore3`, and `musescore` on PATH, plus common Windows installation paths. If MuseScore is unavailable, try `music21`. If both are unavailable, fail with a clear dependency message.

## YouTube And Audio

Use the resource-saving preflight before calling a configured oh-sheet service. Set:

```text
SCORE2MD_OHSHEET_URL=http://localhost:8000
```

Optional controls:

```text
--ohsheet-timeout 900
--ohsheet-prefer-clean-source
--no-ohsheet-prefer-clean-source
--max-media-duration 900
--allow-uncertain-audio
--skip-preflight
```

Default behavior protects transcription resources. It rejects before `/v1/jobs` when metadata, filename, duration, or captions indicate:

- podcast, interview, lecture, webinar, conference, news, vlog, sermon, speech, audiobook, commentary, documentary, reaction, or other spoken-word content
- non-music or not-confidently-music sources
- live streams
- media longer than `--max-media-duration` seconds
- non-piano-looking sources while `--mode compact-piano` is requested

`--allow-uncertain-audio` permits sources that are merely uncertain, such as missing positive metadata, but still blocks clear spoken/non-music rejects. `--skip-preflight` bypasses the guard entirely and should be used only when the user intentionally accepts the transcription cost.

The preflight writes `<cache>/preflight.json`; successful oh-sheet submissions write `<cache>/ohsheet-job.json`; successful normalization writes `<cache>/normalized.musicxml`. Unless `--refresh-cache` is passed, these files prevent duplicate metadata fetches, duplicate `/v1/jobs` submissions, and duplicate transcription for the same source/options.

For audio files:

1. Upload to `/v1/uploads/audio`.
2. Submit `/v1/jobs` with the returned audio object.
3. Poll `/v1/jobs/{job_id}`.
4. Download `/v1/artifacts/{job_id}/musicxml`.

For local video files:

1. Convert the video to a temporary WAV file with `ffmpeg`.
2. Upload the WAV to `/v1/uploads/audio`.
3. Submit, poll, and download the MusicXML artifact as with audio.

Set `SCORE2MD_FFMPEG_PATH` or pass `--ffmpeg-path` when `ffmpeg` is not on PATH.

For YouTube URLs:

1. Fetch lightweight metadata through oEmbed and the watch page when possible.
2. Inspect title, description, duration, and available caption text.
3. Fail safely when metadata cannot be fetched or confidence is too low.
4. Submit `/v1/jobs` with `title` set to the URL only after preflight approval or explicit override.
5. Poll the job.
6. Download the MusicXML artifact.

Non-YouTube HTTP/HTTPS URLs are intentionally rejected in this version. Download direct media URLs to local files before converting.

This path is transcription-derived. Never claim exact notation for audio, video, or YouTube.

## Cache

Non-symbolic normalization writes to:

```text
<output-dir>/.score2md-cache/<hash>/normalized.musicxml
```

The hash uses chunked file hashing plus conversion options so large PDFs and media files do not load fully into memory. Reuse the cached MusicXML by default; pass `--refresh-cache` to rerun OMR, transcription, or media extraction for the same source and options.
