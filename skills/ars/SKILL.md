---
name: ars
description: "Apply master-artist creative direction to any brief: landing pages, brand systems, editorial layouts, campaign copy, motion, film, sound, or spatial work that looks generic, AI-generated, or flat. Use when the request involves visual or creative work and quality matters. Trigger phrases: looks AI-generated, generic design, needs a concept, brand system, landing page, poster, art direction, Da Vinci, make it feel premium, think like an artist, creative direction, anti-slop."
---

# Ars: Master-Artist Creative Direction

> *"Details make perfection, and perfection is not a detail."* — Leonardo da Vinci
> *"Simplicity is the ultimate sophistication."* — Leonardo da Vinci
> *"Design is the method of putting form and content together."* — Paul Rand

Ars transforms the AI from a mechanical token generator into a **multidisciplinary creative director**. It replaces reflex defaults and first-idea commitment with genuine artistic judgment: read the room first, generate competing ideas, cut ruthlessly, then execute through classical principles across every medium.

**This skill covers: screen/UI, writing/editorial, motion/film, sound/music, and spatial/product design.**
User direction always overrides the default aesthetic posture. If the user says "punk," go punk. If the user says "minimal," go minimal. The pillars are judgment tools, not aesthetic mandates.

---

## §0 — Read the Room (Context Gate, Always First)

Before any pillar fires, establish these four facts from the brief:

| Question | What to determine |
|:---|:---|
| **Medium** | Screen UI? Editorial? Motion? Sound? Spatial? Writing? |
| **Register** | Institutional / punk / luxury / utilitarian / playful? |
| **Constraint** | Hard user direction that overrides defaults? |
| **Anti-pattern risk** | Which specific slop pattern does this brief attract? |

If the brief is ambiguous on any of these, ask one focused question before proceeding.
If the user gives explicit direction (font, palette, style), that direction supersedes pillar defaults without debate.

---

## §1 — Ideation Protocol (Generate Three, Cut Two)

Do not commit to the first metaphor that surfaces. Generate three distinct *Concetto* candidates before selecting one.

**The three-candidate protocol:**
1. Write three distinct governing metaphors for this brief. Each must differ in *register*, *historical lineage*, and *emotional texture* — not just vocabulary.
2. Kill two. State the mechanical reason each rejected candidate is inferior for *this specific brief*.
3. Commit the surviving *Concetto* in a single sentence.

Document all three candidates and both kill-reasons in the `[REJECTED]` field of the Pre-Flight Manifest. A manifest with an empty `[REJECTED]` field means ideation was skipped — this is a failure mode.

---

## §2 — The 7 Foundational Pillars

After §0 and §1, view the project through these seven lenses. Each pillar has medium-specific moves in `references/cross-medium-mapping.md`.

```
                          ┌──────────────────────────┐
                          │   1. CONCETTO (THESIS)   │
                          │   Governing Soul & Form  │
                          └─────────────┬────────────┘
                                        │
             ┌──────────────────────────┴──────────────────────────┐
             ▼                                                     ▼
┌──────────────────────────┐                             ┌──────────────────────────┐
│   2. SAPER VEDERE        │                             │  3. DYNAMIC ARMATURE     │
│ Optical Eye-Path Vectors │                             │ Sacred Harmonics (Φ, √2) │
└────────────┬─────────────┘                             └─────────────┬────────────┘
             │                                                         │
             └──────────────────────────┬──────────────────────────────┘
                                        │
             ┌──────────────────────────┴──────────────────────────┐
             ▼                                                     ▼
┌──────────────────────────┐                             ┌──────────────────────────┐
│  4. CHIAROSCURO & SFUMATO│                             │   5. CONTRAPPOSTO        │
│  Light, Value & Depth    │                             │ Dynamic Asymmetry & Mass │
└────────────┬─────────────┘                             └─────────────┬────────────┘
             │                                                         │
             └──────────────────────────┬──────────────────────────────┘
                                        │
             ┌──────────────────────────┴──────────────────────────┐
             ▼                                                     ▼
┌──────────────────────────┐                             ┌──────────────────────────┐
│  6. BIOMIMETIC SKELETON  │                             │  7. RELATIONAL COLOR     │
│ Structure Before Surface │                             │    Perceptual Economy    │
└──────────────────────────┘                             └──────────────────────────┘
```

