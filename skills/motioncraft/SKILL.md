---
name: motioncraft
description: Design and implement premium interface motion systems, smooth scrolling, scroll-linked animation, micro-interactions, springs, easing, gesture feedback, page transitions, reduced-motion variants, and animation performance fixes. Use when Codex needs to make a web or app interface feel professional, alive, smooth, responsive, cinematic, tactile, or high-end; when adding Framer Motion, Motion, GSAP, Lenis, React Spring, CSS, WAAPI, scroll-triggered effects, hover, tap, drag, animated state changes, skeletons, loading motion, layout transitions, or motion tokens; or when reviewing animation jank, motion accessibility, or motion design quality.
---

# Motioncraft

This skill turns motion into a first-class design-system layer. It is for production UI motion, not decorative animation.

## Required Reference

For substantial motion work, read `references/motioncraft.md` before editing code. For a tiny one-off transition, use the quick workflow below and read the reference if the choice is not obvious.

## Quick Workflow

1. Inspect the existing interface, framework, animation libraries, CSS tokens, and performance constraints.
2. Define the motion intent for each change: feedback, continuity, orientation, hierarchy, progress, or delight.
3. Add or reuse motion tokens before adding bespoke values.
4. Prefer CSS transitions for simple hover/focus/state changes, WAAPI for imperative sequences, Motion/React Spring for interruptible springs and layout transitions, GSAP for timeline-heavy storytelling, and Lenis only for sites that need high-craft smooth scroll.
5. Animate `transform` and `opacity` by default. Avoid `transition: all`, layout properties, expensive blur, and per-frame React state updates.
6. Make all motion interruptible and responsive to direct user input.
7. Implement `prefers-reduced-motion` as an alternate motion design, not as an afterthought.
8. Verify in a real browser when motion affects layout, scroll, canvas/WebGL, mobile, or performance.

## Motion Taste Rules

- Direct manipulation must respond within 50 ms and usually complete visible feedback within 80-160 ms.
- Spatial transitions should preserve continuity through shared elements, stable origins, and velocity-aware springs.
- Use springs for gesture handoff, retargeting, drag/reorder, shared layout, and alive-feeling surfaces.
- Use bouncy springs sparingly. Default to bounce `0`; use `0.08-0.2` for tactile UI and rarely above `0.3`.
- Use one signature motion moment per viewport. Keep repeated product interactions quiet.
- Stagger by perception, not decoration: 16-24 ms for dense UI, 32-48 ms for cards/lists, 60-90 ms for editorial reveals.
- Smooth scrolling is for storytelling and premium marketing pages. Avoid scroll hijacking in forms, docs, tables, dashboards, and code-heavy product surfaces.

## Implementation Notes

When adding a motion system to a project:

1. Create tokens for durations, easings, springs, distances, stagger, and reduced-motion scale.
2. Map component patterns: button, link, menu, popover, modal, drawer, toast, tab, card, list, page, scroll section, loading state.
3. Centralize defaults through CSS custom properties, Tailwind theme values, a MotionConfig, or project-local utilities.
4. Keep token names semantic enough for agents and humans to choose by intent.
5. Test the resulting feel on at least one desktop and one mobile viewport.

## Verification

Before finishing motion work, check:

- Reduced motion disables or greatly simplifies transform, scroll, parallax, autoplay, and looping movement.
- Keyboard users can complete the same flow, focus remains visible, and focus is moved/restored for overlays.
- No text overlaps or layout shifts because of animated states.
- No expensive animation runs continuously outside the viewport.
- DevTools performance does not show layout thrash, dropped frames, or long tasks from animation work.
