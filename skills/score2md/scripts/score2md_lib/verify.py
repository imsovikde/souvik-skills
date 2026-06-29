from __future__ import annotations

import json
import re
from pathlib import Path

from .detect import status_for_kind
from .models import ScoreModel, VerificationReport


def source_counts(model: ScoreModel) -> dict[str, int]:
    pitched_notes = 0
    rests = 0
    chord_events = 0
    grace_notes = 0
    ties = 0
    staves: set[int] = set()
    key_sequence: list[str] = []
    time_sequence: list[str] = []
    repeats_endings = 0
    measures = 0
    for part in model.parts:
        for measure in part.measures:
            measures += 1
            key_sequence.append(measure.key.abc_name)
            time_sequence.append(measure.time.abc_name)
            if measure.repeat_start:
                repeats_endings += 1
            if measure.repeat_end:
                repeats_endings += 1
            if measure.ending:
                repeats_endings += 1
            for event in measure.events:
                staves.add(event.staff)
                if event.kind == "rest":
                    rests += 1
                else:
                    pitched_notes += len(event.pitches)
                    if len(event.pitches) > 1:
                        chord_events += 1
                grace_notes += len(event.grace)
                if event.tie_start or event.tie_stop:
                    ties += 1
    key_changes = max(0, len([k for i, k in enumerate(key_sequence) if i == 0 or k != key_sequence[i - 1]]) - 1)
    time_changes = max(0, len([t for i, t in enumerate(time_sequence) if i == 0 or t != time_sequence[i - 1]]) - 1)
    return {
        "pitched_notes": pitched_notes,
        "rests": rests,
        "chord_events": chord_events,
        "grace_notes": grace_notes,
        "ties": ties,
        "staves": len(staves),
        "measures": measures,
        "key_changes": key_changes,
        "time_changes": time_changes,
        "repeats_endings": repeats_endings,
    }


def verify_model(model: ScoreModel, rendered_counts: dict[str, int], strict: bool = True) -> VerificationReport:
    counts = source_counts(model)
    warnings = list(model.warnings)
    source_format = model.source_type
    expected_status = status_for_kind(source_format)  # type: ignore[arg-type]
    status = expected_status
    symbolic = source_format in {"mxl", "musicxml", "xml"}
    if symbolic:
        mismatches = []
        for key in ("pitched_notes", "rests", "chord_events"):
            if counts[key] != rendered_counts.get(key, -1):
                mismatches.append(f"{key}: source={counts[key]} rendered={rendered_counts.get(key)}")
        if mismatches:
            status = "verification failed"
            warnings.extend(mismatches)
            if strict:
                raise ValueError("Strict verification failed: " + "; ".join(mismatches))

    tempo_status = (
        f"Source tempo Q:1/4={model.first_tempo}"
        if model.first_tempo is not None
        else "Tempo was missing in source; default Q:1/4=120 inserted for playback."
    )
    return VerificationReport(
        source_format=source_format,
        reliability_tier=model.reliability_tier,
        title=model.title,
        composer=model.composer,
        parts=len(model.parts),
        staves=counts["staves"],
        measures=counts["measures"],
        pitched_notes=counts["pitched_notes"],
        rests=counts["rests"],
        chord_events=counts["chord_events"],
        grace_notes=counts["grace_notes"],
        ties=counts["ties"],
        key_changes=counts["key_changes"],
        time_changes=counts["time_changes"],
        repeats_endings=counts["repeats_endings"],
        tempo_status=tempo_status,
        status=status,
        warnings=warnings,
    )


def write_report(report: VerificationReport, path: Path) -> None:
    path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")


def verify_markdown_shape(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    problems: list[str] = []
    if text.count("```abc") != 1:
        problems.append("Markdown must contain exactly one ```abc fence")
    if not text.rstrip().endswith("```"):
        problems.append("Markdown must end with a closing code fence")
    if re.search(r"K:[^\n]*\n\n", text):
        problems.append("Markdown contains a blank line after K:")
    if "id=" in text.splitlines()[0]:
        problems.append("Opening code fence must not contain attributes")
    return problems
