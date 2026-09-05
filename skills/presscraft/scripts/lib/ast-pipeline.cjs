"use strict";

const path = require("path");
const fs = require("fs");
const { getLanguageIcon, getCalloutIcon } = require("./icons.cjs");

// Dynamic resolver for dependencies
function resolveModule(moduleName) {
  const searchPaths = [
    path.resolve(__dirname, "../../node_modules", moduleName),
    path.resolve(__dirname, "../../../../node_modules", moduleName),
    path.resolve("C:/Users/imsov/.gemini/antigravity/brain/da0cf17a-a5f4-42a2-b2cf-beb070443afc/scratch/node_modules", moduleName)
  ];

  for (const p of searchPaths) {
    if (fs.existsSync(p)) {
      return require(p);
    }
  }
  return require(moduleName);
}

const MarkdownIt = resolveModule("markdown-it");
const hljs = resolveModule("highlight.js");

function escapeHtml(str) {
  return String(str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function markPlugin(md) {
  function markRule(state, silent) {
    const start = state.pos;
    const max = state.posMax;

    if (state.src.charCodeAt(start) !== 0x3D || state.src.charCodeAt(start + 1) !== 0x3D) {
      return false;
    }

    // Left flanking: next char cannot be whitespace
    const nextChar = state.src.charCodeAt(start + 2);
    if (nextChar === 0x20 || nextChar === 0x09 || nextChar === 0x0A || nextChar === 0x0D) {
      return false;
    }

    // Scan for closing '==' within the same paragraph/line
    let match = -1;
    let pos = start + 2;
    while (pos < max - 1) {
      const ch = state.src.charCodeAt(pos);
      // Stop if hitting a paragraph break
      if (ch === 0x0A && pos + 1 < max && state.src.charCodeAt(pos + 1) === 0x0A) {
        break;
      }
      if (ch === 0x3D && state.src.charCodeAt(pos + 1) === 0x3D) {
        // Right flanking: preceding char cannot be whitespace
        const prevChar = state.src.charCodeAt(pos - 1);
        if (prevChar !== 0x20 && prevChar !== 0x09 && prevChar !== 0x0A && prevChar !== 0x0D) {
          match = pos;
          break;
        }
      }
      pos++;
    }

    if (match === -1) return false;

    const raw = state.src.slice(start + 2, match);
    if (!raw.trim()) return false;

    if (silent) {
      state.pos = match + 2;
      return true;
    }

    let cls = "highlight";
    let prefixLen = 0;
    const prefixMatch = raw.match(/^(key|definition|warn|tip|note|alert|important|summary|takeaway|insight|example):\s*/i);
    if (prefixMatch) {
      const kind = prefixMatch[1].toLowerCase();
      cls = `highlight highlight-${kind}`;
      prefixLen = prefixMatch[0].length;
    }

    const tokenOpen = state.push("mark_open", "mark", 1);
    tokenOpen.attrs = [["class", cls]];

    const oldMax = state.posMax;
    state.pos = start + 2 + prefixLen;
    state.posMax = match;

    state.md.inline.tokenize(state);

    state.push("mark_close", "mark", -1);

    state.pos = match + 2;
    state.posMax = oldMax;
    return true;
  }
  md.inline.ruler.after("emphasis", "mark", markRule);
}

function calloutPlugin(md) {
  md.core.ruler.after("inline", "callouts", function (state) {
    const tokens = state.tokens;

    // Scan backwards to ensure nested structures are handled cleanly
    for (let i = tokens.length - 1; i >= 0; i--) {
      if (tokens[i].type !== "blockquote_open") continue;

      let depth = 1;
      let closeIdx = -1;
      for (let j = i + 1; j < tokens.length; j++) {
        if (tokens[j].type === "blockquote_open") depth++;
        else if (tokens[j].type === "blockquote_close") {
          depth--;
          if (depth === 0) {
            closeIdx = j;
            break;
          }
        }
      }

      if (closeIdx === -1) continue;

      // Check if first inner token is a paragraph with [!TYPE]
      if (i + 2 < closeIdx && tokens[i + 1].type === "paragraph_open" && tokens[i + 2].type === "inline") {
        const inlineToken = tokens[i + 2];
        const children = inlineToken.children || [];

        if (children.length > 0 && children[0].type === "text") {
          const rawText = children[0].content;
          const match = rawText.match(/^\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION|KEY|DEFINITION|SUMMARY|TAKEAWAY|INSIGHT|EXAMPLE)\](?:\s+([^\n\r]*))?(?:\n|$)/i);

          if (match) {
            const calloutType = match[1].toUpperCase();
            const customTitle = (match[2] || "").trim();
            const displayTitle = customTitle || calloutType;
            const iconSvg = getCalloutIcon(calloutType.toLowerCase());

            const remaining = rawText.slice(match[0].length);
            if (remaining.trim()) {
              children[0].content = remaining;
              inlineToken.content = inlineToken.content.slice(match[0].length);
            } else {
              children.shift();
              if (children.length > 0 && children[0].type === "softbreak") {
                children.shift();
              }
              inlineToken.content = children.map((c) => c.content || "").join("");
            }

            // If the paragraph has no visible content left, remove the paragraph wrapper
            if (children.length === 0 || children.every((c) => !c.content || !c.content.trim())) {
              tokens.splice(i + 1, 3);
              closeIdx -= 3;
            }

            // Replace blockquote_open with callout container
            const openToken = new state.Token("html_block", "", 0);
            openToken.content = `
<div class="callout callout-${calloutType.toLowerCase()}">
  <div class="callout-header">
    <span class="callout-icon">${iconSvg}</span>
    <span class="callout-title">${escapeHtml(displayTitle)}</span>
  </div>
  <div class="callout-content">
`;
            tokens[i] = openToken;

            // Replace matching blockquote_close with callout closing tag
            const closeToken = new state.Token("html_block", "", 0);
            closeToken.content = `
  </div>
</div>
`;
            tokens[closeIdx] = closeToken;
          }
        }
      }
    }
  });
}

