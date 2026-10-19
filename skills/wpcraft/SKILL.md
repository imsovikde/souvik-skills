---
name: wpcraft
description: Flawlessly transform any WordPress site into an agency-grade, motion-engineered web experience using Full Site Editing (FSE) block themes (like Frost) while preserving 100% visual CMS editability in the WordPress Site Editor. Use when asked to deeply customize WordPress without bloat, build or clone artistic websites (like shwn.design) into WordPress, implement WebGL/Canvas physics, SVG gooey morphing navigations, custom theme.json design tokens, dynamic typography switchers, squircle Bento grids, and Web Audio synthesis via WP-CLI and the WordPress REST API.
---

# WPCraft: Agency-Grade WordPress FSE & Motion Engineering Engine

WPCraft equips coding agents and developers to transform any standard WordPress installation into an ultra-premium, agency-grade web application without sacrificing native CMS capabilities. It bridges the gap between high-end creative frontend engineering (WebGL/Canvas physics, SVG filter morphing, squircle Bento grids, Web Audio synthesis) and native WordPress Full Site Editing (FSE) block architecture.

---

## 1. The Inviolable Prime Directive: 100% CMS Preservation

The fatal failure mode of traditional "custom" WordPress development is hardcoding templates into static PHP files that break the WordPress Site Editor (`wp-admin/site-editor.php`), leaving non-technical content editors stranded.

WPCraft enforces the **Sacred Invariant of CMS Preservation**:
1. **Gutenberg-Native Block Grammar**: Every section, component, hero headline, and grid item must be registered or wrapped using standard WordPress block markup (`<!-- wp:group -->`, `<!-- wp:heading -->`, `<!-- wp:paragraph -->`, `<!-- wp:html -->`).
2. **Template Part Decoupling**: Structural chrome lives exclusively in template parts (`parts/header.html`, `parts/footer.html`), while page layout lives in block templates (`templates/home.html`, `templates/index.html`).
3. **Full Site Editor Parity**: A site administrator opening `/wp-admin/site-editor.php` must be able to visually click, type, reorder, and save every textual and structural component without breaking underlying motion or physics scripts.
4. **Theme Safety & Isolation**: When activating an FSE theme (such as `wpengine/frost`), never delete existing client themes (e.g., `astra`). Retain legacy themes in an inactive state to enable instantaneous rollback if required.

---

## 2. Architectural Blueprint: Why Pure FSE Block Themes (Frost)

Traditional WordPress themes load bloated jQuery scripts, render-blocking CSS frameworks, and complex PHP template hierarchies. WPCraft standardizes on lightweight, pure FSE block themes (exemplified by **Frost**):

- **Zero PHP Render Overhead**: Templates are pure HTML files containing Gutenberg block comments. The server outputs raw HTML with sub-50ms Time to First Byte (TTFB).
- **Design Token Purity**: Spacing, fluid typography clamps, and palettes are governed cleanly by `theme.json` and REST-accessible Global Styles.
- **Client-Side Module Independence**: Motion physics and audio engines execute as lightweight, zero-dependency vanilla ES modules, enqueued cleanly without framework bloat.

---

## 3. The 5 Core Engineering Systems

### System 1: Interactive Canvas & WebGL2 Physics
High-craft websites (e.g. `shwn.design`) feature interactive natural physics (sunlit water caustics, ripple wave propagation, fish flocking).
- **Dual-Engine Architecture**: Implement high-performance WebGL2 shader pipelines with half-float texture ping-pong for caustics and wave diffusion, coupled with an automatic 2D Canvas fallback for constrained mobile or software-rendered viewports.
- **Procedural Inverse Kinematics (IK)**: Multi-segment spine joints follow swimming sine oscillation trails, giving organic creatures lifelike swimming dynamics.
- **Interactive Disturbance & Flocking**: Listen for pointer/touch coordinates (`pointermove`, `pointerdown`) to propagate ripple waves and scare boids away with acceleration bursts and tail-flick ripples.

### System 2: Liquid / Gooey SVG Floating Navigations
Create fluid, morphing navigation bars that feel tactile and responsive:
- **SVG Filter Matrix**: Declare `#nav-goo` and `#nav-goo-white` filter definitions in the header:
  ```html
  <filter id="nav-goo" x="-20%" y="-50%" width="140%" height="200%" color-interpolation-filters="sRGB">
    <feGaussianBlur in="SourceAlpha" stdDeviation="10.6" result="blur"/>
    <feColorMatrix in="blur" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 30 -11.5" result="outline"/>
    <feFlood flood-color="#f2f2f2" result="grey"/>
    <feComposite in="grey" in2="outline" operator="in" result="goo"/>
    <feComposite in="SourceGraphic" in2="goo" operator="atop"/>
  </filter>
  ```
- **Backdrop & Sticky Staging**: Stage the navigation with `position: fixed; top: 24px; left: 50%; transform: translateX(-50%); z-index: 9999;`, frosted backdrop blur, and smooth spring sliding indicators.

