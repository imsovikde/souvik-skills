#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");

const targetDir = process.argv[2] || ".";
let violations = 0;
let warnings = 0;

function scanCodeFile(filePath) {
  const content = fs.readFileSync(filePath, "utf8");
  const ext = path.extname(filePath);
  
  if (![".html", ".css", ".jsx", ".tsx", ".vue", ".svelte"].includes(ext)) {
    return;
  }

  // 1. Check for AI Purple Gradients in active styles
  if (/gradient.*(#8b5cf6|#6366f1|#3b82f6|rgb\(139,\s*92,\s*246\)|purple.*blue)/i.test(content)) {
    console.error(`[${filePath}] AI SLOP: Generic purple/blue gradient detected. Use intentional OKLCH lighting instead.`);
    violations++;
  }

  // 2. Check for arbitrary padding in styles
  const arbitraryPadding = content.match(/padding:\s*(13|17|19|23|27|29|31|37)px/g);
  if (arbitraryPadding) {
    console.warn(`[${filePath}] HARMONIC VIOLATION: Non-harmonic arbitrary padding detected (${arbitraryPadding.join(", ")}). Use diatonic/golden space tokens.`);
    warnings++;
  }

  // 3. Check for transition: all
  if (/transition:\s*all/i.test(content)) {
    console.warn(`[${filePath}] PERFORMANCE: 'transition: all' detected. Explicitly declare animated properties.`);
    warnings++;
  }

  // 4. Check for nested card wrappers
  if (/class="[^"]*card[^"]*"[\s\S]*class="[^"]*card[^"]*"/i.test(content)) {
    console.warn(`[${filePath}] SUBTRACTION: Nested card containers detected. Apply /ars:cut to flatten hierarchy.`);
    warnings++;
  }
}

function walk(dir) {
  if (!fs.existsSync(dir)) return;
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.name === "node_modules" || entry.name === ".git" || entry.name === "scratch" || entry.name === ".next" || entry.name === "out") continue;
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(fullPath);
    } else if (entry.isFile()) {
      scanCodeFile(fullPath);
    }
  }
}

console.log(`Running Ars Ingenium Audit on: ${targetDir}...`);
walk(targetDir);

if (violations > 0) {
  console.error(`Ars Audit: ${violations} critical violations found.`);
  process.exitCode = 1;
} else {
  console.log(`Ars Audit: Passed with Renaissance excellence (${warnings} advisory warnings).`);
}
