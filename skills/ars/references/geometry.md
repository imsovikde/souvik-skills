# Harmonic Geometry & Dynamic Armatures

> *"Let no man who is not a mathematician read the elements of my work."* — Leonardo da Vinci

---

## 1. Sacred Root Rectangles & Proportions

Master artists and architectural theorists reject arbitrary bounding boxes. Every container, canvas, and modal must be derived from harmonic root proportions:

| Ratio Name | Factor | Construction | Purpose & Application |
|:---|:---|:---|:---|
| **Golden Section ($\Phi$)** | `1.618033` | $\frac{1 + \sqrt{5}}{2}$ | Primary canvas wrappers, hero-to-canvas ratio, golden spiral flow corridors. |
| **Root 2 ($\sqrt{2}$)** | `1.414213` | Diagonal of unit square | ISO paper proportion; ideal for editorial text columns, reading cards, and book grids. |
| **Root 3 ($\sqrt{3}$)** | `1.732050` | Diagonal of unit cube | High-tension widescreen banners, cinematic viewports, horizontal timeline stages. |
| **Root 5 ($\sqrt{5}$)** | `2.236067` | Double Golden rectangle | Monumental landscape spreads, multi-column panorama dashboards. |
| **Hemiolia (3:2)** | `1.500000` | Diatonic Fifth (3:2) | Classic 35mm photographic aspect ratio, gallery viewports, balanced framing. |

---

## 2. Production CSS Grid Armatures

Use these copy-pasteable CSS Grid templates to enforce harmonic root proportions in layout containers:

```css
/* Golden Ratio (1:1.618) Split Layout */
.grid-golden-split {
  display: grid;
  grid-template-columns: 1fr 1.618fr;
  gap: var(--space-m);
}
@media (max-width: 768px) {
  .grid-golden-split {
    grid-template-columns: 1fr;
  }
}

/* Root-2 Harmonic 3-Column Editorial Grid */
.grid-root2-editorial {
  display: grid;
  grid-template-columns: 1fr 1.414fr 1fr;
  gap: var(--space-l);
  align-items: start;
}

/* Asymmetric Contrapposto Grid (Heavy Left / Expansive Void Right) */
.grid-contrapposto {
  display: grid;
  grid-template-columns: minmax(320px, 1.618fr) minmax(240px, 1fr);
  gap: var(--space-xl);
}
```

---

## 3. The Armature Grid & Eye-Path Vectors

Construct the invisible scaffolding across the canvas using 3 geometric lines:
1. **The Primary Reciprocal Diagonal:** Drawn from top-left $(0,0)$ to bottom-right $(100,100)$, intersected perpendicularly from the bottom-left vertex $(0,100)$. The intersection at coordinate $(38.2\%, 35.0\%)$ is the **Primary Eye Anchor (Punctum)**.
2. **The Golden Section Division:** Horizontal and vertical guidelines placed at $0.618$ and $0.382$ of width and height.
3. **The Eye-Path Vector Corridor:** Connect primary focal anchors with 15° to 35° dynamic diagonals to lead the gaze naturally down the page.
