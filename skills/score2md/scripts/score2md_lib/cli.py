from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .detect import detect_source, reliability_tier
from .musicxml_reader import parse_score
from .pipeline import ConversionOptions, convert_to_md, normalize_to_musicxml
from .verify import source_counts, verify_markdown_shape


def add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--mode", default="compact-piano", choices=["compact-piano", "lossless-voices"])
    parser.add_argument("--explicit-accidentals", action="store_true", default=True)
    parser.add_argument("--default-tempo", type=int, default=120)
    parser.add_argument("--line-measures", type=int, default=2)
    parser.add_argument("--verify", default="strict", choices=["strict", "summary"])
    parser.add_argument("--keep-intermediate", action="store_true")
    parser.add_argument("--musescore-path")
    parser.add_argument("--omr-workers", type=int, default=2)
    parser.add_argument("--omr-module")
    parser.add_argument("--ffmpeg-path")
    parser.add_argument("--refresh-cache", action="store_true")
    parser.add_argument("--ohsheet-timeout", type=int, default=900)
    parser.add_argument("--ohsheet-prefer-clean-source", dest="ohsheet_prefer_clean_source", action="store_true", default=True)
    parser.add_argument("--no-ohsheet-prefer-clean-source", dest="ohsheet_prefer_clean_source", action="store_false")
    parser.add_argument("--skip-preflight", action="store_true", help="Bypass the audio/YouTube/video resource guard.")
    parser.add_argument(
        "--allow-uncertain-audio",
        action="store_true",
        help="Allow audio/YouTube/video sources that preflight cannot confidently classify as music.",
    )
    parser.add_argument("--max-media-duration", dest="max_media_duration_sec", type=int, default=900)
    parser.add_argument("--youtube-metadata-timeout", type=int, default=8)


def options_from_args(args: argparse.Namespace) -> dict:
    return {
        "mode": args.mode,
        "explicit_accidentals": args.explicit_accidentals,
        "default_tempo": args.default_tempo,
        "line_measures": args.line_measures,
        "verify": args.verify,
        "keep_intermediate": args.keep_intermediate,
        "musescore_path": args.musescore_path,
        "omr_workers": args.omr_workers,
        "omr_module": args.omr_module,
        "ffmpeg_path": args.ffmpeg_path,
        "refresh_cache": args.refresh_cache,
        "ohsheet_timeout": args.ohsheet_timeout,
        "ohsheet_prefer_clean_source": args.ohsheet_prefer_clean_source,
        "skip_preflight": args.skip_preflight,
        "allow_uncertain_audio": args.allow_uncertain_audio,
        "max_media_duration_sec": args.max_media_duration_sec,
        "youtube_metadata_timeout": args.youtube_metadata_timeout,
    }


def cmd_convert(args: argparse.Namespace) -> int:
    result = convert_to_md(args.input, args.out, **options_from_args(args))
    print(json.dumps(result.to_dict(), indent=2))
    return 0


def cmd_to_musicxml(args: argparse.Namespace) -> int:
    kind = detect_source(args.input)
    options = ConversionOptions(**options_from_args(args))
    out = Path(args.out)
    normalized, _used_cache = normalize_to_musicxml(args.input, kind, out.parent / ".score2md-cache", options)
    if normalized is None:
        raise ValueError(f"Could not normalize {args.input}")
    if Path(normalized).resolve() != out.resolve():
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(Path(normalized).read_bytes())
    print(str(out))
    return 0


def cmd_musicxml_to_md(args: argparse.Namespace) -> int:
    result = convert_to_md(args.input, args.out, **options_from_args(args))
    print(json.dumps(result.to_dict(), indent=2))
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    kind = detect_source(args.musicxml)
    model = parse_score(Path(args.musicxml), kind, reliability_tier(kind))
    counts = source_counts(model)
    problems = verify_markdown_shape(Path(args.markdown))
    print(json.dumps({"source_counts": counts, "markdown_shape_problems": problems}, indent=2))
    return 1 if problems else 0


def cmd_inspect(args: argparse.Namespace) -> int:
    kind = detect_source(args.input)
    info: dict[str, object] = {"source": args.input, "source_type": kind, "reliability_tier": reliability_tier(kind)}
    if kind in {"mxl", "musicxml", "xml"}:
        model = parse_score(Path(args.input), kind, reliability_tier(kind))
        info.update(
            {
                "title": model.title,
                "composer": model.composer,
                "parts": len(model.parts),
                "counts": source_counts(model),
            }
        )
    print(json.dumps(info, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="score2md", description="Convert music sources to playable Markdown ABC.")
    sub = parser.add_subparsers(dest="command", required=True)

    convert = sub.add_parser("convert", help="Convert any supported input to Markdown ABC")
    convert.add_argument("input")
    convert.add_argument("--out", required=True)
    add_common_options(convert)
    convert.set_defaults(func=cmd_convert)

    to_musicxml = sub.add_parser("to-musicxml", help="Normalize a supported input to MusicXML")
    to_musicxml.add_argument("input")
    to_musicxml.add_argument("--out", required=True)
    add_common_options(to_musicxml)
    to_musicxml.set_defaults(func=cmd_to_musicxml)

    musicxml_to_md = sub.add_parser("musicxml-to-md", help="Convert MusicXML/MXL/XML to Markdown ABC")
    musicxml_to_md.add_argument("input")
    musicxml_to_md.add_argument("--out", required=True)
    add_common_options(musicxml_to_md)
    musicxml_to_md.set_defaults(func=cmd_musicxml_to_md)

    verify = sub.add_parser("verify", help="Verify source counts and Markdown ABC shape")
    verify.add_argument("musicxml")
    verify.add_argument("markdown")
    verify.set_defaults(func=cmd_verify)

    inspect = sub.add_parser("inspect", help="Inspect source type and symbolic counts")
    inspect.add_argument("input")
    inspect.set_defaults(func=cmd_inspect)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
