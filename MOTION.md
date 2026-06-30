# Souvik Skills Motion Standard

Use this file before changing animations, route transitions, install tabs, copy buttons, card interactions, filters, theme switching, page reveals, loading states, or mobile navigation. If a request says `notion.md` while discussing animation, treat it as `MOTION.md`.

## Product Frame

- Product archetype: marketplace, docs/devtools, and personal developer brand.
- Emotional tone: fast, tactile, precise, warm, technical, and premium.
- Motion density: medium on marketplace surfaces, sparse on docs, high only on direct input feedback.
- Repeated-use surfaces: nav, filters, skill cards, install tabs, copy buttons, theme toggle.
- Signature moment: command copy/install success.
- Motion risk: too much page choreography would make the site feel gimmicky and slow.

## Core Principle

Every animation must perform a job:

- Feedback: confirm input was received.
- Continuity: show how state changed.
- Orientation: preserve where the user is after routing, filtering, or tab switching.
- Hierarchy: guide attention to the next useful action.
- Progress: make waiting or copying understandable.
- Reward: make completion satisfying without celebration spam.
- Trust: settle cleanly and never feel random.

If the job cannot be named, remove the animation or replace it with static hierarchy.

## Motion Tokens

Use centralized CSS variables or Motion transition presets before inventing custom values.

```css
:root {
  --motion-duration-instant: 50ms;
  --motion-duration-press: 80ms;
  --motion-duration-hover: 120ms;
  --motion-duration-micro: 150ms;
  --motion-duration-response: 180ms;
  --motion-duration-reveal: 220ms;
  --motion-duration-standard: 280ms;
  --motion-duration-panel: 320ms;
  --motion-duration-modal: 400ms;
  --motion-duration-page: 520ms;
  --motion-duration-hero: 700ms;
  --motion-duration-ambient: 2800ms;

  --motion-ease-standard: cubic-bezier(0.4, 0, 0.2, 1);
  --motion-ease-out: cubic-bezier(0, 0, 0.2, 1);
  --motion-ease-out-soft: cubic-bezier(0.16, 1, 0.3, 1);
  --motion-ease-out-crisp: cubic-bezier(0.25, 0.46, 0.45, 0.94);
  --motion-ease-in: cubic-bezier(0.4, 0, 1, 1);
  --motion-ease-bold-move: cubic-bezier(0.4, 0, 0, 1);

  --motion-distance-xs: 4px;
  --motion-distance-sm: 8px;
  --motion-distance-md: 12px;
  --motion-distance-lg: 16px;

  --motion-scale-press: 0.98;
  --motion-scale-press-strong: 0.96;
  --motion-scale-hover: 1.01;
}
```

Use by intent:

| Intent | Duration | Pattern |
| --- | --- | --- |
| Press/tap | 50-90ms | scale/color feedback |
| Hover/control | 100-160ms | color/border/2px movement |
| Popover/menu | 120-180ms | opacity plus 4-8px movement |
| Filter/list reflow | 180-320ms | layout spring or FLIP |
| Panel/tab motion | 260-420ms | shared indicator or small slide |
| Page entrance | 280-520ms | low-distance opacity/y |
| Hero reveal | 520-700ms | limited sequencing |

## Motion Intent Map

| Surface | User action/state | Psychological job | Pattern | Timing/token | Reduced-motion variant | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| Global nav | scroll and route change | orientation, hierarchy | shell compresses, active route pill | spring, 180-320ms | keep active pill, remove scroll compression if needed | desktop and mobile scroll |
| Theme toggle | click | continuity, reward | view-transition reveal from toggle plus thumb movement | 520ms reveal, snappy thumb | instant theme with color/icon feedback | light/dark, reduced motion |
| Page content | route change | orientation | content opacity and 8-10px y movement | 280-420ms spring | opacity only | back/forward, mobile |
| Skill card | hover/focus | hierarchy, trust | translateY -2px, scale 1.01, border/shadow change | 120-180ms | color/border only | keyboard and pointer |
| Marketplace filter | query/category/sort | continuity | layout-preserving reflow with stable keys | 180-320ms spring | instant reflow | search, category chips |
| Select menu | open/close | orientation, feedback | origin-aware opacity/y/scale | 120-180ms | opacity only | keyboard arrows and Escape |
| Install tabs | tab change | continuity | shared moving pill | 180-260ms spring | instant selected state | keyboard/pointer |
| Copy button | click | feedback, reward, trust | press compression, icon morph, glow sweep, toast | 80ms press, 150ms icon, 420ms sweep | icon/color/live status only | clipboard and fallback |
| Command strips | copy/success | perceived performance | restrained background glow near copy button | 320-520ms | no sweep | mobile wrapping |
| Docs cards | enter viewport | hierarchy | single reveal pass, short distance | 220-320ms | static | no content jumps |

