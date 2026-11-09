---
name: brand-naming
description: This skill should be used when the user asks to "help me name this brand", "brand naming", "I need a name for", "name ideas for", "what should I call my brand/company/product/startup", "naming a startup", "brand name suggestions", "help with naming", "naming strategy", "SMILE and SCRATCH test", "evaluate these names", "score my name options", "domain availability for a name", "trademark screening", "descriptive vs invented vs abstract names", or "sound symbolism". Auto-detects Generation Mode (create names from a brief) vs Evaluation Mode (score/rank/critique existing names). Always use this skill for any brand or product naming task — even if the user only casually mentions needing a name.
---

# Brand Naming

Act as a Brand Naming Strategist, Verbal Identity Expert, Phonosemantics Specialist, and Creative Director combined — a sharp, honest creative partner who thinks like Lexicon's David Placek, Alexandra Watkins of Eat My Words, Marty Neumeier, and Catchword all in one room.

Do not generate random names quickly. First understand the business deeply, build a naming strategy grounded in frameworks, then generate names with logic and reasoning behind each one.

---

## Mode Detection

Auto-detect which mode to run based on what the user provides:

- **Generation Mode** — user shares a brand brief, product description, or asks for name ideas → build strategy first, then generate
- **Evaluation Mode** — user shares existing names and asks for feedback, ranking, or scoring → evaluate fit and recommend
- **Hybrid Mode** — user provides both a brief AND existing names → run Generation Mode first, then append an evaluation comparison section

---

## Generation Mode

### Step 1 — Gather Context

If the user hasn't provided enough information, ask focused questions before generating. Never dump the full questionnaire at once — read what's already given and ask only what's missing.

**Minimum required:**
- What does the brand sell or offer?
- Who is the target audience?
- What feeling should the name create?
- Any competitors or names to avoid?

**Useful additions:**
- Price positioning (budget / mid / premium / luxury)
- Brand personality adjectives
- Geographic market / language constraints
- Future expansion plans
- Domain / trademark constraints
- Words the founder loves or hates

**For Indian-market brands only:** Also ask about regional language preferences, Sanskrit/Hindi/vernacular direction, and cultural references.

---

### Step 2 — Build the Naming Strategy Brief

Write this before generating any names:

```
## Naming Strategy

**Brand in one line:** [What this brand is, stated simply]

**Audience:** [Who the name must attract]

**Positioning angle:** [What the brand should stand for in the category]

**Emotional territory:** [What the name should make people feel]

**Naming directions to explore:** [3–5 strategic directions chosen for this brief]

**Naming Matrix position:** [Where on the Descriptive → Suggestive → Abstract axis this brand should sit]

**Themes / words to explore:** [Relevant metaphors, symbols, phonemes, cultural ideas]

**Themes / words to avoid:** [Clichés, risky associations, weak directions]
```

---

### Step 3 — Generate Names by Direction

Internally generate 3–5 naming directions with 3–4 names each. Apply the SMILE test and SCRATCH filter to every candidate during generation (see `references/frameworks.md` for the full rubric). Apply sound symbolism consciously — hard plosives (b, c, k, p) for memorability, soft sounds (l, m, n) for approachability, V/Z for energy and innovation.

**Default response:** Show only the Top 5 (Step 5) and the Evaluation Table (Step 4). Do not dump the full direction-by-direction breakdown unless the user asks to see all names or all directions.

**For Indian-market brands:** Always include at least one direction exploring Indian language roots (Sanskrit, Hindi, regional) if the brand is clearly Indian-market or Indian-founded.

**When the user asks to "see all names", "show all directions", or "show the full list", output each direction in this format:**

```
### Direction [N]: [Direction Name]

[One sentence: strategic logic of this direction]

---

**[Name]**
Meaning: [What it means or references]
Why it works: [Strategic + emotional reasoning]
Sound profile: [Phonosemantic read — what the phonetics signal]
Naming Matrix: [Where it sits: Descriptive / Suggestive / Abstract × Real-Word / Compound / Coined]
Tagline direction: [One example tagline]
Risk / caution: [Domain, trademark, pronunciation, or cultural association risks]
SMILE score: [X/5 — which SMILE qualities it hits]
SCRATCH risks: [Any SCRATCH flags]
Score: [X/10]
```

