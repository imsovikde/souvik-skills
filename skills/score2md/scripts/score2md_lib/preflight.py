from __future__ import annotations

import html
import json
import os
import re
import shutil
import subprocess
import time
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


class PreflightError(RuntimeError):
    pass


@dataclass
class PreflightDecision:
    source: str
    source_type: str
    status: str
    approved: bool
    confidence: float
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PreflightDecision":
        return cls(
            source=str(data.get("source", "")),
            source_type=str(data.get("source_type", "")),
            status=str(data.get("status", "uncertain")),
            approved=bool(data.get("approved", False)),
            confidence=float(data.get("confidence", 0.0)),
            reasons=list(data.get("reasons", [])),
            warnings=list(data.get("warnings", [])),
            metadata=dict(data.get("metadata", {})),
            created_at=float(data.get("created_at", time.time())),
        )


NEGATIVE_TERMS = {
    "podcast",
    "interview",
    "lecture",
    "keynote",
    "conference",
    "webinar",
    "news",
    "vlog",
    "daily vlog",
    "talk show",
    "debate",
    "discussion",
    "panel discussion",
    "sermon",
    "speech",
    "audiobook",
    "spoken word",
    "commentary",
    "documentary",
    "explained",
    "explainer",
    "reaction",
    "storytime",
}

POSITIVE_MUSIC_TERMS = {
    "music",
    "song",
    "instrumental",
    "piano",
    "keyboard",
    "synthesia",
    "sheet music",
    "score",
    "midi",
    "cover",
    "performance",
    "arrangement",
    "orchestra",
    "sonata",
    "nocturne",
    "prelude",
    "etude",
    "waltz",
    "concerto",
    "fugue",
    "bach",
    "beethoven",
    "chopin",
    "mozart",
    "liszt",
    "debussy",
    "rachmaninoff",
}

PIANO_SCORE_TERMS = {
    "piano",
    "keyboard",
    "synthesia",
    "sheet music",
    "piano cover",
    "solo piano",
    "piano tutorial",
    "piano arrangement",
    "piano score",
}

SPOKEN_TRANSCRIPT_MARKERS = {
    "welcome back",
    "today we are",
    "today we're",
    "in this episode",
    "our guest",
    "thanks for watching",
    "subscribe",
    "like and subscribe",
    "let's talk",
    "i'm joined",
    "breaking news",
    "this lecture",
    "this podcast",
    "the interview",
    "question is",
}

DEFAULT_MAX_MEDIA_DURATION_SECONDS = 15 * 60
LARGE_LOCAL_MEDIA_BYTES = 256 * 1024 * 1024


def _contains_any(text: str, terms: set[str]) -> list[str]:
    lowered = text.lower()
    return sorted(term for term in terms if term in lowered)


def _words(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z']+", text.lower())


def _read_limited(response: Any, max_bytes: int) -> bytes:
    data = response.read(max_bytes + 1)
    return data[:max_bytes]


def _fetch_text(url: str, timeout: int, max_bytes: int = 2_000_000) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "score2md-preflight/1.0",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return _read_limited(response, max_bytes).decode("utf-8", errors="replace")


def _json_object_after(text: str, marker: str) -> dict[str, Any] | None:
    index = text.find(marker)
    if index < 0:
        return None
    brace = text.find("{", index)
    if brace < 0:
        return None
    depth = 0
    in_string = False
    escape = False
    for position in range(brace, len(text)):
        char = text[position]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[brace : position + 1])
                except json.JSONDecodeError:
                    return None
    return None


