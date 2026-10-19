# WPCraft Composable Gutenberg Block Patterns Reference

This reference provides production-ready, validated Gutenberg block recipes for every section of a website. Each pattern preserves 100% Full Site Editing (FSE) visual parity in `wp-admin/site-editor.php` while supporting agency-grade motion and styling.

---

## Pattern 1: High-Craft Editorial Hero Section

A clean, typography-led hero with fluid clamp sizing, subtitle, and action buttons.

```html
<!-- wp:group {"align":"full","style":{"spacing":{"padding":{"top":"clamp(3rem, 8vw, 6rem)","bottom":"clamp(3rem, 8vw, 6rem)","left":"24px","right":"24px"}}},"layout":{"type":"constrained","contentSize":"680px"}} -->
<div class="wp-block-group alignfull" style="padding-top:clamp(3rem, 8vw, 6rem);padding-right:24px;padding-bottom:clamp(3rem, 8vw, 6rem);padding-left:24px">
  <!-- wp:heading {"level":1,"className":"wpcraft-target-heading","style":{"typography":{"fontSize":"clamp(2.5rem, 5vw, 4.25rem)","lineHeight":"1.08","letterSpacing":"-0.03em"}}} -->
  <h1 class="wp-block-heading wpcraft-target-heading" style="font-size:clamp(2.5rem, 5vw, 4.25rem);line-height:1.08;letter-spacing:-0.03em">Design engineer exploring tactile web interfaces.</h1>
  <!-- /wp:heading -->

  <!-- wp:paragraph {"style":{"typography":{"fontSize":"1.25rem","lineHeight":"1.6"},"spacing":{"margin":{"top":"1.5rem","bottom":"2rem"}}}} -->
  <p class="has-medium-font-size" style="margin-top:1.5rem;margin-bottom:2rem;font-size:1.25rem;line-height:1.6">Crafting digital products, procedural canvas physics, and zero-bloat Full Site Editing experiences. Every element is customizable directly in the WordPress Site Editor.</p>
  <!-- /wp:paragraph -->

  <!-- wp:buttons {"layout":{"type":"flex","justifyContent":"left"}} -->
  <div class="wp-block-buttons">
    <!-- wp:button {"className":"wpcraft-sound-btn","style":{"border":{"radius":"9999px"}}} -->
    <div class="wp-block-button wpcraft-sound-btn"><a class="wp-block-button__link wp-element-button" href="#work" style="border-radius:9999px">Explore Work</a></div>
    <!-- /wp:button -->
    <!-- wp:button {"className":"is-style-outline wpcraft-sound-btn","style":{"border":{"radius":"9999px"}}} -->
    <div class="wp-block-button is-style-outline wpcraft-sound-btn"><a class="wp-block-button__link wp-element-button" href="mailto:contact@domain.com" style="border-radius:9999px">Get in Touch</a></div>
    <!-- /wp:button -->
  </div>
  <!-- /wp:buttons -->
</div>
<!-- /wp:group -->
```

---

## Pattern 2: Interactive Canvas Physics Island

Isolated 2D/WebGL2 canvas container with keyboard/screen-reader accessible fallback.

```html
<!-- wp:group {"align":"wide","style":{"spacing":{"margin":{"top":"0","bottom":"48px"}}},"layout":{"type":"constrained","wideSize":"1200px"}} -->
<div class="wp-block-group alignwide" style="margin-top:0;margin-bottom:48px">
  <!-- wp:html -->
  <section class="wpcraft-canvas-section" aria-label="Interactive Water Ripple and Physics Simulation" role="region">
    <canvas id="wpcraft-pond-canvas" width="1200" height="380" aria-label="Interactive koi simulation that reacts to touch and pointer movement" role="img"></canvas>
  </section>
  <!-- /wp:html -->
</div>
<!-- /wp:group -->
```

---

## Pattern 3: Dynamic Typography & Depth Switcher Toolbar

In-page live customization toolbar enabling real-time font switching and depth styling.

```html
<!-- wp:html -->
<div class="wpcraft-toolbar-wrapper" data-wpcraft-toolbar aria-label="Design Settings Toolbar">
  <div class="wpcraft-toolbar-group">
    <label for="wpcraft-font-select">Typography:</label>
    <select id="wpcraft-font-select" data-wpcraft-font-select>
      <option value="inherit">Default (System / Sans)</option>
      <option value="'Playfair Display', serif">Playfair Display (Editorial Serif)</option>
      <option value="'Caveat', cursive">Caveat (Organic Handwriting)</option>
      <option value="'Geist', sans-serif">Geist (Modern Monospace / Tech)</option>
      <option value="'Inter', sans-serif">Inter (Clean Neutral)</option>
    </select>
  </div>
  <div class="wpcraft-toolbar-group">
    <span>Surface Depth:</span>
    <button type="button" class="wpcraft-sound-btn is-active" data-wpcraft-depth="flat" data-sound="toggle">Flat</button>
    <button type="button" class="wpcraft-sound-btn" data-wpcraft-depth="blue" data-sound="bloom">Blue Depth</button>
    <button type="button" class="wpcraft-sound-btn" data-wpcraft-depth="warm" data-sound="sparkle">Warm Depth</button>
  </div>
</div>
<!-- /wp:html -->
```

