from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction

from .models import Event, MeasureModel, Pitch, ScoreModel


@dataclass(frozen=True)
class RenderOptions:
    mode: str = "compact-piano"
    explicit_accidentals: bool = True
    line_measures: int = 2
    default_tempo: int = 120
    include_chord_symbols: bool = True


def pitch_to_abc(pitch: Pitch, explicit: bool = True) -> str:
    accidental = ""
    if explicit:
        accidental = {-2: "__", -1: "_", 0: "=", 1: "^", 2: "^^"}.get(pitch.alter, "")
    elif pitch.alter:
        accidental = {-2: "__", -1: "_", 1: "^", 2: "^^"}.get(pitch.alter, "")

    step = pitch.step.upper()
    if pitch.octave == 4:
        note = step
    elif pitch.octave > 4:
        note = step.lower()
        if pitch.octave > 5:
            note += "'" * (pitch.octave - 5)
    else:
        note = step + "," * (4 - pitch.octave)
    return accidental + note


def choose_unit_length(model: ScoreModel) -> Fraction:
    durations: list[Fraction] = []
    for part in model.parts:
        for measure in part.measures:
            durations.extend(event.duration for event in measure.events if not event.grace)
    if not durations:
        return Fraction(1, 16)
    for unit in [Fraction(1, 8), Fraction(1, 16), Fraction(1, 32), Fraction(1, 64)]:
        if all((duration / unit).denominator == 1 for duration in durations):
            if unit == Fraction(1, 8) and any(duration < Fraction(1, 8) for duration in durations):
                continue
            return unit
    return Fraction(1, 16)


def unit_to_abc(unit: Fraction) -> str:
    return f"{unit.numerator}/{unit.denominator}"


def duration_suffix(duration: Fraction, unit: Fraction) -> str:
    ratio = duration / unit
    if ratio == 1:
        return ""
    if ratio.denominator == 1:
        return str(ratio.numerator)
    if ratio.numerator == 1 and ratio.denominator == 2:
        return "/"
    if ratio.numerator == 1:
        return f"/{ratio.denominator}"
    return f"{ratio.numerator}/{ratio.denominator}"


def token_for_event(event: Event, unit: Fraction, options: RenderOptions) -> str:
    suffix = duration_suffix(event.duration, unit)
    if event.kind == "rest" or not event.pitches:
        token = f"z{suffix}"
    elif len(event.pitches) == 1:
        token = f"{pitch_to_abc(event.pitches[0], options.explicit_accidentals)}{suffix}"
    else:
        notes = "".join(pitch_to_abc(p, options.explicit_accidentals) for p in event.pitches)
        token = f"[{notes}]{suffix}"
    if event.tie_start and event.kind == "note":
        token += "-"
    if event.grace:
        grace = " ".join(pitch_to_abc(p, options.explicit_accidentals) for p in event.grace)
        token = "{" + grace + "}" + token
    if options.include_chord_symbols and event.chord_symbol:
        token = f'"{event.chord_symbol}" {token}'
    return token


def staff_label(staff: int) -> str:
    if staff == 1:
        return "RH"
    if staff == 2:
        return "LH"
    return f"S{staff}"


def has_overlapping_independent_rhythm(events: list[Event]) -> bool:
    by_staff: dict[tuple[str, int, int], list[Event]] = defaultdict(list)
    for event in events:
        if event.kind == "note":
            by_staff[(event.part_id, event.measure_index, event.staff)].append(event)
    for staff_events in by_staff.values():
        ordered = sorted(staff_events, key=lambda e: (e.onset, e.duration))
        for index, left in enumerate(ordered):
            left_end = left.onset + left.duration
            for right in ordered[index + 1 :]:
                if right.onset >= left_end:
                    break
                if right.onset == left.onset and right.duration == left.duration:
                    continue
                return True
    return False


