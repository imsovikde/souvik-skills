# Presscraft Design Tokens & Layout Specifications

This document defines the formal typographic hierarchy, color swatches, print margins, and macOS code window metrics utilized across the Presscraft publication engine.

## 1. Page Geometry & Print Sizing

All dimensions are calibrated for physical print and high-DPI digital PDF readers:

| Format | Width (mm) | Height (mm) | Aspect Ratio | Standard Margin |
| :--- | :--- | :--- | :--- | :--- |
| **A4** | 210 | 297 | 1 : 1.414 | `18mm 16mm 20mm 16mm` |
| **Letter** | 215.9 | 279.4 | 1 : 1.294 | `0.75in 0.65in 0.8in 0.65in` |
| **Legal** | 215.9 | 355.6 | 1 : 1.647 | `0.75in 0.65in 0.8in 0.65in` |
| **A5** | 148 | 210 | 1 : 1.414 | `14mm 12mm 15mm 12mm` |
| **A3** | 297 | 420 | 1 : 1.414 | `24mm 20mm 26mm 20mm` |

---

## 2. macOS Code Window Geometry

Every fenced code block is framed within an authentic macOS desktop application window:

- **Outer Radius**: `8px` to `9px`
- **Window Controls (Traffic Lights)**:
  - Close button: `#ff5f56` (Border: `#e0443e`, Diameter: `11px`)
  - Minimize button: `#ffbd2e` (Border: `#dea123`, Diameter: `11px`)
  - Maximize button: `#27c93f` (Border: `#1aab29`, Diameter: `11px`)
  - Spacing: `7px` center-to-center
- **Header Bar**:
  - Height: ~`34px`
  - Padding: `8px 14px`
  - Border: `1px solid var(--theme-code-border)`
- **Line Numbers**:
  - Font Size: `10.5px`
  - Gutter Width: `2.5rem`
  - Right Padding: `1.1rem`
  - Opacity: `0.35`
  - Property: `user-select: none;` (guarantees copied code text does not include line numbers)

---

## 3. Typographic Modular Scale

Scale ratio: **1.250 (Major Third)** with optical line-height adjustments:

- **H1 (Document Title / Chapter)**: `2.1rem` (`~28.5px`), `font-weight: 800`, `line-height: 1.22`
- **H2 (Major Section)**: `1.55rem` (`~21px`), `font-weight: 750`, `line-height: 1.28`
- **H3 (Subsection)**: `1.25rem` (`~17px`), `font-weight: 700`, `line-height: 1.34`
- **H4 (Sub-subsection)**: `1.08rem` (`~14.5px`), `font-weight: 650`, `line-height: 1.4`
- **Body Text**: `13.5px` (`0.84rem`), `font-weight: 400`, `line-height: 1.68`
- **Code Snippets**: `11.5px` (`0.72rem`), `font-weight: 500`, `line-height: 1.60`
- **Table Cells**: `12.5px` (`0.78rem`), `line-height: 1.50`
- **Running Headers/Footers**: `8.0pt` (`~10.6px`), `color: #888888`

---

## 4. Theme Color Tokens

| Token | Storybook | Swiss Minimalist | Tech Executive | Modern Academic | Cyberpunk |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `--theme-bg` | `#fbf8f2` (Ivory) | `#ffffff` (Pure White) | `#ffffff` (Clean) | `#ffffff` (White) | `#090d16` (Obsidian) |
| `--theme-text` | `#2c2520` (Espresso) | `#1e293b` (Slate 800) | `#334155` (Slate 700) | `#111827` (Gray 900) | `#cbd5e1` (Silver) |
| `--theme-heading` | `#1c1511` (Deep Ink) | `#09090b` (Charcoal) | `#0f172a` (Navy) | `#000000` (Pitch) | `#f8fafc` (Bright White)|
| `--theme-accent` | `#b45309` (Amber) | `#0284c7` (Sky) | `#2563eb` (Royal Blue) | `#1d4ed8` (Blue) | `#00f0ff` (Cyan Neon) |
| `--theme-code-bg` | `#1f1a17` (Warm Dark)| `#18181b` (Zinc 900) | `#0f172a` (Navy Dark) | `#1f2937` (Gray 800) | `#050811` (Void Dark) |
| `--theme-code-hdr` | `#181411` | `#09090b` | `#0b1120` | `#111827` | `#0d1322` |
