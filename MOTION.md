# Souvik Skills Motion Standard

Use this file before changing animations, route transitions, install tabs, copy buttons, card interactions, or mobile menu motion.

## Motion Intent

Every animation must do at least one job:

- Feedback: confirm input was received.
- Continuity: show how state changed.
- Orientation: preserve where the user is in the marketplace.
- Hierarchy: guide attention to the next useful action.
- Progress: make waiting or copying understandable.

Remove motion that is only decoration.

## Tokens

Use centralized tokens before inventing bespoke values.

```css
:root {
  --motion-press: 80ms;
  --motion-hover: 140ms;
  --motion-response: 220ms;
  --motion-panel: 360ms;
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-standard: cubic-bezier(0.4, 0, 0.2, 1);
}
```

Use by intent:

- Press/tap: 50-90ms.
- Hover/control feedback: 100-160ms.
- Card/list reflow: 180-280ms.
- Panel/menu/tab movement: 260-420ms.
- Route/page entrance: 280-520ms.

## Required Motion Moments

- Route transition: low-distance opacity/y movement.
- Skill card hover: subtle lift and scale, no layout shift.
- Marketplace filter: layout-preserving reflow with stable card identity.
- Install tabs: shared moving indicator.
- Copy button: press compression, icon morph to check, restrained glow sweep.
- Mobile menu: short opacity/y transition with keyboard-safe state.

## Performance Rules

- Animate `transform` and `opacity` by default.
- Do not use `transition: all`.
- Do not animate width, height, margin, padding, top, left, or expensive filters in hot paths.
- Keep offscreen ambient loops paused or avoid them entirely.
- Avoid per-frame React state for animation.

## Accessibility

- Implement `prefers-reduced-motion: reduce`.
- Reduced motion disables expressive movement, large translations, loops, shimmer, and route movement.
- Keep short opacity/color feedback if it helps state clarity.
- Preserve visible focus rings.
- Keyboard users must be able to operate nav, filters, tabs, links, and copy buttons.

## Mobile Rules

- Motion must not cause horizontal overflow at 360px, 390px, or 430px.
- Hover-only effects must not be required for touch users.
- Install tab transitions must remain readable when tabs stack.
- Command text must wrap cleanly; do not animate command panel width.

## Verification

Before finishing frontend work:

- Test desktop, tablet, 390px mobile, and 360px mobile.
- Check reduced-motion mode.
- Confirm no horizontal overflow.
- Confirm no nested scrollbar appears inside cards, command strips, or install modules.
- Confirm copy animation and toast/state feedback work on every install module.
