# The 12-Level Systematic Verification Checklist

This copyable verification ledger must be executed for every document transcription. Every level requires recorded physical evidence. Any skipped level must be explicitly identified in the final verification report along with the mechanistic justification.

```markdown
### Systematic Verification Audit Ledger

- [ ] **Level 0: Embedded-Text Check**
  - *Evidence / Output*: [Page-by-page character count. Extract born-digital text if present; confirm 0 chars + raster image for true image-only OCR.]
  - *Status*: [PASS | SKIP (Born-digital extracted) | BLOCK]

- [ ] **Level 1: Document Inventory & Quality Controls**
  - *Evidence / Output*: [Total pages, image DPI (target: 300 DPI), ink coverage per page. Blank control page verification (must yield near-zero text). Known ground-truth control page result.]
  - *Status*: [PASS | BLOCK (Control failed)]

- [ ] **Level 2: Deterministic Primary OCR**
  - *Evidence / Output*: [Primary engine used (e.g. PaddleOCR PP-OCRv5 CPU tiled, max side 1500px, 500px strips with 100px overlap). Bounding boxes and confidence scores preserved. Zero LLM cleanup.]
  - *Status*: [PASS | REVIEW | BLOCK]

- [ ] **Level 3: Second-Engine Raw Cross-Check**
  - *Evidence / Output*: [Cross-check engine outputs (RapidOCR ONNX, Tesseract PSM 6 + 11 union). Raw token diff count. Number of confusable character flags generated.]
  - *Status*: [PASS | REVIEW (Flags generated)]

- [ ] **Level 4: Direct Visual Audit**
  - *Evidence / Output*: [High-resolution crop inspection of all flagged tokens, numeric sequences, and table cells against rendered source images. Delivered text confirmed against visual ground truth.]
  - *Status*: [PASS | REVIEW]

- [ ] **Level 5: Mathematics Crop Pass (Symbol-by-Symbol)**
  - *Evidence / Output*: [Formula-level crops evaluated. LaTeX syntax validation and SymPy AST parsing results. Verification of superscripts, subscripts, limits, fraction bars (`\frac`), and operator bounds. Class symbol counts matched.]
  - *Status*: [PASS | REVIEW | BLOCK (Parse/numeric failure)]

- [ ] **Level 6: Table & Structure Verification**
  - *Evidence / Output*: [Uniform column count verified across all table blocks. Cross-footing arithmetic validation: sum of row/column cells reconciled with stated totals. Box audit of numeric cells.]
  - *Status*: [PASS | BLOCK (Cross-foot failure)]

- [ ] **Level 7: Diagrams & Figures Preservation**
  - *Evidence / Output*: [Diagrams retained as image assets with captions. Transcribed text restricted to explicitly boxed, verified labels. Verbal descriptions provided; zero hallucinated data points; zero ASCII art.]
  - *Status*: [PASS | REVIEW]

- [ ] **Level 8: Handwriting & Annotation Pass**
  - *Evidence / Output*: [Line-level crops. Specialist model or disputed vision re-read visually audited. Cursive loops marked [illegible] if unresolvable. Marginalia segregated from body text.]
  - *Status*: [PASS (Measured hand) | REVIEW (Default) | BLOCK]

- [ ] **Level 9: Document-Level Consistency**
  - *Evidence / Output*: [Sequential verification of questions, sections, equations, tables, and figures. Cross-references resolved. Verbatim spelling, regional variants, and typographic anomalies preserved.]
  - *Status*: [PASS | REVIEW]

- [ ] **Level 10: Mechanical Format Validation**
  - *Evidence / Output*: [Execution of `scripts/validate.py`. Delimiter parity ($...$, $$...$$), balanced braces in math regions, table column integrity, and question sequence check.]
  - *Status*: [PASS (Exit 0) | REVIEW (Exit 1) | BLOCK (Exit 2)]

- [ ] **Level 11: Independent Re-Read**
  - *Evidence / Output*: [Blind second-pass inspection of disputed/flagged crops without viewing prior transcriptions. Outcome of comparisons and resolution status.]
  - *Status*: [PASS (Resolved) | REVIEW (Persisting ambiguity) | BLOCK]

- [ ] **Level 12: Delivery & Ship Gate**
  - *Evidence / Output*: [Final itemized verification report prepared. Summary counts of extracted pages, questions, options, equations, tables. Explicit listing of any persisting REVIEW or BLOCK items.]
  - *Status*: [SHIP APPROVED | SHIP BLOCKED]
```
