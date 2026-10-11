#!/usr/bin/env python3
"""
PDF Vector Engine - Lossless Vector PDF Merger
Merges multiple PDF documents preserving vector streams, font dictionaries,
and cross-references, with optional object stream optimization.
"""

import os
import sys
import argparse
from pathlib import Path

try:
    import pikepdf
except ImportError:
    pikepdf = None


def merge_pdfs(input_files, output_file, optimize=True):
    if pikepdf is None:
        print("[ERROR] pikepdf is required for PDF merging. Run: pip install pikepdf", file=sys.stderr)
        return False

    if not input_files:
        print("[ERROR] No input files provided for merging.", file=sys.stderr)
        return False

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"[MERGING] Combining {len(input_files)} PDF files into {output_file}...")

    merged_pdf = pikepdf.Pdf.new()
    total_pages = 0

    for fpath in input_files:
        p = Path(fpath)
        if not p.exists():
            print(f"[ERROR] Input file does not exist: {fpath}", file=sys.stderr)
            return False

        with pikepdf.Pdf.open(p) as src:
            page_count = len(src.pages)
            print(f"  + Appending '{p.name}' ({page_count} pages)")
            merged_pdf.pages.extend(src.pages)
            total_pages += page_count

    if optimize:
        print(f"[OPTIMIZE] Saving with ObjectStreamMode.generate and compressed streams...")
        merged_pdf.save(
            output_file,
            compress_streams=True,
            object_stream_mode=pikepdf.ObjectStreamMode.generate,
        )
    else:
        merged_pdf.save(output_file)

    final_size = os.path.getsize(output_file)
    print(f"[DONE] Merged {total_pages} pages -> {output_file} ({final_size:,} bytes)")
    return True


def main():
    parser = argparse.ArgumentParser(description="Lossless Vector PDF Merger")
    parser.add_argument("--inputs", "-i", nargs="+", required=True, help="List of PDF files to merge in order")
    parser.add_argument("--output", "-o", required=True, help="Output merged PDF file path")
    parser.add_argument("--no-optimize", action="store_true", help="Disable object stream optimization")

    args = parser.parse_args()
    ok = merge_pdfs(args.inputs, args.output, optimize=not args.no_optimize)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
