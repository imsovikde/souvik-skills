# OCR Failure Modes, Mechanistic Causes, and Mandated Responses

This document catalogs known OCR failure modes across print, mathematics, handwriting, tables, and vision models. For every mode, agents must understand the mechanical failure mechanism and apply the non-negotiable verification response.

---

## 1. Superscripts and Exponents

- **Failure**: Collapsed exponents ($x^2$ becomes $x2$, $10^{-3}$ becomes $10-3$, $e^{i\pi}$ becomes $ei\pi$), or exponent tier confusion ($x^{i_k}$ flattened to $x^{ik}$).
- **Mechanistic Root Cause**: Line segmentation algorithms group glyphs into horizontal bounding strips based on font baseline projection. Small superscript glyphs with baselines elevated above the mean line are pulled down into the primary text baseline.
- **Mandated Response**: Full-resolution bounding crop of the formula. Symbol-by-symbol comparison of vertical offsets relative to the base symbol. If vertical offset delta is ambiguous, flag as `REVIEW`. Never guess exponent polarity.

---

## 2. Subscripts and Indices

- **Failure**: Subscripts elevated into normal baseline characters (e.g. $a_n$ becomes $an$, $H_2O$ becomes $H2O$, $v_{max}$ becomes $vmax$), or dropped comma separators ($x_{i,j}$ becomes $x_{ij}$).
- **Mechanistic Root Cause**: Downward descenders trigger bounding box merges or are classified as punctuation noise by textline binarizers (Otsu thresholding disconnecting thin subscript stems).
- **Mandated Response**: Render candidate LaTeX beside source crop at 300% magnification. Verify whether the glyph descends below the primary baseline. In physics and chemistry contexts, validate chemical formula valence and dimensional consistency.

---

## 3. Fractions and Division Bars

- **Failure**: Omission of horizontal fraction bars resulting in stacked numerals merged into integers (e.g. $\frac{3}{4}$ transcribed as $34$), or horizontal division bar linearized into a misplaced slash that changes mathematical associativity (e.g. $\frac{a}{b+c}$ transcribed as $a/b+c$).
- **Mechanistic Root Cause**: Thin horizontal fraction lines resemble underline artifacts, rule lines, or scan folds; morphological erosion or binarization filters discard them as non-text geometric paths.
- **Mandated Response**: If a horizontal bar exists in the source image, the output MUST use `\frac{numerator}{denominator}` or equivalent bracketed division. A linear slash is permitted ONLY if the source physically prints a solidus slash (`/`). Verify expression parsing in SymPy; associativity regressions trigger `BLOCK`.

---

## 4. Sums, Integrals, and Limits

- **Failure**: Missing upper and lower limits on summation ($\sum$) or integral ($\int$) signs; confusion between capital Greek Sigma ($\Sigma$) and summation operator ($\sum$); integral sign misidentified as 'f', 'l', or vertical bar '$|$'.
- **Mechanistic Root Cause**: Limit notations positioned directly above and below operators lie outside standard horizontal text bands. Engines segment limits as separate orphaned lines or drop them during line consolidation.
- **Mandated Response**: Inspect operator bounding envelope. Verify upper limit, lower limit, and integrand variable ($dx, dt$). Output must format as `\sum_{lower}^{upper}` and `\int_{lower}^{upper}`. Count total symbols in crop versus output; any mismatch is a `BLOCK`.

---

## 5. Matrices, Determinants, and Vectors

- **Failure**: Flattening 2D matrix arrays into single concatenated strings; omitting enclosing parentheses `(...)` or square brackets `[...]`; misidentifying determinant vertical bars `$|...|$` as absolute values or '1'.
- **Mechanistic Root Cause**: Connected component analysis segments matrix entries as distinct horizontal lines without preserving multi-column cell coordinates.
- **Mandated Response**: Reconstruct matrix in LaTeX environment (`\begin{pmatrix}` or `\begin{bmatrix}`). Verify dimensions $(M \times N)$ match the source image row and column count exactly. Validate determinant properties if numerical values are populated.

---

## 6. Tables and Dense Forms

- **Failure**: Column collapse where empty cells are omitted, causing rightward entries to shift left; line wraps within a single cell treated as separate table rows; multi-tier column headers flattened.
- **Mechanistic Root Cause**: Lack of physical ruling lines (borderless tables) causes projection-profile detectors to misjudge column boundaries based solely on whitespace gaps.
- **Mandated Response**: Table model pass. Enforce uniform column count across every row. Apply **cross-footing**: every row total and column total stated in the document must equal the exact arithmetic sum of its constituent cells within rounding. An arithmetic cross-foot failure is `BLOCK`.

---

## 7. Diagrams, Graphs, and Geometric Figures

- **Failure**: Transcribing unlabelled curve coordinates as factual table data; inventing intermediate values; converting 2D engineering drawings into distorted ASCII-art strings.
- **Mechanistic Root Cause**: Vision models hallucinate numeric data when prompted for table extractions on images containing charts; deterministic engines output garbled character noise from line drawings.
- **Mandated Response**: Figures must be extracted as cropped image assets with verbatim captions. Transcribe ONLY explicitly printed, boxed, verified numeric labels. Never generate ASCII art diagrams unless the user explicitly commands ASCII art. Describe geometric diagrams verbally in plain English.

---

## 8. Handwriting and Marginalia

- **Failure**: Inventing words to complete cursive loops; merging marginal handwritten student notes or marks into the printed body of an exam question.
- **Mechanistic Root Cause**: Language models use strong language priors to predict the next word when character recognition confidence is near zero.
- **Mandated Response**: Line-level cropping. Default verdict is `REVIEW`, never `PASS`. Unreadable or ambiguous handwriting must be labeled `[illegible]`. Marginalia and annotations must be segregated into an explicit `### Annotations` section, never merged into printed questions.

---

## 9. Vision-Language Model Confabulation (Quiet Hallucination)

- **Failure**: A degraded scan of "Invoice # 10842" is cleanly transcribed as "Invoice # 10042" with 100% syntactical fluency and zero visual garble.
- **Mechanistic Root Cause**: Autoregressive token generation chooses high-probability token trajectories when image tokens are corrupted or low-resolution.
- **Mandated Response**: VLM outputs may NEVER be the sole authority for numbers or codes. Bounding crops for every numeric sequence must be cross-checked against deterministic engine output (PaddleOCR/RapidOCR). Any VLM-deterministic disagreement is an automatic `BLOCK` requiring human visual audit.

---

## 10. Correlated Engine Errors

- **Failure**: Two independent OCR tools produce the identical incorrect character (e.g. reading $\rho$ as 'p').
- **Mechanistic Root Cause**: Both engines share similar convolutional backbones, training distributions (e.g., standard synthetic Latin text), or identical ONNX ports of the same base weights (such as RapidOCR and PaddleOCR).
- **Mandated Response**: Agreement between engines is evidence, not absolute proof. In high-stakes documents, every confusable character in a formula or table cell must be confirmed against the physical crop during Level 4 visual audit.

---

## 11. LLM Post-Processing Cleanup

- **Failure**: An LLM "cleans up" an archaic or unusual spelling (e.g. converting "centre" to "center", "connexion" to "connection", or correcting a teacher's typographical error in an exam).
- **Mechanistic Root Cause**: Instruction-following models are fine-tuned to fix grammatical and orthographic errors, violating the verbatim transcription contract.
- **Mandated Response**: Zero LLM text cleanup. All spelling variants, typographical errors, and punctuation oddities in the source must be preserved verbatim. Document any notable oddity in the verification report rather than fixing it.
