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

## 2. Sfumato (Edge Acuity & Atmospheric Gradation)

In physical reality, there are no hard 1px borders cutting through space:
- **Focal Zone:** Crisp, high-frequency micro-contrast on interactive targets and primary typography.
- **Peripheral / Receding Zones:** Atmospheric soft-focus (*sfumato*) created via:
  - Subtle opacity roll-off (`opacity: 0.7`).
  - Low-contrast, diffused boundaries (`border-color: oklch(0.5 0.01 240 / 0.12)`).
  - Soft, multi-layered ambient shadow spreads rather than harsh single-drop shadows.

---

## 3. Relational Color Physics (Itten & Goethe)

1. **The 90 / 8 / 2 Law:**
   - **90% Ground:** Neutral/tinted atmospheric environment.
   - **8% Structure:** Harmonized tints for containment and division.
   - **2% Chroma Strike:** Unadulterated, saturated pure accent at the climax.
2. **Temperature Oscillation:**
   - If key illumination is warm (`oklch(0.95 0.03 65)`), shadows and receding voids must tilt cool (`oklch(0.15 0.02 245)`).
