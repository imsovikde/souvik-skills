---
name: motioncraft
description: Design, audit, and implement project-specific premium interface motion systems using motion psychology, product archetypes, animation tokens, micro-interactions, route transitions, scroll storytelling, gesture feedback, springs, easing, reduced-motion variants, and performance repair. Use when Codex needs to make a web or app interface feel top-tier, responsive, cinematic, tactile, alive, trustworthy, or high-end; when choosing or reviewing Motion, Framer Motion, GSAP, Lenis, React Spring, CSS transitions, WAAPI, View Transitions, scroll-linked effects, hover, tap, drag, command-copy success, loading states, layout transitions, motion tokens, or animation quality; or when fixing generic motion, jank, accessibility failures, scroll hijacking, mobile motion issues, or unverified animation work.
---

# Motioncraft

Turn motion into a project-specific design-system layer. Do not add generic fade-and-slide animation. Diagnose the product, decide what the user should feel and understand, then implement the smallest motion system that makes the interface clearer, faster, and more memorable.

## Required Reference

For substantial motion work, read `references/motioncraft.md` before editing code. Use it for product archetypes, motion psychology, benchmark method, tokens, recipes, anti-patterns, and the quality rubric.

Useful bundled resources:

- `scripts/audit-motioncraft.cjs`: run a read-only motion audit against a target project.
- `assets/templates/motion-map.md`: copy or adapt when planning a motion system.
- `assets/templates/motion-tokens.css` and `assets/templates/motion-tokens.ts`: starter token sets.
- `assets/templates/reduced-motion.css`: reduced-motion baseline.
- `assets/templates/motion-qa-checklist.md`: verification checklist.

## Non-Negotiable Protocol

Before adding animation, create a motion intent map in your working notes or final plan. Every major animation must name:

1. Surface or component.
2. User action or state change.
3. Psychological job: feedback, continuity, orientation, hierarchy, progress, reward, perceived performance, trust, or brand memory.
4. Product archetype and emotional tone.
5. Pattern, library, duration/easing/spring, reduced-motion alternative, and verification method.

If you cannot name the job, remove the animation or replace it with static visual hierarchy.

## Workflow

1. Inspect the project: framework, routes, components, CSS system, animation libraries, tokens, design docs, target users, mobile constraints, and performance risks.
2. Classify the surface: SaaS/dashboard, docs/devtools, marketplace, portfolio/editorial, AI/chat tool, ecommerce, mobile app, creative/game, or mixed product.
3. Define motion psychology: what should feel fast, stable, premium, playful, technical, calm, powerful, safe, or memorable.
4. Benchmark 3-5 relevant high-quality references when the project benefits from it. Extract principles only; do not copy assets, copy, or brand-specific choreography.
5. Build or extend motion tokens before adding bespoke values.
6. Choose the stack by job: CSS for simple states, WAAPI for imperative sequences, Motion/React Spring for springs/layout/gesture, GSAP for timeline-heavy storytelling, Lenis only for high-craft narrative scroll.
7. Implement reusable primitives first: press, hover, focus, reveal, overlay, page transition, list reflow, copy success, toast, loading, and reduced-motion utilities.
8. Apply motion component by component, keeping repeated product interactions quiet and reserving one signature moment per page or flow.
9. Verify in a real browser for mobile, keyboard, reduced motion, layout stability, scroll behavior, and performance.
10. Delete motion that feels delayed, noisy, decorative, inaccessible, or detached from user intent.

## Taste Rules

- Direct manipulation must respond within 50 ms and visible feedback usually completes in 80-160 ms.
- Dense product UI should feel precise and low-noise; serious tools rarely need bounce above `0.16`.
- Spatial transitions should preserve continuity through shared elements, stable origins, and velocity-aware springs.
- Stagger by perception, not decoration: 16-24 ms for dense UI, 32-48 ms for cards/lists, 60-90 ms for editorial reveals.
- Motion should never hide broken layout, unclear hierarchy, weak copy, poor contrast, or missing affordance.
- Smooth scrolling belongs in narrative/product storytelling. Avoid it in docs, dashboards, tables, forms, admin tools, and code-heavy workflows.
- Reduced motion is an alternate design, not an afterthought: remove large translations, parallax, zoom, rotation, scroll smoothing, autoplay, and loops while preserving essential state feedback.

## Verification

Before finishing motion work, verify:

- Every major animation has an intent-map entry.
- Motion tokens are centralized and semantic.
- No `transition: all` or hot-path layout-property animation exists.
- Keyboard users receive equivalent state feedback, visible focus, and correct focus movement/restoration.
- No text overlaps, horizontal overflow, layout jump, or scroll trap is introduced.
- Offscreen ambient animation is paused or avoided.
- Reduced-motion mode is tested, not merely written.
- DevTools or browser testing shows no layout thrash, dropped-frame obviousness, or long tasks caused by animation.
