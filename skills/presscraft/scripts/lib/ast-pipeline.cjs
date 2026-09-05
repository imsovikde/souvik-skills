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
    if (state.src.charCodeAt(start) !== 0x3D || state.src.charCodeAt(start + 1) !== 0x3D) {
      return false;
    }
    if (silent) return false;

    let match = -1;
    let pos = start + 2;
    const max = state.posMax;
    while (pos < max - 1) {
      if (state.src.charCodeAt(pos) === 0x3D && state.src.charCodeAt(pos + 1) === 0x3D) {
        match = pos;
        break;
      }
      pos++;
    }
    if (match === -1) return false;

    const raw = state.src.slice(start + 2, match);
    if (!raw.trim()) return false;

    let cls = "highlight";
    let innerText = raw;
    const prefixMatch = raw.match(/^(key|definition|warn|tip|note|alert|important|summary|takeaway|insight|example):\s*(.*)$/i);
    if (prefixMatch) {
      const kind = prefixMatch[1].toLowerCase();
      cls = `highlight highlight-${kind}`;
      innerText = prefixMatch[2];
    }

    state.pos = match + 2;
    const tokenOpen = state.push("mark_open", "mark", 1);
    tokenOpen.attrs = [["class", cls]];

    const tokenText = state.push("text", "", 0);
    tokenText.content = innerText;

    state.push("mark_close", "mark", -1);
    return true;
  }
  md.inline.ruler.after("emphasis", "mark", markRule);
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

  // Process Callouts / GitHub Alerts & Page Breaks
  function renderDocument(markdownText) {
    // Standardize page break notations before parsing
    let text = markdownText
      .replace(/<!--\s*(?:pagebreak|newpage)\s*-->/gi, '\n\n<div class="page-break"></div>\n\n')
      .replace(/^\\newpage\b/gm, '\n\n<div class="page-break"></div>\n\n')
      .replace(/^---(?:pagebreak|newpage)---\s*$/gm, '\n\n<div class="page-break"></div>\n\n');

    let html = md.render(text);

    // Transform blockquotes with [!NOTE], [!TIP], [!IMPORTANT], [!WARNING], [!CAUTION], [!KEY], [!DEFINITION], etc.
    const calloutRegex = /<blockquote>\s*<p>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION|KEY|DEFINITION|SUMMARY|TAKEAWAY|INSIGHT|EXAMPLE)\](?:\s*<br\s*\/?>)?([\s\S]*?)<\/blockquote>/gi;

    html = html.replace(calloutRegex, (match, type, content) => {
      const calloutType = type.toUpperCase();
      const iconSvg = getCalloutIcon(calloutType.toLowerCase());
      let cleanedContent = content.trim();

      if (cleanedContent && !cleanedContent.startsWith("<p>") && !cleanedContent.startsWith("<div>") && !cleanedContent.startsWith("<ul>") && !cleanedContent.startsWith("<ol>")) {
        cleanedContent = `<p>${cleanedContent}`;
      }
      if (cleanedContent && !cleanedContent.endsWith("</p>") && !cleanedContent.endsWith("</div>") && !cleanedContent.endsWith("</ul>") && !cleanedContent.endsWith("</ol>")) {
        cleanedContent = `${cleanedContent}</p>`;
      }

      return `
<div class="callout callout-${calloutType.toLowerCase()}">
  <div class="callout-header">
    <span class="callout-icon">${iconSvg}</span>
    <span class="callout-title">${calloutType}</span>
  </div>
  <div class="callout-content">
    ${cleanedContent}
  </div>
</div>`;
    });

    return html;
  }

  return {
    md,
    renderDocument
  };
}

module.exports = {
  createAstPipeline
};
