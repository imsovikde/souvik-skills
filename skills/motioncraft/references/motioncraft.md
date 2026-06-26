# Motioncraft Reference

Premium Interface Motion Standard for AI Coding Agents

## Purpose

Motion is a design-system layer. Treat it with the same rigor as typography, spacing, color, and accessibility. Every animation must make the interface easier to understand, faster to operate, more continuous, or more emotionally rewarding.

This standard codifies production motion for web interfaces with special attention to smooth scrolling, scroll-linked storytelling, micro-interactions, spring feedback, layout transitions, loading states, and performance.

## Research Basis

This standard synthesizes:

- Apple Human Interface Guidelines and WWDC spring guidance: continuity, velocity preservation, duration plus bounce, natural settling, layered spatial transitions.
- Linear homepage and product writing: quiet precision, low-noise hierarchy, dense product UI that feels fast and refined.
- Stripe engineering writing: custom curves, CSS/WAAPI first, transform and opacity, IntersectionObserver, sub-500 ms interaction pacing.
- Vercel Web Interface Guidelines: accessibility, CSS-first animation, compositor-friendly properties, interruptibility, no `transition: all`.
- Motion.dev: tween, spring, inertia, gesture velocity, visualDuration, bounce, stiffness, damping, mass.
- Lenis: smooth scroll that keeps native scroll, sticky positioning, anchors, and accessibility usable while enabling scroll-linked animation.
- Carbon, Atlassian, Shopify Polaris, Material, and other design systems: semantic duration/easing tokens, purposeful choreography, reduced-motion variants.
- Live site observations on 2026-06-26 for apple.com, anthropic.com, elevenlabs.io, linear.app, stripe.com, framer.com, and vercel.com.

Observed examples:

- Linear used frequent 100-160 ms UI transitions with `cubic-bezier(0.25, 0.46, 0.45, 0.94)` and long linear ambient loops around 2800 ms.
- Apple iPhone pages used 320 ms nav/color transitions with `cubic-bezier(0.4, 0, 0.6, 1)`, small reveal offsets, and progressive delays around 20 ms.
- Anthropic used restrained 200 ms ease transitions and 400 ms navigation opacity transitions with `cubic-bezier(0.77, 0, 0.175, 1)`, plus a GSAP-driven ambient element.
- ElevenLabs and Vercel leaned on 150 ms `cubic-bezier(0.4, 0, 0.2, 1)` UI transitions and selective long-running or scroll-linked effects.

## Philosophy

### Motion Has A Job

Use motion only when it performs at least one job:

- Feedback: confirm that input was received.
- Continuity: show where an object came from, where it went, or how state changed.
- Orientation: preserve context during navigation, filtering, expansion, or reordering.
- Hierarchy: guide attention toward the next useful thing.
- Progress: make waiting understandable and stable.
- Delight: create a memorable moment without stealing control.

If the motion does not have a job, remove it.

### Alive Means Responsive, Not Busy

An interface feels alive when it reacts immediately, preserves momentum, settles naturally, and lets the user interrupt it. It does not need constant movement. Premium motion is often felt more than noticed.

### The Best Motion Is Spatially Honest

Objects should move from plausible origins, scale from the point of action, and preserve visual identity across states. Avoid arbitrary fades when a user needs to understand continuity.

### Motion Must Stay Under The User

User input outranks choreography. Hover, press, drag, scroll, route changes, and keyboard navigation should cancel or retarget animation without awkward jumps.

## Motion Personalities To Borrow

### Apple

- Use springs for continuity and velocity handoff.
- Use layered transitions: background, primary object, secondary details.
- Let objects settle with a natural tail.
- Use bounce as character, not as default.
- Prefer shared elements and zoom-like continuity for navigation.

### Linear

- Keep product UI fast and low-noise.
- Use 100-160 ms transitions for controls.
- Make structure perceptible through subtle state changes rather than visible decoration.
- Prioritize clarity, density, and repeat-use speed.

### Stripe

- Use custom curves instead of browser defaults.
- Use CSS for simple motion, WAAPI for chainable interactive sequences, and low-level animation only when needed.
- Keep most UI animation under 500 ms.
- Trigger expensive narrative animation only when visible.

### Vercel

- Prefer CSS, then WAAPI, then JavaScript libraries.
- Animate `transform` and `opacity`.
- Avoid `transition: all`.
- Make animations interruptible and input-driven.
- Use reduced-motion variants.

