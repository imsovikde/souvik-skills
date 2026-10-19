# WP-CLI & WordPress REST API Automation Reference

This reference documents the deterministic commands, REST endpoints, and authentication protocols used by WPCraft to automate theme customization, template deployment, and cache invalidation.

---

## 1. Authentication & Security Protocols

Automated interactions with WordPress require authenticated credentials with administrative capabilities.

### Application Passwords (Recommended)
WordPress Core (5.6+) supports Application Passwords, which allow API access without exposing the user's primary account password.
1. Generate an Application Password via WordPress Admin (`Users -> Profile -> Application Passwords`) or via WP-CLI:
   ```bash
   wp user application-password create <user-id> "wpcraft-deploy"
   ```
2. Pass credentials using HTTP Basic Auth:
   ```bash
   # Base64 encoded user:app_password
   AUTH_HEADER="Authorization: Basic $(echo -n 'imsovik:xxxx xxxx xxxx xxxx' | base64)"
   ```

---

## 2. Template Parts API (`/wp/v2/template-parts`)

Template parts are reusable structural components stored in the database or filesystem under `parts/`.

### Querying Template Parts
```bash
# List all template parts for active theme
curl -s -H "$AUTH_HEADER" \
  "https://imsovikde.me/wp-json/wp/v2/template-parts?theme=frost"

# Get specific template part (e.g., frost//header)
curl -s -H "$AUTH_HEADER" \
  "https://imsovikde.me/wp-json/wp/v2/template-parts/frost//header"
```

### Updating or Creating a Template Part
To update a template part, send a `POST` request with the new block content:
```bash
curl -s -X POST -H "$AUTH_HEADER" -H "Content-Type: application/json" \
  -d '{
    "slug": "header",
    "theme": "frost",
    "title": "Header (WPCraft Liquid Nav)",
    "content": "<!-- wp:html -->\n<div class=\"wpcraft-nav-wrapper\">...</div>\n<!-- /wp:html -->"
  }' \
  "https://imsovikde.me/wp-json/wp/v2/template-parts/frost//header"
```

---

## 3. Block Templates API (`/wp/v2/templates`)

Templates govern full page layouts (`templates/home.html`, `templates/index.html`).

### Querying Templates
```bash
# Inspect the active home template
curl -s -H "$AUTH_HEADER" \
  "https://imsovikde.me/wp-json/wp/v2/templates/frost//home"
```

### Updating or Creating a Block Template
Deploying a full page layout:
```bash
curl -s -X POST -H "$AUTH_HEADER" -H "Content-Type: application/json" \
  -d '{
    "slug": "home",
    "theme": "frost",
    "title": "Home",
    "content": "<!-- wp:template-part {\"slug\":\"header\",\"theme\":\"frost\"} /-->\n<!-- wp:group {\"layout\":{\"type\":\"constrained\"}} -->\n<main class=\"wp-block-group\">...</main>\n<!-- /wp:group -->\n<!-- wp:template-part {\"slug\":\"footer\",\"theme\":\"frost\"} /-->"
  }' \
  "https://imsovikde.me/wp-json/wp/v2/templates/frost//home"
```

---

## 4. Global Styles & Design Tokens API (`/wp/v2/global-styles`)

WordPress manages user-defined styles and design tokens (from `theme.json`) in the `wp_global_styles` post type.

### Inspecting Global Styles
```bash
# Locate active user style customization ID
curl -s -H "$AUTH_HEADER" \
  "https://imsovikde.me/wp-json/wp/v2/global-styles"
```

### Mutating Global Styles
Update typography scales, palettes, and layout constraints:
```bash
curl -s -X POST -H "$AUTH_HEADER" -H "Content-Type: application/json" \
  -d '{
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
  }' \
  "https://imsovikde.me/wp-json/wp/v2/global-styles/<id>"
```

---

## 5. WP-CLI Command Equivalent Matrix

When local SSH or WP-CLI is available on the host machine:

| Operation | WP-CLI Command |
| :--- | :--- |
| **Verify Active Theme** | `wp theme list --status=active` |
| **Install & Activate Frost** | `wp theme install frost --activate` |
| **Get Template Part** | `wp post list --post_type=wp_template_part` |
| **List Global Styles** | `wp post list --post_type=wp_global_styles` |
| **Purge Object Cache** | `wp cache flush` |
| **Purge Rewrite Rules** | `wp rewrite flush` |

---

## 6. Cache Invalidation & Edge CDN Purge

Deployments to production environments with aggressive caching (e.g. LiteSpeed Cache, Cloudflare, Fastly) must invalidate stale HTML immediately.

### LiteSpeed Cache Invalidation
1. **Via LiteSpeed REST / Action**:
   Trigger the purge hook or clear the litespeed cache option:
   ```bash
   wp litespeed-purge all
   ```
2. **Via HTTP Purge Header**:
   ```bash
   curl -s -X PURGE "https://imsovikde.me/*"
   ```
3. **Verification**:
   Inspect response headers:
   ```bash
   curl -I "https://imsovikde.me/" | grep -E "x-litespeed-cache|cf-cache-status"
   ```
   Ensure `x-litespeed-cache: miss` on immediate subsequent query, confirming cache invalidation.
