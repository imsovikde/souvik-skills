# Souvik Skills Frontend Design Standard

Use this file before changing the Souvik Skills website, marketplace cards, skill pages, install modules, or brand assets.

## Identity

- Brand: Souvik Skills.
- Owner: Souvik Dey.
- Product shape: personal skill marketplace for reusable AI-agent workflows.
- Visual position: warm editorial craft plus dark macOS terminal/product surfaces.
- Never use Anthropic, Claude, Vercel, or third-party brand marks as Souvik Skills identity assets.

## Layout

- The site is a multi-page marketplace, not a single landing page.
- Public routes must include `/`, `/skills`, `/skills/<skill-name>`, `/install`, `/docs`, and `/motion`.
- Skill pages are generated from the local `skills/` directory at build time.
- Do not hard-code current public skill names as the source of truth.
- Use normal document scrolling only. Do not create full-page scroll traps.
- Avoid nested scrollbars inside cards, install modules, command panels, drawers, or code windows.

## Mobile Responsiveness

- Design mobile first at 360px, then verify 390px, 430px, tablet, desktop, and wide desktop.
- No horizontal overflow is acceptable.
- Command text must wrap or soft-break cleanly instead of forcing inner scrollbars.
- Cards stack to one column on mobile.
- Touch targets should be at least 44px where practical.
- Buttons may become full-width on narrow screens.

## Visual System

- Canvas: warm cream, not pure white.
- Text: warm near-black on light surfaces and cream text on dark surfaces.
- Accent: restrained coral for primary actions and selected states.
- Product surfaces: dark macOS-style panels with traffic lights, subtle hairlines, and command strips.
- Marketplace cards should feel like code-window cards, not generic SaaS feature cards.
- Keep border radius purposeful: 8px for small controls, 12-18px for cards, 24-28px for hero/product panels.
- Avoid purple gradients, decorative blobs, stock imagery, generic AI ornaments, and one-note color palettes.

## Brand Mark

- Use the current interlocking Souvik Skills glyph in `components/brand.jsx`, `app/icon.svg`, `app/favicon.ico`, and generated touch icons.
- Logo SVGs must be self-contained, flat-fill, legible at favicon size, and readable on light/dark surfaces.
- Do not use the rejected blocky prototype logo.

## Install Modules

- Every skill page must include the dark macOS-style install module.
- Required tabs: Project, Global, Try once.
- Required agent selector: Claude Code, Codex, Cursor, Gemini CLI, OpenCode, GitHub Copilot.
- Copy buttons must be visible, keyboard focusable, and animated.
- Helper text must explain where the selected install mode writes or what it does.

## Content

- Keep copy concise and practical.
- Skill cards show: display name, category, description, command preview, copy action, source link, and page link.
- Skill pages show: what the skill does, when to use it, default prompt, install commands, and source resources.
- Use `SKILL.md` and `agents/openai.yaml` as the content authority.
