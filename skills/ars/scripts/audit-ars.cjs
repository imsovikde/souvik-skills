#!/usr/bin/env node
"use strict";

/**
 * audit-ars.cjs — Ars Ingenium automated style audit
 *
 * SCOPE DISCLAIMER:
 * This script checks deterministic, pattern-matchable violations in HTML/CSS/JSX/TSX/Vue/Svelte files.
 * It cannot verify: whether a Concetto was generated, whether ideation produced 3 candidates,
 * whether the manifest was filled, whether font choices are appropriate for the project register,
 * or whether the overall composition achieves artistic judgment. Those require human review.
 * A clean audit is a necessary condition, not a sufficient one.
 *
 * Usage: node audit-ars.cjs <path-to-file-or-dir>
 */

const fs = require("fs");
const path = require("path");

const targetDir = process.argv[2] || ".";
let violations = 0;
let warnings = 0;

// Known harmonic values from the Ars diatonic/golden spacing scale (rem values at 16px base)
// 0.25, 0.5, 0.75, 1.0, 1.618, 2.618, 4.236, 6.854
// Pixel equivalents: 4, 8, 12, 16, 26, 42, 68, 110
const HARMONIC_PX = new Set([4, 8, 12, 16, 26, 42, 68, 110]);

// Second-order slop fonts — fonts that became the "distinctive alternative" and are now overused
const SECOND_ORDER_SLOP_FONTS = [
  "Instrument Serif",
  "instrument-serif",
  "InstrumentSerif",
];

function isHarmonicPx(px) {
  // Allow values within 1px of a harmonic value (e.g., 25px ≈ 26px)
  for (const h of HARMONIC_PX) {
    if (Math.abs(px - h) <= 1) return true;
  }
  return false;
}

function scanCodeFile(filePath) {
  const content = fs.readFileSync(filePath, "utf8");
  const ext = path.extname(filePath).toLowerCase();

  if (![".html", ".css", ".jsx", ".tsx", ".vue", ".svelte"].includes(ext)) {
    return;
  }

  // 1. Check for AI Purple Gradients in active styles
  if (
    /gradient.*(#8b5cf6|#6366f1|#3b82f6|rgb\(139,\s*92,\s*246\)|purple.*blue|violet.*blue)/i.test(
      content
    )
  ) {
    console.error(
      `[VIOLATION] [${filePath}] AI SLOP: Generic purple/blue gradient detected. Use intentional OKLCH atmospheric falloff instead.`
    );
    violations++;
  }

  // 2. Check for non-harmonic pixel padding/margin/gap values
  // Finds any px value in a padding/margin/gap declaration and checks if it's off-scale
  const pxValuePattern = /(?:padding|margin|gap)\s*:[^;]*?(\d+)px/gi;
  let match;
  const offScaleValues = [];
  while ((match = pxValuePattern.exec(content)) !== null) {
    const px = parseInt(match[1], 10);
    if (px > 0 && !isHarmonicPx(px)) {
      offScaleValues.push(`${px}px`);
    }
  }
  if (offScaleValues.length > 0) {
    // Deduplicate
    const unique = [...new Set(offScaleValues)];
    console.warn(
      `[WARNING]   [${filePath}] HARMONIC VIOLATION: Non-harmonic spacing detected (${unique.join(
        ", "
      )}). Use diatonic/golden space tokens (4, 8, 12, 16, 26, 42, 68, 110px).`
    );
    warnings++;
  }

  // 3. Check for transition: all (performance violation)
  if (/transition\s*:\s*all/i.test(content)) {
    console.warn(
      `[WARNING]   [${filePath}] PERFORMANCE: 'transition: all' detected. Explicitly declare animated properties.`
    );
    warnings++;
  }

  // 4. Check for nested card wrappers (cards-inside-cards)
  if (
    /class="[^"]*card[^"]*"[\s\S]{0,200}class="[^"]*card[^"]*"/i.test(content)
  ) {
    console.warn(
      `[WARNING]   [${filePath}] SUBTRACTION: Nested card containers detected within 200 chars. Apply /ars:cut to flatten hierarchy.`
    );
    warnings++;
  }

  // 5. Check for second-order slop fonts
  for (const font of SECOND_ORDER_SLOP_FONTS) {
    if (content.includes(font)) {
      console.warn(
        `[WARNING]   [${filePath}] SECOND-ORDER SLOP: '${font}' detected. This font became the 'distinctive' default in the design-skill ecosystem — verify it's a deliberate choice for this project's register, not a reflex.`
      );
      warnings++;
      break; // Only one warning per file for this category
    }
  }

  // 6. Check for dead center alignment (every major block centered)
  const centerMatches = content.match(/text-align\s*:\s*center/gi) || [];
  if (centerMatches.length >= 3) {
    console.warn(
      `[WARNING]   [${filePath}] CONTRAPPOSTO: 'text-align: center' appears ${centerMatches.length} times. Check for dead-center composition. Use asymmetrical poise where appropriate.`
    );
    warnings++;
  }
}

function walk(dir) {
  if (!fs.existsSync(dir)) return;
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    if (
      ["node_modules", ".git", "scratch", ".next", "out", "dist", ".cache"].includes(
        entry.name
      )
    )
      continue;
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(fullPath);
    } else if (entry.isFile()) {
      scanCodeFile(fullPath);
    }
  }
}

console.log(`\nArs Ingenium Audit — ${targetDir}`);
console.log("─".repeat(60));
console.log(
  "SCOPE: HTML/CSS/JSX/TSX/Vue/Svelte files only. Cannot verify ideation protocol,\nmanifest completion, font register appropriateness, or compositional judgment.\n"
);

walk(targetDir);

console.log("─".repeat(60));
if (violations > 0) {
  console.error(
    `\nResult: FAILED — ${violations} critical violation(s), ${warnings} advisory warning(s).`
  );
  process.exitCode = 1;
} else if (warnings > 0) {
  console.log(
    `\nResult: PASSED with advisory warnings — 0 violations, ${warnings} warning(s). Review warnings before shipping.`
  );
} else {
  console.log(
    `\nResult: CLEAN — 0 violations, 0 warnings. Mechanistic checks passed. Human review of ideation and composition still required.`
  );
}