def output_voice_map(model: ScoreModel, mode: str) -> dict[tuple[str, int, str], str]:
    keys: set[tuple[str, int, str]] = set()
    all_events: list[Event] = []
    for part in model.parts:
        for measure in part.measures:
            all_events.extend(measure.events)
            for event in measure.events:
                keys.add((part.id, event.staff, event.voice))

    if mode == "compact-piano" and not has_overlapping_independent_rhythm(all_events):
        return {key: staff_label(key[1]) for key in keys}

    labels: dict[tuple[str, int, str], str] = {}
    used: set[str] = set()
    for part_id, staff, voice in sorted(keys, key=lambda item: (item[0], item[1], item[2])):
        base = staff_label(staff)
        clean_voice = "".join(ch for ch in voice if ch.isalnum()) or "1"
        label = f"{base}{clean_voice}"
        if label in {"RH1", "LH1"} and (part_id, staff, voice) in keys:
            label = base if label not in used else label
        while label in used:
            label += "X"
        labels[(part_id, staff, voice)] = label
        used.add(label)
    return labels


def merge_voice_events(events: list[Event]) -> list[Event]:
    merged: list[Event] = []
    for event in sorted(events, key=lambda e: (e.onset, e.duration, e.kind)):
        found = None
        for existing in merged:
            if (
                existing.kind == event.kind == "note"
                and existing.onset == event.onset
                and existing.duration == event.duration
                and existing.tie_start == event.tie_start
                and existing.tie_stop == event.tie_stop
            ):
                found = existing
                break
        if found is None:
            clone = Event(
                part_id=event.part_id,
                measure_index=event.measure_index,
                staff=event.staff,
                voice=event.voice,
                onset=event.onset,
                duration=event.duration,
                kind=event.kind,
                pitches=list(event.pitches),
                grace=list(event.grace),
                tie_start=event.tie_start,
                tie_stop=event.tie_stop,
                chord_symbol=event.chord_symbol,
            )
            merged.append(clone)
        else:
            found.pitches.extend(event.pitches)
            if event.chord_symbol and not found.chord_symbol:
                found.chord_symbol = event.chord_symbol
    return merged


def render_measure(events: list[Event], measure: MeasureModel, unit: Fraction, options: RenderOptions) -> str:
    tokens: list[str] = []
    cursor = Fraction(0, 1)
    for event in merge_voice_events(events):
        if event.onset > cursor:
            tokens.append("z" + duration_suffix(event.onset - cursor, unit))
            cursor = event.onset
        tokens.append(token_for_event(event, unit, options))
        cursor = max(cursor, event.onset + event.duration)
    if cursor < measure.time.measure_length:
        tokens.append("z" + duration_suffix(measure.time.measure_length - cursor, unit))
    return " ".join(tokens) if tokens else "z" + duration_suffix(measure.time.measure_length, unit)


def build_score_directive(labels: list[str]) -> str:
    if labels == ["RH", "LH"]:
        return "%%score {RH LH}"
    return "%%score {" + " ".join(labels) + "}"


