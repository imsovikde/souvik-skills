#!/usr/bin/env node
"use strict";

/**
 * audit-apex-bug-hunter.cjs
 * Deterministic automated audit for the apex-bug-hunter skill package (v2.0 100/100/100 Edition).
 * Verifies file anatomy, frontmatter compliance, zero-dash hygiene, line limits,
 * and architectural coverage.
 */

const fs = require("fs");
const path = require("path");

const repoRoot = path.resolve(__dirname, "../../..");
const skillDir = path.resolve(__dirname, "..");
const skillMdPath = path.join(skillDir, "SKILL.md");
const pluginJsonPath = path.join(skillDir, ".claude-plugin", "plugin.json");
const openaiYamlPath = path.join(skillDir, "agents", "openai.yaml");

console.log("==================================================");
console.log("   Apex Bug Hunter: Architectural Skill Audit v2.0");
console.log("==================================================");
console.log(`Target: ${skillDir}`);

let checksPassed = 0;
let checksFailed = 0;

function assert(condition, message) {
  if (condition) {
    console.log(`[PASS] ${message}`);
    checksPassed++;
  } else {
    console.error(`[FAIL] ${message}`);
    checksFailed++;
  }
}

// 1. Structural File Checks (12 Required Files)
const requiredFiles = [
  "SKILL.md",
  ".claude-plugin/plugin.json",
  "agents/openai.yaml",
  "references/differential-call-graph-audit.md",
  "references/scientific-root-cause-and-ponytail-fixes.md",
  "references/anti-reward-hacking-and-verification-locks.md",
  "references/external-protocol-and-mcp-audit.md",
  "scripts/preflight-diff-and-boundary-scan.sh",
  "scripts/preflight-diff-and-boundary-scan.cjs",
  "scripts/preflight-diff-and-boundary-scan.js",
  "scripts/verify-mcp-and-schema-parity.js",
  "scripts/verify-citations-and-ast-seams.js",
];

for (const rel of requiredFiles) {
  const full = path.join(skillDir, rel);
  assert(fs.existsSync(full), `File exists: ${rel}`);
}

// 2. SKILL.md Frontmatter and Hygiene
if (fs.existsSync(skillMdPath)) {
  const content = fs.readFileSync(skillMdPath, "utf8");
  const lines = content.split(/\r?\n/);

  assert(lines.length < 450, `SKILL.md is under 450 lines (actual: ${lines.length})`);

  const fmMatch = content.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
  assert(Boolean(fmMatch), "SKILL.md has valid YAML frontmatter");

  if (fmMatch) {
    const rawFm = fmMatch[1];
    const nameMatch = rawFm.match(/^name:\s*(.+)$/m);
    const descMatch = rawFm.match(/^description:\s*(.+)$/m);

    assert(Boolean(nameMatch && nameMatch[1].trim() === "apex-bug-hunter"), "Frontmatter name is 'apex-bug-hunter'");
    assert(Boolean(descMatch && descMatch[1].trim().length >= 40), "Description is >= 40 chars");
    assert(Boolean(descMatch && descMatch[1].trim().length < 1024), "Description is < 1024 chars");
  }

  // Dash and ASCII art checks
  assert(!content.includes("\u2014"), "Zero em-dashes (\\u2014) in SKILL.md");
  assert(!content.includes("\u2013"), "Zero en-dashes (\\u2013) in SKILL.md");
  assert(!content.includes("┌") && !content.includes("└"), "Zero decorative ASCII box-drawings in SKILL.md");

  // Core invariant keywords
  assert(content.includes("8-Pass") || content.includes("7-Pass"), "SKILL.md covers multi-pass inspection pipeline");
  assert(content.includes("Karpathy"), "SKILL.md covers Karpathy surgical coding laws");
  assert(content.includes("3-Strike"), "SKILL.md covers 3-Strike Architectural Halt");
  assert(content.includes("outputSchema"), "SKILL.md covers MCP outputSchema verification");
  assert(content.includes("verify-mcp-and-schema-parity"), "SKILL.md references verify-mcp-and-schema-parity");
  assert(content.includes("verify-citations-and-ast-seams"), "SKILL.md references verify-citations-and-ast-seams");
  assert(content.includes("Green Build Fallacy") || content.includes("Green-Build") || content.includes("green-build"), "SKILL.md covers green-build delusion");
  assert(content.includes("Complexity Router") || content.includes("Four-Lane"), "SKILL.md covers operational complexity router");
  assert(content.includes("3-Axis") || content.includes("Three Orthogonal Axes") || content.includes("orthogonal"), "SKILL.md covers 3-axis verdict separation");
}

// 3. Reference Files Checks
const refDir = path.join(skillDir, "references");
if (fs.existsSync(refDir)) {
  const refFiles = fs.readdirSync(refDir).filter((f) => f.endsWith(".md"));
  for (const rf of refFiles) {
    const refContent = fs.readFileSync(path.join(refDir, rf), "utf8");
    assert(refContent.length > 500, `Reference file '${rf}' has substantial content (${refContent.length} bytes)`);
    assert(!refContent.includes("\u2014"), `Reference file '${rf}' contains zero em-dashes`);
    assert(!refContent.includes("\u2013"), `Reference file '${rf}' contains zero en-dashes`);
  }
}

// 4. Scripts Hygiene Checks
const scriptsDir = path.join(skillDir, "scripts");
if (fs.existsSync(scriptsDir)) {
  const scriptFiles = fs.readdirSync(scriptsDir);
  for (const sf of scriptFiles) {
    const scriptContent = fs.readFileSync(path.join(scriptsDir, sf), "utf8");
    assert(!scriptContent.includes("\u2014"), `Script file '${sf}' contains zero em-dashes`);
    assert(!scriptContent.includes("\u2013"), `Script file '${sf}' contains zero en-dashes`);
  }
}

// 5. Plugin Manifest and Agent UI Parity
if (fs.existsSync(pluginJsonPath)) {
  try {
    const pluginData = JSON.parse(fs.readFileSync(pluginJsonPath, "utf8"));
    assert(pluginData.name === "apex-bug-hunter", "plugin.json name matches 'apex-bug-hunter'");
  } catch (err) {
    assert(false, `plugin.json is valid JSON: ${err.message}`);
  }
}

if (fs.existsSync(openaiYamlPath)) {
  const yamlContent = fs.readFileSync(openaiYamlPath, "utf8");
  assert(yamlContent.includes("display_name:"), "openai.yaml has display_name");
  assert(yamlContent.includes("short_description:"), "openai.yaml has short_description");
  assert(yamlContent.includes("default_prompt:"), "openai.yaml has default_prompt");
  assert(yamlContent.includes("$apex-bug-hunter"), "openai.yaml default_prompt mentions $apex-bug-hunter");
}

console.log("--------------------------------------------------");
console.log(`Results: ${checksPassed} passed, ${checksFailed} failed`);
console.log("--------------------------------------------------");

if (checksFailed > 0) {
  console.error("FAIL: apex-bug-hunter audit failed.");
  process.exit(1);
}

console.log("SUCCESS: apex-bug-hunter conforms to all architectural standards.");
process.exit(0);