## Required Motion Moments

### Command Copy Success

- Press starts immediately.
- Button compresses to `0.96-0.98`.
- Icon morphs to check within 100-160ms.
- A short glow sweep may pass behind the copy button or command strip.
- Toast enters from the nearest edge and exits quietly.
- Reduced motion keeps icon/color/live-status feedback and removes sweep/translation.

### Install Tabs

- Shared moving pill expresses continuity.
- Content updates must not jump layout.
- Tabs remain readable when stacked on narrow screens.

### Skill Cards

- Hover lift is subtle and does not change document flow.
- Focus state is visible and equivalent to pointer affordance.
- Card text remains still.

### Marketplace Filtering

- Filter changes preserve card identity.
- Stagger is short and capped under 360ms.
- Search input feedback is immediate.

### Theme Switch

- Theme switch may use View Transitions when available.
- The transition starts from the toggle location.
- Reduced motion skips the reveal and keeps instant theme feedback.

## Performance Rules

- Animate `transform` and `opacity` by default.
- Do not use `transition: all`.
- Do not animate width, height, margin, padding, top, left, or expensive filters in hot paths.
- Avoid per-frame React state for animation.
- Keep offscreen ambient animation paused or do not create it.
- Large blur, heavy shadows, and backdrop effects must be static or extremely limited.
- Motion must never block clicks, scrolling, typing, or route changes.

## Accessibility Rules

- Implement `prefers-reduced-motion: reduce`.
- Reduced motion removes large translations, parallax, zooms, rotations, view-transition reveals, shimmer, and expressive loops.
- Keep short opacity/color feedback when it clarifies state.
- Preserve focus rings.
- Keyboard users must operate nav, filters, selects, install tabs, links, and copy actions.
- Escape closes menus and returns focus to the trigger.
- Motion cannot be the only success signal.

## Mobile Rules

- Verify 360px, 390px, and 430px widths.
- No motion may cause horizontal overflow.
- Hover-only effects are enhancements, not required affordances.
- Command text must wrap; do not animate command panel width.
- Sticky nav compression must remain readable and touch-safe.

## Stack Decisions

- CSS transitions: hover, focus, color, border, transform, opacity.
- CSS keyframes: copy sweep and tiny nonessential status glows only.
- Motion for React: page presence, layout reflow, shared tab pills, button tap states, select popovers.
- View Transition API: theme reveal only, with fallback.
- No smooth scrolling library for this site. It is a marketplace/docs surface, not a narrative scroll story.
- No GSAP/Lenis unless a future motion page becomes a dedicated showcase and `MOTION.md` is updated first.

## QA Checklist

- [ ] Product archetype and emotional tone are still accurate.
- [ ] Every changed animation has an intent-map entry.
- [ ] Motion tokens are centralized.
- [ ] Direct feedback starts within 50ms.
- [ ] Repeated interactions complete inside 80-220ms.
- [ ] No `transition: all` ships.
- [ ] No hot-path layout property animation ships.
- [ ] Reduced-motion mode is tested.
- [ ] Keyboard focus remains visible.
- [ ] Copy feedback works with Clipboard API and fallback.
- [ ] No horizontal overflow at 360px, 390px, 430px, tablet, desktop, or wide desktop.
- [ ] Live hosted pages are verified when public frontend output changes.
