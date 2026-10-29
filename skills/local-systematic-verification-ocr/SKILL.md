---
name: local-systematic-verification-ocr
description: Transcribe and convert any non-OCR PDF, scanned PDF, image-only PDF, document image, photo of a document, handwritten note, or maths worksheet into Markdown or LaTeX with 100% verified-or-flagged coverage. Enforces a 12-level systematic verification stack with multi-engine deterministic cross-checks (PaddleOCR PP-OCRv5, RapidOCR, Tesseract PSM 6+11), symbol-by-symbol formula verification, cross-footing tables, and visual crop audits. Use when the user asks to OCR, transcribe, digitise, convert a scanned PDF, or run PDF to Markdown conversion where precision and mathematical accuracy override speed.
---

# Systematic Verification OCR

Transfer non-OCR (scanned, image-only) PDFs and high-resolution document images into structured Markdown, LaTeX, or user-specified target formats with 100% verified-or-flagged coverage. Every character is either verified against its source crop, or explicitly categorized as `REVIEW`, `BLOCK`, or `[illegible]`. No character is silently invented, interpolated, or "fixed" to appear plausible.

---

## 1. Honesty Contract

This contract overrides all pressure to produce smooth, complete-looking outputs:

1. **Hard Input Honesty**: Never claim 100% proven correctness on degraded scans, cursive handwriting, dense tables, or complex mathematical formulas. On clean print, verified accuracy approaches near-perfection. On degraded or ambiguous input, items land in `REVIEW` or `BLOCK`. That is the skill functioning correctly, not failing.
2. **Uncalibrated Confidence**: Never present raw engine confidence scores as probabilities of correctness. OCR engine confidence is uncalibrated until empirically fitted against the user's specific document corpus.
3. **Vendor Claims**: Never state vendor-reported accuracy metrics as unvarnished facts. Any vendor metric must be labeled as vendor-claimed along with its originating benchmark and document sample source.
4. **Physical Audit Trail**: Never claim a three-engine execution that did not occur, a GPU run that was not provisioned, or a benchmark not executed on the user's own physical files. The credibility of this skill rests entirely on its physical evidence audit trail.

---

## 2. When to Use and When NOT to Use

### When to Use
- Image-only, scanned, or non-OCR PDFs containing zero embedded selectable text.
- High-resolution scans or photos of academic papers, exam papers, scientific monographs, and technical specifications.
- Mathematical worksheets and dense algebraic documents where exponents, subscripts, fractions, and Greek symbols must be verified without loss.
- Financial or numerical tabular documents where row/column totals must be arithmetically verified via cross-footing.
- Handwritten notes, forms, and marginal annotations requiring explicit segregation between printed text and handwritten additions.

### When NOT to Use
- Born-digital PDFs containing an intact, clean text layer (extract via `pdftotext` or Python `pypdf`/`pdfplumber` directly; do not OCR).
- Casual text extraction requests where the user explicitly demands speed over verification and rejects audit overhead.
- Tasks requiring creative rewriting, summarization, or synthesis rather than faithful, verbatim transcription.
- Inferring or predicting missing document content beyond what is physically visible in the scan.

---

## 3. Quick Start Workflow

Follow this deterministic sequence for every document conversion:

```bash
# 1. Inspect PDF text layer (Level 0)
python3 -c "import pypdf; r=pypdf.PdfReader('input.pdf'); print([len(p.extract_text() or '') for p in r.pages])"

# 2. Render pages to 300 DPI PNGs (Level 1)
pdftoppm -png -r 300 input.pdf page

# 3. Run primary deterministic OCR (PaddleOCR tiled, Level 2)
# Environment: PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True enable_mkldnn=False ocr_version="PP-OCRv5"

# 4. Run secondary cross-check (RapidOCR + Tesseract PSM 6+11, Level 3)
# Compare raw token streams and emit discrepancy flags

# 5. Execute visual crop audits for every flag and formula (Levels 4 & 5)
# Reconcile discrepancies against rendered 300 DPI crops

# 6. Run format validator script (Level 10)
python3 scripts/validate.py output.md

# 7. Compile Level 12 Verification Report and deliver alongside output
```

For engine routing by hardware and input type, consult `references/engine-matrix.md`.

---

## 4. Prerequisites and the Proven Stack

This skill builds upon an empirically tested CPU-first OCR stack:

- **Core Pinned Stack**: PaddleOCR 3.7.0, PaddleX 3.7.2, PaddlePaddle 3.3.1 (CPU), `rapidocr`, Tesseract 5.3.4, OCRmyPDF 15.2.0, Ghostscript 10.02.1.
- **Mandatory PaddleOCR Quirks**:
  - `PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True` (blocks outbound network dependency checks).
  - `enable_mkldnn=False` (prevents CPU segmentation faults).
  - `ocr_version="PP-OCRv5"`. Disable unwarping, textline orientation, and angle classifiers unless page rotation is explicitly verified.
  - **Page Tiling**: Set maximum image dimension to 1500px; slice into 500px vertical strips with 100px overlap. `PP-OCRv5_server_det` triggers OS OOM-kills on images exceeding approximately 1M pixels in containerized environments.
