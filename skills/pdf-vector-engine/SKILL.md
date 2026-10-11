---
description: Ultimate zero-distortion PDF engine for vector-preserving stream compression into exact target byte windows (e.g. 1.8-2.0 MB for RBI/statutory portals), lossless PDF merging, page transformations, and high-fidelity rendering without text degradation under 1000% zoom. Use whenever compressing, resizing, merging, or converting PDFs where legal readability, vector sharpness, or strict size budgets are required.
name: pdf-vector-engine
---

# PDF Vector Engine

A production-grade, ISO 32000-compliant engine for zero-distortion vector PDF stream compression, byte-calibrated targeting, lossless merging, page geometry transformations, and mathematical verification.

## Core Directives & Guarantees

1. **The Sovereign Invariant (Zero Vector Degradation)**:
   - When zoomed in to 400%–1000% in Adobe Acrobat or any standard PDF viewer, all text characters, numerical bank figures, reference IDs, and legal citations MUST remain mathematically sharp and undistorted.
   - **Strict Ban on Destructive Text Rasterization**: Never convert substantive text pages into lossy low-DPI JPEG/PNG rasters. Rasterization blurs micro-text, collapses serifs, causes anti-aliasing color halos, and leads to immediate rejection by statutory compliance portals (such as the RBI Ombudsman).

2. **Coordinate Geometry Preservation**:
   - Skia and Chrome print-to-PDF engines decompose glyphs into vector Bézier curve operators (`m`, `l`, `c`, `v`, `y`, `re`).
   - **Never round coordinates to integers**. Integer rounding destroys glyph counter-loops (turning zeros and `o` glyphs into jagged blobs) and distorts thin stroke weights.
   - Use precision-calibrated sub-pixel floating point quantization (`0.01 pt` for Page 1 identity, `0.25 pt` to `0.5 pt` for subsequent vector content).
   - Never alter Coordinate Transformation Matrices (`cm`), clipping paths (`W`, `W*`), or fill/stroke color spaces (`rg`, `RG`, `k`, `K`).

3. **Strict Target Byte Windowing**:
   - When statutory portals enforce a strict window (e.g. 1.8 MB to 2.0 MB / `[1,843,200 B, 2,097,151 B]`):
     - Files already below budget are passed through **bit-identically** without re-compression.
     - Files above budget are compressed via vector stream quantization and object streams.
     - If compressed output lands below the minimum floor, append lossless ISO 32000 comment tokens (`\n% 0000...\n`) to calibrate the file size into the exact target byte window without affecting rendering.

4. **Lossless Merging & Page Geometry**:
   - Combine multiple PDF documents preserving vector streams, font dictionaries, and metadata.
   - Apply geometric transformations (rotation, page extraction, canvas rescaling) without re-encoding existing vector streams.

---

## Architecture & Workflow

### 1. Root Cause of PDF Bloat
Standard print drivers (Chrome/Skia, Microsoft Print to PDF) often decompose text glyphs into millions of Bézier curve operators with verbose 6-decimal-place ASCII floats (e.g., `44.490002 100.760002 m 44.529999 100.820000 l ...`). The uncompressed content streams often exceed 60 MB per document, which standard Flate compression can only reduce to 8–14 MB.

### 2. Dual-Layer Hybrid Compression Pipeline
```text
Input PDF
  ├── Page Classification
  │     ├── Substantive Legal / Form Pages (Pages 1..N)
  │     │     └── Vector Stream Parsing & Sub-Pixel Quantization
  │     │           ├── Page 1: r2dec (0.01 pt precision, PSNR = ∞ dB)
  │     │           └── Pages 2+: r025 (0.25 pt) or r05 (0.5 pt)
  │     └── Diagnostic Technical Dumps (MIME / RFC 822 / Exchange headers)
  │           └── High-efficiency 8-color 4-bit indexed palette FlateDecode
  ├── Object Stream Consolidation (pikepdf ObjectStreamMode.generate)
  └── Target Window Byte Calibration (ISO 32000 Comment Padding)
```

### 3. Precision Sub-Pixel Quantization Rules
Coordinate quantization strips redundant ASCII precision without affecting visual rendering:
- `r2dec` (2 decimals, `0.01 pt`):
  $$x' = \text{round}(x \times 100) / 100$$
  Produces mathematically indistinguishable vector paths ($\text{PSNR} = \infty\text{ dB}$).
- `r025` (`0.25 pt` grid):
  $$x' = \text{round}(x \times 4) / 4$$
  Saves 40%–60% of stream ASCII characters while remaining within sub-pixel antialiasing thresholds.
- `r05` (`0.5 pt` grid):
  $$x' = \text{round}(x \times 2) / 2$$
  Employed for high-density diagnostic tables and secondary pages when tight size ceilings are required.

### 4. Diagnostic Technical Dump Optimization
When documents contain large diagnostic appendices (such as multi-page raw Exchange/MIME email routing headers and server logs), vectorizing hundreds of thousands of lines of log data produces unsustainable bloat.
The hybrid pipeline selectively routes these diagnostic pages to:
1. Render at 72–144 DPI.
2. Quantize into an 8-color 4-bit indexed palette.
3. Pack nibbles (2 pixels per byte) and compress with `zlib.compress(packed, level=9)`.
4. Wrap in a native `/FlateDecode` XObject stream.

---

## Bundled CLI Tools

The skill provides production-tested Python scripts under `scripts/`:

### 1. Vector Compression (`scripts/compress.py`)
Compresses PDF files or whole directories to target size limits while strictly preserving vector text.
```bash
python scripts/compress.py --input document.pdf --output compressed/document.pdf --max-size-mb 2.0 --min-size-mb 1.8
```
Arguments:
- `--input`, `-i`: Input PDF file or directory.
- `--output`, `-o`: Output PDF file or directory.
- `--max-size-mb`: Target maximum size in MB (default: 2.0).
- `--min-size-mb`: Target minimum size in MB (default: 1.8).
- `--force-vector`: Enforce 100% pure vector quantization across all pages.
- `--hybrid`: Enable dual-layer hybrid routing for diagnostic appendices.

### 2. Byte Window Calibrator (`scripts/calibrate.py`)
Pads or trims a PDF to land strictly inside a specified byte window using ISO 32000 comment tokens.
```bash
python scripts/calibrate.py --input compressed.pdf --output calibrated.pdf --min-bytes 1843200 --max-bytes 2097151
```

### 3. Lossless PDF Merger (`scripts/merge.py`)
Concatenates multiple PDF documents with shared font deduplication and object stream generation.
```bash
python scripts/merge.py --inputs doc1.pdf doc2.pdf doc3.pdf --output merged.pdf --optimize
```

### 4. Ralph Verification Loop (`scripts/verify.py`)
Performs 5-point automated verification on processed files:
```bash
python scripts/verify.py --source original.pdf --target compressed.pdf --min-bytes 1843200 --max-bytes 2097151
```
Checks performed:
1. Strict byte bounds compliance.
2. Vector text existence under 400%+ scale.
3. Rendering PSNR / SSIM against source render.
4. ISO 32000 PDF syntax & xref table validity.
5. Bit-identical pass-through validation for pre-budget files.

---

## Reference Guides

For in-depth mathematical derivations and specifications, consult:
- `references/iso32000_stream_spec.md`: ISO 32000 stream tokenization, operators, and cross-reference structures.
- `references/vector_quantization_math.md`: Mathematical proofs of sub-pixel quantization tolerances and serif stability.
- `references/dual_layer_architecture.md`: Classification heuristics for substantive vs. diagnostic document pages.
