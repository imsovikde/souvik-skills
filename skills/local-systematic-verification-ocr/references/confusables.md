# Character Confusables Registry & Context Rules

In OCR transcription, glyph visual similarity frequently induces subtle, catastrophic misidentifications—particularly in numbers, chemical formulas, physical units, and mathematical equations.

**The Absolute Confusable Rule**: Any confusable glyph appearing in a number, physical unit, algebraic expression, chemical notation, table data cell, or reference code MUST remain classified as `REVIEW` until visually verified against the high-resolution source crop.

---

## 1. Master Confusables Inventory

| Glyphs & Characters | Primary Confusion Pairs | High-Risk Contexts | Disambiguation Protocol |
| :--- | :--- | :--- | :--- |
| **0 / O / o / \Theta / \phi / \emptyset / °** | Digit zero `0`, uppercase Latin `O`, lowercase `o`, Greek Theta `\theta`, Greek Phi `\phi`, empty set `\emptyset`, degree symbol `°` | Serial numbers, angles, temperatures, algebraic exponents ($x^0$ vs $x^O$) | Verify glyph aspect ratio (zeros are narrower), internal diagonal bars, and baseline alignment. |
| **1 / l / I / \| / ! / / / \iota / ' / \prime** | Digit one `1`, lowercase `l`, uppercase `I`, pipe `\|`, exclamation `!`, slash `/`, Greek iota `\iota`, prime symbol `\prime` | Numeric values ($100$ vs $l00$), variables ($I_{max}$ vs $1_{max}$), derivatives ($f'(x)$ vs $f1(x)$) | Inspect top serif on '1' vs flat top on 'I'/'l'; check vertical descender on pipe; verify mathematical context. |
| **2 / Z / z / \ge / \sqrt{}** | Digit two `2`, uppercase `Z`, lowercase `z`, greater-than-or-equal `\ge`, radical symbol `\sqrt{}` | Algebraic equations ($2z$ vs $zz$), inequalities, radicals ($2\sqrt{x}$ vs $z\sqrt{x}$) | Check for cross-stroke on 'Z'; inspect rounded upper loop on '2'; check radical checkmark tail. |
| **5 / S / s / \int / \varsigma** | Digit five `5`, uppercase `S`, lowercase `s`, integral `\int`, final sigma `\varsigma` | Constants, formulas ($5s$ vs $ss$), units (seconds `s` vs digit `5`) | Inspect flat horizontal top bar and right-angle neck on '5' vs continuous smooth curve on 'S'. |
| **6 / b / \sigma / \partial** | Digit six `6`, lowercase `b`, Greek sigma `\sigma`, partial derivative `\partial` | Coordinates, calculus expressions ($\partial f / \partial x$ vs $6f / 6x$), standard deviations ($\sigma$) | Check ascender on 'b' rising above mean line; verify curvature and horizontal exit on $\sigma$ and $\partial$. |
| **8 / B / \beta / & / \infty** | Digit eight `8`, uppercase `B`, Greek beta `\beta`, ampersand `&`, infinity `\infty` | Magnetic fields ($B$), physical constants ($\beta$-decay), infinity symbols, numeric coefficients | Inspect vertical left stem on 'B'; descender below baseline on $\beta$; symmetrical loops on '8'. |
| **9 / g / q / \rho** | Digit nine `9`, lowercase `g`, lowercase `q`, Greek rho `\rho` | Densities ($\rho$), charges ($q$), acceleration ($g$), numeric values ($9.8\text{ m/s}^2$) | Check bottom descender tail: straight vertical on 'q', curved upward loop on 'g', curved serif on $\rho$. |
| **x / \times / X / \chi / \kappa** | Lowercase `x`, multiplication `\times`, uppercase `X`, Greek chi `\chi`, Greek kappa `\kappa` | Multiplication signs ($2 \times 10^4$), variables, chemical fractions ($\chi$), vector cross products | Multiplication operator is vertically centered with uniform stroke width; variable 'x' exhibits baseline serifs. |
| **+ / t / \dagger** | Plus operator `+`, lowercase `t`, dagger `\dagger` | Arithmetic expressions, time variables ($t$), quantum adjoints ($A^\dagger$) | Plus sign is strictly horizontal/vertical centered; 't' features curved bottom hook and offset horizontal crossbar. |
| **- / – / — / − / ¯** | Hyphen `-`, en-dash `–`, em-dash `—`, minus sign `−`, macron/overline `\bar{}` | Negative numbers ($-5$), ranges ($10–20$), subtraction, vector overlines | In mathematical expressions, always use mathematical minus `−` or `$-$`; preserve verbatim punctuation in prose. |
| **· / . / • / ∘** | Center dot `\cdot`, period `.`, bullet `\bullet`, degree / composition `\circ` | Decimal points ($3.14$), scalar products ($A \cdot B$), function compositions ($f \circ g$) | Check vertical positioning: decimal points sit on baseline; scalar dots sit precisely at font midline. |
| **p / \rho / P / \Rho** | Latin lowercase `p`, Greek rho `\rho`, Latin uppercase `P`, Greek uppercase Rho | Momentum ($p$), density ($\rho$), pressure ($P$), power | Greek $\rho$ has rounded single-stroke loop with no left serif; Latin 'p' features distinct vertical stem and left serif. |
| **v / \nu / \upsilon / V** | Latin lowercase `v`, Greek nu `\nu`, Greek upsilon `\upsilon`, Latin uppercase `V` | Velocity ($v$), frequency ($\nu$), voltage ($V$), volume | Greek $\nu$ has rounded cursive base with tilted right stroke; Latin 'v' features sharp bottom vertex. |
| **w / \omega / W / \Omega** | Latin lowercase `w`, Greek omega `\omega`, uppercase `W`, uppercase Greek Omega `\Omega` | Angular frequency ($\omega$), resistance ($\Omega$), work ($W$), weight ($w$) | Lowercase $\omega$ consists of two rounded curved bowls; 'w' consists of sharp angular intersections. |
| **u / \mu / \cup** | Latin lowercase `u`, Greek mu `\mu`, set union `\cup` | Micro- prefix ($\mu\text{m}$), coefficient of friction ($\mu$), set theory, atomic mass | Greek $\mu$ features prominent left descender extending well below baseline; 'u' sits flat on baseline. |
| **k / \kappa / K** | Latin lowercase `k`, Greek kappa `\kappa`, Latin uppercase `K` | Boltzmann constant ($k$), dielectric constant ($\kappa$), Kelvin ($K$) | Greek $\kappa$ is rounded and cursive; Latin 'k' has tall ascender reaching ascender height. |
| **c / \subset / C** | Latin lowercase `c`, subset operator `\subset`, uppercase `C` | Speed of light ($c$), capacitance ($C$), set containment | Mathematical subset symbol is elongated horizontally without character serifs. |
| **e / \epsilon / \in / \mathcal{E}** | Latin `e`, Greek epsilon `\epsilon`, set membership `\in`, EMF / energy $\mathcal{E}$ | Exponential ($e^x$), permittivity ($\epsilon$), set membership ($x \in S$), electromotive force | Distinct symbols with distinct semantic and syntactic roles; verify mathematical context. |

---

## 2. Context-Sensitive Escalation Rules

1. **Numeric Strings**:
   - If a string consists purely of digits (e.g. `10842`), any occurrence of `O`, `l`, `I`, `S`, `B`, or `Z` is a high-confidence substitution error. Flag as `BLOCK` until checked against source crop.
2. **Physical Dimensions & Units**:
   - In physics expressions, check dimensional homogeneity. If an equation equates velocity ($v$) to frequency times wavelength ($\nu \lambda$), transcribing $\nu$ as $v$ breaks dimensional sense. Inspect crop at Level 5.
3. **Chemical Formulas**:
   - In chemical formulas (e.g., $CO$ vs $Co$, $SO_4^{2-}$), casing distinguishes elements (Carbon Monoxide vs Cobalt). Casing confusions are treated as semantic defects and flagged `BLOCK`.
4. **Delivered Text Standard**:
   - Delivered text is ALWAYS what the crop physically shows. Never change a character to fix a perceived spelling error by the author; preserve verbatim anomalies and document them in the Level 12 report.
