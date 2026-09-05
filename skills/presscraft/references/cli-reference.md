# Presscraft CLI Reference & Usage Guide

## Command Signature

```bash
node skills/presscraft/scripts/presscraft.cjs --input <path> --output <path.pdf> [options]
```

## Options Matrix

### `--input, -i <path>` (Required)
Path to the input document. Supported extensions:
- `.md`, `.markdown`: Parsed via CommonMark with code fence interception and GitHub alert styling.
- `.html`, `.htm`: Processed directly through the theme styling pipeline.
- `.py`, `.js`, `.ts`, `.json`, `.sql`, `.sh`, `.css`, etc.: Wrapped inside a macOS syntax-highlighted code window.
- `.txt`: Formatted as clean paragraphs.

### `--output, -o <path>` (Optional)
Path for the rendered PDF file. Defaults to `<input-basename>.pdf` in the current working directory.

### `--theme, -t <theme-name|file-path>` (Optional, Default: `minimalist`)
Select one of the built-in themes or supply a path to a custom CSS file:
- `storybook`: Warm ivory parchment, Garamond serif typography, fleurons, and drop-caps.
- `minimalist`: Swiss clean typographic styling, Inter sans-serif, crisp borders.
- `executive`: Modern enterprise whitepaper, royal blue accents, geometric sans.
- `academic`: Scientific computer science journal, justified columns, formal rules.
- `cyberpunk`: Dark-mode terminal, neon cyan and emerald accents, luminous borders.
- `/path/to/theme.css`: Custom theme stylesheet.

### `--format, -f <format>` (Optional, Default: `A4`)
Specifies the paper dimensions: `A4`, `Letter`, `Legal`, `A3`, `A5`.

### `--landscape` (Optional, Default: `false`)
Renders the document in landscape orientation.

### `--margin, -m <margin>` (Optional, Default: `15mm`)
Sets uniform margins (e.g. `15mm`, `20mm`, `1in`, `0.75in`).

### `--title <string>` (Optional)
Explicit title override. If omitted, Presscraft automatically parses the first `# Heading` in the markdown file.

### `--author <string>` (Optional)
Specifies the document author. Displayed on the cover page and in running footers.

### `--cover` (Optional, Default: `false`)
Generates an elegant cover page with title, subtitle, author, divider, and publication date.

### `--css <rules>` (Optional)
Arbitrary inline CSS overrides for prompt-driven custom styling.

### `--no-line-numbers` (Optional)
Disables line numbering inside macOS code windows.

### `--no-header-footer` (Optional)
Suppresses running headers and footers with dynamic page numbers.

### `--wait <ms>` (Optional, Default: `600`)
Additional millisecond wait time before PDF rasterization to allow remote web fonts to settle.