### Anthropic

- Keep motion calm, confident, and content-led.
- Use restrained fades, opacity, masks, and simple transforms.
- Avoid over-expressive UI on text-heavy pages.
- Let motion create confidence instead of spectacle.

### ElevenLabs And Framer

- Use smooth reveals and scrubbed storytelling for creative product demonstrations.
- Give hero/media experiences a tactile rhythm.
- Use dynamic previews and state changes to make capability tangible.
- Keep controls crisp while letting media carry expressive motion.

## Canonical Tokens

Use tokens. Do not scatter raw durations and cubic-beziers throughout a codebase.

### Duration Tokens

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
  --motion-duration-story: 900ms;
  --motion-duration-ambient-fast: 1200ms;
  --motion-duration-ambient: 2800ms;
  --motion-duration-ambient-slow: 6000ms;
}
```

Use by intent:

- 50-80 ms: press, tap, immediate tactile feedback.
- 100-160 ms: hover, color, border, small icon movement, direct controls.
- 180-240 ms: dropdowns, tooltips, small popovers, inline validation.
- 260-360 ms: tabs, panels, list insert/remove, card reveal.
- 360-520 ms: modals, drawers, page-level transitions.
- 600-900 ms: hero reveals, scroll scenes, complex marketing sequences.
- 1200 ms and above: ambient loops, skeleton shimmer, marquee, background life.

### Easing Tokens

```css
:root {
  --motion-ease-linear: cubic-bezier(0, 0, 1, 1);
  --motion-ease-standard: cubic-bezier(0.4, 0, 0.2, 1);
  --motion-ease-standard-productive: cubic-bezier(0.2, 0, 0.38, 0.9);
  --motion-ease-standard-expressive: cubic-bezier(0.4, 0.14, 0.3, 1);
  --motion-ease-out: cubic-bezier(0, 0, 0.2, 1);
  --motion-ease-out-soft: cubic-bezier(0.16, 1, 0.3, 1);
  --motion-ease-out-crisp: cubic-bezier(0.25, 0.46, 0.45, 0.94);
  --motion-ease-in: cubic-bezier(0.4, 0, 1, 1);
  --motion-ease-in-practical: cubic-bezier(0.6, 0, 0.8, 0.6);
  --motion-ease-in-out: cubic-bezier(0.4, 0, 0.6, 1);
  --motion-ease-bold-enter: cubic-bezier(0, 0.4, 0, 1);
  --motion-ease-bold-move: cubic-bezier(0.4, 0, 0, 1);
  --motion-ease-stripe: cubic-bezier(0.2, 1, 0.2, 1);
  --motion-ease-menu: cubic-bezier(0.77, 0, 0.175, 1);
}
```

Use by intent:

- `standard`: default material UI and Vercel-like utility interactions.
- `out`: entrances, reveals, tooltip/popover entrance.
- `out-crisp`: Linear-like product controls.
- `in`: exits that leave the screen.
- `in-out`: symmetric nav/menu color and simple movement.
- `bold-enter`: emphasized panel entrance.
- `bold-move`: shared indicator, tab underline, repositioning.
- `stripe`: polished marketing/product storytelling.
- `menu`: large menu opacity or overlay transitions.

### Spring Tokens

Use duration plus bounce when the library supports it; use physics values when needed.

```ts
export const springs = {
  instant: { type: "spring", visualDuration: 0.24, bounce: 0 },
  snappy: { type: "spring", visualDuration: 0.34, bounce: 0.08 },
  responsive: { type: "spring", visualDuration: 0.42, bounce: 0.12 },
  smooth: { type: "spring", visualDuration: 0.52, bounce: 0 },
  expressive: { type: "spring", visualDuration: 0.62, bounce: 0.18 },
  drag: { type: "spring", visualDuration: 0.45, bounce: 0.22 },
  settle: { type: "spring", visualDuration: 0.7, bounce: -0.12 }
};

