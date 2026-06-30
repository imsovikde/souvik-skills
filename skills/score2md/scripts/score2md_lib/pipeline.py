from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

from .abc_render import RenderOptions, render_abc, wrap_abc
from .adapters import image_to_musicxml, midi_to_musicxml, ohsheet_to_musicxml, pdf_to_musicxml
from .detect import detect_source, reliability_tier, status_for_kind
from .models import VerificationReport
from .musicxml_reader import parse_score
from .preflight import DEFAULT_MAX_MEDIA_DURATION_SECONDS, run_media_preflight
from .verify import verify_markdown_shape, verify_model, write_report


@dataclass
class ConversionOptions:
    mode: str = "compact-piano"
    explicit_accidentals: bool = True
    line_measures: int = 2
    default_tempo: int = 120
    preserve_repeats: bool = True
    expand_repeats: bool = False
    include_chord_symbols: bool = True
    verify: str = "strict"
    keep_intermediate: bool = False
    musescore_path: str | None = None
    omr_workers: int = 2
    omr_module: str | None = None
    ffmpeg_path: str | None = None
    refresh_cache: bool = False
    ohsheet_timeout: int = 900
    ohsheet_prefer_clean_source: bool = True
    skip_preflight: bool = False
    allow_uncertain_audio: bool = False
    max_media_duration_sec: int = DEFAULT_MAX_MEDIA_DURATION_SECONDS
    youtube_metadata_timeout: int = 8


@dataclass
class ConversionResult:
    source_path: str
    source_type: str
    reliability_tier: str
    musicxml_path: str | None
    markdown_path: str
    abc_path: str | None
    cache_path: str | None
    used_cache: bool
    verification: VerificationReport | None
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "source_path": self.source_path,
            "source_type": self.source_type,
            "reliability_tier": self.reliability_tier,
            "musicxml_path": self.musicxml_path,
            "markdown_path": self.markdown_path,
            "abc_path": self.abc_path,
            "cache_path": self.cache_path,
            "used_cache": self.used_cache,
            "verification": self.verification.to_dict() if self.verification else None,
            "warnings": self.warnings,
        }


def hash_source(h: "hashlib._Hash", source: str | Path) -> None:
    path = Path(str(source))
    if path.exists():
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                h.update(chunk)
    else:
        h.update(str(source).encode("utf-8"))


def cache_key(source: str | Path, options: ConversionOptions) -> str:
    h = hashlib.sha256()
    hash_source(h, source)
    cache_options = {key: value for key, value in options.__dict__.items() if key != "refresh_cache"}
    h.update(json.dumps(cache_options, sort_keys=True).encode("utf-8"))
    h.update(b"score2md-v2")
    return h.hexdigest()


def normalize_to_musicxml(
    source: str | Path,
    kind: str,
    output_dir: Path,
    options: ConversionOptions,
) -> tuple[Path | None, bool]:
    path = Path(str(source))
    output_dir.mkdir(parents=True, exist_ok=True)
    if kind in {"mxl", "musicxml", "xml"}:
        return path, False
    normalized = output_dir / "normalized.musicxml"
    if normalized.exists() and not options.refresh_cache:
        return normalized, True
    if kind == "midi":
        return midi_to_musicxml(path, normalized, options.musescore_path), False
    if kind == "pdf":
        return pdf_to_musicxml(path, normalized, omr_workers=options.omr_workers, omr_module=options.omr_module), False
    if kind == "image":
        return image_to_musicxml(path, normalized, omr_module=options.omr_module), False
    if kind in {"audio", "video"}:
        run_media_preflight(
            path,
            kind,
            output_dir / "preflight.json",
            mode=options.mode,
            skip_preflight=options.skip_preflight,
            allow_uncertain_audio=options.allow_uncertain_audio,
            refresh_cache=options.refresh_cache,
            max_media_duration_sec=options.max_media_duration_sec,
            ffmpeg_path=options.ffmpeg_path,
        )
        return ohsheet_to_musicxml(
            path,
            normalized,
            is_youtube=False,
            is_video=kind == "video",
            ffmpeg_path=options.ffmpeg_path,
            timeout_sec=options.ohsheet_timeout,
            prefer_clean_source=options.ohsheet_prefer_clean_source,
            job_cache_path=output_dir / "ohsheet-job.json",
            refresh_job=options.refresh_cache,
        ), False
    if kind == "youtube":
        run_media_preflight(
            str(source),
            kind,
            output_dir / "preflight.json",
            mode=options.mode,
            skip_preflight=options.skip_preflight,
            allow_uncertain_audio=options.allow_uncertain_audio,
            refresh_cache=options.refresh_cache,
            max_media_duration_sec=options.max_media_duration_sec,
            youtube_metadata_timeout=options.youtube_metadata_timeout,
        )
        return ohsheet_to_musicxml(
            str(source),
            normalized,
            is_youtube=True,
            timeout_sec=options.ohsheet_timeout,
            prefer_clean_source=options.ohsheet_prefer_clean_source,
            job_cache_path=output_dir / "ohsheet-job.json",
            refresh_job=options.refresh_cache,
        ), False
    return None, False