- **Tesseract Dual-PSM Union**: PSM 6 alone misses table interiors; PSM 11 alone misses single-digit data cells. Run both modes and inspect the union.
- **Environmental Missing-Engine Resilience**: System apt packages do not survive container replacement. If Tesseract is missing, record `tesseract_available=false` and execute PaddleOCR + RapidOCR dual-engine verification. Never silently substitute a cloud API.
- **Docling Exclusion**: On controlled 3-line precision testing ("Precision test 12345" / "Rohit OCR check Rs 100" / "No hallucination allowed"), Docling scrambled line word order and hallucinated an invented word ("a"). Docling is permanently excluded as a text source of truth (structure proposals only).
- **Historical Benchmark (H.Y. Physics Exam Paper)**: 14 pages, Adobe Scan, 0 embedded characters, Q1–Q33, 96 MCQ options, 10 OR alternatives, 6 diagrams described verbally, zero ASCII art. Cross-check between PaddleOCR and RapidOCR generated 219 raw token flags (including PaddleOCR dropping `x` in Q2 option (c) and RapidOCR reading `900 m` as `9o0m`). Visual crop audit verified all 219 flags with zero change to the delivered file.

---

## 5. The 12-Level Systematic Verification Stack

Every level generates physical evidence. Any skipped level must be explicitly justified in the final report.

### Level 0: Embedded-Text Check
Evaluate page-by-page character counts of the PDF text layer. If a clean text layer exists, extract it directly. If zero characters are extracted and each page consists of a raster image, OCR is required.

### Level 1: Document Inventory & Quality Controls
Record total page count, render resolution (target: 300 DPI), and per-page ink density.
- **Control Checks**: Every batch includes a synthetic blank page control (must yield near-empty output) and a known ground-truth control page containing numbers, fractions, Greek characters, and tables. If either control fails, quarantine the batch immediately.

### Level 2: Deterministic Primary OCR
Generate 300 DPI page images and maintain as immutable visual ground truth. Execute PaddleOCR PP-OCRv5 with tiling. Preserve raw character bounding boxes and engine confidence scores. Zero LLM post-processing or cleanup.

### Level 3: Second-Engine Raw Cross-Check
Execute RapidOCR and Tesseract (PSM 6 + 11 union) on identical pages. Compare raw token streams prior to any formatting. Every token disagreement generates a review flag. Scan for character confusables in numeric and scientific contexts against `references/confusables.md`. Agreement between engines is corroborating evidence, never definitive proof.

### Level 4: Direct Visual Audit
Inspect rendered 300 DPI page images directly. Every flagged token, and every formula, table, and number—flagged or unflagged—is audited word-by-word against its high-resolution crop. Apply zoom crops for small print, superscripts, marks columns, and diagram labels. The delivered text is the visually confirmed text.

### Level 5: Mathematics Crop Pass (Symbol-by-Symbol)
Crop each equation block separately at full resolution. Never apply prose-cleaning within `$...$` or `$$...$$` regions.
- Render candidate LaTeX beside source crop and compare symbol-by-symbol: bases, superscript and subscript vertical offsets, numerator vs denominator, summation and integral limits, brackets, Greek symbols, and operators.
- Validate via LaTeX-to-SymPy parser. Expressions must parse without syntax errors. Check numeric equivalence on random test values where applicable.
- Count symbols by class in crop vs output. Any count mismatch is `BLOCK`.
- Horizontal fraction bars must format as `\frac{...}{...}`, never linearized as slashes unless the source prints a slash. Review known math failure modes in `references/failure-modes.md`.

### Level 6: Table & Structure Pass
Enforce a uniform column model across every row in a table block.
- **Cross-Footing**: Every stated subtotal and total must equal the exact sum of its components within rounding. A cross-foot discrepancy is an automatic `BLOCK` requiring visual crop audit.
- Box-audit every numeric cell in high-stakes documents. Preserve empty cells as empty markdown cells (`| |`), never filled with guesses.

### Level 7: Diagrams & Figures Pass
Retain diagrams and figures as cropped image assets with their verbatim captions. Transcribe only explicitly boxed, verified numeric labels.
- Describe geometric diagrams verbally in plain English.
- Never output chart data values unless printed as numeric labels in the figure.
- **Zero ASCII Art**: Never draw ASCII art diagrams unless the user explicitly requests ASCII art.

### Level 8: Handwriting Pass
Isolate handwriting via line-level crops. Transcribe using a specialist model or disputed vision re-read, followed by visual audit. Default verdict is `REVIEW`, never `PASS`. Unresolvable cursive loops remain `[illegible]`. Segregate handwritten annotations into an `### Annotations` section; never merge into printed text.

