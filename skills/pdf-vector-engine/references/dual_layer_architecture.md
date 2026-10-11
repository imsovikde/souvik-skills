# Dual-Layer Hybrid Architecture for Document Compression

## Executive Summary

Legal dispute petitions and financial submissions submitted to regulatory bodies (e.g. RBI Ombudsman) comprise two fundamentally different categories of pages:
1. **Primary Substantive Legal Content**: Complaint narratives, legal notices, statutory declarations, bank account statements, dispute tickets, and authorization letters.
2. **Diagnostic Technical Dumps**: Multi-page raw email exchange headers (RFC 822 / MIME), SMTP transport trees, DKIM/SPF logs, and system error traces appended as evidentiary trails.

Treating both types identically leads to failure: pure vector quantization of millions of log lines produces oversized files (>8 MB), while full-document rasterization blurs primary legal notices and causes rejection.

The **Dual-Layer Hybrid Architecture** solves this trade-off deterministically.

---

## 1. Page Classification Heuristics

The engine classifies each page $P_i$ ($i = 1, \dots, N$) into either the **Substantive Vector Rail** or the **Diagnostic Dump Rail** based on structural and contextual analysis:

- **Page 1 Invariant**: Page 1 is ALWAYS processed on the **Substantive Vector Rail** using `r2dec` (0.01 pt precision). It carries the master letterhead, regulatory references, case IDs, and signatures.
- **Content Inspection**:
  - If page content consists of formatted paragraphs, tables, legal seals, or scanned exhibits $\rightarrow$ **Substantive Vector Rail**.
  - If page content exhibits high-density monospace text blocks exceeding 80 lines/page containing headers such as `Received: from`, `X-MS-Exchange-`, `Authentication-Results:`, `Message-ID:`, `Thread-Index:` $\rightarrow$ **Diagnostic Dump Rail**.
  - CLI flag `--hybrid` enables automatic routing. The user can also supply explicit page ranges (e.g., `--diagnostic-pages 3-8`).

---

## 2. Processing Rails

### Rail 1: Substantive Vector Rail (Infinite Scalability)
- Content streams are parsed using tokenized regular expressions.
- Coordinate operands for curve operators (`m`, `l`, `c`, `v`, `y`, `re`) are quantized to sub-pixel grids (`r2dec` or `r025`).
- Coordinate Transformation Matrices (`cm`), clipping paths (`W`, `W*`), and color spaces (`rg`, `RG`, `k`, `K`) are preserved without change.
- Text maintains infinite vector scalability under 400%–1000% zoom.

### Rail 2: Diagnostic Dump Rail (8-Color 4-Bit Indexed Flate)
For diagnostic logs where vector curve operators consume millions of tokens:
1. **Rasterization**: Render page at 72–144 DPI using `pypdfium2`.
2. **Palette Quantization**: Map RGB values to an adaptive 8-color palette (retaining crisp background, black text, and status badge colors).
3. **Bit-Packing**: Pack 3-bit palette indices into 4-bit nibbles (2 pixels per byte), reducing raw pixel data by 75% compared to 24-bit RGB.
4. **Flate Compression**: Compress packed bytes using `zlib.compress(packed, level=9)`.
5. **Stream Embedding**: Inject the compressed image as a native `/XObject` with `/ColorSpace [/Indexed /DeviceRGB 7 <Palette>]`, `/BitsPerComponent 4`, and `/Filter /FlateDecode`.

---

## 3. Consolidation and Calibration

Once both rails complete:
1. Pages are re-assembled into a single `pikepdf.Pdf` container.
2. Cross-reference tables and non-stream objects are packed into object streams using `pikepdf.ObjectStreamMode.generate`.
3. If the final file size is below the target lower bound (e.g., `< 1.8 MB`), the calibrator appends ISO 32000 comment padding (`\n% 0000...\n`) to bring the size strictly into the compliance window.
