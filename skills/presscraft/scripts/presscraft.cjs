#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const { createAstPipeline } = require("./lib/ast-pipeline.cjs");
const { printToPdf } = require("./lib/puppeteer-printer.cjs");

function parseArgs(argv) {
  const options = {
    input: null,
    output: null,
    theme: "reader",
    format: "A4",
    landscape: false,
    margin: "15mm",
    title: null,
    author: null,
    cover: false,
    css: null,
    wait: 600,
    lineNumbers: true,
    headerFooter: true
  };

  const positional = [];

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];

    if (arg === "--input" || arg === "-i") {
      options.input = argv[++i];
    } else if (arg.startsWith("--input=")) {
      options.input = arg.slice(8);
    } else if (arg === "--output" || arg === "-o") {
      options.output = argv[++i];
    } else if (arg.startsWith("--output=")) {
      options.output = arg.slice(9);
    } else if (arg === "--theme" || arg === "-t") {
      options.theme = argv[++i];
    } else if (arg.startsWith("--theme=")) {
      options.theme = arg.slice(8);
    } else if (arg === "--format" || arg === "-f") {
      options.format = argv[++i];
    } else if (arg.startsWith("--format=")) {
      options.format = arg.slice(9);
    } else if (arg === "--margin" || arg === "-m") {
      options.margin = argv[++i];
    } else if (arg.startsWith("--margin=")) {
      options.margin = arg.slice(9);
    } else if (arg === "--title") {
      options.title = argv[++i];
    } else if (arg.startsWith("--title=")) {
      options.title = arg.slice(8);
    } else if (arg === "--author") {
      options.author = argv[++i];
    } else if (arg.startsWith("--author=")) {
      options.author = arg.slice(9);
    } else if (arg === "--css") {
      options.css = argv[++i];
    } else if (arg.startsWith("--css=")) {
      options.css = arg.slice(6);
    } else if (arg === "--wait") {
      options.wait = parseInt(argv[++i], 10);
    } else if (arg.startsWith("--wait=")) {
      options.wait = parseInt(arg.slice(7), 10);
    } else if (arg === "--landscape") {
      options.landscape = true;
    } else if (arg === "--cover") {
      options.cover = true;
    } else if (arg === "--no-line-numbers") {
      options.lineNumbers = false;
    } else if (arg === "--no-header-footer") {
      options.headerFooter = false;
    } else if (!arg.startsWith("-")) {
      positional.push(arg);
    }
  }

  if (!options.input && positional.length > 0) {
    options.input = positional[0];
  }
  if (!options.output && positional.length > 1) {
    options.output = positional[1];
  }

  return options;
}

function resolveThemeCss(themeName) {
  const stylesDirs = [
    path.resolve(__dirname, "../styles"),
    path.resolve(__dirname, "../assets/styles")
  ];

  // Check if theme is a direct path to a CSS file
  if (fs.existsSync(themeName)) {
    return fs.readFileSync(path.resolve(themeName), "utf8");
  }

  let cleanTheme = (themeName || "reader").toLowerCase().replace(/^theme-/, "");
  if (cleanTheme === "reading" || cleanTheme === "read") {
    cleanTheme = "reader";
  }

  for (const dir of stylesDirs) {
    const candidate = path.join(dir, `theme-${cleanTheme}.css`);
    if (fs.existsSync(candidate)) {
      return fs.readFileSync(candidate, "utf8");
    }
  }

  // Fallback to reader then minimalist
  for (const dir of stylesDirs) {
    const readerFallback = path.join(dir, "theme-reader.css");
    if (fs.existsSync(readerFallback)) {
      return fs.readFileSync(readerFallback, "utf8");
    }
    const miniFallback = path.join(dir, "theme-minimalist.css");
    if (fs.existsSync(miniFallback)) {
      return fs.readFileSync(miniFallback, "utf8");
    }
  }

  return "";
}

function loadBaseCss() {
  const stylesDirs = [
    path.resolve(__dirname, "../styles"),
    path.resolve(__dirname, "../assets/styles")
  ];

  for (const dir of stylesDirs) {
    const candidate = path.join(dir, "base.css");
    if (fs.existsSync(candidate)) {
      return fs.readFileSync(candidate, "utf8");
    }
  }

  return "";
}

