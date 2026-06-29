from __future__ import annotations

import re
import zipfile
from collections import defaultdict
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
from xml.etree import ElementTree as ET

from .models import Event, KeySignature, MeasureModel, PartModel, Pitch, ScoreModel, TimeSignature


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def children(element: ET.Element, name: str | None = None) -> list[ET.Element]:
    return [child for child in list(element) if name is None or local_name(child.tag) == name]


def first_child(element: ET.Element | None, name: str) -> ET.Element | None:
    if element is None:
        return None
    for child in list(element):
        if local_name(child.tag) == name:
            return child
    return None


def first_desc(element: ET.Element, name: str) -> ET.Element | None:
    for child in element.iter():
        if child is not element and local_name(child.tag) == name:
            return child
    return None


def text_of(element: ET.Element | None, default: str = "") -> str:
    if element is None or element.text is None:
        return default
    return element.text.strip()


def int_text(element: ET.Element | None, default: int = 0) -> int:
    raw = text_of(element)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return int(float(raw))


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def read_musicxml_bytes(path: Path) -> bytes:
    if path.suffix.lower() != ".mxl":
        return path.read_bytes()
    with zipfile.ZipFile(path) as archive:
        rootfile = None
        try:
            container = ET.fromstring(archive.read("META-INF/container.xml"))
            for item in container.iter():
                if local_name(item.tag) == "rootfile":
                    rootfile = item.attrib.get("full-path")
                    break
        except KeyError:
            rootfile = None
        if not rootfile:
            candidates = [
                name
                for name in archive.namelist()
                if name.lower().endswith((".musicxml", ".xml"))
                and not name.lower().startswith("meta-inf/")
            ]
            if not candidates:
                raise ValueError(f"No MusicXML score found inside {path}")
            rootfile = candidates[0]
        return archive.read(rootfile)


def parse_musicxml_root(path: Path) -> ET.Element:
    root = ET.fromstring(read_musicxml_bytes(path))
    root_name = local_name(root.tag)
    if root_name == "score-timewise":
        raise ValueError("score-timewise MusicXML is not supported in score2md v1")
    if root_name != "score-partwise":
        raise ValueError(f"Expected score-partwise MusicXML, got <{root_name}>")
    return root


def part_names(root: ET.Element) -> dict[str, str]:
    out: dict[str, str] = {}
    part_list = first_child(root, "part-list")
    if part_list is None:
        return out
    for score_part in part_list.iter():
        if local_name(score_part.tag) != "score-part":
            continue
        part_id = score_part.attrib.get("id", "")
        if part_id:
            out[part_id] = clean_text(text_of(first_child(score_part, "part-name"), part_id))
    return out


def metadata(root: ET.Element, fallback_title: str) -> tuple[str, str | None]:
    title = text_of(first_desc(root, "work-title"))
    if not title:
        title = text_of(first_child(root, "movement-title"))
    composer = ""
    identification = first_child(root, "identification")
    if identification is not None:
        for creator in children(identification, "creator"):
            creator_type = creator.attrib.get("type", "").lower()
            if creator_type in {"composer", "arranger", ""}:
                composer = text_of(creator)
                if composer:
                    break
    return clean_text(title or fallback_title), clean_text(composer) or None


def pitch_from_note(note: ET.Element) -> Pitch | None:
    pitch = first_child(note, "pitch")
    if pitch is None:
        return None
    step = text_of(first_child(pitch, "step")).upper()
    alter = int_text(first_child(pitch, "alter"), 0)
    octave = int_text(first_child(pitch, "octave"), 4)
    return Pitch(step=step, alter=alter, octave=octave)


def has_tie(note: ET.Element, tie_type: str) -> bool:
    for tie in children(note, "tie"):
        if tie.attrib.get("type") == tie_type:
            return True
    notations = first_child(note, "notations")
    if notations is not None:
        for tied in children(notations, "tied"):
            if tied.attrib.get("type") == tie_type:
                return True
    return False