---

## Pattern 4: Squircle Bento Showcase Grid (12-Column Responsive)

Responsive Bento grid layout featuring 8-col and 4-col card pairings with Apple-grade spring physics.

```html
<!-- wp:group {"align":"wide","className":"wpcraft-bento-section","layout":{"type":"default"}} -->
<div class="wp-block-group alignwide wpcraft-bento-section">
  <div class="wpcraft-bento-grid">
    <!-- Bento Card: 8 Columns -->
    <div class="wpcraft-bento-card wpcraft-col-8" data-sound="sparkle">
      <div class="wpcraft-card-content">
        <span class="wpcraft-badge">Featured Case Study</span>
        <h3>Fluid Physics &amp; WebGL Shaders</h3>
        <p>Interactive caustics simulation with half-float texture ping-pong buffers and procedural inverse kinematics.</p>
      </div>
      <div class="wpcraft-card-footer">
        <a href="#" class="wpcraft-card-link">View Prototype &rarr;</a>
      </div>
    </div>

    <!-- Bento Card: 4 Columns -->
    <div class="wpcraft-bento-card wpcraft-col-4" data-sound="chime">
      <div class="wpcraft-card-content">
        <span class="wpcraft-badge">SVG Matrix</span>
        <h3>Gooey NavPill</h3>
        <p>Liquid organic morphing navigation dock using SVG Gaussian blur and alpha clipping.</p>
      </div>
      <div class="wpcraft-card-footer">
        <a href="#" class="wpcraft-card-link">Inspect Code &rarr;</a>
      </div>
    </div>

    <!-- Bento Card: 6 Columns -->
    <div class="wpcraft-bento-card wpcraft-col-6" data-sound="bloom">
      <div class="wpcraft-card-content">
        <span class="wpcraft-badge">Audio Synthesizer</span>
        <h3>Zero-Asset Web Audio API</h3>
        <p>Mathematical harmonic bell synthesis and droplet frequency glides without external MP3 assets.</p>
      </div>
    </div>

    <!-- Bento Card: 6 Columns -->
    <div class="wpcraft-bento-card wpcraft-col-6" data-sound="droplet">
      <div class="wpcraft-card-content">
        <span class="wpcraft-badge">Architecture</span>
        <h3>100% FSE Parity</h3>
        <p>Fully editable via wp-admin/site-editor.php. Zero hardcoded static PHP files.</p>
      </div>
    </div>
  </div>
</div>
<!-- /wp:group -->
```

---

## Pattern 5: Liquid Floating Gooey Navigation Dock (Header Part)

Placed inside `parts/header.html` or deployed to `frost//header`.

```html
<!-- wp:html -->
<div class="wpcraft-nav-container" role="navigation" aria-label="Main Floating Navigation">
  <a href="#top" class="wpcraft-nav-link is-active" data-sound="toggle">Home</a>
  <a href="#work" class="wpcraft-nav-link" data-sound="toggle">Work</a>
  <a href="#experiments" class="wpcraft-nav-link" data-sound="toggle">Experiments</a>
  <a href="#writing" class="wpcraft-nav-link" data-sound="toggle">Writing</a>
  <a href="#about" class="wpcraft-nav-link" data-sound="toggle">About</a>
</div>

<svg style="position: absolute; width: 0; height: 0; pointer-events: none;" aria-hidden="true">
  <defs>
    <filter id="nav-goo" x="-20%" y="-50%" width="140%" height="200%" color-interpolation-filters="sRGB">
      <feGaussianBlur in="SourceAlpha" stdDeviation="10.6" result="blur" />
      <feColorMatrix in="blur" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 30 -11.5" result="outline" />
      <feFlood flood-color="#f2f2f2" result="grey" />
      <feComposite in="grey" in2="outline" operator="in" result="goo" />
      <feComposite in="SourceGraphic" in2="goo" operator="atop" />
    </filter>
  </defs>
</svg>
<!-- /wp:html -->
```

---

## Pattern 6: Editorial Minimalist Signoff & Timezone Footer

Placed inside `parts/footer.html` or deployed to `frost//footer`.

```html
<!-- wp:group {"align":"full","style":{"spacing":{"padding":{"top":"48px","bottom":"48px","left":"24px","right":"24px"}}},"layout":{"type":"constrained","contentSize":"680px"}} -->
<div class="wp-block-group alignfull" style="padding-top:48px;padding-right:24px;padding-bottom:48px;padding-left:24px">
  <!-- wp:html -->
  <footer class="wpcraft-editorial-footer">
    <div class="wpcraft-footer-inner">
      <p class="wpcraft-footer-signoff">peace out</p>
      <div class="wpcraft-footer-status">
        <span class="wpcraft-status-dot" aria-hidden="true"></span>
        <span class="wpcraft-status-text">Available for select client collaborations</span>
      </div>
    </div>
  </footer>
  <!-- /wp:html -->
</div>
<!-- /wp:group -->
```
