---
name: universal-video-downloader
description: Universal multi-quality video and media stream downloader supporting YouTube, Vimeo, Twitch, and direct public HLS/DASH/HTML5 streams with REA-style evidence probing, multi-resolution selection (4K/2160p, 1440p, 1080p, 720p, audio-only MP3), lossless stream merging, archive resume tracking, and conditional 18+ verification for adult content. Use when asked to probe, inspect, analyze, or download any publicly accessible video, playlist, or media stream across any website or direct URL.
---

# Universal Video Downloader

A production-grade, multi-script skill combining the multi-platform capabilities of `yt-dlp` with the evidence-first reverse-engineering methodology of **REA** (*Reverse Engineer Anything*).

Supports YouTube, Vimeo, Twitch, SoundCloud, and any public domain hosting direct HTML5, HLS (`.m3u8`), or MPEG-DASH (`.mpd`) video streams.

---

## Architecture & Workflow Pipeline

Downloads follow a deterministic three-stage pipeline governed by a conditional compliance gate:

```text
[Public Video URL]
        │
        ▼
Stage 1: Conditional 18+ Compliance Check (`scripts/verify_compliance.py`)
        │
        ├──> [General Audience Media (age_limit < 18)] ──> AUTO-PASS (Immediate Access)
        └──> [Explicit / Age-Gated Media (age_limit >= 18)] ──> Enforces 18+ Adult Confirmation
        ▼
Stage 2: REA Evidence Probing (`scripts/probe_stream.py`)
        │   - Queries yt-dlp format matrices (4K, 1440p, 1080p, AV1, VP9, Opus)
        │   - Probes public HTML5 <video>, HLS (.m3u8), and DASH (.mpd) manifests
        │   - Computes manifest SHA-256 hashes and HTTP status codes
        ▼
Stage 3: Multi-Quality Download & Verification (`scripts/download_video.py`)
        │   - Multi-fragment stream acceleration (4 workers)
        │   - Lossless audio/video multiplexing via FFmpeg
        │   - Resumable archive tracking (.download_archive.txt)
        │   - Computes output SHA-256 checksum and verifies streams
        ▼
[Verified Production Media in Downloads]
```

---

## Quick Start (Step-by-Step)

### Standard (General Audience) Videos
For normal public videos (YouTube, Dailymotion, Vimeo, etc.), **no 18+ prompt or confirmation is required**. You can probe and download directly:

```bash
# 1. Inspect streams and available resolutions (REA probe)
python scripts/probe_stream.py --url "https://www.youtube.com/watch?v=VIDEO_ID"

# 2. Download in full high quality (1080p / 4K MP4)
python scripts/download_video.py "https://www.youtube.com/watch?v=VIDEO_ID" -q best -f mp4 -o "./downloads"
```

### Age-Restricted (18+ / Adult) Videos
If a video is age-restricted (`age_limit >= 18`), provide adult confirmation directly in the prompt or command:

```bash
# Direct confirmation flag:
python scripts/download_video.py "https://example.com/video" --confirm-adult-18plus -q best -o "./downloads"

# Or generate a reusable signed attestation token:
python scripts/verify_compliance.py --url "https://example.com/video" --confirm-adult-18plus --signature "Your Name"
```

---

## Detailed Options & Capabilities

### Quality Settings (`-q` / `--quality`)
- `best` (default): Highest resolution available on the platform (4K, 1440p, or 1080p60).
- `2160p`: 4K Ultra HD (3840 x 2160).
- `1440p`: Quad HD / 2K (2560 x 1440).
- `1080p`: Full HD (1920 x 1080).
- `720p`: Standard HD (1280 x 720).
- `480p`, `360p`, `worst`.

### Container Formats (`-f` / `--format`)
- `mp4` (default): Universal compatibility (AV1/H.264 + AAC/Opus).
- `mkv`: Matroska container for complex subtitle streams and multiple audio tracks.
- `webm`: Royalty-free web container (VP9/AV1 + Opus).

### Audio Extraction (`-a` / `--audio-only`)
Extracts the highest-bitrate audio track and encodes it into standalone MP3:
```bash
python scripts/download_video.py "URL" -a -o "./downloads"
```

### Subtitles & Captions (`-s` / `--subtitles`)
Downloads and embeds all public and auto-generated subtitles into the video container:
```bash
python scripts/download_video.py "URL" -s -o "./downloads"
```

### Playlist Downloading (`--playlist`)
By default, the downloader safely processes single videos. To download an entire playlist:
```bash
python scripts/download_video.py "PLAYLIST_URL" --playlist -o "./downloads/Playlist_Name"
```
Maintains `.download_archive.txt` so interrupted or recurring downloads skip previously downloaded videos in seconds.

---

## Reference Guides

For deep technical specifications, consult the companion guides:
- [Evidence Probing & REA Workflow](references/evidence-and-probing.md)
- [Quality Matrices & Codec Selection](references/quality-and-formats.md)
- [Compliance Gate & Conditional 18+ Protocol](references/compliance-gate.md)
