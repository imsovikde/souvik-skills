# Souvik Skills Design Standard

Use this file before changing the Souvik Skills website, marketplace cards, skill pages, install modules, docs pages, brand assets, typography, spacing, color, or responsive behavior. Treat it as the visual contract for the site.

## Product Frame

- Brand: Souvik Skills.
- Owner: Souvik Dey.
- Product type: public marketplace and install directory for reusable AI-agent skills.
- Audience: developers, AI-agent users, maintainers, and visitors deciding whether a skill is trustworthy enough to install.
- Design archetype: developer marketplace plus personal craft studio.
- Desired feeling: precise, warm, fast, collected, terminal-literate, and quietly premium.
- Primary trust job: make every skill feel inspectable, installable, and maintained.

## Visual Theme And Atmosphere

Souvik Skills should feel like a handcrafted developer console sitting on a warm editorial canvas. The page should not look like a generic SaaS landing page, a heavy docs portal, or a decorative AI toy.

The first impression should communicate:

- personal authorship from Souvik Dey
- serious repository hygiene
- fast copy-and-install workflows
- code-window familiarity
- calm visual confidence
- enough motion polish to feel alive without interrupting reading

Avoid sterile white dashboards, purple AI gradients, decorative blobs, mascot-style illustration, oversized marketing hero cards, nested card stacks, and one-note color palettes.

## Typography

Use self-hosted Google fonts through `next/font/google` so Vercel and Cloudflare builds emit local font assets.

| Role | Font | Usage |
| --- | --- | --- |
| Primary UI and display | Bricolage Grotesque | body text, headings, cards, buttons, navigation |
| Monospace | Geist Mono | commands, code, metadata, short technical labels |
| System fallback | system UI stack | fallback only while web fonts load |

Typography rules:

- Use Bricolage Grotesque for the site personality: warm, technical, and slightly expressive.
- Use Geist Mono only for command-line or metadata surfaces.
- Do not use viewport-width font scaling. Use fixed rem sizes with media-query steps.
- Letter spacing is `0` by default. Use positive tracking only for short uppercase metadata labels.
- Hero-scale type is reserved for page heroes and major section titles.
- Cards, sidebars, nav items, filters, and install modules must use compact type.
- Long skill names must wrap cleanly and never overlap controls.

Type scale:

| Token | Mobile | Tablet | Desktop | Use |
| --- | --- | --- | --- | --- |
| `--type-hero` | 3.35rem | 5.75rem | 7.5rem | home hero only |
| `--type-page` | 3rem | 4.8rem | 6.4rem | route titles |
| `--type-section` | 2.15rem | 3.35rem | 4.4rem | section/display headings |
| `--type-card` | 1.08rem | 1.12rem | 1.16rem | card headings |
| `--type-body` | 1rem | 1rem | 1rem | normal text |
| `--type-lede` | 1.08rem | 1.18rem | 1.28rem | hero supporting copy |
| `--type-micro` | 0.74rem | 0.76rem | 0.78rem | metadata and labels |

## Color Palette And Roles

| Token | Light | Dark | Role |
| --- | --- | --- | --- |
| `--canvas` | `#f7f2e9` | `#11100e` | page background |
| `--canvas-deep` | `#efe6d7` | `#171512` | subtle bands |
| `--ink` | `#151411` | `#f8f0e4` | headings and high-emphasis text |
| `--body` | `#423f38` | `#d8cfc0` | body copy |
| `--muted` | `#6d675e` | `#a99f90` | secondary copy |
| `--line` | `#ded2c2` | `#383229` | light surface borders |
| `--panel` | `#1c1c22` | `#1a1a20` | terminal panels |
| `--panel-soft` | `#24242b` | `#23232b` | nested terminal surfaces |
| `--panel-text` | `#f8f3ea` | `#fff7ec` | text on dark panels |
| `--coral` | `#d87258` | `#e57b60` | primary action and brand accent |
| `--coral-strong` | `#b95b42` | `#ff9a7c` | active states and links |
| `--mint` | `#69d391` | `#69d391` | terminal success |
| `--blue` | `#8fb4ff` | `#8fb4ff` | secondary technical cue |
| `--amber` | `#f0b85f` | `#f0b85f` | warning/status accent |

Color rules:

- Coral is the primary action color. Use it sparingly.
- Dark terminal panels carry commands, skill cards, install modules, and source metadata.
- Warm cream canvas is the public-site default; pure white should be rare.
- Do not let purple, blue, beige, brown, or orange dominate the full page.
- Text contrast must remain readable in both themes.

## Layout Principles

- The site is a multi-page marketplace, not a single landing page.
- Required public routes: `/`, `/skills`, `/skills/<skill-name>`, `/install`, `/docs`, and `/motion`.
- Skill pages must be generated from `skills/`, `SKILL.md`, and `agents/openai.yaml`.
- The homepage should show the product immediately, then reveal skill cards and install workflows.
- Use one constrained content container: `--container: 1180px`.
- Use full-width sections and unframed layouts. Do not put page sections inside cards.
- Cards are for repeated items, install modules, terminal panels, and detail modules only.
- Do not put cards inside cards.
- Normal document scrolling only. No scroll traps, nested card scrollbars, or full-page hijacking.
- Command text wraps or soft-breaks; it must not force horizontal page overflow.