function escapeHtml(str) {
  return String(str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

async function compilePdf(options) {
  if (!options.input) {
    throw new Error("Missing required argument: --input <path>");
  }

  const inputPath = path.resolve(options.input);
  if (!fs.existsSync(inputPath)) {
    throw new Error(`Input file not found: ${inputPath}`);
  }

  const outputPath = options.output
    ? path.resolve(options.output)
    : path.resolve(process.cwd(), `${path.parse(inputPath).name}.pdf`);

  const fileExt = path.extname(inputPath).toLowerCase();
  const rawContent = fs.readFileSync(inputPath, "utf8");

  // Title extraction
  let extractedTitle = options.title;
  if (!extractedTitle) {
    const h1Match = rawContent.match(/^#\s+(.+)$/m);
    if (h1Match) {
      extractedTitle = h1Match[1].trim();
    } else {
      extractedTitle = path.parse(inputPath).name.replace(/[-_]/g, " ");
    }
  }

  const pipeline = createAstPipeline({ lineNumbers: options.lineNumbers });
  let renderedBodyHtml = "";

  if (fileExt === ".html" || fileExt === ".htm") {
    // If it's already full HTML
    if (rawContent.includes("<html") || rawContent.includes("<body")) {
      renderedBodyHtml = rawContent;
    } else {
      renderedBodyHtml = `<div class="presscraft-document">${rawContent}</div>`;
    }
  } else if ([".py", ".js", ".ts", ".json", ".sql", ".sh", ".bash", ".css", ".yaml", ".yml"].includes(fileExt)) {
    // Wrap source code in a markdown fence
    const lang = fileExt.slice(1);
    const codeMarkdown = `\`\`\`${lang}\n${rawContent}\n\`\`\``;
    renderedBodyHtml = `<div class="presscraft-document">${pipeline.renderDocument(codeMarkdown)}</div>`;
  } else {
    // Default: Markdown or text
    renderedBodyHtml = `<div class="presscraft-document">${pipeline.renderDocument(rawContent)}</div>`;
  }

  // Cover page generation
  let coverHtml = "";
  if (options.cover) {
    coverHtml = `
      <div class="cover-page">
        <div class="cover-title">${escapeHtml(extractedTitle)}</div>
        ${options.author ? `<div class="cover-subtitle">${escapeHtml(options.author)}</div>` : ""}
        <div class="cover-divider"></div>
        <div class="cover-meta">${new Date().toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })}</div>
      </div>
    `;
  }

  const baseCss = loadBaseCss();
  const themeCss = resolveThemeCss(options.theme || "minimalist");
  const customCss = options.css ? `<style>\n${options.css}\n</style>` : "";

  const completeHtml = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${escapeHtml(extractedTitle)}</title>
  <style>
${baseCss}
${themeCss}
  </style>
  ${customCss}
</head>
<body>
  ${coverHtml}
  ${renderedBodyHtml}
</body>
</html>`;

  const printOptions = {
    format: options.format || "A4",
    landscape: options.landscape,
    margin: options.margin || "15mm",
    title: extractedTitle,
    author: options.author,
    headerFooter: options.headerFooter,
    wait: options.wait
  };

  const startTime = Date.now();
  const result = await printToPdf(completeHtml, outputPath, printOptions);
  const elapsedSec = ((Date.now() - startTime) / 1000).toFixed(2);

  return {
    ...result,
    elapsedSec,
    title: extractedTitle
  };
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args.includes("--help") || args.includes("-h")) {
    console.log(`
Presscraft: Ultimate Verbatim Markdown-to-PDF Publication Engine
==============================================================

Usage:
  node presscraft.cjs --input <path> --output <path.pdf> [options]

Options:
  --input, -i <path>       Source file path (.md, .html, source code, .txt)
  --output, -o <path>      Destination PDF file path
  --theme, -t <theme>      Theme: reader (default), storybook, minimalist, executive, academic, cyberpunk
  --format, -f <format>    Page size: A4, Letter, Legal, A3, A5 (default: A4)
  --margin, -m <margin>    Uniform margin (e.g. 15mm, 20mm, 1in, default: 15mm)
  --landscape              Landscape page orientation
  --title <string>         Document title (auto-detected from H1 if omitted)
  --author <string>        Document author for header/footer
  --cover                  Generate an editorial title cover page
  --css <rules>            Custom inline CSS overrides for prompt-driven styling
  --no-line-numbers        Disable line numbers in macOS code windows
  --no-header-footer       Disable running header and footer with page numbers
  --wait <ms>              Wait time in milliseconds for fonts (default: 600)

Examples:
  node presscraft.cjs -i guide.md -o guide.pdf --theme reader
  node presscraft.cjs -i book.md -o book.pdf --theme storybook
  node presscraft.cjs -i api.md -o api.pdf --theme minimalist --format Letter
  node presscraft.cjs -i report.md -o report.pdf --theme executive --cover --author "Lead Architect"
`);
    process.exit(args.includes("--help") || args.includes("-h") ? 0 : 1);
  }

  const options = parseArgs(args);

  try {
    console.log(`Presscraft: Compiling ${options.input}...`);
    const res = await compilePdf(options);
    console.log(`✓ PDF successfully generated: ${res.outputPath}`);
    console.log(`  File size: ${(res.bytes / 1024).toFixed(1)} KB`);
    console.log(`  Render time: ${res.elapsedSec}s`);
  } catch (err) {
    console.error(`Presscraft compilation error: ${err.message}`);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = {
  compilePdf
};
