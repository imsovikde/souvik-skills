#!/usr/bin/env python3
"""
PDF Vector Engine - Target Window Byte Calibrator
Calibrates PDF file sizes into strict statutory byte windows using ISO 32000
comment padding tokens without modifying rendering or object offsets.
"""

import os
import sys
import argparse
import shutil
from pathlib import Path


def calibrate_file(input_file, output_file, min_bytes, max_bytes):
    input_path = Path(input_file)
    output_path = Path(output_file)
    cur_size = os.path.getsize(input_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if cur_size > max_bytes:
        print(f"[ERROR] {input_file} ({cur_size:,} B) exceeds max window ({max_bytes:,} B). Re-compression required.", file=sys.stderr)
        return False

    if min_bytes <= cur_size <= max_bytes:
        print(f"[OK] {input_file} already within target window [{min_bytes:,} B, {max_bytes:,} B].")
        if input_path.resolve() != output_path.resolve():
            shutil.copy2(input_path, output_path)
        return True

    # cur_size < min_bytes -> append ISO 32000 comment padding
    pad_needed = min_bytes - cur_size + 2048  # Aim comfortably inside the window
    if cur_size + pad_needed > max_bytes:
        pad_needed = min_bytes - cur_size + 64

    if input_path.resolve() != output_path.resolve():
        shutil.copy2(input_path, output_path)

    # ISO 32000 section 7.2.3: comment token starts with '%' outside strings/streams
    comment_payload = b"\n% " + (b"0" * (pad_needed - 4)) + b"\n"
    with open(output_path, "ab") as f:
        f.write(comment_payload)

    new_size = os.path.getsize(output_path)
    success = min_bytes <= new_size <= max_bytes
    print(f"[CALIBRATED] {input_file} ({cur_size:,} B) -> {output_path} ({new_size:,} B) [Success: {success}]")
    return success


def main():
    parser = argparse.ArgumentParser(description="Calibrate PDF to target byte window")
    parser.add_argument("--input", "-i", required=True, help="Input PDF file")
    parser.add_argument("--output", "-o", required=True, help="Output PDF file")
    parser.add_argument("--min-bytes", type=int, default=1843200, help="Minimum byte floor (default: 1,843,200 = 1.8 MB)")
    parser.add_argument("--max-bytes", type=int, default=2097151, help="Maximum byte ceiling (default: 2,097,151 = 2.0 MB)")

    args = parser.parse_args()
    ok = calibrate_file(args.input, args.output, args.min_bytes, args.max_bytes)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