export const physicsSprings = {
  instant: { type: "spring", stiffness: 700, damping: 46, mass: 0.8 },
  snappy: { type: "spring", stiffness: 520, damping: 36, mass: 0.9 },
  responsive: { type: "spring", stiffness: 420, damping: 32, mass: 1 },
  smooth: { type: "spring", stiffness: 280, damping: 30, mass: 1 },
  expressive: { type: "spring", stiffness: 260, damping: 22, mass: 0.95 },
  drag: { type: "spring", stiffness: 460, damping: 30, mass: 1.1 },
  settle: { type: "spring", stiffness: 180, damping: 28, mass: 1.2 }
};
```

Spring rules:

- Default to bounce `0` for professional product UI.
- Use bounce `0.08-0.16` for tactile controls, cards, shared indicators, and small success moments.
- Use bounce `0.18-0.28` for drag release, reorder, swipe-to-dismiss, playful consumer UI, or creative demos.
- Avoid bounce above `0.3` unless the product is intentionally playful.
- Use negative bounce or high damping for serious apps that should feel stable and premium.
- Preserve velocity when a gesture hands off to a spring.
- Retarget springs instead of restarting from zero.

### Distance And Scale Tokens

```css
:root {
  --motion-distance-2xs: 2px;
  --motion-distance-xs: 4px;
  --motion-distance-sm: 8px;
  --motion-distance-md: 12px;
  --motion-distance-lg: 16px;
  --motion-distance-xl: 24px;
  --motion-distance-2xl: 40px;
  --motion-distance-3xl: 64px;

  --motion-scale-press: 0.98;
  --motion-scale-press-strong: 0.96;
  --motion-scale-enter: 0.97;
  --motion-scale-hover: 1.01;
  --motion-scale-hero: 1.04;
}
```

### Stagger Tokens

```css
:root {
  --motion-stagger-dense: 16ms;
  --motion-stagger-ui: 24ms;
  --motion-stagger-list: 36ms;
  --motion-stagger-card: 48ms;
  --motion-stagger-editorial: 72ms;
}
```

Stagger rules:

- Cap total stagger under 360 ms for product UI.
- Cap total stagger under 700 ms for marketing/editorial reveals.
- Do not stagger controls that users need immediately.
- Use group-level reveals before item-level reveals when a page is dense.

## Global Motion Rules

### Performance

- Animate `transform` and `opacity` by default.
- Avoid animating `width`, `height`, `top`, `left`, `margin`, `padding`, `filter`, `box-shadow`, and deep CSS variables.
- If blur is required, keep it small and short. Large blur is expensive, especially in Safari.
- Never use `transition: all`.
- Add `will-change` only shortly before an animation and remove it after completion.
- Batch layout reads and writes. Do not read layout after writing styles in the same frame.
- Avoid per-frame React state for animation. Use CSS, WAAPI, Motion values, refs, or requestAnimationFrame.
- Use `content-visibility`, virtualization, or canvas/WebGL for large animated sets.
- Pause or remove offscreen loops.
- Profile on lower-end devices and Safari, not only a fast desktop Chrome.

### Accessibility

- Always provide a `prefers-reduced-motion: reduce` variant.
- Reduced motion should remove large translations, parallax, smooth scroll, scrubbed effects, zooms, rotations, autoplay, and loops.
- Reduced motion may keep short opacity or color changes when useful for state clarity.
- Never hide essential information behind animation timing.
- Preserve focus visibility. Do not animate focus rings in a way that makes them hard to see.
- Manage focus for modals, drawers, menus, route transitions, and async states.
- Avoid vestibular triggers: large z-axis movement, rotation, zoom tunnels, scroll-jacking, and persistent parallax.

### Interaction Integrity

- Press feedback starts immediately and completes quickly.
- Hover does not shift layout.
- Keyboard and pointer interactions have equivalent state feedback.
- Loading states have a short show delay and minimum visible time to prevent flicker.
- Animations must be cancelable by user input.
- Motion must not block clicks, scrolling, typing, or route changes.

## Implementation Decision Tree

Use CSS transitions when:

- The animation is a simple hover, focus, active, color, opacity, transform, or small reveal.
- Values are known ahead of time.
- No gesture velocity or complex choreography is needed.

Use CSS keyframes when:

- The motion repeats, has multiple steps, or runs independently of app state.
- Examples: shimmer, spinner, small ambient loop, marquee.

Use Web Animations API when:

- You need imperative control, sequence chaining, play/pause/reverse, or dynamic runtime values.
- You want CSS-like performance without a full animation library.

Use Motion / Framer Motion when:

- You need React layout transitions, shared elements, `AnimatePresence`, gesture velocity, springs, scroll values, or interruptible state transitions.

Use React Spring when:

- You need deeply physical, continuous, data-driven spring values.

Use GSAP when:

- You need timeline choreography, ScrollTrigger, scrubbed storytelling, pinned scenes, SVG morphing, or complex marketing pages.

Use Lenis when:

- The site needs premium smooth scroll and scroll-linked animation.
- Native scroll semantics, anchor links, sticky positioning, and accessibility must still work.
- The page is marketing/editorial, not a productivity surface.

Use native CSS scroll timelines when:

- Browser support and project requirements allow.
- The effect is simple, declarative, and does not require custom smoothing or complex pinning.

## Smooth Scrolling And Scroll-Linked System

### When To Use Smooth Scrolling

Use smooth scrolling for:

- Narrative landing pages.
- Product storytelling.
- Scroll-scrubbed media.
- Pinned feature sections.
- Parallax layers in visual experiences.

Avoid smooth scrolling for:

- Dashboards.
- Docs.
- Code views.
- Tables.
- Forms.
- Admin tools.
- Any flow where scroll speed and browser-native feel are part of productivity.

### Core Algorithm

Use a frame-rate-independent interpolation, not a fixed per-frame magic number:

```ts
function damp(current: number, target: number, lambda: number, dt: number) {
  const alpha = 1 - Math.exp(-lambda * dt);
  return current + (target - current) * alpha;
}
```

Recommended values:

- `lambda: 10-14` for calm desktop smooth scroll.
- `lambda: 14-18` for responsive product demos.
- `lambda: 8-10` for cinematic long-form pages.
- Clamp velocity during large wheel spikes.
- Stop when distance to target is below `0.1px`.

### Scroll Progress Model

Every scroll-linked scene should expose:

```ts
type ScrollScene = {
  start: number;
  end: number;
  progress: number; // 0..1
  velocity: number; // px/s
  direction: 1 | -1;
  isActive: boolean;
};
```

Rules:

- Compute progress from measured section bounds.
- Recalculate on resize, font load, content load, and media load.
- Use `IntersectionObserver` to activate/deactivate scenes.
- Use `ResizeObserver` for dynamic content.
- Use transforms for visual response.
- Keep text readable; do not parallax body text more than 2-4 percent of viewport height.

### Parallax Strengths

- Background texture: 2-5 percent of viewport height.
- Product image: 4-10 percent.
- Foreground accent: 8-16 percent.
- Text: 0-4 percent.
- Fixed/pinned product scene: scrub progress instead of moving the whole layout.

### Scroll-Linked Patterns

Reveal on enter:

- Start at 8-24 px offset and opacity 0.
- End at neutral transform and opacity 1.
- Duration 220-420 ms.
- Trigger around 12-20 percent into viewport.
- Do not retrigger repeatedly unless the product intentionally needs it.

Pinned product story:

- Pin the visual area.
- Map scroll progress to 3-5 discrete beats.
- Crossfade labels with 120-180 ms overlap.
- Scrub media transforms with progress.
- Keep navigation and keyboard flow usable.

Direction-aware nav:

- Hide or compact on downward velocity after a threshold.
- Reveal immediately on upward scroll.
- Never hide if focus is inside nav.
- Prefer transform `translateY`, not layout changes.

Velocity-aware details:

- Use scroll velocity to add small secondary offsets.
- Clamp aggressively.
- Return to neutral with a damped spring.
- Do not make content chase the pointer or wheel so much that it harms reading.

### Lenis With GSAP

```ts
import Lenis from "lenis";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

