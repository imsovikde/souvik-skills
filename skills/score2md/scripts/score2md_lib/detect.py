from __future__ import annotations

import re
from pathlib import Path

from .models import SourceKind


YOUTUBE_RE = re.compile(
    r"^(https?://)?(www\.)?(youtube\.com|youtu\.be|music\.youtube\.com)/",
    re.IGNORECASE,
)


def is_url(value: str) -> bool:
    return value.lower().startswith(("http://", "https://"))


def detect_source(source: str | Path) -> SourceKind:
    value = str(source)
    if YOUTUBE_RE.search(value):
        return "youtube"
    if is_url(value):
        raise ValueError(
            "HTTP/HTTPS URLs are only supported for YouTube sources. "
            "Download direct audio or video URLs to a local file before converting."
        )

    suffix = Path(value).suffix.lower()
    if suffix == ".mxl":
        return "mxl"
    if suffix == ".musicxml":
        return "musicxml"
    if suffix == ".xml":
        return "xml"
    if suffix == ".abc":
        return "abc"
    if suffix in {".mid", ".midi", ".kar"}:
        return "midi"
    if suffix == ".pdf":
        return "pdf"
    if suffix in {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".webp"}:
        return "image"
    if suffix in {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg"}:
        return "audio"
    if suffix in {".mp4", ".mov", ".mkv", ".webm"}:
        return "video"
    raise ValueError(f"Unsupported source format: {source}")


def reliability_tier(kind: SourceKind) -> str:
    if kind in {"mxl", "musicxml", "xml", "abc"}:
        return "Tier A symbolic"
    if kind == "midi":
        return "Tier B MIDI-derived"
    if kind in {"pdf", "image"}:
        return "Tier C OMR-derived"
    return "Tier D transcription-derived"


def status_for_kind(kind: SourceKind) -> str:
    if kind in {"mxl", "musicxml", "xml", "abc"}:
        return "verified symbolic conversion"
    if kind == "midi":
        return "MIDI-derived conversion; pitch/timing preserved, notation inferred"
    if kind in {"pdf", "image"}:
        return "OMR-derived conversion; recognition may require correction"
    return "audio-transcription-derived conversion; approximate score reconstruction"
