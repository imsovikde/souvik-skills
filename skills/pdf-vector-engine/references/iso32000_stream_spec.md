# ISO 32000 PDF Stream Specification & Tokenization Architecture

## Overview

ISO 32000-1 (PDF 1.7) and ISO 32000-2 (PDF 2.0) define content streams as sequence of PDF operators and operands enclosed within stream dictionary objects. In standard documents, text is represented by font selection operators (`Tf`), positioning (`Td`, `Tm`), and character rendering (`Tj`, `TJ`).

However, modern print-to-PDF drivers (notably Chromium's Skia graphics engine and Microsoft Print to PDF) frequently rasterize or decompose font glyphs into raw vector path construction operators:
- `m`: Move current point (`x y m`)
- `l`: Draw straight line segment (`x y l`)
- `c`: Append cubic Bézier curve segment (`x1 y1 x2 y2 x3 y3 c`)
- `v`: Append cubic Bézier curve where first control point coincides with current point (`x2 y2 x3 y3 v`)
- `y`: Append cubic Bézier curve where second control point coincides with end point (`x1 y1 x3 y3 y`)
- `re`: Append rectangle (`x y w h re`)
- `h`: Close current subpath
- `f`, `f*`, `B`, `B*`: Path painting and fill operators

## Token Stream Representation

In raw content streams, operands precede operators as ASCII tokens separated by whitespace or delimiters. Skia emits floating-point values with 6 fractional digits:
```ps
44.490002 100.760002 m
44.529999 100.820000 44.580002 100.870003 44.639999 100.910004 c
44.700001 100.949997 44.759998 100.980003 44.820000 101.000000 c
```

Each curve segment (`c`) requires 6 float operands. Across thousands of glyph outlines per page, an uncompressed content stream easily inflates to 10–30 MB of ASCII representations of floating-point numbers.

## Stream Tokenization & Reconstruction

The compression kernel parses content streams by isolating numbers preceding path construction operators. 
Crucially:
- Coordinate Transformation Matrices (`cm`) must never be altered: `a b c d e f cm` dictates viewport scaling, orientation, and translation. Any modification leads to page clipping, rotation distortion, or displacement.
- Clipping Path Operators (`W`, `W*`) must preserve exact sub-pixel boundaries.
- Color Operators (`rg`, `RG`, `k`, `K`, `g`, `G`) must retain exact color space definitions.

## Object Stream Consolidation

PDF 1.5 introduced Object Streams (`/ObjStm`), allowing non-stream indirect objects to be compressed within a single data stream via `/FlateDecode`.
By leveraging `pikepdf.ObjectStreamMode.generate`, dictionary bloat, font descriptors, and cross-reference entries (`/XRef`) are compressed together, saving an additional 15%–30% of total PDF file size without altering rendering data.

## ISO 32000 Comment Tokens for Target Calibration

Section 7.2.3 of ISO 32000 specifies that any sequence of characters preceded by the percent character (`%`) outside of strings or streams constitutes a comment token and is strictly ignored by all conforming PDF consumer applications.
Appending structured comment tokens:
```ps
% 00000000000000000000000000000000...
```
at the trailer boundary allows calibrated byte sizing down to the exact byte without modifying cross-reference tables or object offsets.
