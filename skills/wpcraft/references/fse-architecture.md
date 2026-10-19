# WordPress Full Site Editing (FSE) Architectural Reference

This reference details the technical structure, block markup rules, and global styles protocols governing Full Site Editing in WordPress 6.x+.

---

## 1. Directory Structure of an FSE Block Theme

A pure block theme (such as Frost) eliminates legacy PHP template files in favor of structured HTML block markup:

```text
wp-content/themes/frost/
├── theme.json               # Canonical design token and block style definitions
├── functions.php            # Minimal theme setup and script enqueuing
├── style.css                # Theme metadata header (name, version, author)
├── templates/               # Top-level full page block templates
│   ├── index.html           # Universal fallback template
│   ├── home.html            # Front page / blog homepage template
│   ├── single.html          # Individual post template
│   ├── page.html            # Static page template
│   ├── 404.html             # Error page template
│   └── archive.html         # Taxonomy & category archive template
└── parts/                   # Reusable structural components (Template Parts)
    ├── header.html          # Global header / navigation
    ├── footer.html          # Global footer / credits
    └── comments.html        # Comment list and reply form
```

---

## 2. Block Markup Specification

Block templates are standard HTML files annotated with Gutenberg comment delimiters. WordPress parses these delimiters into an Abstract Syntax Tree (AST) at render time.

### Block Comment Grammar
```html
<!-- Self-closing block with JSON attributes -->
<!-- wp:site-title {"level":1,"isLink":true} /-->

<!-- Block with inner content -->
<!-- wp:group {"layout":{"type":"constrained"}} -->
<div class="wp-block-group">
  <!-- Inner blocks -->
</div>
<!-- /wp:group -->

<!-- Template Part Reference -->
<!-- wp:template-part {"slug":"header","tagName":"header","className":"site-header","theme":"frost"} /-->

<!-- Unfiltered Custom HTML Block -->
<!-- wp:html -->
<section class="custom-canvas-section">
  <canvas id="interactive-pond"></canvas>
</section>
<!-- /wp:html -->
```

### Critical Gutenberg Invariants
1. **Attribute Encodings**: Attributes inside block comments must be valid, unescaped JSON. A syntax error inside `<!-- wp:block {...} -->` causes Gutenberg to flag the block as invalid or corrupted.
2. **Tag Matching**: Every opening block comment `<!-- wp:name -->` must have an exact matching closing comment `<!-- /wp:name -->`, wrapping an HTML container with matching classes (e.g. `class="wp-block-name"`).
3. **Template Part Slugs**: When including a template part, the `slug` attribute must match the filename in `parts/<slug>.html` (without the `.html` extension), and `theme` must specify the theme stylesheet identifier.

---

## 3. Global Styles & `theme.json` Schema v3

Global Styles allow setting design tokens, layout dimensions, and typography clamps that WordPress compiles into native CSS custom properties (`--wp--preset--*`).

### Key Schema Sections
```json
{
  "$schema": "https://schemas.wp.org/trunk/theme.json",
  "version": 3,
  "settings": {
    "layout": {
      "contentSize": "650px",
      "wideSize": "1200px"
    },
    "typography": {
      "fluid": true,
      "fontFamilies": [
        {
          "fontFamily": "'Public Sans', sans-serif",
          "name": "Public Sans",
          "slug": "public-sans"
        },
        {
          "fontFamily": "'Caveat', cursive",
          "name": "Caveat",
          "slug": "caveat"
        }
      ]
    },
    "color": {
      "palette": [
        { "color": "#fbfbfb", "name": "Base", "slug": "base" },
        { "color": "#111111", "name": "Contrast", "slug": "contrast" },
        { "color": "#1a49f5", "name": "Primary", "slug": "primary" }
      ]
    }
  },
  "styles": {
    "color": {
      "background": "var(--wp--preset--color--base)",
      "text": "var(--wp--preset--color--contrast)"
    }
  }
}
```

---

## 4. REST API Endpoints for FSE Operations

WordPress exposes full REST endpoints to inspect, create, and update templates and template parts programmatically:

| Operation | REST Endpoint | Allowed Methods |
| :--- | :--- | :--- |
| List Templates | `/wp/v2/templates` | `GET` |
| Get Template | `/wp/v2/templates/{theme}//{slug}` | `GET` |
| Update Template | `/wp/v2/templates/{theme}//{slug}` | `POST`, `PUT` |
| List Template Parts | `/wp/v2/template-parts` | `GET` |
| Get Template Part | `/wp/v2/template-parts/{theme}//{slug}` | `GET` |
| Update Template Part | `/wp/v2/template-parts/{theme}//{slug}` | `POST`, `PUT` |
| Theme Styles | `/wp/v2/global-styles/themes/{theme}` | `GET` |
| Custom Global Styles | `/wp/v2/global-styles/{id}` | `GET`, `POST` |
