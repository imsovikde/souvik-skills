"use strict";

const ICONS = {
  // Callouts
  note: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>`,
  tip: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-7 7c0 2.38 1.19 4.47 3 5.74V17a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1v-2.26c1.81-1.27 3-3.36 3-5.74a7 7 0 0 0-7-7z"/></svg>`,
  important: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>`,
  warning: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
  caution: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`,

  // Programming Languages
  python: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M11.9 1.5c-3.1 0-5 1.7-5 4v2.7h5.1V9H4.6C2.3 9 1 10.8 1 13.5c0 2.9 1.7 4.5 4.5 4.5h2.1v-2.7c0-2.3 1.9-4.2 4.3-4.2h5.1V9c0-2.3-1.9-7.5-5.1-7.5zm-1.8 2.2a1 1 0 1 1 0 2 1 1 0 0 1 0-2zm7.3 6.8c-2.4 0-4.3 1.9-4.3 4.2v2.7H8v2.1c0 2.3 1.3 4.1 3.6 4.1h7.4c2.8 0 4.5-1.6 4.5-4.5v-4.4c0-2.3-1.9-4.2-4.2-4.2h-1.9zm-1.8 10.3a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"/></svg>`,
  javascript: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 3h18v18H3V3zm13.8 14.5c1.4 0 2.2-.7 2.2-1.9 0-1.3-.9-1.8-2.5-2.5-2.2-.9-3.4-1.8-3.4-3.8 0-2.2 1.7-3.7 4.2-3.7 1.8 0 3 .6 3.7 1.9l-1.9 1.2c-.4-.8-1-1.2-1.8-1.2-1 0-1.6.6-1.6 1.4 0 1 .7 1.4 2.3 2.1 2.3 1 3.7 1.9 3.7 4.2 0 2.6-2 4-4.7 4-2.6 0-4.1-1.2-4.8-2.6l2-1.2c.5 1 1.2 1.5 2.6 1.5zm-6.6-8.4v7.6c0 1.9-.9 2.8-2.5 2.8-.9 0-1.7-.3-2.3-.8l1-1.8c.3.3.6.5 1.1.5.5 0 .8-.3.8-1v-7.3h1.9z"/></svg>`,
  typescript: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 3h18v18H3V3zm7.5 7.1H5.8v2h1.9v7.8h2.6v-7.8h1.9v-2h-1.7zm8.3 4.7c0-2.1-1.5-3-3.6-3.7-1.4-.5-1.8-.9-1.8-1.5 0-.6.5-1.1 1.4-1.1.9 0 1.6.4 2.1 1.1l1.7-1.4c-.9-1.2-2.1-1.7-3.8-1.7-2.4 0-4 1.4-4 3.4 0 2 1.4 2.9 3.4 3.6 1.5.5 2 .9 2 1.6 0 .7-.6 1.2-1.6 1.2-1.2 0-2-.6-2.6-1.5l-1.8 1.4c1 1.5 2.5 2.2 4.4 2.2 2.7 0 4.4-1.5 4.4-3.6z"/></svg>`,
  terminal: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>`,
  code: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>`,
  database: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>`
};

function getLanguageIcon(lang) {
  const l = (lang || "").toLowerCase().trim();
  if (l === "py" || l === "python") return ICONS.python;
  if (l === "js" || l === "javascript") return ICONS.javascript;
  if (l === "ts" || l === "typescript") return ICONS.typescript;
  if (["bash", "sh", "shell", "zsh"].includes(l)) return ICONS.terminal;
  if (["sql", "psql", "sqlite", "mysql", "postgres"].includes(l)) return ICONS.database;
  return ICONS.code;
}

function getCalloutIcon(type) {
  const t = (type || "").toLowerCase().trim();
  return ICONS[t] || ICONS.note;
}

module.exports = {
  ICONS,
  getLanguageIcon,
  getCalloutIcon
};