function createAstPipeline(options = {}) {
  const showLineNumbers = options.lineNumbers !== false;

  const md = new MarkdownIt({
    html: true,
    xhtmlOut: false,
    breaks: false,
    langPrefix: "language-",
    linkify: true,
    typographer: true
  });

  md.use(markPlugin);
  md.use(calloutPlugin);

  // Intercept fenced code blocks
  md.renderer.rules.fence = function (tokens, idx) {
    const token = tokens[idx];
    const info = token.info ? token.info.trim() : "";
    const lang = info ? info.split(/\s+/)[0] : "text";
    const rawCode = token.content;

    let highlightedHtml = "";
    if (lang && hljs.getLanguage(lang)) {
      try {
        highlightedHtml = hljs.highlight(rawCode, { language: lang, ignoreIllegals: true }).value;
      } catch {
        highlightedHtml = escapeHtml(rawCode);
      }
    } else {
      try {
        highlightedHtml = hljs.highlightAuto(rawCode).value;
      } catch {
        highlightedHtml = escapeHtml(rawCode);
      }
    }

    const lines = highlightedHtml.split("\n");
    if (lines.length > 0 && lines[lines.length - 1] === "") {
      lines.pop();
    }

    const lineCount = lines.length;
    let codeBody = "";

    if (showLineNumbers && lineCount > 1) {
      codeBody = lines
        .map((line, i) => `<span class="line"><span class="line-num">${i + 1}</span><span class="line-content">${line || " "}</span></span>`)
        .join("\n");
    } else {
      codeBody = highlightedHtml;
    }

    const displayLang = (lang || "TEXT").toUpperCase();
    const langIcon = getLanguageIcon(lang);

    return `
<div class="code-window">
  <div class="code-header">
    <div class="window-controls">
      <span class="control close"></span>
      <span class="control minimize"></span>
      <span class="control maximize"></span>
    </div>
    <div class="window-title">
      <span class="code-lang-icon">${langIcon}</span>
      <span class="code-lang-badge">${escapeHtml(displayLang)}</span>
    </div>
    <div class="window-actions">
      <span class="line-count">${lineCount} ${lineCount === 1 ? "line" : "lines"}</span>
    </div>
  </div>
  <pre><code class="hljs language-${escapeHtml(lang)}">${codeBody}</code></pre>
</div>
`;
  };

  // Process Page Breaks and AST Render
  function renderDocument(markdownText) {
    // Standardize page break notations before parsing
    const text = markdownText
      .replace(/<!--\s*(?:pagebreak|newpage)\s*-->/gi, '\n\n<div class="page-break"></div>\n\n')
      .replace(/^\\newpage\b/gm, '\n\n<div class="page-break"></div>\n\n')
      .replace(/^---(?:pagebreak|newpage)---\s*$/gm, '\n\n<div class="page-break"></div>\n\n');

    return md.render(text);
  }

  return {
    md,
    renderDocument
  };
}

module.exports = {
  createAstPipeline
};
