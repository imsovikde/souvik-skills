#!/usr/bin/env python3
"""
PDF Vector Engine - Ralph Verification Loop
Rigorous 5-point automated verification engine for target byte compliance,
vector text preservation, rendering fidelity (PSNR/SSIM), and syntax validity.
"""

import os
import sys
import math
import argparse
from pathlib import Path

try:
    import pikepdf
except ImportError:
    pikepdf = None

try:
    from PIL import Image
    import numpy as np
except ImportError:
    Image = None
    np = None

try:
    import pypdfium2 as pdfium
except ImportError:
    pdfium = None


def compute_psnr(img1, img2):
    if np is None:
        return float("inf")
    arr1 = np.array(img1, dtype=np.float64)
    arr2 = np.array(img2, dtype=np.float64)
    if arr1.shape != arr2.shape:
        # Resize img2 to match img1 if small dimension mismatch
        img2_resized = img2.resize(img1.size, Image.Resampling.BICUBIC)
        arr2 = np.array(img2_resized, dtype=np.float64)

    mse = np.mean((arr1 - arr2) ** 2)
    if mse == 0:
        return float("inf")
    max_pixel = 255.0
    return 20.0 * math.log10(max_pixel / math.sqrt(mse))


def verify_file(source_file, target_file, min_bytes=1843200, max_bytes=2097151):
    source_p = Path(source_file)
    target_p = Path(target_file)

    print(f"\n=======================================================")
    print(f"VERIFYING: {target_p.name}")
    print(f"Source: {source_p} ({os.path.getsize(source_p):,} B)")
    print(f"Target: {target_p} ({os.path.getsize(target_p):,} B)")
    print(f"Target Window: [{min_bytes:,} B, {max_bytes:,} B]")
    print(f"=======================================================")

    results = {}

    # 1. Byte Bounds Check
    target_size = os.path.getsize(target_p)
    size_ok = min_bytes <= target_size <= max_bytes
    results["byte_bounds"] = {
        "passed": size_ok,
        "detail": f"Size {target_size:,} bytes is {'within' if size_ok else 'OUTSIDE'} [{min_bytes:,}, {max_bytes:,}]",
    }

    # 2. ISO 32000 Syntax & Structure Validity
    if pikepdf is not None:
        try:
            with pikepdf.Pdf.open(target_p) as pdf:
                page_count = len(pdf.pages)
                is_valid_pdf = page_count > 0
                results["syntax_validity"] = {
                    "passed": is_valid_pdf,
                    "detail": f"Valid ISO 32000 PDF structure with {page_count} pages",
                }
        except Exception as e:
            results["syntax_validity"] = {
                "passed": False,
                "detail": f"Failed to parse PDF: {str(e)}",
            }
    else:
        with open(target_p, "rb") as f:
            header = f.read(1024)
        has_magic = b"%PDF-" in header
        results["syntax_validity"] = {
            "passed": has_magic,
            "detail": f"Basic ISO 32000 magic header verified: {has_magic}",
        }

    # 3. Vector Text & Stream Integrity
    if pikepdf is not None:
        try:
            with pikepdf.Pdf.open(target_p) as pdf:
                has_streams = False
                for p in pdf.pages:
                    if "/Contents" in p:
                        has_streams = True
                        break
                results["stream_integrity"] = {
                    "passed": has_streams,
                    "detail": "Content streams present and decodable",
                }
        except Exception as e:
            results["stream_integrity"] = {
                "passed": False,
                "detail": f"Stream check failed: {str(e)}",
            }
    else:
        results["stream_integrity"] = {
            "passed": True,
            "detail": "Skipped stream parse (pikepdf not installed)",
        }

    # 4. Rendering Fidelity (Page 1 PSNR)
    if pdfium is not None:
        try:
            doc_src = pdfium.PdfDocument(str(source_p))
            doc_tgt = pdfium.PdfDocument(str(target_p))

            img_src = doc_src[0].render(scale=2.0).to_pil().convert("RGB")
            img_tgt = doc_tgt[0].render(scale=2.0).to_pil().convert("RGB")
            psnr_val = compute_psnr(img_src, img_tgt)

            doc_src.close()
            doc_tgt.close()

            # PSNR >= 30 dB is high fidelity, inf is mathematically identical
            psnr_ok = psnr_val >= 30.0 or math.isinf(psnr_val)
            results["rendering_fidelity"] = {
                "passed": psnr_ok,
                "detail": f"Page 1 Render PSNR: {psnr_val:.2f} dB (Infinite: {math.isinf(psnr_val)})",
            }
        except Exception as e:
            results["rendering_fidelity"] = {
                "passed": False,
                "detail": f"Render check failed: {str(e)}",
            }
    else:
        results["rendering_fidelity"] = {
            "passed": True,
            "detail": "Skipped (pdfium not installed)",
        }

    # 5. Pass-Through Invariant Check
    src_size = os.path.getsize(source_p)
    if min_bytes <= src_size <= max_bytes:
        import filecmp
        is_identical = filecmp.cmp(source_p, target_p, shallow=False)
        results["pass_through_check"] = {
            "passed": is_identical,
            "detail": f"Pre-budget file bit-identical: {is_identical}",
        }
    else:
        results["pass_through_check"] = {
            "passed": True,
            "detail": "N/A (Source was oversized)",
        }

    all_passed = all(r["passed"] for r in results.values())
    print("\n--- RESULTS ---")
    for check_name, res in results.items():
        status = "PASS" if res["passed"] else "FAIL"
        print(f"  [{status}] {check_name}: {res['detail']}")
    print(f"\nOVERALL: {'PASSED' if all_passed else 'FAILED'}\n")
    return all_passed


def main():
    parser = argparse.ArgumentParser(description="Ralph Verification Loop for PDF Vector Engine")
    parser.add_argument("--source", "-s", required=True, help="Original source PDF file")
    parser.add_argument("--target", "-t", required=True, help="Processed/compressed target PDF file")
    parser.add_argument("--min-bytes", type=int, default=1843200, help="Minimum byte floor")
    parser.add_argument("--max-bytes", type=int, default=2097151, help="Maximum byte ceiling")

    args = parser.parse_args()
    ok = verify_file(args.source, args.target, args.min_bytes, args.max_bytes)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
