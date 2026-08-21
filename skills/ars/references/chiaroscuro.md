# Chiaroscuro & Sfumato: The Physics of Light & Optics

> *"Shadow is the diminution alike of light and of darkness, and stands between darkness and light."* — Leonardo da Vinci

---

## 1. The 5-Tier Luminance Hierarchy

An interface is not a set of colored boxes; it is a three-dimensional volume illuminated by directional light:

```
  [Level 1: Specular Highlight]  --> Peak luminance (OKLCH L: 0.98, C: 0.05). Reserved for focal point.
             │
  [Level 2: Core Light]          --> Primary surfaces, critical text (OKLCH L: 0.90, C: 0.01).
             │
  [Level 3: Midtone / Ambient]   --> Secondary information, subtle structural chrome (OKLCH L: 0.65, C: 0.01).
             │
  [Level 4: Form Shadow]         --> Receding structural planes, inactive zones (OKLCH L: 0.35, C: 0.01).
             │
  [Level 5: Deep Void / Ground]  --> Atmospheric canvas baseline (OKLCH L: 0.12, C: 0.01 for dark, L: 0.96 for light).
```

---

## 2. Four Calibrated Master OKLCH Palettes

### Palette A: Obsidian Noir (Cinematic Dark Register)
```css
:root {
  --color-ground:      oklch(0.12 0.01 260); /* Atmospheric deep black-blue */
  --color-shadow:      oklch(0.20 0.01 260); /* Receding structural plane */
  --color-midtone:     oklch(0.45 0.01 260); /* Subtle metadata & chrome */
  --color-core:        oklch(0.92 0.01 260); /* Crisp core typography */
  --color-highlight:   oklch(0.98 0.02 260); /* Specular focal target */
  --color-strike:      oklch(0.75 0.19 55);  /* 2% Pure amber flame strike */
}
```

### Palette B: Architectural Limestone (Warm Editorial Light Register)
```css
:root {
  --color-ground:      oklch(0.96 0.01 85);  /* Warm honed limestone */
  --color-shadow:      oklch(0.90 0.01 85);  /* Soft mineral plane */
  --color-midtone:     oklch(0.55 0.02 60);  /* Editorial muted caption */
  --color-core:        oklch(0.18 0.02 50);  /* Dense carbon ink */
  --color-highlight:   oklch(0.10 0.01 50);  /* Deepest focal ink */
  --color-strike:      oklch(0.58 0.22 28);  /* 2% Vermilion lacquer strike */
}
```

### Palette C: Titanium Monolith (Industrial High-Tech Register)
```css
:root {
  --color-ground:      oklch(0.15 0.005 240); /* Cold brushed titanium */
  --color-shadow:      oklch(0.25 0.005 240); /* Structural bezel */
  --color-midtone:     oklch(0.60 0.005 240); /* Machined technical text */
  --color-core:        oklch(0.94 0.005 240); /* Luminous phosphor readout */
  --color-highlight:   oklch(0.99 0.005 240); /* Peak laser highlight */
  --color-strike:      oklch(0.82 0.16 142);  /* 2% Laser emerald strike */
}
```

### Palette D: Mineral Earth (Organic Tactile Register)
```css
:root {
  --color-ground:      oklch(0.94 0.015 75); /* Raw unbleached clay */
  --color-shadow:      oklch(0.86 0.020 75); /* Terracotta shadow */
  --color-midtone:     oklch(0.48 0.030 65); /* Weathered loam */
  --color-core:        oklch(0.22 0.025 55); /* Dark umber */
  --color-highlight:   oklch(0.12 0.015 50); /* Burnt sienna core */
  --color-strike:      oklch(0.65 0.18 160); /* 2% Malachite mineral strike */
}
```

---

## 3. Sfumato & Multi-Layered Shadow Elevation

Never use harsh 1-step drop shadows. In physical light, ambient diffusion creates layered penumbras:

```css
/* Sfumato Atmospheric Elevation Stack */
.elevation-sfumato-low {
  box-shadow: 
    0 1px 2px oklch(0 0 0 / 0.06),
    0 2px 6px oklch(0 0 0 / 0.04);
}

.elevation-sfumato-high {
  box-shadow: 
    0 2px 4px oklch(0 0 0 / 0.04),
    0 8px 24px oklch(0 0 0 / 0.08),
    0 24px 64px oklch(0 0 0 / 0.12);
}
```
