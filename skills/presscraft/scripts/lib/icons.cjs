"use strict";

const ICONS = {
  // Callouts
  note: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>`,
  tip: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-7 7c0 2.38 1.19 4.47 3 5.74V17a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1v-2.26c1.81-1.27 3-3.36 3-5.74a7 7 0 0 0-7-7z"/></svg>`,
  important: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>`,
  warning: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
  caution: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`,
  key: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 2l-2 2m-1.5 1.5L14 9l-1.5-1.5L11 9l-1.5-1.5L8 9c-3.3 0-6 2.7-6 6s2.7 6 6 6 6-2.7 6-6c0-.9-.2-1.7-.5-2.5L21 4V2h-2z"/><circle cx="8" cy="15" r="2"/></svg>`,
  summary: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>`,
  insight: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a7 7 0 0 1 7 7c0 2.38-1.19 4.47-3 5.74V17a1 1 0 0 1-1 1H9a1 1 0 0 1-1-1v-2.26C6.19 13.47 5 11.38 5 9a7 7 0 0 1 7-7z"/><path d="M10 21h4"/></svg>`,
  example: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>`,

  // Programming Languages
  python: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M11.9 1.5c-3.1 0-5 1.7-5 4v2.7h5.1V9H4.6C2.3 9 1 10.8 1 13.5c0 2.9 1.7 4.5 4.5 4.5h2.1v-2.7c0-2.3 1.9-4.2 4.3-4.2h5.1V9c0-2.3-1.9-7.5-5.1-7.5zm-1.8 2.2a1 1 0 1 1 0 2 1 1 0 0 1 0-2zm7.3 6.8c-2.4 0-4.3 1.9-4.3 4.2v2.7H8v2.1c0 2.3 1.3 4.1 3.6 4.1h7.4c2.8 0 4.5-1.6 4.5-4.5v-4.4c0-2.3-1.9-4.2-4.2-4.2h-1.9zm-1.8 10.3a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"/></svg>`,
  javascript: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 3h18v18H3V3zm13.8 14.5c1.4 0 2.2-.7 2.2-1.9 0-1.3-.9-1.8-2.5-2.5-2.2-.9-3.4-1.8-3.4-3.8 0-2.2 1.7-3.7 4.2-3.7 1.8 0 3 .6 3.7 1.9l-1.9 1.2c-.4-.8-1-1.2-1.8-1.2-1 0-1.6.6-1.6 1.4 0 1 .7 1.4 2.3 2.1 2.3 1 3.7 1.9 3.7 4.2 0 2.6-2 4-4.7 4-2.6 0-4.1-1.2-4.8-2.6l2-1.2c.5 1 1.2 1.5 2.6 1.5zm-6.6-8.4v7.6c0 1.9-.9 2.8-2.5 2.8-.9 0-1.7-.3-2.3-.8l1-1.8c.3.3.6.5 1.1.5.5 0 .8-.3.8-1v-7.3h1.9z"/></svg>`,
  typescript: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 3h18v18H3V3zm7.5 7.1H5.8v2h1.9v7.8h2.6v-7.8h1.9v-2h-1.7zm8.3 4.7c0-2.1-1.5-3-3.6-3.7-1.4-.5-1.8-.9-1.8-1.5 0-.6.5-1.1 1.4-1.1.9 0 1.6.4 2.1 1.1l1.7-1.4c-.9-1.2-2.1-1.7-3.8-1.7-2.4 0-4 1.4-4 3.4 0 2 1.4 2.9 3.4 3.6 1.5.5 2 .9 2 1.6 0 .7-.6 1.2-1.6 1.2-1.2 0-2-.6-2.6-1.5l-1.8 1.4c1 1.5 2.5 2.2 4.4 2.2 2.7 0 4.4-1.5 4.4-3.6z"/></svg>`,
  terminal: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>`,
  code: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>`,
  database: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>`,
  json: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 6c0-1.7 1.3-3 3-3h1v2H7c-.6 0-1 .4-1 1v3c0 1.1-.9 2-2 2 1.1 0 2 .9 2 2v3c0 .6.4 1 1 1h1v2H7c-1.7 0-3-1.3-3-3v-3.5c0-.8-.7-1.5-1.5-1.5.8 0 1.5-.7 1.5-1.5V6zm16 0c0-1.7-1.3-3-3-3h-1v2h1c.6 0 1 .4 1 1v3c0 1.1.9 2 2 2-1.1 0-2 .9-2 2v3c0 .6-.4 1-1 1h-1v2h1c1.7 0 3-1.3 3-3v-3.5c0-.8.7-1.5 1.5-1.5-.8 0-1.5-.7-1.5-1.5V6z"/></svg>`,
  html: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 3l1.5 16.5L12 22l6.5-2.5L20 3H4z"/><path d="M8 8h8l-.5 5H8.5l.3 3 3.2.9 3.2-.9.2-2"/></svg>`,
  css: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 3l1.5 16.5L12 22l6.5-2.5L20 3H4z"/><path d="M7.5 8h9l-.4 4.5H8.2l.3 3.5 3.5 1 3.5-1 .2-2"/></svg>`,
  yaml: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/></svg>`,
  markdown: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M7 15V9l3 3 3-3v6"/><path d="M17 12l-2 3h4l-2-3z"/></svg>`,
  docker: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19a9 9 0 0 0 16 0"/><path d="M2 13h20"/><rect x="4" y="9" width="3" height="3"/><rect x="8" y="9" width="3" height="3"/><rect x="12" y="9" width="3" height="3"/><rect x="8" y="5" width="3" height="3"/></svg>`
};

function getLanguageIcon(lang) {
  const l = (lang || "").toLowerCase().trim();
  if (l === "py" || l === "python") return ICONS.python;
  if (l === "js" || l === "javascript") return ICONS.javascript;
  if (l === "ts" || l === "typescript") return ICONS.typescript;
  if (["bash", "sh", "shell", "zsh"].includes(l)) return ICONS.terminal;
  if (["sql", "psql", "sqlite", "mysql", "postgres"].includes(l)) return ICONS.database;
  if (l === "json") return ICONS.json;
  if (l === "html" || l === "htm") return ICONS.html;
  if (l === "css" || l === "scss" || l === "sass" || l === "less") return ICONS.css;
  if (l === "yaml" || l === "yml") return ICONS.yaml;
  if (l === "markdown" || l === "md") return ICONS.markdown;
  if (l === "docker" || l === "dockerfile") return ICONS.docker;
  return ICONS.code;
}

function getCalloutIcon(type) {
  const t = (type || "").toLowerCase().trim();
  if (t === "key" || t === "definition") return ICONS.key;
  if (t === "summary" || t === "takeaway") return ICONS.summary;
  if (t === "insight") return ICONS.insight;
  if (t === "example") return ICONS.example;
  return ICONS[t] || ICONS.note;
}

module.exports = {
  ICONS,
  getLanguageIcon,
  getCalloutIcon
};
