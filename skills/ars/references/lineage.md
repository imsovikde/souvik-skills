# Ars Lineage: Borrowed vs. Invented

Honest breakdown of which ideas in this skill derive from verifiable historical sources versus original inventions. This document exists because the original skill contained specific misattributions.

---

## Verified Historical Sources

These ideas genuinely trace to the named sources. Citations are approximate — none of these figures published with DOIs.

| Concept | Source | What was actually borrowed |
|:---|:---|:---|
| **Concetto** as governing philosophical thesis | Italian Renaissance workshop practice; documented in Leonardo's *Treatise on Painting* and Vasari's *Lives of the Artists* | The term "concetto" (governing idea/concept) for a work of art. The application to UI and software is an original extension. |
| **Saper Vedere** ("Knowing How to See") | Leonardo da Vinci, *Treatise on Painting* | The phrase and the concept that perception is an active, learnable skill. The eye-path choreography framework is an original adaptation. |
| **Contrapposto** | Classical sculpture (Polykleitos, Praxiteles); codified in Italian Renaissance practice | The principle of counterbalanced opposing weights creating dynamic equilibrium. Application to 2D layout and writing rhythm is original. |
| **Sfumato** | Leonardo da Vinci, documented in his painting technique | The technique of soft, smoky edge transitions. Application to UI blur/opacity falloff is a metaphorical extension. |
| **Sacred geometry / Golden Section** | Historical — Euclid documented the Golden Ratio; Luca Pacioli applied it to art in *De Divina Proportione* (1509) | The Golden Section ratio (Φ = 1.618) and root rectangles. The specific CSS token scale is original. |
| **Chiaroscuro** | Baroque painting tradition — Caravaggio, Rembrandt, Vermeer | The principle of dramatic light-and-dark contrast for depth and focus. The 5-tier luminance hierarchy is an *original framework* adapted from this tradition (see below). |
| **Color temperature oscillation** | Impressionist painting practice (Monet, Cézanne, Pissarro) | The observation that warm light creates cool shadow. Not a specific doctrine by Itten or Goethe for the screen use case. |

---

## Original Inventions in This Skill

These do not trace to named historical sources. They are original analytical frameworks invented for this skill.

| Framework | What it is | Attribution status |
|:---|:---|:---|
| **5-Tier Luminance Hierarchy** (Specular Highlight → Core Light → Midtone → Form Shadow → Deep Void) | A five-step value staging framework adapted from Baroque painting for screen/product design | **Original.** Inspired by chiaroscuro tradition, but not a doctrine of any named theorist. Do not attribute to any historical figure. |
| **~90/8/2 Chroma Economy Ratio** | A quantified ratio for atmospheric ground, structural harmony, and chroma strike | **Original.** Itten wrote about simultaneous contrast and color chords; Goethe wrote about color perception and symbolism. Neither proposed this specific ratio. The Ars 90/8/2 rule is invented. |
| **Biomimetic Skeleton / Skin Model** | The framework of separating information topology (skeleton) from surface aesthetics (skin) | **Original.** The dissection metaphor is inspired by Leonardo's anatomical study method, but the framework as applied to software and writing is invented here. |
| **Cross-Medium Pillar Mapping** | Applying the 7 pillars to writing, film, sound, and spatial work | **Original.** No historical precedent maps all these disciplines to a single Renaissance framework. |

---

## Framing and Lineage Notes

The `/ars:critique` command includes a "Kill Your Darlings" step. This phrase has a long literary history and is widely attributed to various sources (Faulkner, Chekhov, Hemingway — none verifiably). It is used here as a common creative-writing maxim, not attributed to any specific origin.

The broad "creative director" framing has parallels to other agent skills in the ecosystem (including `creative-director-skill` by various authors). The Ars skill makes no claim of being first or unique in this space. The specific combination of Renaissance vocabulary, medium-agnostic mapping, and the 3-candidate ideation protocol is original to this skill.

---

## Licensing

This skill is published under MIT license in the `imsovikde/souvik-skills` repository. The historical concepts borrowed (Concetto, Contrapposto, Chiaroscuro, etc.) are in the public domain. The original frameworks (5-Tier Luminance, 90/8/2 Chroma Economy, etc.) are original to this skill and covered by the MIT license.

No verifiable third-party license requires attribution for derivative use of the concepts listed above. If a future version incorporates code or text from a specifically licensed source, that source must be noted here with its license terms.