def _extract_meta_content(page: str, name: str) -> str | None:
    patterns = [
        rf'<meta[^>]+name=["\']{re.escape(name)}["\'][^>]+content=["\']([^"\']+)["\']',
        rf'<meta[^>]+property=["\']{re.escape(name)}["\'][^>]+content=["\']([^"\']+)["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, page, flags=re.IGNORECASE)
        if match:
            return html.unescape(match.group(1))
    return None


def _transcript_from_caption_tracks(caption_tracks: list[dict[str, Any]], timeout: int) -> str:
    for track in caption_tracks[:2]:
        base_url = track.get("baseUrl")
        if not isinstance(base_url, str):
            continue
        try:
            xml = _fetch_text(base_url, timeout=timeout, max_bytes=500_000)
        except Exception:
            continue
        text = re.sub(r"<[^>]+>", " ", xml)
        text = html.unescape(text)
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            return text[:5000]
    return ""


def fetch_youtube_metadata(url: str, timeout: int = 8) -> dict[str, Any]:
    metadata: dict[str, Any] = {"url": url}

    try:
        oembed_url = "https://www.youtube.com/oembed?" + urllib.parse.urlencode({"url": url, "format": "json"})
        oembed = json.loads(_fetch_text(oembed_url, timeout=timeout, max_bytes=100_000))
        metadata["title"] = oembed.get("title")
        metadata["author_name"] = oembed.get("author_name")
    except Exception as exc:
        metadata["oembed_error"] = str(exc)

    try:
        page = _fetch_text(url, timeout=timeout)
    except Exception as exc:
        metadata["watch_error"] = str(exc)
        return metadata

    player = _json_object_after(page, "ytInitialPlayerResponse")
    if player:
        details = player.get("videoDetails", {})
        if isinstance(details, dict):
            metadata["title"] = details.get("title") or metadata.get("title")
            metadata["description"] = details.get("shortDescription")
            metadata["is_live"] = details.get("isLiveContent")
            length = details.get("lengthSeconds")
            if length is not None:
                try:
                    metadata["duration_seconds"] = int(length)
                except (TypeError, ValueError):
                    pass
        tracks = (
            player.get("captions", {})
            .get("playerCaptionsTracklistRenderer", {})
            .get("captionTracks", [])
        )
        if isinstance(tracks, list):
            transcript = _transcript_from_caption_tracks(tracks, timeout=timeout)
            if transcript:
                metadata["transcript"] = transcript

    metadata["title"] = metadata.get("title") or _extract_meta_content(page, "og:title")
    metadata["description"] = metadata.get("description") or _extract_meta_content(page, "description")
    return metadata


def find_ffprobe_binary(ffmpeg_path: str | Path | None = None) -> Path | None:
    if ffmpeg_path:
        configured = Path(ffmpeg_path)
        sibling = configured.with_name("ffprobe.exe" if os.name == "nt" else "ffprobe")
        if sibling.exists():
            return sibling
    found = shutil.which("ffprobe")
    if found:
        return Path(found)
    if os.name == "nt":
        for candidate in [
            Path(r"C:\Program Files\ffmpeg\bin\ffprobe.exe"),
            Path(r"C:\ffmpeg\bin\ffprobe.exe"),
        ]:
            if candidate.exists():
                return candidate
    return None


def probe_media_duration(path: Path, ffmpeg_path: str | Path | None = None) -> float | None:
    binary = find_ffprobe_binary(ffmpeg_path)
    if binary is None:
        return None
    try:
        result = subprocess.run(
            [
                str(binary),
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return float(result.stdout.strip())
    except Exception:
        return None


def _duration_reject(duration: float | int | None, max_seconds: int) -> str | None:
    if duration is None:
        return None
    if float(duration) > max_seconds:
        return f"media duration {int(float(duration))}s exceeds preflight limit {max_seconds}s"
    return None


def _classify_metadata(
    *,
    source: str,
    source_type: str,
    metadata: dict[str, Any],
    mode: str,
    max_media_duration_sec: int,
) -> PreflightDecision:
    title = str(metadata.get("title") or "")
    description = str(metadata.get("description") or "")
    transcript = str(metadata.get("transcript") or "")
    text_blob = " ".join([title, description, transcript])

    reasons: list[str] = []
    warnings: list[str] = []
    negative_hits = _contains_any(text_blob, NEGATIVE_TERMS)
    positive_hits = _contains_any(text_blob, POSITIVE_MUSIC_TERMS)
    piano_hits = _contains_any(text_blob, PIANO_SCORE_TERMS)
    spoken_hits = _contains_any(transcript, SPOKEN_TRANSCRIPT_MARKERS)
    duration = metadata.get("duration_seconds")

    duration_reason = _duration_reject(duration if isinstance(duration, (int, float)) else None, max_media_duration_sec)
    if duration_reason:
        return PreflightDecision(source, source_type, "rejected", False, 0.99, [duration_reason], metadata=metadata)

    if metadata.get("is_live") is True:
        return PreflightDecision(source, source_type, "rejected", False, 0.95, ["live streams are not suitable for deterministic score transcription"], metadata=metadata)

    if negative_hits:
        return PreflightDecision(
            source,
            source_type,
            "rejected",
            False,
            0.95,
            [f"metadata indicates spoken/non-score content: {', '.join(negative_hits[:6])}"],
            metadata=metadata,
        )

    transcript_words = _words(transcript)
    if len(transcript_words) >= 120 and (len(spoken_hits) >= 2 or not positive_hits):
        return PreflightDecision(
            source,
            source_type,
            "rejected",
            False,
            0.9,
            ["caption transcript strongly resembles spoken-word content"],
            metadata=metadata,
        )

    if not title and not description and not transcript:
        return PreflightDecision(
            source,
            source_type,
            "uncertain",
            False,
            0.1,
            ["metadata/transcript could not be fetched; refusing to spend transcription resources"],
            metadata=metadata,
        )

    if mode == "compact-piano" and not piano_hits:
        return PreflightDecision(
            source,
            source_type,
            "uncertain",
            False,
            0.45,
            ["piano-score mode requested but metadata does not indicate piano, keyboard, synthesia, or sheet music"],
            metadata=metadata,
        )

    if not positive_hits:
        return PreflightDecision(
            source,
            source_type,
            "uncertain",
            False,
            0.35,
            ["metadata does not confidently identify a music source"],
            metadata=metadata,
        )

    reasons.append(f"music indicators found: {', '.join(positive_hits[:6])}")
    if piano_hits:
        reasons.append(f"piano/score indicators found: {', '.join(piano_hits[:4])}")
    if duration:
        reasons.append(f"duration {int(float(duration))}s is within limit")
    if transcript and len(transcript_words) > 60:
        warnings.append("captions exist; preflight allowed because music/piano indicators were stronger than speech signals")
    return PreflightDecision(source, source_type, "approved", True, 0.86, reasons, warnings, metadata)


def _classify_local_media(
    source: str | Path,
    source_type: str,
    *,
    mode: str,
    max_media_duration_sec: int,
    ffmpeg_path: str | Path | None,
) -> PreflightDecision:
    path = Path(source)
    metadata: dict[str, Any] = {"title": path.stem}
    if path.exists():
        metadata["file_size_bytes"] = path.stat().st_size
        duration = probe_media_duration(path, ffmpeg_path)
        if duration is not None:
            metadata["duration_seconds"] = int(duration)
    decision = _classify_metadata(
        source=str(source),
        source_type=source_type,
        metadata=metadata,
        mode=mode,
        max_media_duration_sec=max_media_duration_sec,
    )
    file_size = metadata.get("file_size_bytes")
    if (
        not decision.approved
        and decision.status == "uncertain"
        and isinstance(file_size, int)
        and file_size > LARGE_LOCAL_MEDIA_BYTES
        and "duration_seconds" not in metadata
    ):
        decision.status = "rejected"
        decision.confidence = 0.82
        decision.reasons = ["large local media has unknown duration; refusing preflight by default"]
    return decision


def _load_cached_decision(cache_path: Path) -> PreflightDecision | None:
    if not cache_path.exists():
        return None
    try:
        return PreflightDecision.from_dict(json.loads(cache_path.read_text(encoding="utf-8")))
    except Exception:
        return None


def _write_cached_decision(cache_path: Path, decision: PreflightDecision) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(decision.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def explain_rejection(decision: PreflightDecision) -> str:
    reasons = "; ".join(decision.reasons) if decision.reasons else "no approval reason was available"
    return (
        f"Audio/YouTube/video preflight {decision.status}: {reasons}. "
        "Use --skip-preflight only when you intentionally want to spend transcription resources on this source."
    )


def run_media_preflight(
    source: str | Path,
    source_type: str,
    cache_path: Path,
    *,
    mode: str,
    skip_preflight: bool = False,
    allow_uncertain_audio: bool = False,
    refresh_cache: bool = False,
    max_media_duration_sec: int = DEFAULT_MAX_MEDIA_DURATION_SECONDS,
    youtube_metadata_timeout: int = 8,
    ffmpeg_path: str | Path | None = None,
) -> PreflightDecision:
    if skip_preflight:
        decision = PreflightDecision(
            str(source),
            source_type,
            "skipped",
            True,
            1.0,
            ["preflight skipped by explicit user override"],
            ["resource-saving media guard was bypassed"],
        )
        _write_cached_decision(cache_path, decision)
        return decision

    cached = None if refresh_cache else _load_cached_decision(cache_path)
    if cached is not None:
        if cached.approved or (cached.status == "uncertain" and allow_uncertain_audio):
            return cached
        raise PreflightError(explain_rejection(cached))

    if source_type == "youtube":
        metadata = fetch_youtube_metadata(str(source), timeout=youtube_metadata_timeout)
        decision = _classify_metadata(
            source=str(source),
            source_type=source_type,
            metadata=metadata,
            mode=mode,
            max_media_duration_sec=max_media_duration_sec,
        )
    else:
        decision = _classify_local_media(
            source,
            source_type,
            mode=mode,
            max_media_duration_sec=max_media_duration_sec,
            ffmpeg_path=ffmpeg_path,
        )

    if decision.status == "uncertain" and allow_uncertain_audio:
        decision.approved = True
        decision.warnings.append("uncertain audio/video source allowed by --allow-uncertain-audio")

    _write_cached_decision(cache_path, decision)
    if not decision.approved:
        raise PreflightError(explain_rejection(decision))
    return decision