const lenis = new Lenis({
  duration: 1.0,
  easing: (t) => 1 - Math.pow(1 - t, 3),
  smoothWheel: true,
  wheelMultiplier: 0.9,
  touchMultiplier: 1
});

lenis.on("scroll", ScrollTrigger.update);

gsap.ticker.add((time) => {
  lenis.raf(time * 1000);
});

gsap.ticker.lagSmoothing(0);
```

Disable this setup for reduced motion:

```ts
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
if (reduceMotion) {
  lenis.destroy();
  ScrollTrigger.getAll().forEach((trigger) => trigger.kill());
}
```

## Component Patterns

### Buttons

Default:

- Hover: color/background/border, 100-150 ms, `out-crisp` or `standard`.
- Press: scale `0.98`, 60-100 ms, immediate.
- Release: spring `instant` or `snappy`.
- Loading: preserve label width, add spinner after 150-300 ms delay, keep visible 300-500 ms.

Do:

- Use transform on an inner wrapper if scaling text changes antialiasing.
- Increase contrast on hover/active.
- Keep focus ring stable and visible.

Avoid:

- Big hover lifts on dense product buttons.
- Bouncy buttons in serious tools.
- Motion that changes button size.

### Links

- Use color or underline motion, 100-160 ms.
- Use small arrow translation only on clear call-to-action links.
- Do not animate text tracking or font weight unless already designed for it.

### Menus, Popovers, Tooltips

Enter:

- Opacity 0 to 1.
- Translate 4-8 px from trigger.
- Scale `0.98-1` for larger popovers.
- Duration 120-180 ms.
- Easing `out` or `out-crisp`.
- Transform origin points to the trigger.

Exit:

- Duration 80-140 ms.
- Easing `in`.
- No stagger unless menu is large and content-led.

### Modals

- Overlay fades in 140-220 ms.
- Panel uses translate 8-16 px plus scale `0.97-1`.
- Enter with `smooth` spring or 280-400 ms `out-soft`.
- Exit faster, 140-220 ms.
- Focus moves into modal and returns on close.
- Reduced motion uses instant placement plus short opacity change.

### Drawers And Side Panels

- Use translateX/Y from the physical edge.
- Duration 280-420 ms depending on size.
- Keep overlay separate from panel.
- Use `overscroll-behavior: contain`.
- Preserve scroll position behind the drawer.

### Tabs And Segmented Controls

- Use a shared indicator.
- Indicator uses spring `snappy` or 180-260 ms `bold-move`.
- Content changes use opacity plus 4-8 px directional slide.
- Avoid large content movement for rapid tab switching.

### Cards

- Clickable card hover: translateY `-2px`, scale up to `1.01`, shadow/contrast, 120-180 ms.
- Non-clickable cards should not hover.
- Media cards can use subtle image scale `1.02-1.04`, 400-700 ms, `out-soft`.
- Keep body text still.

### Lists And Reorder

- Use FLIP or layout springs.
- Preserve item identity with stable keys and shared layout ids.
- Insert: opacity plus 8 px y, 160-240 ms.
- Remove: opacity plus 4-8 px y, 120-180 ms.
- Reorder: spring `smooth` or `responsive`.
- Do not animate hundreds of rows; virtualize.

### Toasts

- Enter from edge with 8-16 px translate and opacity.
- Duration 180-260 ms.
- Stack changes use layout spring.
- Exit 120-180 ms.
- Give users enough time to read; motion should not rush content away.

### Forms

- Validation appears near the field.
- Error text reveal: opacity plus small y, 120-180 ms.
- Field border/color: 100-160 ms.
- Avoid dramatic shake. If used, limit to 2-4 px, under 180 ms, and never for routine validation.
- Keep input value stable during async validation.

### Page Transitions

Product apps:

- 180-280 ms.
- Preserve shell; transition content region only.
- Use shared layout for selected item to detail page.
- Keep scroll restoration correct.

Marketing pages:

- 400-700 ms.
- Sequence hero copy, primary media, and CTA.
- Use scroll-triggered continuation after first viewport.
- Do not block navigation until animation completes.

### Loading And Skeletons

- Delay spinner/skeleton by 150-300 ms to avoid flicker.
- Keep loading state visible for 300-500 ms once shown.
- Skeletons match final layout exactly.
- Shimmer: 1200-1800 ms, low contrast, linear.
- Prefer optimistic UI for likely success.

### Drag, Swipe, And Gesture

- While dragging, the object follows the pointer 1:1.
- Use constraints and rubber-banding only when they clarify boundaries.
- On release, preserve velocity and spring to destination.
- Use inertia for flingable surfaces.
- Disable text selection while dragging.
- Keep hover/focus states from fighting drag state.

## The Reward Algorithm

Use this sequence for premium emotional response:

1. Immediate acknowledgement: within 50 ms, show press, highlight, cursor, soundless tactile response, or optimistic state.
2. Continuity: within 80-180 ms, move or morph the object from the source of action to the result.
3. Secondary settle: within 180-420 ms, let surrounding elements adjust with slight delay or spring.
4. Resolution: confirm the result with a small state change, not a celebration every time.
5. Memory: reserve one distinctive motion idea for the product's signature workflow.

Rules:

- Reward should follow user intent, not distract before it.
- Smaller elements move faster; larger elements move slower.
- Elements closer to the user's action move first.
- Related elements share easing but may have different durations.
- Secondary motion should be 20-60 ms behind primary motion.
- Anticipation is subtle in UI: scale `0.98`, translate 2-4 px, or soften opacity before release.
- Follow-through is subtle: spring tail, secondary icon settle, count-up, or content reveal.

## Stack-Agnostic Implementation

### CSS Token Setup

```css
@media (prefers-reduced-motion: reduce) {
  :root {
    --motion-duration-instant: 0ms;
    --motion-duration-press: 0ms;
    --motion-duration-hover: 0ms;
    --motion-duration-micro: 0ms;
    --motion-duration-response: 0ms;
    --motion-duration-reveal: 0ms;
    --motion-duration-standard: 1ms;
    --motion-duration-panel: 1ms;
    --motion-duration-modal: 1ms;
    --motion-duration-page: 1ms;
  }

  *,
  *::before,
  *::after {
    scroll-behavior: auto !important;
  }
}
```

### CSS Button Example

```css
.button {
  transition:
    background-color var(--motion-duration-hover) var(--motion-ease-standard),
    color var(--motion-duration-hover) var(--motion-ease-standard),
    border-color var(--motion-duration-hover) var(--motion-ease-standard),
    transform var(--motion-duration-press) var(--motion-ease-out);
}

