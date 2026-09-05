# Cognitive Visual Ergonomics & Information Architecture for Publication-Grade PDFs

This reference outlines the neuroscientific, ophthalmologic, and typographical principles that govern the **Presscraft Reader Design System** (`theme-reader.css` and `theme-readability.css`). It explains how human visual perception and memory encoding function during deep technical and literary reading, and how Presscraft deterministically translates these principles into publication-grade PDFs.

---

## 1. Ocular Mechanics & Saccadic Reading Rhythms

### A. The Foveal Window and Saccades
Human eyes do not glide continuously across text. Reading consists of rapid ballistic eye jumps (**saccades**, lasting 20–35 ms) alternating with stationary pauses (**fixations**, lasting 200–250 ms).
- **Foveal Vision**: High visual acuity is restricted to the fovea centralis, spanning only 1° to 2° of visual arc (roughly 6 to 8 characters at typical viewing distances).
- **Parafoveal Preview**: The parafoveal field (extending up to 5° eccentricity, ~15 characters) pre-processes word lengths, initial letters, and word boundaries to guide the next saccadic launch.

### B. The 64–72 Characters Per Line (CPL) Measure
- **Return-Sweep Errors**: When line measure exceeds 75–80 characters, the ocular muscles struggle to execute the long return saccade to the start of the succeeding line. Readers frequently suffer from "double-landing" or line-skipping, forcing corrective regression saccades and causing cognitive fatigue.
- **Fragmented Fixations**: When line measure drops below 45 characters, sentences break across too many lines, disrupting clause chunking and syntactical comprehension.
- **The Golden Measure**: Presscraft constrains body prose measure to **64 to 72 CPL** (enforced via `max-width: 44rem` at 13.5–14px font scale). This matches the human foveal-parafoveal span and ensures effortless return sweeps.

---

## 2. Photopic Reflectance, Luminance & Glare Mitigation

### A. The Problem with Pure White (`#FFFFFF`)
Pure digital white emits 100% luminance across all RGB channels. On backlit displays (and high-brightness paper under office lighting), `#FFFFFF` induces:
1. **Photopic Glare**: Over-saturation of retinal photoreceptors.
2. **Pupillary Constriction Strain**: Sustained contraction of the iris sphincter muscle to limit flux, leading to asthenopia (eyestrain), headaches, and dry eyes.

### B. The 90% Diffuse Reflectance Ivory Substrate (`#fbf9f5`)
Presscraft utilizes a warm, alabaster ivory substrate (`#fbf9f5` with subtle surface tones `#f5f1e9`), matching high-grade archival book papers (e.g. Cambridge University Press and Penguin Classics editions).
- **Luminance Balance**: Diffuses high-energy blue wavelengths.
- **Soft Background Radiation**: Provides a tranquil reading backdrop that enables hours of sustained focus without optical fatigue.

---

## 3. Contrast Dynamics & Irradiation Elimination

### A. The Irradiation (Halation) Hazard of 21:1 Contrast
Black text on stark white (`#000000` on `#FFFFFF`) yields a 21:1 contrast ratio. While high contrast is desirable, extreme contrast causes **irradiation**: high luminance bleeds across the dark stroke boundaries in the visual cortex, causing fine serifs and glyph stems to vibrate or appear blurred at the edges.

### B. Calibrated 13.5:1 Deep Espresso Typography (`#242120`)
- **WCAG AAA Compliance**: WCAG AAA requires a minimum 7:1 contrast ratio for normal body text.
- **The 13.5:1 Sweet Spot**: `#242120` on `#fbf9f5` provides a **13.5:1 contrast ratio**—nearly double the AAA requirement—while eliminating edge halation. Letterforms remain razor-sharp and optically grounded.

---

## 4. Typographic Hierarchy & Vertical Rhythm

### A. High-x-Height Humanist Serif Body
- **Body Font Cascade**: `Source Serif 4, Charter, Merriweather, Georgia, Cambria, serif`.
- Humanist serifs feature open counters, bracketed serifs, and tall x-heights, ensuring effortless glyph distinction even at small print sizes (13.5px / 10pt).
- **Proportional Leading (1.72 Line-Height)**: Generous interline spacing allows ascenders and descenders to clear comfortably, preventing line-collision during saccades.

### B. Clean Grotesque Sans Headings
- **Heading Font Cascade**: `Plus Jakarta Sans, Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif`.
- Modern geometric grotesque headings provide clear visual signposts that structure information hierarchically, enabling fast parafoveal scanning.

---