Spacing scale:

| Token | Value | Use |
| --- | --- | --- |
| `--space-1` | 4px | fine control gaps |
| `--space-2` | 8px | chip/button gaps |
| `--space-3` | 12px | compact padding |
| `--space-4` | 16px | card inner spacing |
| `--space-5` | 20px | dense module padding |
| `--space-6` | 24px | section blocks |
| `--space-8` | 32px | major grouping |
| `--space-10` | 48px | tight section rhythm |
| `--space-12` | 72px | mobile section rhythm |
| `--space-16` | 96px | desktop section rhythm |

## Component Styling

### Navigation

- Sticky, glassy, compact, and readable.
- Header may compress on scroll, but it must not obscure content or cause mobile overflow.
- Active route state needs a visible pill or surface state.
- GitHub link remains visible as a utility action.
- Mobile nav may scroll horizontally only for the top nav row, never the page.

### Buttons

- Use icon plus text for route or install commands when useful.
- Primary buttons use coral fill.
- Secondary buttons use warm surface fill and visible border.
- Dark buttons live on terminal panels.
- Press feedback is required and must start immediately.
- Button text must never clip at 360px.

### Skill Cards

- Cards should feel like compact macOS/code-window objects.
- Required content: category, display name, description, install command, copy action, skill page link, source link.
- Hover lift is subtle and layout-stable.
- Descriptions may clamp to preserve card rhythm, but full copy must exist on the skill detail page.

### Install Modules

- Every skill page and install page module uses the dark macOS-style installer.
- Required tabs: Project, Global, Try once.
- Required agent selector: Claude Code, Codex, Cursor, Gemini CLI, OpenCode, GitHub Copilot.
- Copy action must be visible, keyboard focusable, animated, and paired with live status feedback.
- Helper text explains destination or behavior.

### Forms And Filters

- Search input must be easy to find and operate on mobile.
- Category chips must have visible selected state.
- Reflow must preserve card identity.
- Result count or visible change should be obvious without flashy animation.

### Source Lists And Docs

- Source file lists use dark panels when the content is technical.
- Markdown snippets must preserve line wrapping.
- Docs pages should be concise, navigable, and current with the repository behavior.

## Depth And Elevation

- Use hairline borders and soft shadows for separation.
- Terminal panels can cast deeper shadows than light content cards.
- Avoid floating page sections.
- Avoid heavy blur on large animated surfaces.
- Shadows must not be the only selected/hover state.

Radius rules:

- Small controls: 8px to 13px.
- Buttons and inputs: 13px to 16px.
- Cards/modules: 18px.
- Hero/product terminal panels: 24px to 28px.
- Pills: 999px only for nav chips, tabs, and compact labels.

## Motion Relationship

Design and motion are linked. Before changing visual or interactive behavior, read `MOTION.md` as well.

The visual system creates the stable structure; motion adds feedback and continuity. If motion is removed, the design must still work. If design hierarchy is weak, do not use motion to hide it.

## Responsive Behavior

Required checks:

- 360px mobile
- 390px mobile
- 430px mobile
- tablet
- desktop
- wide desktop

Rules:

- No horizontal overflow is acceptable.
- Cards stack to one column on mobile.
- Command modules keep copy buttons reachable.
- Touch targets should be at least 44px where practical.
- Button rows become full-width when narrow.
- Long skill names and install commands wrap.
- Sticky sidebars become normal flow on mobile/tablet.

## Accessibility

- Preserve visible focus rings.
- Keyboard users must operate nav, filters, selects, tabs, copy buttons, and links.
- Copy feedback must use `role="status"` or equivalent live feedback.
- Color must not be the only state signal.
- Reduced-motion mode must preserve state feedback.
- Do not animate text while users are trying to read it.

## Do

- Use repository content as the source of truth.
- Keep all public skill names derived from `skills/`.
- Use Bricolage Grotesque and Geist Mono through local font assets generated by Next.
- Keep command surfaces dark and readable.
- Use warm editorial spacing around dense terminal components.
- Check mobile before finishing.

## Do Not

- Do not hard-code current skill names into route generation.
- Do not create `context.md`.
- Do not use third-party brand marks as Souvik Skills identity.
- Do not add decorative blobs, generic AI gradients, stock imagery, or irrelevant illustrations.
- Do not use viewport-width font scaling.
- Do not create nested cards or nested scrollbars.
- Do not ship frontend changes without reading and updating this file when the design language changes.

## Agent Prompt Guide

When asked to change the site, use this operating prompt:

```text
Read AGENTS.md, DESIGN.md, and MOTION.md first. Preserve the Souvik Skills marketplace identity: warm Bricolage Grotesque typography, dark terminal install surfaces, coral primary actions, self-generated skill pages, mobile-first layout, zero horizontal overflow, and purpose-driven motion from MOTION.md.
```