def tempo_from_measure(measure: ET.Element) -> int | None:
    for item in measure.iter():
        if local_name(item.tag) == "sound" and item.attrib.get("tempo"):
            try:
                return round(float(item.attrib["tempo"]))
            except ValueError:
                pass
        if local_name(item.tag) == "metronome":
            per_minute = text_of(first_child(item, "per-minute"))
            if per_minute:
                try:
                    return round(float(per_minute))
                except ValueError:
                    pass
    return None


def harmony_label(harmony: ET.Element) -> str | None:
    root = first_child(harmony, "root")
    if root is None:
        return None
    step = text_of(first_child(root, "root-step")).upper()
    alter = int_text(first_child(root, "root-alter"), 0)
    accidental = "#" * max(0, alter) + "b" * max(0, -alter)
    kind_el = first_child(harmony, "kind")
    kind_text = kind_el.attrib.get("text") if kind_el is not None else ""
    kind_value = text_of(kind_el).lower() if kind_el is not None else ""
    if kind_text:
        suffix = kind_text
    elif kind_value in {"minor", "min"}:
        suffix = "m"
    elif kind_value in {"dominant"}:
        suffix = "7"
    elif kind_value in {"major-seventh"}:
        suffix = "maj7"
    elif kind_value in {"minor-seventh"}:
        suffix = "m7"
    else:
        suffix = ""
    return f"{step}{accidental}{suffix}"


def update_attributes(
    measure: ET.Element,
    divisions: int,
    key: KeySignature,
    time: TimeSignature,
) -> tuple[int, KeySignature, TimeSignature]:
    attrs = first_child(measure, "attributes")
    if attrs is None:
        return divisions, key, time
    divisions = max(1, int_text(first_child(attrs, "divisions"), divisions))
    key_el = first_child(attrs, "key")
    if key_el is not None:
        key = KeySignature(
            fifths=int_text(first_child(key_el, "fifths"), key.fifths),
            mode=text_of(first_child(key_el, "mode"), key.mode or "major") or "major",
        )
    time_el = first_child(attrs, "time")
    if time_el is not None:
        time = TimeSignature(
            beats=int_text(first_child(time_el, "beats"), time.beats),
            beat_type=int_text(first_child(time_el, "beat-type"), time.beat_type),
        )
    return divisions, key, time


def parse_barlines(measure: ET.Element) -> tuple[bool, bool, str | None]:
    repeat_start = False
    repeat_end = False
    ending = None
    for barline in children(measure, "barline"):
        location = barline.attrib.get("location", "")
        repeat = first_child(barline, "repeat")
        if repeat is not None:
            direction = repeat.attrib.get("direction")
            if direction == "forward" or location == "left":
                repeat_start = True
            if direction == "backward" or location == "right":
                repeat_end = True
        ending_el = first_child(barline, "ending")
        if ending_el is not None and ending_el.attrib.get("type") in {"start", "discontinue"}:
            ending = ending_el.attrib.get("number") or text_of(ending_el) or "1"
    return repeat_start, repeat_end, ending


def add_or_merge(events: list[Event], event: Event) -> None:
    if event.kind == "rest":
        events.append(event)
        return
    for existing in events:
        if (
            existing.kind == "note"
            and existing.part_id == event.part_id
            and existing.staff == event.staff
            and existing.voice == event.voice
            and existing.onset == event.onset
            and existing.duration == event.duration
            and existing.tie_start == event.tie_start
            and existing.tie_stop == event.tie_stop
            and existing.grace == event.grace
        ):
            existing.pitches.extend(event.pitches)
            if event.chord_symbol and not existing.chord_symbol:
                existing.chord_symbol = event.chord_symbol
            return
    events.append(event)


