# Evidence-Driven Stream Inspection & Manifest Probing (REA Method)

This guide documents the evidence-first methodology adopted from REA (*Reverse Engineer Anything*) for probing public media URLs before initiating high-bandwidth downloads.

---

## 1. The REA Evidence Principle

In complex media streaming architectures, never assume stream availability, codecs, or bitrate tiers based purely on URL substrings. Instead, apply the REA evidence workflow:

1. **Passive Probing**: Inspect public manifest headers and structural descriptors without altering the target environment.
2. **Separation of Concerns**: Strictly differentiate between **Confirmed Observations** (data returned directly from HTTP response headers and manifest files) and **Inferred Constraints** (heuristics regarding optimal container formats and player compatibility).
3. **Reproducibility**: Record cryptographic SHA-256 hashes of manifest headers and sample media chunks to preserve an immutable audit trail.

---

## 2. Manifest Formats & Structural Decomposition

### A. Apple HTTP Live Streaming (HLS — `.m3u8`)
HLS delivers media via M3U playlists referencing segmented transport streams (`.ts` or fragmented `.mp4`).

- **Master Playlist Structure**:
  ```m3u8
  #EXTM3U
  #EXT-X-VERSION:6
  #EXT-X-STREAM-INF:BANDWIDTH=6000000,RESOLUTION=1920x1080,CODECS="avc1.64002a,mp4a.40.2",FRAME-RATE=60.000
  1080p/index.m3u8
  #EXT-X-STREAM-INF:BANDWIDTH=3500000,RESOLUTION=1280x720,CODECS="avc1.4d401f,mp4a.40.2",FRAME-RATE=30.000
  720p/index.m3u8
  ```
- **Probing Checklist**:
  - Verify `Content-Type: application/vnd.apple.mpegurl` or `application/x-mpegURL`.
  - Parse `#EXT-X-STREAM-INF` to extract exact bitrate tiers, frame rates, and codec strings (`avc1` for H.264, `hvc1` for HEVC, `av01` for AV1).
  - Test chunk reachability by requesting the first 100 KB using an HTTP `Range: bytes=0-102400` request.

### B. Dynamic Adaptive Streaming over HTTP (MPEG-DASH — `.mpd`)
DASH uses XML Media Presentation Description (`.mpd`) documents.

- **Manifest XML Structure**:
  ```xml
  <MPD xmlns="urn:mpeg:dash:schema:mpd:2011" minBufferTime="PT1.5S">
    <Period>
      <AdaptationSet contentType="video" mimeType="video/mp4" codecs="av01.0.08M.08">
        <Representation id="video_4k" bandwidth="15000000" width="3840" height="2160" frameRate="60"/>
        <Representation id="video_1080p" bandwidth="4500000" width="1920" height="1080" frameRate="60"/>
      </AdaptationSet>
      <AdaptationSet contentType="audio" mimeType="audio/mp4" codecs="mp4a.40.2">
        <Representation id="audio_en" bandwidth="128000"/>
      </AdaptationSet>
    </Period>
  </MPD>
  ```
- **Probing Checklist**:
  - Verify `Content-Type: application/dash+xml`.
  - Extract `<AdaptationSet>` definitions for separated video and audio tracks.
  - Determine initialization segment URLs (`<Initialization sourceURL="..."/>`).

---

## 3. DOM & Metadata Discovery (HTML5 Fallback)

When standard platform extractors are not applicable (e.g. self-hosted landing pages or public web archives), `probe_stream.py` inspects the public DOM:

1. **HTML5 `<video>` Elements**:
   ```html
   <video controls preload="metadata">
     <source src="https://cdn.example.org/video-1080p.mp4" type="video/mp4">
     <source src="https://cdn.example.org/manifest.m3u8" type="application/x-mpegURL">
   </video>
   ```
2. **OpenGraph & Twitter Card Metadata**:
   - `<meta property="og:video" content="https://...">`
   - `<meta property="og:video:type" content="video/mp4">`
   - `<meta name="twitter:player:stream" content="https://...">`
3. **Embedded JSON-LD**:
   - Scan for `"@type": "VideoObject"` containing `"contentUrl"` or `"embedUrl"`.

---

## 4. Cryptographic Observation Verification

To ensure reproducibility across sessions:
- For discovered manifests, `probe_stream.py` reads the initial 64 KB and computes:
  $$\text{Manifest Hash} = \text{SHA-256}(\text{Initial Chunk Bytes})$$
- This confirms that downstream downloads operate against the identical version probed in the preliminary inspection stage.
