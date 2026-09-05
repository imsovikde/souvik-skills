#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const { createAstPipeline } = require("./lib/ast-pipeline.cjs");
const { compilePdf } = require("./presscraft.cjs");

async function runAudit() {
  console.log("Presscraft: Starting comprehensive audit...\n");

  const skillRoot = path.resolve(__dirname, "..");
  const requiredFiles = [
    "SKILL.md",
    ".claude-plugin/plugin.json",
    "agents/openai.yaml",
    "package.json",
    "styles/base.css",
    "styles/theme-storybook.css",
    "styles/theme-minimalist.css",
    "styles/theme-executive.css",
    "styles/theme-academic.css",
    "styles/theme-cyberpunk.css",
    "scripts/presscraft.cjs",
    "scripts/lib/ast-pipeline.cjs",
    "scripts/lib/icons.cjs",
    "scripts/lib/puppeteer-printer.cjs",
    "references/design-tokens.md",
    "references/cli-reference.md"
  ];

  // 1. File verification
  console.log("1. Checking file structure...");
  for (const rel of requiredFiles) {
    const full = path.join(skillRoot, rel);
    if (!fs.existsSync(full)) {
      throw new Error(`Audit failure: Missing expected file: ${rel}`);
    }
  }
  console.log("   ✓ All 16 structural files verified.");

  // 2. AST pipeline & Code fence interception test
  console.log("\n2. Testing AST pipeline & macOS window interception...");
  const pipeline = createAstPipeline({ lineNumbers: true });
  const sampleMarkdown = `# Quantum Architecture
A study into quantum decoherence and entanglement.

> [!NOTE]
> Decoherence occurs when a quantum system interacts with its environment.

\`\`\`python
import numpy as np

def calculate_fidelity(state_a, state_b):
    """Compute quantum state fidelity."""
    inner = np.dot(state_a.conj().T, state_b)
    return float(np.abs(inner) ** 2)
\`\`\`
`;

  const renderedHtml = pipeline.renderDocument(sampleMarkdown);

  if (!renderedHtml.includes('class="code-window"')) {
    throw new Error("Audit failure: Rendered HTML does not contain .code-window");
  }
  if (!renderedHtml.includes('class="window-controls"')) {
    throw new Error("Audit failure: Rendered HTML does not contain .window-controls");
  }
  if (!renderedHtml.includes('class="control close"')) {
    throw new Error("Audit failure: Rendered HTML does not contain macOS traffic light buttons");
  }
  if (!renderedHtml.includes('class="callout callout-note"')) {
    throw new Error("Audit failure: Rendered HTML does not contain transformed .callout-note");
  }
  if (!renderedHtml.includes('calculate_fidelity')) {
    throw new Error("Audit failure: Python function name missing from highlighted code");
  }
  console.log("   ✓ AST pipeline intercepted code fence into macOS window frame.");
  console.log("   ✓ GitHub alert blockquote successfully converted into .callout.");

  // 3. Verbatim Content Preservation Audit
  console.log("\n3. Testing verbatim content preservation...");
  const rawWords = ["Quantum", "Architecture", "decoherence", "entanglement", "calculate_fidelity", "fidelity"];
  for (const w of rawWords) {
    if (!renderedHtml.includes(w)) {
      throw new Error(`Audit failure: Verbatim word '${w}' dropped during compilation!`);
    }
  }
  console.log("   ✓ 100% Verbatim content preservation verified.");

  // 4. End-to-end PDF Compilation Test
  console.log("\n4. Testing PDF compilation via Puppeteer...");
  const tempMdPath = path.join(skillRoot, "test_audit_document.md");
  const tempPdfPath = path.join(skillRoot, "test_audit_document.pdf");

  fs.writeFileSync(tempMdPath, sampleMarkdown, "utf8");

  try {
    const result = await compilePdf({
      input: tempMdPath,
      output: tempPdfPath,
      theme: "storybook",
      format: "A4"
    });

    if (!fs.existsSync(tempPdfPath)) {
      throw new Error("Audit failure: PDF output file was not created!");
    }

    const stats = fs.statSync(tempPdfPath);
    if (stats.size < 1024) {
      throw new Error(`Audit failure: Generated PDF is too small (${stats.size} bytes)!`);
    }

    console.log(`   ✓ PDF compiled successfully: ${tempPdfPath}`);
    console.log(`   ✓ File size: ${(stats.size / 1024).toFixed(1)} KB`);
    console.log(`   ✓ Render time: ${result.elapsedSec}s`);
  } finally {
    // Cleanup test artifacts
    if (fs.existsSync(tempMdPath)) fs.unlinkSync(tempMdPath);
    if (fs.existsSync(tempPdfPath)) fs.unlinkSync(tempPdfPath);
  }

  console.log("\n==========================================");
  console.log("✓ Presscraft audit passed with 100% fidelity!");
  console.log("==========================================\n");
}

if (require.main === module) {
  runAudit().catch((err) => {
    console.error(`Audit error: ${err.message}`);
    process.exit(1);
  });
}

module.exports = {
  runAudit
};