def parse_score(path: Path, source_type: str, reliability_tier: str) -> ScoreModel:
    root = parse_musicxml_root(path)
    names = part_names(root)
    title, composer = metadata(root, path.stem)
    parts: list[PartModel] = []
    first_key = KeySignature()
    first_time = TimeSignature()
    first_tempo: int | None = None

    for part_index, part_el in enumerate(children(root, "part"), start=1):
        part_id = part_el.attrib.get("id", f"P{part_index}")
        part = PartModel(id=part_id, name=names.get(part_id, part_id))
        divisions = 1
        current_key = KeySignature()
        current_time = TimeSignature()
        pending_grace: dict[tuple[int, str], list[Pitch]] = defaultdict(list)

        for measure_index, measure_el in enumerate(children(part_el, "measure")):
            divisions, current_key, current_time = update_attributes(
                measure_el, divisions, current_key, current_time
            )
            if part_index == 1 and measure_index == 0:
                first_key = deepcopy(current_key)
                first_time = deepcopy(current_time)
            tempo = tempo_from_measure(measure_el)
            if tempo is not None and first_tempo is None:
                first_tempo = tempo

            repeat_start, repeat_end, ending = parse_barlines(measure_el)
            measure = MeasureModel(
                number=measure_el.attrib.get("number", str(measure_index + 1)),
                index=measure_index,
                key=deepcopy(current_key),
                time=deepcopy(current_time),
                divisions=divisions,
                repeat_start=repeat_start,
                repeat_end=repeat_end,
                ending=ending,
            )

            cursor = Fraction(0, 1)
            last_start_by_voice: dict[tuple[int, str], Fraction] = {}
            harmony_by_offset: dict[Fraction, str] = {}

            for item in list(measure_el):
                name = local_name(item.tag)
                if name == "backup":
                    cursor -= Fraction(int_text(first_child(item, "duration"), 0), divisions * 4)
                    cursor = max(cursor, Fraction(0, 1))
                    continue
                if name == "forward":
                    cursor += Fraction(int_text(first_child(item, "duration"), 0), divisions * 4)
                    continue
                if name == "harmony":
                    label = harmony_label(item)
                    if label:
                        harmony_by_offset[cursor] = label
                    continue
                if name != "note":
                    continue

                voice = text_of(first_child(item, "voice"), "1")
                staff = int_text(first_child(item, "staff"), 1)
                voice_key = (staff, voice)
                is_grace = first_child(item, "grace") is not None
                pitch = pitch_from_note(item)
                if is_grace:
                    if pitch is not None:
                        pending_grace[voice_key].append(pitch)
                    continue

                is_chord = first_child(item, "chord") is not None
                is_rest = first_child(item, "rest") is not None
                raw_duration = int_text(first_child(item, "duration"), 0)
                duration = Fraction(raw_duration, divisions * 4) if raw_duration > 0 else Fraction(1, divisions * 4)
                onset = last_start_by_voice.get(voice_key, cursor) if is_chord else cursor
                if not is_chord:
                    last_start_by_voice[voice_key] = onset
                chord_symbol = harmony_by_offset.pop(onset, None)
                event = Event(
                    part_id=part_id,
                    measure_index=measure_index,
                    staff=staff,
                    voice=voice,
                    onset=onset,
                    duration=duration,
                    kind="rest" if is_rest or pitch is None else "note",
                    pitches=[] if is_rest or pitch is None else [pitch],
                    grace=pending_grace.pop(voice_key, []),
                    tie_start=has_tie(item, "start"),
                    tie_stop=has_tie(item, "stop"),
                    chord_symbol=chord_symbol,
                )
                add_or_merge(measure.events, event)
                if not is_chord:
                    cursor += duration

            part.measures.append(measure)
        parts.append(part)

    warnings: list[str] = []
    if first_tempo is None:
        warnings.append("Tempo was missing in source; default Q:1/4=120 inserted for playback.")

    return ScoreModel(
        title=title,
        composer=composer,
        parts=parts,
        first_key=first_key,
        first_time=first_time,
        first_tempo=first_tempo,
        source_type=source_type,
        reliability_tier=reliability_tier,
        warnings=warnings,
        normalized_musicxml_path=str(path),
    )
