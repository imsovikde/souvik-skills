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


@dataclass
class ConversionResult:
    source_path: str
    source_type: str
    reliability_tier: str
    musicxml_path: str | None
    markdown_path: str
    abc_path: str | None
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
            "verification": self.verification.to_dict() if self.verification else None,
            "warnings": self.warnings,
        }


def cache_key(source: str | Path, options: ConversionOptions) -> str:
    h = hashlib.sha256()
    path = Path(str(source))
    if path.exists():
        h.update(path.read_bytes())
    else:
        h.update(str(source).encode("utf-8"))
    h.update(json.dumps(options.__dict__, sort_keys=True).encode("utf-8"))
    h.update(b"score2md-v1")
    return h.hexdigest()


def normalize_to_musicxml(source: str | Path, kind: str, output_dir: Path, options: ConversionOptions) -> Path | None:
    path = Path(str(source))
    output_dir.mkdir(parents=True, exist_ok=True)
    if kind in {"mxl", "musicxml", "xml"}:
        return path
    normalized = output_dir / "normalized.musicxml"
    if kind == "midi":
        return midi_to_musicxml(path, normalized, options.musescore_path)
    if kind == "pdf":
        return pdf_to_musicxml(path, normalized, omr_workers=options.omr_workers)
    if kind == "image":
        return image_to_musicxml(path, normalized)
    if kind in {"audio", "video"}:
        return ohsheet_to_musicxml(path, normalized, is_youtube=False)
    if kind == "youtube":
        return ohsheet_to_musicxml(str(source), normalized, is_youtube=True)
    return None


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
        return ConversionResult(str(source), kind, tier, None, str(output), str(abc_path), report, shape_problems)

    musicxml_path = normalize_to_musicxml(source, kind, work_dir, options)
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
        verification=report,
        warnings=report.warnings,
    )