## 5. Pre-Attentive Processing & Semantic Highlighting Taxonomy

According to Allan Paivio's **Dual-Coding Theory (1971)**, the human brain processes visual and verbal information through separate, concurrent cognitive channels. Combining standardized semantic colors and contextual icons accelerates concept recognition and recall by up to 36%.

Presscraft establishes an immutable 6-tier color-coded cognitive highlighting system:

| Highlighter Syntax | Semantic Intent | Visual Hue | Hex / RGB Token | Cognitive Role |
| :--- | :--- | :--- | :--- | :--- |
| `==universal==` | General Emphasis | Sunshine Butter | `#facc15` (`rgba(254, 240, 138, 0.55)`) | General focus point |
| `==key:...==` | Core Definition | Warm Amber | `#d97706` (`rgba(245, 158, 11, 0.16)`) | Vocabulary & mental model anchor |
| `==tip:...==` | Actionable Guidance | Soft Emerald | `#059669` (`rgba(16, 185, 129, 0.14)`) | Practical technique & shortcut |
| `==note:...==` | Cognitive Insight | Azure Sky | `#0284c7` (`rgba(14, 165, 233, 0.14)`) | Architectural rationale & context |
| `==warn:...==` | Hazard / Pitfall | Coral Crimson | `#dc2626` (`rgba(239, 68, 68, 0.13)`) | Error trap, edge case, alert |
| `==important:...==` | System Invariant | Royal Violet | `#7c3aed` (`rgba(139, 92, 246, 0.14)`) | Non-negotiable rule, law, invariant |

### Rules for Highlighting Without Hallucinating Content
1. **Verbatim Preservation**: Highlighting wraps existing phrases; it never modifies, shortens, or rewrites original text.
2. **Selective Density**: Highlight no more than 10–15% of any given section. Over-highlighting destroys visual contrast and triggers cognitive habituation.
3. **Delimiter Hygiene**: Standard Markdown `==content==` with optional semantic prefix `==kind:content==`. Never cross paragraph boundaries.

---

## 6. Contextual Iconography & Admonition Architecture

Blockquote admonitions are converted into responsive callout cards with inline SVGs:

- `> [!KEY] [Title]` — Amber border (`#d97706`), Key icon. For definitions and core formulas.
- `> [!SUMMARY] [Title]` or `> [!TAKEAWAY]` — Mineral pine border (`#0f766e`), Checklist icon. For chapter wrap-ups and executive takeaways.
- `> [!INSIGHT] [Title]` — Sky blue border (`#0284c7`), Lightbulb icon. For engineering rationale and design trade-offs.
- `> [!EXAMPLE] [Title]` — Indigo border (`#4f46e5`), Layers icon. For concrete walkthroughs.
- `> [!TIP] [Title]` — Emerald green border (`#059669`), Sparkle icon. For best practices.
- `> [!WARNING] [Title]` — Amber border (`#d97706`), Caution triangle icon. For operational hazards.
- `> [!CAUTION] [Title]` — Crimson border (`#e11d48`), Shield alert icon. For irreversible actions.
- `> [!NOTE] [Title]` — Slate blue border (`#0284c7`), Info icon. For background notes.
- `> [!IMPORTANT] [Title]` — Violet border (`#7c3aed`), Star icon. For architectural invariants.

---

## 7. Deterministic CSS Page Break Hygiene

In paged PDF rendering, unexpected page fragmentation breaks mental flow. Presscraft enforces deterministic pagination:

1. **Headings**: `h1, h2, h3, h4, h5, h6` enforce `break-after: avoid; page-break-after: avoid; break-inside: avoid; page-break-inside: avoid;`. A heading is never left stranded at the bottom of a page.
2. **Code Blocks & Line Numbers**: `.code-window` enforces `break-inside: avoid; page-break-inside: avoid;`. Individual `.line` elements enforce `break-inside: avoid; page-break-inside: avoid;`, guaranteeing that no line of code is sliced in half horizontally.
3. **Table Rows & Headers**: `tr` enforces `break-inside: avoid; page-break-inside: avoid;`. Table headers enforce `thead { display: table-header-group; }`, ensuring table column names repeat automatically at the top of subsequent pages.
4. **Paragraphs**: `p` enforces `orphans: 3; widows: 3;`. Isolated single lines at page tops or bottoms are completely prevented.
5. **Explicit Page Breaks**: Authors can insert deterministic page breaks anywhere using `<!-- pagebreak -->`, `<!-- newpage -->`, `\newpage`, or `---pagebreak---`.
