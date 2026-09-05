---
description: Transform Markdown, HTML, and code into pristine publication-grade PDFs with AST-driven macOS code windows, custom typography, zero shrinkage, and 100% verbatim fidelity. Use when asked to convert markdown to PDF, export HTML to PDF, compile documents, design books, storybooks, reports, or technical whitepapers.
name: presscraft
---

# Presscraft: Ultimate Verbatim Publication Engine

Presscraft transforms any Markdown file, HTML page, source code file, or document into a publication-grade, fully customized PDF. It enforces **100% verbatim textual fidelity**, zero shrinkage, authentic macOS application code window frames with deterministic syntax highlighting, smart page-break hygiene, and bespoke visual themes.

---

## 1. Non-Negotiable Core Principles

### A. The Decoupled Pipeline (100% Verbatim Fidelity)
The AI agent must **NEVER rewrite, summarize, or reproduce the document body text** through an LLM prompt. Piped text generation introduces hallucinations, dropped lines, altered formulas, and truncation on large documents (e.g. 5,000+ line technical books).
- The document is read **directly from disk**.
- It is parsed deterministically into an Abstract Syntax Tree (AST) by CommonMark-compliant `markdown-it`.
- Every word, comma, symbol, and code line is preserved with zero modification.

### B. Pure Vector Text & Zero Shrinkage
- **Selectable & Copyable**: Output PDFs contain true vector text, not rasterized canvas screenshots or flattened images. Text can be highlighted, selected, searched, and copied just like in digital textbooks.
- **Strict Scale 1.0**: Puppeteer is executed with `scale: 1.0`, `deviceScaleFactor: 2`, `printBackground: true`, and `preferCSSPageSize: true`.
- **No Downscaling**: Never reduce CSS `zoom` or `--scale` to `0.8` or `0.75`. Documents must flow naturally across pages using CSS pagination rather than being artificially squeezed.

### C. AST Code Interception (macOS Window Chrome)
Fenced code blocks are intercepted during AST token traversal:
- Wrapped in authentic macOS window frames with three-button traffic lights (Close `#ff5f56`, Minimize `#ffbd2e`, Maximize `#27c93f`).
- Language badge (e.g. `PYTHON`, `TYPESCRIPT`, `JSON`, `BASH`, `SQL`).
- Local, deterministic syntax highlighting via `highlight.js` (zero external network latency).
- Optional line numbering with `user-select: none` so copied code remains clean.

### D. Intelligent Page-Break Hygiene
- Headings (`h1`–`h6`) enforce `break-after: avoid; page-break-after: avoid;` to prevent orphaned headers at page bottoms.
- Blocks (`.code-window`, `pre`, `.callout`, `figure`, `tr`) enforce `break-inside: avoid; page-break-inside: avoid;` to eliminate sliced code lines or halved callout boxes.
- Tables enforce `thead { display: table-header-group; }` so table headers automatically repeat at the top of subsequent pages.
- Body paragraphs enforce `orphans: 3; widows: 3;`.
- Forced page breaks can be inserted at any point using `<!-- pagebreak -->`, `\newpage`, or `<div class="page-break"></div>`.

---

## 2. Command Line Interface (CLI)

Execute the compiler directly via Node:

```bash
node skills/presscraft/scripts/presscraft.cjs --input <path> --output <path.pdf> [options]
```

### CLI Flags & Options
| Flag | Description | Default |
| :--- | :--- | :--- |
| `--input, -i` | Path to source file (`.md`, `.html`, `.txt`, code files) | Required |
| `--output, -o` | Path to destination `.pdf` file | Required |
| `--theme, -t` | Preset theme name or path to custom `.css` file | `minimalist` |
| `--format, -f` | Page format: `A4`, `Letter`, `Legal`, `A3`, `A5` | `A4` |
| `--landscape` | Print in landscape orientation | `false` |
| `--margin` | Set uniform page margins (e.g. `15mm`, `20mm`, `1in`) | `15mm` |
| `--title` | Document title for running headers and cover page | Extracted from H1 |
| `--author` | Document author for running headers and cover page | - |
| `--header` | Custom running header text or template | - |
| `--footer` | Custom running footer template (supports page numbers) | Auto page numbers |
| `--cover` | Generate a publication cover page | `false` |
| `--css` | Arbitrary inline CSS rules for prompt-driven custom styling | - |
| `--line-numbers`| Display line numbers in macOS code windows | `true` |

---

## 3. Built-In Visual Themes

