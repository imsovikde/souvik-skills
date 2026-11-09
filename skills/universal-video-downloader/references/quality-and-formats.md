# Format Selection Matrix, Codec Compatibility & Stream Merging

This reference provides technical details on video/audio stream formats, container selection, and `ffmpeg` merging protocols used by `universal-video-downloader`.

---

## 1. Quality Selection Matrix

Modern media platforms separate high-resolution video streams from audio streams (Dynamic Adaptive Streaming). The downloader automatically selects and merges the best available pairs:

| Quality Flag | Target Resolution | Typical Dimensions | Target FPS | Bitrate Range | Recommended Video Codec |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`2160p`** / **`4k`** | 4K Ultra HD | 3840 x 2160 | 60 / 30 | 12 - 25 Mbps | AV1 (`av01`) / VP9 |
| **`1440p`** / **`2k`** | Quad HD | 2560 x 1440 | 60 / 30 | 6 - 12 Mbps | AV1 (`av01`) / VP9 |
| **`1080p`** | Full HD | 1920 x 1080 | 60 / 30 | 2.5 - 6 Mbps | AV1 / AVC1 (H.264) |
| **`720p`** | HD | 1280 x 720 | 60 / 30 | 1.2 - 2.5 Mbps | AVC1 (H.264) |
| **`480p`** | Standard Definition | 854 x 480 | 30 | 500 - 900 kbps | AVC1 (H.264) |
| **`360p`** | Low Bandwidth | 640 x 360 | 30 | 300 - 500 kbps | AVC1 (H.264) |
| **`best`** | Platform Maximum | Maximum available | Native | Native | Best available |

---

## 2. Video & Audio Codec Evaluation

### Video Codecs
1. **AOMedia Video 1 (AV1 — `av01`)**:
   - Best compression efficiency (30% better than VP9, 50% better than H.264).
   - Supported natively in MP4, MKV, and WebM containers.
   - Hardware accelerated on modern Intel Arc, AMD RDNA3, NVIDIA RTX 30/40+, and Apple M3/M4 GPUs.
2. **VP9 (`vp09`)**:
   - High-efficiency open video codec commonly deployed for 1440p and 4K streams.
   - Supported in WebM and MKV, and in MP4 via modern muxers.
3. **Advanced Video Coding (H.264 / AVC — `avc1`)**:
   - Universal baseline compatibility across all legacy hardware, embedded decoders, and smart TVs.

### Audio Codecs
1. **Opus (`opus`)**:
   - Standard for modern dynamic streaming (48 kHz sample rate, transparent quality at 128-160 kbps).
2. **Advanced Audio Coding (AAC — `mp4a.40.2`)**:
   - The universal standard audio codec for MP4 containers.
3. **MP3 (`mp3`)**:
   - Used for standalone audio extraction (`-a` / `--audio-only`) with LAME VBR Quality 0 (~245 kbps).

---

## 3. Container Formats

| Container | Ext | Native Stream Support | Subtitles Support | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **MP4** | `.mp4` | H.264, H.265, AV1, AAC, Opus | Mov_text (embedded) | Universal cross-device compatibility |
| **MKV** | `.mkv` | Any video/audio codec | SubRip, ASS, VobSub | Archival with multi-track audio & complex subs |
| **WebM** | `.webm` | VP8, VP9, AV1, Vorbis, Opus | WebVTT | Open web standards |

---

## 4. Stream Multiplexing & FFmpeg Engine Rules

When combining separate video and audio streams, `download_video.py` performs **lossless multiplexing**:
- Video and audio streams are copied directly into the container (`-c copy`) without re-encoding, eliminating generational quality loss and ensuring maximum speed.
- If AAC audio is extracted from an ADTS stream into an MP4 container, the bitstream filter `-bsf:a aac_adtstoasc` is applied to ensure standard container compliance.
- Multi-fragment downloads use `--concurrent-fragments 4` to download separate byte ranges simultaneously.
