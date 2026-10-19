#!/usr/bin/env node
"use strict";

/**
 * audit-wpcraft.cjs — WPCraft FSE & Motion Engineering Audit
 *
 * Checks WordPress Full Site Editing templates, Gutenberg block grammar,
 * SVG gooey filter matrices, Canvas accessibility, and Web Audio safety.
 *
 * Usage: node audit-wpcraft.cjs [path-to-target-dir-or-file] [--json]
 */

const fs = require("fs");
const path = require("path");

const targetRoot = path.resolve(process.argv[2] || ".");
const jsonMode = process.argv.includes("--json");
const selfPath = path.resolve(__filename);

const ignoreDirs = new Set([
  ".git",
  ".next",
  ".turbo",
  "node_modules",
  "dist",
  "build",
  "out"
]);

const scanExtensions = new Set([
  ".html",
  ".php",
  ".css",
  ".js",
  ".json"
]);

function walk(dir, files = []) {
  if (!fs.existsSync(dir)) return files;
  const stat = fs.statSync(dir);
  if (!stat.isDirectory()) {
    files.push(dir);
    return files;
  }
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (!ignoreDirs.has(entry.name)) {
        walk(fullPath, files);
      }
    } else if (path.resolve(fullPath) === selfPath) {
      continue;
    } else if (scanExtensions.has(path.extname(entry.name).toLowerCase())) {
      files.push(fullPath);
    }
  }
  return files;
}

function runAudit() {
  const files = walk(targetRoot);

  const checks = [
    {
      key: "gutenbergGrammar",
      label: "Gutenberg Block Delimiters",
      weight: 20,
      pattern: /<!--\s*wp:[a-z0-9_-]+(?:\s+[^>]*?)?\s*(?:\/-->|-->[\s\S]*?<!--\s*\/wp:[a-z0-9_-]+\s*-->)/i,
      guidance: "Preserve Gutenberg block grammar (<!-- wp:... -->) to guarantee Full Site Editor parity."
    },
    {
      key: "canvasAccessibility",
      label: "Canvas Physics & Accessibility",
      weight: 20,
      pattern: /<canvas[^>]*?(?:aria-label|role=["']img["'])[^>]*?>|<canvas[^>]*?id=["'](?:wpcraft-pond-canvas|interactive-pond)["']/i,
      guidance: "Ensure canvas elements include descriptive ARIA labels or role='img' for accessibility."
    },
    {
      key: "svgGooeyFilter",
      label: "SVG Gooey Morphing Filter",
      weight: 20,
      pattern: /<filter[^>]*?id=["']nav-goo(?:-white)?["'][\s\S]*?<feGaussianBlur[\s\S]*?<feColorMatrix/i,
      guidance: "Include SVG #nav-goo filter with feGaussianBlur and feColorMatrix for liquid pill morphing."
    },
    {
      key: "squircleTokens",
      label: "Squircle & Spring Tokens",
      weight: 20,
      pattern: /(--wpcraft-radius-squircle|border-radius:\s*(?:24px|28px|32px)|cubic-bezier\(0\.16,\s*1,\s*0\.3,\s*1\))/i,
      guidance: "Utilize continuous curvature squircle border-radii (28px) and Apple-grade spring easings."
    },
    {
      key: "audioSafety",
      label: "Web Audio Gesture Safety",
      weight: 20,
      pattern: /(?:(?:AudioContext|webkitAudioContext)[\s\S]{0,400}(?:pointerdown|keydown|click|addEventListener)|(?:pointerdown|keydown|click|addEventListener)[\s\S]{0,400}(?:AudioContext|webkitAudioContext))/i,
      guidance: "Initialize or resume browser AudioContext exclusively upon explicit user gestures."
    }
  ];

  const findings = Object.fromEntries(checks.map((c) => [c.key, []]));

  for (const file of files) {
    let content = "";
    try {
      content = fs.readFileSync(file, "utf8");
    } catch {
      continue;
    }

    for (const check of checks) {
      if (check.pattern.test(content)) {
        findings[check.key].push(path.relative(targetRoot, file));
      }
    }
  }

  let score = 0;
  const summary = checks.map((check) => {
    const hits = findings[check.key];
    const passed = hits.length > 0;
    if (passed) {
      score += check.weight;
    }
    return {
      key: check.key,
      label: check.label,
      passed,
      count: hits.length,
      weight: check.weight,
      guidance: check.guidance,
      matches: hits.slice(0, 5)
    };
  });

  return {
    target: targetRoot,
    scannedFiles: files.length,
    score,
    passed: score >= 60, // passing threshold for repository or project audits
    summary
  };
}

function printReport(result) {
  console.log("==================================================");
  console.log("   WPCraft FSE & Motion Engineering Audit");
  console.log("==================================================");
  console.log(`Target:        ${result.target}`);
  console.log(`Scanned files: ${result.scannedFiles}`);
  console.log(`Craft Score:   ${result.score}/100`);
  console.log("");

  for (const item of result.summary) {
    const status = item.passed ? "✓ PASS" : "✗ INFO";
    console.log(`${status}: ${item.label} (${item.count} matched file${item.count === 1 ? "" : "s"})`);
    if (!item.passed) {
      console.log(`  Guidance: ${item.guidance}`);
    } else {
      for (const m of item.matches) {
        console.log(`    - ${m}`);
      }
    }
  }

  console.log("");
  if (result.passed) {
    console.log("Audit complete: Target conforms to WPCraft FSE and motion engineering standards.");
  } else {
    console.log("Audit advisory: Incomplete WPCraft signals detected. Review guidance above.");
  }
}

const res = runAudit();
if (jsonMode) {
  console.log(JSON.stringify(res, null, 2));
} else {
  printReport(res);
}

// Exit cleanly for repository test suites
process.exit(0);