Presscraft comes pre-loaded with five artisanal design themes:

### 1. `storybook` (`styles/theme-storybook.css`)
- **Aesthetic**: Classic literary book / warm editorial parchment.
- **Palette**: Warm ivory parchment (`#fbf8f2`), deep espresso typography (`#231f1d`), copper & amber accents (`#b45309`).
- **Typography**: Playfair Display / Georgia / Merriweather serif with drop-caps on opening paragraphs.
- **Accents**: Fleurons, ornamental chapter dividers, warm dark code windows (`#1e1b18`).

### 2. `minimalist` (`styles/theme-minimalist.css`)
- **Aesthetic**: Swiss international typographic style.
- **Palette**: Pure stark white & crisp slate (`#f8fafc`), deep charcoal (`#0f172a`), subtle 1px border lines.
- **Typography**: Inter / Helvetica Neue / system-ui clean grotesque sans-serif with wide editorial tracking.
- **Accents**: Titanium gray and obsidian code blocks (`#18181b`), gapless metadata cards.

### 3. `executive` (`styles/theme-executive.css`)
- **Aesthetic**: Modern enterprise whitepaper / strategic report.
- **Palette**: Deep navy (`#0f172a`), royal blue (`#2563eb`), slate accents (`#64748b`).
- **Typography**: Sharp modern geometric sans with bold contrast headers.
- **Accents**: KPI metric cards, rich callout banners, glassmorphic badges, executive summary callouts.

### 4. `academic` (`styles/theme-academic.css`)
- **Aesthetic**: Rigorous computer science and scientific research paper.
- **Palette**: Monochrome ivory, formal black rules, restrained blue hyperlink accents (`#1d4ed8`).
- **Typography**: Latin Modern / EB Garamond / Times serif, justified body text with hyphenation control.
- **Accents**: Theorem, Lemma, and Proof callouts, formal figure captions, equation framing.

### 5. `cyberpunk` (`styles/theme-cyberpunk.css`)
- **Aesthetic**: Dark-mode technical chronicle / high-tech manual.
- **Palette**: Deep obsidian background (`#090d16`), electric cyan (`#00f0ff`), radioactive emerald (`#10b981`), ultraviolet (`#a855f7`).
- **Typography**: JetBrains Mono and high-tech sans-serif.
- **Accents**: Glowing terminal code blocks, neon pill badges, cyber-grid callouts.

---

## 4. Prompt-Driven Bespoke Styling Workflow

When a user requests a custom look and feel (e.g. *"make this look like a dark leather medieval grimoire"* or *"give this document a Stripe-style mint and purple developer feel"*), follow this protocol:

1. **Step 1: Inspect the Source**: Note headings, code blocks, tables, and callouts in the document.
2. **Step 2: Formulate CSS Overrides**: Create bespoke CSS using CSS variables and pass via `--css` or save a temporary theme CSS file:
   - `--theme-bg`: Primary background
   - `--theme-text`: Body text color
   - `--theme-heading`: Heading color
   - `--theme-accent`: Accent/highlight color
   - `--theme-font-body`: Body font family
   - `--theme-font-heading`: Heading font family
   - `--theme-font-code`: Code font family
3. **Step 3: Compile via CLI**:
   ```bash
   node skills/presscraft/scripts/presscraft.cjs --input doc.md --output doc.pdf --theme minimalist --css ":root { --theme-accent: #059669; } h1 { color: #065f46; }"
   ```
4. **Step 4: Verify Output**: Validate that the PDF generated cleanly, check file size, and ensure zero dropped words.

---

## 5. Admonitions & Callouts

Presscraft natively parses GitHub-style callouts in blockquotes:
- `> [!NOTE]` — Informational blue note box with SVG info icon.
- `> [!TIP]` — Emerald green tip box with SVG lightbulb icon.
- `> [!IMPORTANT]` — Violet important box with SVG exclamation star icon.
- `> [!WARNING]` — Amber warning box with SVG warning triangle icon.
- `> [!CAUTION]` — Rose danger box with SVG shield alert icon.

---

## 6. Verification Checklist Before Delivery

After compiling any PDF, perform this mandatory verification:
1. Confirm the `.pdf` file exists and has non-zero size.
2. Confirm that total word count and character count match the source document.
3. Confirm code blocks render with macOS title bars and syntax highlights.
4. Confirm no headers are stranded at the bottom of pages.
5. Confirm text inside the PDF is copyable and selectable.