### System 3: Dynamic In-Page Typography & Micro-Interactions
Equip pages with live interactive design toolbars that change typography and visual depth in real time:
- **Real-Time Font Switcher**: Provide clean dropdown controls allowing users to switch target roles between diverse font families (`Public Sans`, `Caveat`, `Playfair Display`, `Inter`, `Geist`) and depth treatments (`Flat`, `Blue depth`, `Warm depth`, `Spectrum`).
- **Deterministic Micro-Icon Animations**: Animate inline SVG elements on parent hover using isolated keyframes (e.g., `.building-icon` tower stretch & flag flow, `.leaf-icon` hand tap & heart wave, `.heart-icon` dual-beat cardiac pulse).

### System 4: Squircle Bento Prototype Showcase Grids
Showcase product features, portfolio work, or interactive prototypes using Bento grid structures:
- **Continuous Curvature Squircles**: Apply smooth border radii (`border-radius: 28px;`) with continuous curvature fallbacks, subtle borders (`rgba(0,0,0,0.06)`), and tactile paper elevation shadows.
- **Spring-Damper Hover Physics**: Apply Apple-grade spring transforms (`transform: translateY(-6px) scale(1.02); transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);`).
- **Interactive Micro-Mockups**: Embed self-contained miniature interactive widgets (Cassette Walkman with spinning reels, dynamic glass toolbars, 3D folder flaps, sliding wallet cards, retro CRT monitors, rotary dials, command palettes).

### System 5: Pure Web Audio API Sound Synthesizer
Add subtle, tactile audio feedback without loading heavy MP3/WAV assets:
- **Zero-Dependency Synthesis**: Synthesize pleasant user feedback directly via the browser `AudioContext` using oscillators and noise filters.
- **Procedural Sound Bank**:
  - `chime`: Dual sine wave bells with shimmer delay feedback.
  - `sparkle`: Four-stage arpeggiated high chime with high-pass sparkle.
  - `bloom`: Warm detuned 528Hz chords with low-pass resonance.
  - `droplet`: Sine frequency glide (1200Hz -> 550Hz) simulating water drops.
  - `toggle`: Dual bandpass noise bursts simulating physical mechanical clicks.
  - `page`: Soft lowpass paper rustle for navigation events.

---

## 4. Design Tokens & Global Styles Protocol

Never hardcode arbitrary CSS colors into templates. Manage visual tokens through WordPress Global Styles:
1. **Query Existing Styles**: Inspect active tokens via `GET /wp/v2/global-styles/themes/frost` or the custom styles post `GET /wp/v2/global-styles/{id}`.
2. **Inject Design Tokens**: Update the global styles post via `POST /wp/v2/global-styles/{id}`:
   ```json
   {
     "settings": {
       "layout": { "contentSize": "650px", "wideSize": "1200px" },
       "color": {
         "palette": {
           "theme": [
             { "color": "#fbfbfb", "name": "Base", "slug": "base" },
             { "color": "#111111", "name": "Contrast", "slug": "contrast" },
             { "color": "#1a49f5", "name": "Primary", "slug": "primary" }
           ]
         }
       }
     },
     "styles": {
       "color": { "background": "#fbfbfb", "text": "#111111" }
     }
   }
   ```
3. **Verify via WP-CLI**: Execute `wp rest wp_global_styles get <id>` to ensure settings are active.

---

## 5. Deployment Protocol: WP-CLI & Remote REST API

Deploying changes reliably requires deterministic, authenticated REST operations:
1. **Configure Credentials**: Use WordPress core Application Passwords (e.g. user `imsovik` with token).
2. **Deploy Template Parts**:
   - Header: `POST /wp/v2/template-parts/{theme}//header`
   - Footer: `POST /wp/v2/template-parts/{theme}//footer`
3. **Deploy Block Templates**:
   - Home: `POST /wp/v2/templates/{theme}//home`
   - Index (Fallback): `POST /wp/v2/templates/{theme}//index`
4. **Invalidate Server Caches**: Immediately trigger cache purge via host API (e.g. LiteSpeed Cache `wordpress_litespeed-cache_purge-lite-speed`) to ensure frontend visitors receive the new markup without stale HTML delays.

---

## 6. Verification & Quality Rubric

Before presenting work as complete, run the automated verification suite:
```bash
node skills/wpcraft/scripts/audit-wpcraft.cjs <target-url-or-html-file>
```
Verify every item on the checklist:
- [ ] **HTTP 200 OK**: Live home URL responds with valid status.
- [ ] **Block Grammar Integrity**: Gutenberg block comments are unstripped and syntactically balanced.
- [ ] **Site Editor Reachability**: `wp-admin/site-editor.php` loads cleanly (HTTP 200).
- [ ] **Canvas & Physics Presence**: Canvas elements feature explicit ARIA accessibility roles and labels.
- [ ] **SVG Filter Definitions**: Filter matrices (`#nav-goo`) exist in DOM before consumption.
- [ ] **Audio Safety**: Web Audio contexts initialize or resume only after the first user gesture.
- [ ] **Responsive Fluidity**: Viewport scales gracefully from 360px mobile to 1440px desktop with zero horizontal scroll overflow.
- [ ] **Zero AI Slop**: No generic centered purple mesh gradients, no stock marketing clichés, and no broken asset links.