def strip_abc_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```abc"):
        lines = stripped.splitlines()
        if lines[-1].strip() == "```":
            return "\n".join(lines[1:-1]).strip()
    return stripped


def normalize_abc_text(text: str) -> str:
    abc = strip_abc_fence(text)
    lines = [line.rstrip() for line in abc.splitlines()]
    cleaned: list[str] = []
    in_body = False
    for line in lines:
        if line.startswith("K:"):
            in_body = True
            cleaned.append(line)
            continue
        if in_body and not line.strip():
            continue
        if line.strip():
            cleaned.append(line)
    if not any(line.startswith("X:") for line in cleaned):
        cleaned.insert(0, "X:1")
    if not any(line.startswith("T:") for line in cleaned):
        cleaned.insert(1, "T:Converted ABC")
    if not any(line.startswith("K:") for line in cleaned):
        cleaned.append("K:C")
        cleaned.append("z8 |]")
    if not cleaned[-1].rstrip().endswith("|]"):
        cleaned[-1] = cleaned[-1].rstrip().rstrip("|") + " |]"
    return "\n".join(cleaned)


def convert_to_md(source: str | Path, output_path: str | Path, **kwargs) -> ConversionResult:
    options = ConversionOptions(**kwargs)
    kind = detect_source(source)
    tier = reliability_tier(kind)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    work_dir = output.parent / ".score2md-cache" / cache_key(source, options)
    work_dir.mkdir(parents=True, exist_ok=True)

    if kind == "abc":
        abc = normalize_abc_text(Path(str(source)).read_text(encoding="utf-8"))
        md = wrap_abc(abc)
        output.write_text(md, encoding="utf-8")
        abc_path = output.with_suffix(".abc")
        abc_path.write_text(abc + "\n", encoding="utf-8")
        shape_problems = verify_markdown_shape(output)
        report = VerificationReport(
            source_format=kind,
            reliability_tier=tier,
            title="Converted ABC",
            composer=None,
            parts=1,
            staves=1,
            measures=abc.count("|"),
            pitched_notes=0,
            rests=0,
            chord_events=abc.count("["),
            grace_notes=abc.count("{"),
            ties=abc.count("-"),
            key_changes=max(0, abc.count("\nK:")),
            time_changes=max(0, abc.count("\nM:")),
            repeats_endings=abc.count("|:") + abc.count(":|") + abc.count("[1") + abc.count("[2"),
            tempo_status="Preserved from ABC when present.",
            status=status_for_kind(kind),
            warnings=shape_problems,
        )
        write_report(report, Path(str(output) + ".verify.json"))
        return ConversionResult(
            str(source),
            kind,
            tier,
            None,
            str(output),
            str(abc_path),
            str(work_dir),
            False,
            report,
            shape_problems,
        )

    musicxml_path, used_cache = normalize_to_musicxml(source, kind, work_dir, options)
    if musicxml_path is None:
        raise ValueError(f"Could not normalize {source} to MusicXML")
    model = parse_score(musicxml_path, kind, tier)
    render_options = RenderOptions(
        mode=options.mode,
        explicit_accidentals=options.explicit_accidentals,
        line_measures=options.line_measures,
        default_tempo=options.default_tempo,
        include_chord_symbols=options.include_chord_symbols,
    )
    abc, rendered_counts = render_abc(model, render_options)
    report = verify_model(model, rendered_counts, strict=options.verify == "strict")
    md = wrap_abc(abc)
    output.write_text(md, encoding="utf-8")
    abc_path = output.with_suffix(".abc")
    abc_path.write_text(abc + "\n", encoding="utf-8")
    write_report(report, Path(str(output) + ".verify.json"))
    problems = verify_markdown_shape(output)
    if problems:
        raise ValueError("Markdown shape verification failed: " + "; ".join(problems))
    return ConversionResult(
        source_path=str(source),
        source_type=kind,
        reliability_tier=tier,
        musicxml_path=str(musicxml_path),
        markdown_path=str(output),
        abc_path=str(abc_path),
        cache_path=str(work_dir),
        used_cache=used_cache,
        verification=report,
        warnings=report.warnings,
    )