### Level 9: Document-Level Consistency
Verify sequential ordering of questions, sections, equations, tables, and figures. Confirm that internal cross-references resolve.
- **Preserve Verbatim Oddities**: Preserve spelling variants (e.g. "centre" vs "center"), typographical anomalies, and notation mismatches (e.g. text `$K$` vs diagram `$k$`). Never normalize or "correct" the source.

### Level 10: Mechanical Format Validation
Execute `scripts/validate.py` on the output markdown file. The script deterministically enforces:
- Balanced inline math (`$...$`) and display math (`$$...$$`) delimiters.
- Balanced curly braces (`{...}`) within math spans.
- Uniform column counts across all table rows.
- Sequential numbering of `**Q<number>.` headings.
- Detection of prohibited ASCII-art lines.
A parse failure or syntax defect triggers `BLOCK`.

### Level 11: Independent Re-Read
Perform a fresh blind audit over flagged lines: inspect the source crop without viewing previous transcriptions, then compare. Agreement upgrades `REVIEW` to `PASS`; persistent discrepancy remains `REVIEW` or escalates to `BLOCK`.

### Level 12: Delivery & Ship Gate
Execute each level against the copyable ledger in `references/verification-checklist.md`. Deliver the final converted document alongside a complete verification report formatted according to `examples/good-verification-report.md`.
- **Stop Rule**: Ship only when every flag is resolved to `PASS` or explicitly accepted by the user, or when unresolved `BLOCK` items are listed in an appendix. Never ship silent guesses. Never bulk-accept flags.

---

## 6. Verdicts

- **PASS**: Primary and secondary engines agree or visual crop audit confirms transcription; confidence meets corpus calibration; all structural and format checks green.
- **REVIEW**: Engine discrepancies, character confusables in numbers/symbols, handwriting, unverified table cells, or ambiguous scan crops requiring user confirmation.
- **BLOCK**: Blank page control failed, table cross-foot failed, LaTeX unparseable, missing page detected, or unresolved discrepancies in high-stakes numbers. Blocked content is quarantined in an appendix, never silently deleted.

---

## 7. Output Contract

1. **Requested Scope Only**: Transcribe only the requested content. If the user requests "only the questions", exclude running headers, page numbers, form IDs, and "End of Paper" markers from question text.
2. **Mathematical Consistency**: Use Unicode math for prose or LaTeX `$...$` / `$$...$$` when LaTeX is requested. Maintain uniform conventions throughout the file.
3. **Diagrams**: Retain as linked image crops with verbal explanations. Never generate ASCII art unless explicitly commanded.
4. **Verbatim Fidelity**: Preserve source typos, archaic spellings, and idiosyncratic notations verbatim with explanatory notes in the audit report.
5. **Mandatory Delivery TLDR**: End every substantive delivery with a concise summary:
   - What was done (pages processed, engines used).
   - What was found (discrepancy counts, resolved flags).
   - What the user needs to do next (actions for persisting `REVIEW` items).

---

## 8. Error Handling

- **Missing Engine**: Log missing binary (e.g. `tesseract_available=false`), proceed with remaining deterministic engines, report missing coverage in Level 12 report. Never silently invoke cloud vision APIs.
- **GPU Unavailable**: Fall back to CPU-tiled execution. Do not switch to remote proprietary models.
- **Unparseable LaTeX / Broken Braces**: Escalate to `BLOCK`. Record line number and raw formula string in the verification appendix.
- **VLM vs Deterministic Disagreement**: When a vision model disagrees with deterministic engines, treat as `BLOCK`. The physical 300 DPI crop is the sole decider.
- **Answers / Solutions**: Transcribing questions and generating solutions are distinct tasks. Never append answers or solutions unless explicitly requested.

---

## 9. Testing Before Shipping

Before declaring a skill implementation or document conversion complete, verify the 6 validation gates:

1. **Frontmatter Gate**: Name matches directory exactly, description is under 1024 characters with all trigger keywords, frontmatter contains only `name` and `description`.
2. **Structure Gate**: All files in `scripts/`, `references/`, and `examples/` exist; all reference links resolve one level deep without chaining.
3. **Script Gate**: `scripts/validate.py` exits 0 on valid documents and exits 2 (`BLOCK`) on unbalanced delimiters or broken tables.
4. **Trigger Gate**: Description reliably triggers on OCR/transcription keywords and rejects born-digital or summarization queries.
5. **Regression Gate**: Reproduce H.Y. paper benchmark counts (14 pages, Q1–Q33, 96 options, 10 alternatives, 6 diagrams, 219 flags).
6. **Failure Gate**: Blank page control yields near-empty output; hallucinated text on blank page fails the run.