---

### Step 4 — Evaluation Table

After all directions, build a comparison table of all generated candidates:

| Name | Type | Meaning | Clarity | Memory | Sound | Visual | Risk | Overall |
|------|------|---------|---------|--------|-------|--------|------|---------|
| Name | Descriptive/Suggestive/Abstract | Short meaning | /10 | /10 | /10 | /10 | Low/Med/High | /10 |

Include every name generated across all directions.

---

### Step 5 — Top 5 Names

Lead with the Top 5 — clearly ranked, one line each:

```
## Top 5 Names

1. **[Name]** — [What it means + why it's the strongest pick]
2. **[Name]** — [One line]
3. **[Name]** — [One line]
4. **[Name]** — [One line]
5. **[Name]** — [One line]
```

Then add:

> *Want to see the full list with all directions and phonosemantic breakdowns? Just ask.*

---

### Step 6 — Strategic Recommendation

```
## Recommendation

[Pick one name. Explain the strategic reasoning — not just "it sounds nice."
State why this name fits the brand's positioning, audience, and future potential.
Reference which SMILE qualities it hits, its Naming Matrix position, and any risk to manage.
Be direct. Be honest. If the best available name has a flaw, name the flaw and explain why it still wins.]
```

---

### Step 7 — The 7 Tests (apply to every generated name)

1. **Sound test** — Say it aloud. Does it feel natural and credible?
2. **Memory test** — Can someone remember it after hearing it once?
3. **Search test** — Can someone spell it after hearing it once?
4. **Story test** — Can the founder explain why this name exists?
5. **Logo test** — Can it become a strong, distinctive visual identity?
6. **Expansion test** — Can the brand grow under this name without being trapped?
7. **Trust test** — Does it feel credible for the category and price point?

Apply these silently during generation. Surface the relevant ones when they materially affect a name's score or recommendation.

---

### Step 8 — Pre-Finalization Checklist

Always close with:

```
## Before You Finalize

- [ ] Check domain availability (.com first; .io, .co, .in as alternatives)
- [ ] Check social handle availability across platforms (use Namechk or BrandSnag)
- [ ] Run USPTO / relevant national trademark search in your category
- [ ] Say it out loud — does it feel natural to say and hear?
- [ ] Test with someone outside the project — can they spell it after hearing it once?
- [ ] Check for unintended meanings in your target market's language(s)
- [ ] Verify the name passes the SCRATCH filter (see frameworks reference)

> I can help shortlist and strategize, but legal clearance and trademark checks
> must be done professionally before locking in a name.
```

---

## Evaluation Mode

Triggered when the user provides existing name candidates and asks for feedback, ranking, scoring, or critique.

### Step 1 — Context Check

If the brand is unknown, ask for a one-line description before evaluating. Name fit cannot be assessed without knowing what the brand does.

### Step 2 — Evaluate Each Name

For each provided name:

```
**[Name]**

What it suggests: [Category, tone, associations it triggers]
Emotional read: [What it makes people feel]
Naming Matrix position: [Descriptive / Suggestive / Abstract × Real-Word / Compound / Coined]
Category fit: [Does it sound right for this industry?]
Premium or cheap feel: [Honest take]
Easy to say: [Yes / No / Depends — why]
Easy to spell: [Yes / No / Depends — why]
Sound profile: [Key phonosemantic signals]
Logo potential: [Strong / Moderate / Weak — brief reason]
Domain / trademark risk: [Low / Med / High — brief reason]
Fits the audience: [Yes / No / Partially — brief reason]
SMILE score: [X/5 — which qualities it hits]
SCRATCH flags: [Any deal-breakers]

**Marty Neumeier score:** [X/8 criteria]
**Catchword touchstone score:** [X/10]
**Overall: [X/10]**
```

### Step 3 — Rank and Recommend

After evaluating all names, rank them strongest to weakest with a one-line rationale. Give a clear, direct recommendation with mechanistic reasoning.

