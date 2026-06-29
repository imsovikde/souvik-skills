from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Literal


SourceKind = Literal[
    "mxl",
    "musicxml",
    "xml",
    "abc",
    "midi",
    "pdf",
    "image",
    "audio",
    "video",
    "youtube",
]


@dataclass(frozen=True)
class Pitch:
    step: str
    alter: int
    octave: int


@dataclass
class Event:
    part_id: str
    measure_index: int
    staff: int
    voice: str
    onset: Fraction
    duration: Fraction
    kind: Literal["note", "rest"]
    pitches: list[Pitch] = field(default_factory=list)
    grace: list[Pitch] = field(default_factory=list)
    tie_start: bool = False
    tie_stop: bool = False
    chord_symbol: str | None = None


@dataclass
class KeySignature:
    fifths: int = 0
    mode: str = "major"

    @property
    def abc_name(self) -> str:
        major = {
            -7: "Cb",
            -6: "Gb",
            -5: "Db",
            -4: "Ab",
            -3: "Eb",
            -2: "Bb",
            -1: "F",
            0: "C",
            1: "G",
            2: "D",
            3: "A",
            4: "E",
            5: "B",
            6: "F#",
            7: "C#",
        }
        minor = {
            -7: "Abm",
            -6: "Ebm",
            -5: "Bbm",
            -4: "Fm",
            -3: "Cm",
            -2: "Gm",
            -1: "Dm",
            0: "Am",
            1: "Em",
            2: "Bm",
            3: "F#m",
            4: "C#m",
            5: "G#m",
            6: "D#m",
            7: "A#m",
        }
        table = minor if self.mode.lower().startswith("min") else major
        return table.get(self.fifths, "C")


@dataclass
class TimeSignature:
    beats: int = 4
    beat_type: int = 4

    @property
    def abc_name(self) -> str:
        if self.beats == 2 and self.beat_type == 2:
            return "C|"
        return f"{self.beats}/{self.beat_type}"

    @property
    def measure_length(self) -> Fraction:
        return Fraction(self.beats, self.beat_type)


@dataclass
class MeasureModel:
    number: str
    index: int
    key: KeySignature
    time: TimeSignature
    divisions: int
    events: list[Event] = field(default_factory=list)
    repeat_start: bool = False
    repeat_end: bool = False
    ending: str | None = None


@dataclass
class PartModel:
    id: str
    name: str
    measures: list[MeasureModel] = field(default_factory=list)


@dataclass
class ScoreModel:
    title: str
    composer: str | None
    parts: list[PartModel]
    first_key: KeySignature
    first_time: TimeSignature
    first_tempo: int | None
    source_type: str
    reliability_tier: str
    warnings: list[str] = field(default_factory=list)
    normalized_musicxml_path: str | None = None


@dataclass
class VerificationReport:
    source_format: str
    reliability_tier: str
    title: str
    composer: str | None
    parts: int
    staves: int
    measures: int
    pitched_notes: int
    rests: int
    chord_events: int
    grace_notes: int
    ties: int
    key_changes: int
    time_changes: int
    repeats_endings: int
    tempo_status: str
    status: str
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "source_format": self.source_format,
            "reliability_tier": self.reliability_tier,
            "title": self.title,
            "composer": self.composer,
            "parts": self.parts,
            "staves": self.staves,
            "measures": self.measures,
            "pitched_notes": self.pitched_notes,
            "rests": self.rests,
            "chord_events": self.chord_events,
            "grace_notes": self.grace_notes,
            "ties": self.ties,
            "key_changes": self.key_changes,
            "time_changes": self.time_changes,
            "repeats_endings": self.repeats_endings,
            "tempo_status": self.tempo_status,
            "status": self.status,
            "warnings": self.warnings,
        }
