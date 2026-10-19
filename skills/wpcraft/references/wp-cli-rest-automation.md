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

## 6. Section-by-Section Surgical Mutation Protocol

To transform a specific section (e.g. only the hero, only the footer, or only a bento grid) without overwriting the rest of the template:

1. **Fetch Existing Template Content**:
   ```bash
   TEMPLATE_JSON=$(curl -s -H "$AUTH_HEADER" "https://imsovikde.me/wp-json/wp/v2/templates/{theme}//home")
   CONTENT=$(echo "$TEMPLATE_JSON" | jq -r '.content.raw')
   ```
2. **Surgically Replace Target Block**:
   Locate the specific Gutenberg block comment boundary (e.g., `<!-- wp:group {"metadata":{"name":"Hero"}} -->...<!-- /wp:group -->`) and replace only that section with the new composable pattern.
3. **Deploy Updated Template**:
   ```bash
   curl -s -X POST -H "$AUTH_HEADER" -H "Content-Type: application/json" \
     -d "{\"content\": $(echo "$NEW_CONTENT" | jq -sR .)}" \
     "https://imsovikde.me/wp-json/wp/v2/templates/{theme}//home"
   ```

---

## 7. Instant Factory Reversion & Rollback Protocol

When reverting customized templates or template parts back to the theme's original factory files:

1. **Delete Custom Template Overrides**:
   Sending a `DELETE` request with `force=true` deletes the user's custom `wp_template` database post, causing WordPress to immediately fall back to the pristine theme file (`source: theme`):
   ```bash
   # Revert Home & Index templates
   curl -s -X DELETE -H "$AUTH_HEADER" \
     "https://imsovikde.me/wp-json/wp/v2/templates/frost//home?force=true"

   curl -s -X DELETE -H "$AUTH_HEADER" \
     "https://imsovikde.me/wp-json/wp/v2/templates/frost//index?force=true"
   ```

2. **Delete Custom Template Part Overrides**:
   ```bash
   # Revert Header & Footer template parts
   curl -s -X DELETE -H "$AUTH_HEADER" \
     "https://imsovikde.me/wp-json/wp/v2/template-parts/frost//header?force=true"

   curl -s -X DELETE -H "$AUTH_HEADER" \
     "https://imsovikde.me/wp-json/wp/v2/template-parts/frost//footer?force=true"
   ```

3. **Reset User Global Styles**:
   Reset `settings` and `styles` to empty objects `{}` to clear custom token overrides:
   ```bash
   curl -s -X POST -H "$AUTH_HEADER" -H "Content-Type: application/json" \
     -d '{"settings": {}, "styles": {}}' \
     "https://imsovikde.me/wp-json/wp/v2/global-styles/<id>"
   ```

4. **Verify Clean Theme Fallback**:
   Query the REST endpoints and confirm `"source": "theme"` on all items.

---

## 8. Cache Invalidation & Edge CDN Purge

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