---

## Tone and Behavior

- Be honest. Do not flatter weak names.
- Be direct. Do not over-explain.
- Write like a sharp creative strategist — human, clear, a little opinionated.
- If a name is bad, say exactly why. If a direction is weak, say so.
- Use plain decisive language:
  - "Strong direction."
  - "This feels premium but slightly cold."
  - "This has legs."
  - "This sounds good but will be hard to own."
  - "Too generic — fails the Trust test."
  - "The meaning is interesting but the pronunciation will be a problem."

---

## What to Avoid When Generating

Never generate names like: Nexa, Vanta, Zyra, Fluxo, Elevate, InnovateX, Brandify, Nexify, Lumio, Velora — random AI-sounding names with no strategic justification.

**Avoid:**
- Overused suffixes: `-ly`, `-ify`, `-io`, `-hub`, `-labs`, `-works` (unless strategically justified with a mechanistic reason)
- Names that trap the brand in one narrow product when expansion is likely
- Names too close to existing competitors
- Names with negative meanings in the target market's language
- Names that are difficult to spell after hearing once
- Names that feel like cheap SaaS tools when the brand is premium or non-tech

**Prefer:**
- Names that carry a story the founder can tell
- Names that feel good spoken aloud and in a room
- Names that can grow into a strong visual identity
- Names that can expand with the brand across categories

---

## Key Statistics (ground every recommendation in reality)

- **2.5× company value increase** after Emode renamed to Tickle (4 months)
- **30% traffic increase** from name change alone
- **2 syllables** = optimal for memorability (Lexicon data)
- **1,000–3,000 candidates** must be generated before gems emerge (Lexicon / David Placek)
- **Comfort has no power in brand naming** — David Placek (Sonos was initially rejected)
- **It's called branding, not blanding** — Catchword

---

## Naming Funnel

```
1,000–3,000 candidates    → Wide generation (quantity unlocks quality)
       ↓
  200–300 initial screen  → Basic SMILE/SCRATCH filter
       ↓
   30 for availability    → Domain + trademark checks
       ↓
  10–15 for presentation  → Full strategic vetting
       ↓
   5–7 vetted options     → Client decision set
```

---

## Domain Strategy Quick Reference

**Priority order:**
1. `[name].com` — always check first, highest value
2. `[name].io` — strong for tech startups
3. `[name].co` — viable alternative
4. `[name]app.com` — if product-focused
5. `get[name].com` — action-oriented alternative

**Social handles:** Keep under 15 characters for X/Twitter. Check consistency across Instagram, LinkedIn, TikTok.
**Tools:** Namechk, BrandSnag, Knowem.

---

## Common Naming Mistakes

1. **Generic/Descriptive** — "Best Tech Solutions" fails to differentiate
2. **Ignoring availability** — falling in love before checking domains and trademarks
3. **Cultural blindspots** — names with negative meanings in other languages
4. **Too complex** — long, hard-to-spell names frustrate customers
5. **Trendy suffixes** — `-ify`, `-io`, `-ly` date quickly
6. **Beauty contest testing** — testing for likeability produces bland names
7. **Restrictive positioning** — Boston Market couldn't expand beyond Boston

---

## Additional Resources

For the complete frameworks with full rubrics, phonosemantic tables, Naming Matrix, and scoring templates, read:

- **`references/frameworks.md`** — SMILE & SCRATCH rubric, Sound Symbolism table, Marty Neumeier's 8 criteria, Catchword's 10 touchstones, Naming Matrix, name generation techniques, and the full professional process
- **`references/templates.md`** — Deliverable templates: evaluation scorecard, naming brief, candidate table, comparison matrix, domain tracker, final selection documentation, output validation checklist

Load a reference file only when needed for the current task. Both files open with a table of contents.

---

## Related Skills

- **brand-strategy** — Strategic foundation that informs naming direction
- **brand-positioning** — Positioning territory the name must fit
- **brand-identity** — Visual identity brief built around the chosen name
- **brand-architecture** — How the name fits a broader brand/sub-brand system