.button:hover {
  background-color: var(--button-hover-bg);
}

.button:active {
  transform: scale(var(--motion-scale-press));
}

@media (prefers-reduced-motion: reduce) {
  .button {
    transition-duration: 0ms;
    transform: none;
  }
}
```

### Motion For React Defaults

```tsx
import { MotionConfig } from "motion/react";

const transition = {
  type: "spring",
  visualDuration: 0.42,
  bounce: 0.08
};

export function MotionProvider({ children }: { children: React.ReactNode }) {
  return (
    <MotionConfig reducedMotion="user" transition={transition}>
      {children}
    </MotionConfig>
  );
}
```

### WAAPI Sequence Example

```ts
export function reveal(element: HTMLElement) {
  return element.animate(
    [
      { opacity: 0, transform: "translateY(12px)" },
      { opacity: 1, transform: "translateY(0)" }
    ],
    {
      duration: 280,
      easing: "cubic-bezier(0, 0, 0.2, 1)",
      fill: "both"
    }
  );
}
```

## Agent Workflow

When an AI coding agent uses this file:

1. Audit the current UI and identify existing libraries and motion patterns.
2. Define a motion map for the requested surface:
   - direct controls
   - overlays
   - page/route changes
   - lists/layout changes
   - loading/progress
   - scroll-linked moments
   - reduced-motion behavior
3. Create or extend tokens before adding animations.
4. Implement the smallest reusable primitives needed.
5. Apply patterns component by component.
6. Verify in browser, including reduced motion and mobile viewport.
7. Remove or simplify anything that feels delayed, noisy, or hard to read.

## QA Checklist

- [ ] Every animation has an intent.
- [ ] Motion tokens are centralized.
- [ ] Direct input feedback begins within 50 ms.
- [ ] Repeated product interactions complete within 80-220 ms.
- [ ] Large transitions preserve spatial continuity.
- [ ] Springs preserve gesture velocity where relevant.
- [ ] Reduced-motion mode is implemented and tested.
- [ ] Keyboard focus is visible and managed.
- [ ] No animation uses `transition: all`.
- [ ] No layout properties animate in hot paths.
- [ ] Offscreen animations are paused or avoided.
- [ ] Scroll-linked scenes recalculate on resize and content changes.
- [ ] Smooth scroll is disabled where productivity or accessibility would suffer.
- [ ] Browser performance is acceptable on lower-end devices.

## Source Links

- Apple HIG Motion: https://developer.apple.com/design/human-interface-guidelines/motion
- Apple WWDC23 Animate with springs: https://developer.apple.com/videos/play/wwdc2023/10158/
- Vercel Web Interface Guidelines: https://vercel.com/design/guidelines
- Motion transitions: https://motion.dev/docs/react-transitions
- Lenis repository: https://github.com/darkroomengineering/lenis
- Lenis site: https://www.lenis.dev/
- Carbon motion: https://carbondesignsystem.com/elements/motion/overview/
- Atlassian motion: https://atlassian.design/foundations/motion
- Shopify Polaris motion tokens: https://polaris-react.shopify.com/tokens/motion
- Material 3 easing and duration: https://m3.material.io/styles/motion/easing-and-duration
- Stripe Connect front-end experience: https://stripe.com/blog/connect-front-end-experience
- Linear design refresh: https://linear.app/now/behind-the-latest-design-refresh
