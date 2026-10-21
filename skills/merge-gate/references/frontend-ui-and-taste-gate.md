# Frontend UI and Taste Gate Reference

This reference establishes the zero-tolerance frontend, UI, responsive layout, accessibility, and anti-slop pre-merge checklist. It absorbs the core visual invariants of `tasteskill.dev` (`design-taste-frontend`) and modern web standards.

## 1. Responsive Geometry: 320px to 1440px Viewport Integrity

Every user interface merged into `main` must function without layout breakage from narrow mobile devices (320px) to wide desktop viewports (1440px+).

### 1.1 The Horizontal Overflow Ban
- Horizontal scrolling on the page root (`body` or `html`) is a critical defect.
- Band-aid solutions (`overflow-x: hidden` on `body`) that mask overflowing elements instead of fixing container geometry are strictly prohibited.
- Check fixed-width elements: flag any `w-[360px]`, `w-[400px]`, or `min-w-[400px]` that exceeds the 320px mobile viewport without a responsive prefix (`sm:`, `md:`).
- Verify long strings: confirm text containers apply `break-words` or `overflow-wrap: anywhere` on user-generated content, hashes, URLs, and filenames.

### 1.2 Viewport Units and Modern Height Discipline
- The legacy unit `h-screen` (100vh) is prohibited on mobile layouts because mobile browser address bars cause viewport recalculation jitter and vertical content clipping.
- Use dynamic viewport units: `min-h-dvh` or `h-dvh` (100dvh) for full-screen hero sections and application shells.

## 2. Interactive UI State Completeness

Every interactive component, data-fetching view, and form submission surface must implement all seven fundamental UI states:

| UI State | Required Behavior | Banned Anti-Pattern |
| :--- | :--- | :--- |
| **1. Loading** | Skeleton screens, progress spinners, or disabled buttons with loading indicators | Freezing the UI or leaving a blank white screen during network operations |
| **2. Empty** | Meaningful empty state graphic or illustration with an actionable next step or CTA | Blank containers or confusing "No data found" text without guidance |
| **3. Error** | Human-readable error message explaining what failed, with a retry button | Silently failing, showing raw exception stack traces, or console-only logs |
| **4. Disabled** | Visual opacity reduction, `cursor-not-allowed`, and `aria-disabled="true"` | Allowing clicks that trigger silent rejections or duplicate submissions |
| **5. Hover** | Subtle background, border, or elevation transitions on pointer devices | Heavy layout shifts or hovering effects that trap touch users on mobile |
| **6. Focus-Visible** | High-contrast focus rings (`focus-visible:ring-2 focus-visible:outline-none`) | Stripping focus outlines (`outline: none`) without replacement rings |
| **7. Active** | Pressed state feedback (e.g. `active:scale-[0.98]`) | Zero tactile feedback when buttons or interactive rows are tapped |

## 3. React Hook, State, and Hydration Discipline

### 3.1 Stale Closures and Hook Dependency Arrays
- Every variable, prop, and state reference read inside `useEffect`, `useCallback`, and `useMemo` must be declared in the dependency array.
- Disabling the linter with `// eslint-disable-next-line react-hooks/exhaustive-deps` without an explicit architectural justification is flagged as `P1 CRITICAL`.
- Check event handlers and async callbacks for stale closures where state is read after an `await` without using a functional state updater (`setState(prev => ...)`).

### 3.2 SSR Hydration Hygiene
- Client-side-only browser primitives (`window`, `document`, `localStorage`, `navigator.userAgent`) must never be read directly in the render phase of server-rendered components.
- Banned hack: Using `suppressHydrationWarning` on root divs to silence hydration errors caused by mismatched timestamps, random IDs, or client-rendered dates.

## 4. Strictly Banned Frontend APIs and Patterns

| Banned API / Pattern | Severity | Production Risk | Modern Replacement |
| :--- | :--- | :--- | :--- |
| `alert(`, `confirm(`, `prompt(` | P0 BLOCKER | Blocks browser event loop, crashes headless tests, looks unprofessional | Design-system modal dialog or inline confirm popover |
| `dangerouslySetInnerHTML` | P0 BLOCKER | Direct XSS vulnerability if rendering un-sanitized user strings | DOMPurify sanitization or structured markdown parser |
| `window.addEventListener('scroll')` | P1 CRITICAL | Runs on every frame, creates scroll jank and high CPU consumption | `IntersectionObserver`, CSS scroll-driven animations, or `useScroll()` |
| Hardcoded pure black `#000000` | P2 MAJOR | Harsh visual contrast against white backdrops; violates design harmony | Use dark neutrals like `#09090b` (zinc-950) or theme tokens |
| Missing reduced-motion media query | P2 MAJOR | Vestibular motion triggers for sensitive users | `@media (prefers-reduced-motion: reduce)` or `motion-reduce:` |

## 5. Web Accessibility (WCAG AA) and Design Token Parity

### 5.1 Contrast Ratios
- Normal body text (under 18px / 14pt bold) must maintain a minimum contrast ratio of `4.5:1` against its background.
- Large text (18px+ or 14pt+ bold) and interactive UI components (buttons, input borders) must maintain a minimum contrast ratio of `3:1`.
- Ghost buttons and transparent pills over photography must include a background scrim, stroke, or backdrop blur (`backdrop-blur-md`).

### 5.2 Reduced Motion Discipline
Every CSS transition, CSS keyframe animation, and GSAP/Motion timeline must respect user accessibility settings:

```css
@media (prefers-reduced-motion: reduce) {
  *, ::before, ::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

## 6. Anti-Slop Visual Rules (from tasteskill.dev)

1. **Zero Decorative Status Dots:** A colored circle or pulsing green dot before every list item, nav link, or badge is banned. Use dots only when indicating real server or connection health.
2. **Zero Fake Div Screenshots:** Simulated application screenshots built from nested `<div>` rectangles with fake task rows or mock terminals are banned. Use real imagery or real functional components.
3. **Zero Display Serif Defaults:** Reaching automatically for `Fraunces` or `Instrument_Serif` on every landing page is an LLM design tell. Select typefaces that match the specific domain.
4. **Zero Version Hero Eyebrows:** Eyebrows like `v2.0 RELEASE`, `BETA`, or `INVITE-ONLY` are banned unless the PR specifically implements a product preview announcement.
5. **Zero Em-Dashes in UI Copy:** The em-dash is completely banned in UI copy, buttons, headlines, and tooltips. Use periods, colons, or standard hyphens.
