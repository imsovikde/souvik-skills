# Harmonic Geometry & Dynamic Armatures

> *"Let no man who is not a mathematician read the elements of my work."* — Leonardo da Vinci

---

## 1. Sacred Root Rectangles & Proportions

Master artists and architectural theorists reject arbitrary bounding boxes. Every container, canvas, and modal must be derived from harmonic root proportions:

| Ratio Name | Numerical Factor | Geometric Construction | Harmonic Purpose |
|:---|:---|:---|:---|
| **Golden Section ($\Phi$)** | `1.618033...` | $\frac{1 + \sqrt{5}}{2}$ | Ideal for primary layout containers, golden spirals, and hero-to-canvas relationships. |
| **Root 2 ($\sqrt{2}$)** | `1.414213...` | Diagonal of a unit square | ISO paper aspect ratio; optimal for editorial columns, books, and card bounds. |
| **Root 3 ($\sqrt{3}$)** | `1.732050...` | Diagonal of a unit cube | High-tension horizontal banners, widescreen cinematics, dynamic displays. |
| **Root 5 ($\sqrt{5}$)** | `2.236067...` | Double golden rectangle span | Panorama storytelling, widescreen landscape sequences, timeline flows. |
| **Hemiolia (3:2)** | `1.500000` | Musical Fifth (3:2) | Classic photographic aspect ratio, gallery viewports, balanced framing. |

---

## 2. Diatonic Musical Harmonic Scales for Spacing & Type

Do not pick random pixel or rem values (e.g. `13px`, `27px`). Spacing and typographic scale must follow the harmonic overtone series:

```css
:root {
  /* Diatonic Harmonic Type Scale (Major Second 8:9 / Minor Third 5:6 / Golden 1.618) */
  --font-step--2: clamp(0.69rem, 0.65rem + 0.2vw, 0.75rem); /* Micro caption */
  --font-step--1: clamp(0.83rem, 0.78rem + 0.25vw, 0.90rem); /* Fine label */
  --font-step-0:  clamp(1.00rem, 0.95rem + 0.3vw, 1.125rem); /* Body baseline */
  --font-step-1:  clamp(1.20rem, 1.10rem + 0.5vw, 1.44rem);  /* Subheading */
  --font-step-2:  clamp(1.44rem, 1.30rem + 0.8vw, 1.80rem);  /* Section Title */
  --font-step-3:  clamp(1.73rem, 1.50rem + 1.2vw, 2.25rem);  /* Headline */
  --font-step-4:  clamp(2.07rem, 1.80rem + 1.8vw, 2.81rem);  /* Major Display */
  --font-step-5:  clamp(2.49rem, 2.10rem + 2.5vw, 3.52rem);  /* Hero Climax */

  /* Harmonic Modular Spacing (Based on Phi & Musical Diatonic intervals) */
  --space-3xs: 0.25rem;  /* 4px */
  --space-2xs: 0.5rem;   /* 8px */
  --space-xs:  0.75rem;  /* 12px */
  --space-s:   1.0rem;   /* 16px */
  --space-m:   1.618rem; /* 26px - Golden Division */
  --space-l:   2.618rem; /* 42px - Phi Squared */
  --space-xl:  4.236rem; /* 68px - Phi Cubed */
  --space-2xl: 6.854rem; /* 110px - Monumental Void */
}
```

---

## 3. The Armature Grid & Eye-Path Vectors

Construct the invisible scaffolding across the canvas using 3 geometric lines:
1. **The Primary Reciprocal Diagonal:** Drawn from top-left to bottom-right, intersected perpendicularly from the bottom-left vertex. The intersection is the **Primary Eye Anchor (Punctum)**.
2. **The Golden Section Division:** Horizontal and vertical lines placed at 0.618 and 0.382 of width and height.
3. **The Eye-Path Vector Corridor:** Connect primary focal anchors with 15° to 35° dynamic diagonals to lead the eye naturally down the page.
