# Engine Routing & Hardware Execution Matrix

This reference documents exact engine routing rules by input document type and local hardware constraints. It incorporates the empirical findings, licensing parameters, and architectural boundaries established for systematic verification OCR.

---

## 1. Core Architectural Principle: The Asymmetry of Failure

The primary justification for multi-engine deterministic cross-checking over pure vision-language model (VLM) extraction is the fundamental asymmetry of failure:

- **Deterministic OCR fails loudly**: When a deterministic engine (like PaddleOCR or Tesseract) encounters degraded pixels, unfamiliar fonts, or complex equations, it outputs visible garble (e.g. `9o0m`, `~#&`, dropped characters). This noise immediately flags the text during Level 3 cross-check and Level 4 visual audit.
- **Vision-Language Models fail quietly**: When a vision model or multimodal LLM encounters ambiguous or low-contrast numbers, it confabulates smooth, syntactically clean, plausible values without warning. In an empirical analysis of DeepSeek-OCR, precision on natural conversational text was approximately 90%, but collapsed to 19.84% on zero-prior random numeric strings. Under the exact same condition, PaddleOCR PP-OCRv5 experienced only a 4.9-point drop.

**Mandate**: Never use a Vision-Language Model as the sole transcriber of numbers, coordinates, financial sums, or mathematical symbols. Use VLMs strictly for high-level structure hints or disputed-region re-reads that are subsequently visually audited against full-resolution crops.

---

## 2. Input Type Routing Matrix

| Document Category | Primary Engine | Secondary / Cross-Check Engine | Critical Operational Constraints |
| :--- | :--- | :--- | :--- |
| **Printed Text (CPU-only)** | PaddleOCR PP-OCRv5 (CPU) | RapidOCR (ONNX) + Tesseract (PSM 6 + PSM 11 union) | Tile high-res pages (max side 1500px, 500px strips, 100px overlap). RapidOCR uses `rapidocr` package, not stale `rapidocr-onnxruntime`. |
| **Tables & Structured Forms** | PP-StructureV3 | Tesseract PSM 6 (tables) + PSM 11 (sparse cells) | Reconcile every row/column total. Docling is strictly excluded as a text source of truth (structure hints only). |
| **Scientific / Academic Pages (GPU)** | Marker or olmOCR (7B) | Pix2Text + Math Crop Pass | olmOCR requires local GPU. Every formula must undergo symbol-by-symbol crop verification. |
| **Mathematics (Mixed Page)** | Pix2Text | texify | Segregate inline math (`$...$`) from block math (`$$...$$`). Never prose-clean inside equations. |
| **Mathematics (Single Equation Block)** | LaTeX-OCR (pix2tex) | Visual symbol-by-symbol crop audit | Parse output via SymPy / LaTeX parser. Validate numeric equality on random test inputs. |
| **Academic Whole-Page (Specialized)** | Nougat (Meta) | Manual / Deterministic Crop Pass | Per author paper: Nougat math scores substantially lower than plain text; tables are weakest component. |
| **Handwritten Notes & Annotations** | TrOCR (line-level) | Specialist model or Disputed Vision Re-read | TrOCR is line-only; requires upstream textline detector. Default verdict is always REVIEW, never PASS. |
| **Dense Multi-column Layouts** | Surya 2 or PP-Structure | PaddleOCR PP-OCRv5 on detected blocks | Surya 2 is a single ~650M parameter VLM (served via vLLM on GPU or llama.cpp on CPU). Read licensing threshold. |

---

## 3. Exclusion Registry: Unfit Sources of Truth

### Docling Text Exclusion
In empirical precision testing on a controlled 3-line input:
- **Line 1**: "Precision test 12345"
- **Line 2**: "Rohit OCR check Rs 100"
- **Line 3**: "No hallucination allowed"

Docling scrambled word ordering across lines and hallucinated an invented word ("a"). Consequently, Docling is **permanently excluded as an authoritative text source of truth**. It may only be referenced for preliminary bounding-box layout proposals, never for transcription characters.

### Raw Vendor Benchmarks Exclusion
- Vendor claims, such as PaddleOCR-VL-1.5's claimed 94.5% on OmniDocBench, are vendor-reported figures, not independently reproduced cross-corpus benchmarks.
- No single vendor benchmark evaluates mixed scientific print, handwriting, and complex mathematics under adversarial scanning conditions.
- System agents must benchmark on the user's specific document corpus rather than relying on published rankings.

---

## 4. Hardware Constraints & Environmental Fallbacks

### CPU-First Proven Stack Configuration
When running on CPU-constrained environments (e.g., standard virtual machines or containerized CI runners):

1. **Virtual Environment & Tool Paths**:
   - Stack path: `~/workspace/.ocr-venv` or local virtual environment.
   - Pinned packages: PaddleOCR 3.7.0, PaddleX 3.7.2, PaddlePaddle 3.3.1 (CPU), `rapidocr`, Tesseract 5.3.4, OCRmyPDF 15.2.0, Ghostscript 10.02.1.
2. **Mandatory PaddleOCR Environment Flags**:
   - `export PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True` (prevents network timeouts and external dependency pings).
   - `enable_mkldnn=False` (prevents segmentation faults on certain CPU architectures).
   - `ocr_version="PP-OCRv5"` (ensures v5 server/mobile models are loaded).
   - Turn off unwarping, textline orientation, and angle classifiers unless page rotation is explicitly verified.
3. **Memory Management (OOM Prevention)**:
   - `PP-OCRv5_server_det` triggers OS OOM-kills on images exceeding approximately 1,000,000 pixels on 4GB-8GB VMs.
   - Mandate page tiling: Set maximum dimension to 1500 pixels. Slice pages into 500px vertical strips with 100px overlap. Deduplicate bounding boxes across seams using intersection-over-union (IoU > 0.6).
4. **Tesseract Resilience & Missing Engine Protocol**:
   - System packages (apt) do not always survive container/VM restarts. If Tesseract binary is unavailable, record `tesseract_available=false` in the Level 12 audit report.
   - Fall back immediately to PaddleOCR + RapidOCR dual-engine verification. Never silently invoke cloud vision APIs as a substitute.

---

## 5. Licensing & Commercial Boundaries

- **Surya 2**: Weights distributed under modified Open RAIL-M license. Free for academic and commercial use below $5,000,000 total capital raised or annual revenue. Entities exceeding this threshold require a commercial agreement from Datalab.
- **Nougat**: Apache 2.0 license. High GPU memory footprint during autoregressive decoding.
- **TrOCR**: Apache 2.0 license. Requires transformer weights from Hugging Face Hub (ensure offline caching).
- **PaddleOCR / RapidOCR**: Apache 2.0 license. Permissible for unrestricted commercial and private deployment.