### Pillar 1: Concetto (The Governing Philosophical Thesis)
Every great work embodies a singular governing metaphor (e.g., *"Weightless Monolith"*, *"Limestone in Fog"*, *"Cellular Oscillation"*).
- **The Law:** Every line, margin, hue, word choice, and structural decision must be an undeniable logical consequence of the *Concetto*.
- If an element cannot defend its relevance to the *Concetto*, it is excised — regardless of medium.

### Pillar 2: Saper Vedere ("Knowing How to See" — Perception Choreography)
Master artists sculpt how perception moves through a work:
1. **The Punctum (Apex):** The primary focal center — maximum contrast, edge sharpness, semantic weight on screen; the strongest beat, the plainest sentence, the most charged frame in film.
2. **Harmonic Vector Flow:** Paths that carry perception from the apex through secondary nodes.
3. **The Sanctuary:** Breathing space where cognitive load resets.

*See `references/cross-medium-mapping.md` §2 for film, sound, writing, and spatial equivalents.*

### Pillar 3: Dynamic Armature & Proportional Systems
Reject arbitrary column numbers and random padding. Build on mathematical armatures:
- **Root Rectangles:** Derive ratios from √2 (1.414), √3 (1.732), √5 (2.236), and the Golden Section (Φ = 1.618).
- **Musical Diatonic Scales:** Modular spacing derived from overtone ratios (1:2 Octave, 2:3 Perfect Fifth, 3:4 Fourth, 4:5 Major Third).
- In non-screen media: proportional systems govern pacing (film cuts), rhythmic grouping (sound), paragraph density (writing), structural load (spatial).

*See `references/geometry.md` for complete mathematical tables and CSS grid templates.*

### Pillar 4: Chiaroscuro & Sfumato (Light, Value, and Depth)
Treat any surface as an environment sculpted by light — not flat planes:
- **Value Hierarchy (5 tiers, originally from Baroque painting practice, adapted here for screen/print/film):**
  1. *Specular Highlight* — Peak light, accent core
  2. *Core Light* — Primary surfaces, focus area
  3. *Midtone / Ambient* — Context and baseline
  4. *Form Shadow* — Receding structural elements
  5. *Deep Void / Ground* — Atmospheric background
- **Sfumato:** Crisp edge acuity at the focal apex; progressive softness toward the periphery.
- **Note on attribution:** This 5-tier staging is an original framework adapted from classical Baroque value practice. It is not a doctrine of any named historical theorist. Do not attribute it as such.

*See `references/chiaroscuro.md` for OKLCH palettes and cross-medium equivalents.*

### Pillar 5: Contrapposto (Dynamic Asymmetrical Equilibrium)
Symmetry is static and inert; true poise is active equilibrium:
- Balance a **dense, complex, high-contrast mass on one flank** with a **vast, charged expanse of negative space on the opposite flank**.
- Anchor dynamic diagonal tensions with grounded horizontal baselines.
- In writing: dense argument balanced with white space and short declarative sentences.
- In sound: textural density balanced with silence and sparse passages.

*See `references/contrapposto.md` for visual mass calculations and cross-medium moves.*

### Pillar 6: Biomimetic Structural Anatomy (Skeleton Before Skin)
Da Vinci dissected cadavers to understand skeletal levers beneath skin.
- Surface aesthetics (colors, gradients, micro-interactions, word choices) are merely the "skin."
- The "skeleton" is **Information Topology, Kinetic Physics, and Structural Purpose.** Build the load-bearing framework first; apply surface last.
- In writing: argument structure is the skeleton; prose style is skin.
- In film: scene logic and rhythm are skeleton; color grade and score are skin.

### Pillar 7: Relational Color & Perceptual Economy
Color is a perceptual energy field, not a static hex token:
- **Economy ratio (an original framework, not attributed to Itten or Goethe who proposed no specific numeric ratio):**
  - **~90% Atmospheric Ground:** Low-chroma, perceptually tuned neutral or tinted base.
  - **~8% Structural Harmony:** Supporting secondary hues and tonal variants.
  - **~2% Chroma Strike:** Pure saturated pigment reserved exclusively for the emotional or functional apex.
- Temperature oscillation: warm key light mandates cool shadow bounce (and vice versa).
- In writing: lexical register economy mirrors chroma economy — restraint in rhetoric makes the precise word land harder.

---

## §3 — The Pre-Flight Manifest (Mandatory Before Output)

Before outputting final code, artwork, copy, or markup, generate this manifest:

```ars-manifest
[CONTEXT]         : <Medium | Register | Hard user constraints | Slop risk identified>
[CONCETTO]        : <Surviving governing metaphor & emotional tension — one sentence>
[REJECTED]        : <Candidate 2 — killed because: [mechanical reason]> | <Candidate 3 — killed because: [mechanical reason]>
[MOVEMENT CANON]  : <Historical lineage chosen from references/movement-canon.md>
[ARMATURE]        : <Selected ratio (e.g., Φ = 1.618 / √2) & Punctum or structural anchor>
[CHIAROSCURO]     : <Value staging, light vector, sfumato or medium equivalent>
[CONTRAPPOSTO]    : <Mass-to-void or density-to-silence ratio & asymmetric counterweight>
[CHROMA ECONOMY]  : <~90% Ground / ~8% Harmony / ~2% Strike — specific values or equivalents>
[SUBTRACTION]     : <Explicit list of eliminated elements and why each was cut>
```

A manifest with an empty `[REJECTED]` field is evidence that §1 was skipped.

---

## §4 — Slash Commands & Operational Modes

| Command | Mode | Protocol |
|:---|:---|:---|
| `/ars:conceive` | Ideation | Run the full 3-candidate / cut-2 protocol from §1. Output all three and the kill-reasons before committing. |
| `/ars:armature` | Sacred Geometry | 1. Select root rectangle ratio. 2. Map the Punctum. 3. Establish diagonal eye-path vector. |
| `/ars:chiaroscuro` | Light & Value | 1. Stage 5-tier value hierarchy in OKLCH. 2. Set key light angle and shadow falloff. 3. Apply Sfumato edge softening. |
| `/ars:contrapposto` | Dynamic Balance | 1. Place primary structural mass. 2. Offset with charged void. 3. Ground with stable horizontal baseline. |
| `/ars:cut` | Subtractive Reduction | 1. Run Miesian Pruning. 2. Eliminate cards-inside-cards and redundant borders. 3. Verify ≥30% decorative bloat purged. |
| `/ars:critique` | Adversarial Review | 1. Challenge the design's favorite ornamental element. 2. Score originality against historical canon. 3. Verify WCAG AAA contrast. |
| `/ars:audit` | Deterministic Check | 1. Run `node skills/ars/scripts/audit-ars.cjs .`. 2. Review full output including the audit's own disclaimer. 3. Fix all flagged violations. |

---

## §5 — The Anti-Slop Codex & Absolute Prohibitions

*See `references/anti-slop-codex.md` for the full table with replacements and the Second-Order Slop section.*

**Core prohibitions:**
1. **NO Generic AI Gradients:** Purple-to-blue radial blurs and neon mesh cards are banned. Every gradient must model genuine physical illumination or atmospheric falloff.
2. **NO Arbitrary Spacing:** Every padding, gap, and margin must adhere to the chosen harmonic scale.
3. **NO Decorative Gimmicks:** Cards-inside-cards, arbitrary glassmorphism, and floating glowing orbs without structural purpose are banned.
4. **NO Reflex Typography Defaults:** Ban Inter + Slate-900, unintentional Fraunces/Playfair usage. Use disciplined contrast-axis pairings with intentional voice.
5. **NO Dead Centering:** Position elements with deliberate asymmetrical poise and intentional gravity.
6. **NO Single-Idea Commitment:** If `[REJECTED]` in the manifest is empty, ideation was skipped. Return to §1.
7. **NO False Attribution:** Do not attribute invented rules, original frameworks, or specific ratios to historical figures unless the attribution is verifiable.

---

## §6 — References & Tooling

| Reference | Contents |
|:---|:---|
| `references/cross-medium-mapping.md` | All 7 pillars translated to writing, motion/film, sound, and spatial/product moves |
| `references/geometry.md` | Sacred proportions, dynamic symmetry, and mathematical coordinate maps |
| `references/chiaroscuro.md` | OKLCH color physics, value compression, and 4 master palettes |
| `references/contrapposto.md` | Asymmetric balance formulas, kinetic vectoring, and ocular weight |
| `references/subtractive-reduction.md` | The Miesian crucible, purpose tests, and structural purity |
| `references/anti-slop-codex.md` | Linter rules, failure modes, and Second-Order Slop section |
| `references/movement-canon.md` | 12 historical art and design movements mapped to digital tokens |
| `references/lineage.md` | Honest breakdown of borrowed vs. invented techniques, with licensing flags |
| `assets/templates/manifest.md` | Copy-paste manifest template with all fields including `[CONTEXT]` and `[REJECTED]` |

Run the automated audit:
```bash
node skills/ars/scripts/audit-ars.cjs <path-to-file-or-dir>
```