def render_abc(model: ScoreModel, options: RenderOptions) -> tuple[str, dict[str, int]]:
    unit = choose_unit_length(model)
    voice_map = output_voice_map(model, options.mode)
    labels = sorted(set(voice_map.values()), key=lambda label: (label.startswith("LH"), label))
    if "RH" in labels and "LH" in labels:
        labels = ["RH", "LH"] + [label for label in labels if label not in {"RH", "LH"}]

    tempo = model.first_tempo or options.default_tempo
    lines = [
        "X:1",
        f"T:{model.title or 'Converted Score'}",
    ]
    if model.composer:
        lines.append(f"C:{model.composer}")
    lines.extend(
        [
            f"M:{model.first_time.abc_name}",
            f"Q:1/4={tempo}",
            f"L:{unit_to_abc(unit)}",
        ]
    )
    if labels:
        lines.append(build_score_directive(labels))
        for label in labels:
            clef = "bass" if label.startswith("LH") else "treble"
            name = "Piano LH" if label.startswith("LH") else "Piano RH"
            lines.append(f'V:{label} clef={clef} name="{name}"')
    lines.append(f"K:{model.first_key.abc_name}")

    measures_by_index: dict[int, list[MeasureModel]] = defaultdict(list)
    max_measure = 0
    for part in model.parts:
        for measure in part.measures:
            measures_by_index[measure.index].append(measure)
            max_measure = max(max_measure, measure.index + 1)

    current_key = model.first_key.abc_name
    current_meter = model.first_time.abc_name
    line_measures = max(1, options.line_measures)
    rendered_counts = {
        "pitched_notes": 0,
        "rests": 0,
        "chord_events": 0,
        "grace_notes": 0,
        "ties": 0,
        "key_changes": 0,
        "time_changes": 0,
        "repeats_endings": 0,
    }

    start = 0
    while start < max_measure:
        end = min(max_measure, start + line_measures)
        for measure_index in range(start + 1, end):
            previous = measures_by_index[measure_index - 1][0]
            current = measures_by_index[measure_index][0]
            if current.key.abc_name != previous.key.abc_name or current.time.abc_name != previous.time.abc_name:
                end = measure_index
                break

        group_indices = list(range(start, end))
        first_measure = measures_by_index[group_indices[0]][0]
        if first_measure.key.abc_name != current_key:
            current_key = first_measure.key.abc_name
            lines.append(f"K:{current_key}")
            rendered_counts["key_changes"] += 1
        if first_measure.time.abc_name != current_meter:
            current_meter = first_measure.time.abc_name
            lines.append(f"M:{current_meter}")
            rendered_counts["time_changes"] += 1

        for measure_index in group_indices:
            measure_model = measures_by_index[measure_index][0]
            if measure_model.repeat_start:
                rendered_counts["repeats_endings"] += 1
            if measure_model.repeat_end:
                rendered_counts["repeats_endings"] += 1
            if measure_model.ending:
                rendered_counts["repeats_endings"] += 1

        for label in labels:
            rendered_measures: list[str] = []
            for measure_index in group_indices:
                measure_events: list[Event] = []
                measure_model = measures_by_index[measure_index][0]
                for measure in measures_by_index[measure_index]:
                    measure_model = measure
                    for event in measure.events:
                        key = (event.part_id, event.staff, event.voice)
                        if voice_map.get(key) == label:
                            measure_events.append(event)
                            if event.kind == "note":
                                rendered_counts["pitched_notes"] += len(event.pitches)
                                if len(event.pitches) > 1:
                                    rendered_counts["chord_events"] += 1
                            elif event.kind == "rest":
                                rendered_counts["rests"] += 1
                            rendered_counts["grace_notes"] += len(event.grace)
                            if event.tie_start or event.tie_stop:
                                rendered_counts["ties"] += 1
                prefix = ""
                if measure_model.repeat_start:
                    prefix += "|: "
                if measure_model.ending:
                    prefix += f"[{measure_model.ending} "
                rendered = render_measure(measure_events, measure_model, unit, options)
                suffix = " :|" if measure_model.repeat_end else ""
                rendered_measures.append((prefix + rendered + suffix).strip())
            is_last_voice_line = end >= max_measure
            final_bar = "|]" if is_last_voice_line else "|"
            lines.append(f"[V:{label}] " + " | ".join(rendered_measures) + f" {final_bar}")
        start = end

    abc = "\n".join(lines)
    validate_abc_shape(abc)
    return abc, rendered_counts


def wrap_abc(abc: str) -> str:
    return "```abc\n" + abc.strip() + "\n```\n"


def validate_abc_shape(abc: str) -> None:
    lines = abc.splitlines()
    if not any(line.startswith("K:") for line in lines):
        raise ValueError("ABC output is missing K: header")
    for index, line in enumerate(lines[:-1]):
        if line.startswith("K:") and lines[index + 1] == "":
            raise ValueError("ABC output has a blank line after K:")
    if any(line == "" for line in lines):
        raise ValueError("ABC output contains a blank line inside the tune")
    if not abc.rstrip().endswith("|]"):
        raise ValueError("ABC output must end with |]")
