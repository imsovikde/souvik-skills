#!/usr/bin/env node
/**
 * verify-citations-and-ast-seams.js
 * Deterministic anti-hallucination, anti-short-circuiting, and citation verifier for apex-bug-hunter.
 *
 * Usage:
 *   1. Verify a report or doc:
 *      node verify-citations-and-ast-seams.js <report-file.md>
 *   2. Verify a specific file:line:symbol tuple:
 *      node verify-citations-and-ast-seams.js --check-tuple <file:line:symbol>
 */

import fs from 'node:fs';
import path from 'node:path';

const ROOT_DIR = process.cwd();

function printUsage() {
  console.log('Usage:');
  console.log('  node verify-citations-and-ast-seams.js <markdown-file>');
  console.log('  node verify-citations-and-ast-seams.js --check-tuple <file:line:symbol>');
}

function verifyTuple(tupleStr) {
  const parts = tupleStr.split(':');
  if (parts.length < 3) {
    console.error(`[ERROR] Invalid tuple format "${tupleStr}". Expected <file:line:symbol>.`);
    process.exit(1);
  }

  const filePath = parts[0];
  const lineNum = parseInt(parts[1], 10);
  const symbol = parts.slice(2).join(':');

  const fullPath = path.resolve(ROOT_DIR, filePath);
  if (!fs.existsSync(fullPath)) {
    console.error(`[FAIL] File does not exist: ${filePath}`);
    process.exit(1);
  }

  const content = fs.readFileSync(fullPath, 'utf8');
  const lines = content.split('\n');

  if (isNaN(lineNum) || lineNum < 1 || lineNum > lines.length) {
    console.error(`[FAIL] Line ${lineNum} out of range for ${filePath} (1-${lines.length}).`);
    process.exit(1);
  }

  const start = Math.max(0, lineNum - 6);
  const end = Math.min(lines.length, lineNum + 5);
  const windowLines = lines.slice(start, end);
  const found = windowLines.some((l) => l.includes(symbol));

  if (!found) {
    console.error(`[FAIL] Symbol "${symbol}" not found within +/-5 lines of ${filePath}:${lineNum}.`);
    console.error('Inspection window:');
    windowLines.forEach((l, idx) => console.error(`  ${start + idx + 1}: ${l}`));
    process.exit(1);
  }

  console.log(`[OK] Verified tuple: ${filePath}:${lineNum} contains symbol "${symbol}" (within +/-5 lines).`);
  process.exit(0);
}

function verifyMarkdownReport(reportPath) {
  const fullPath = path.resolve(ROOT_DIR, reportPath);
  if (!fs.existsSync(fullPath)) {
    console.error(`[ERROR] Target file does not exist: ${reportPath}`);
    process.exit(1);
  }

  const content = fs.readFileSync(fullPath, 'utf8');
  const lines = content.split('\n');
  const isRuleDoc = reportPath.endsWith('SKILL.md') || reportPath.includes('references/') || reportPath.includes('references\\');

  let violations = 0;

  // 1. Scan for banned short-circuiting and sycophancy (in reports, excluding rule definitions)
  if (!isRuleDoc) {
    const bannedPatterns = [
      { pattern: /\/\/\s*\.\.\.\s*existing\s*code/i, name: 'Short-circuit placeholder (// ... existing code)' },
      { pattern: /\/\*\s*\.\.\.\s*rest\s*of/i, name: 'Short-circuit placeholder (/* ... rest of */)' },
      { pattern: /<!--\s*same\s*as\s*before\s*-->/i, name: 'Short-circuit placeholder (<!-- same as before -->)' },
      { pattern: /reviewed the remaining .* and found no issues/i, name: 'Bulk summary hand-waving' },
      { pattern: /\b(great question|you are absolutely right|fixed flawlessly|100% perfect)\b/i, name: 'AI sycophancy phrase' }
    ];

    lines.forEach((line, idx) => {
      // Skip lines that define or ban the pattern
      if (/ban|banned|prohibit|never|example|such as/i.test(line)) return;
      for (const { pattern, name } of bannedPatterns) {
        if (pattern.test(line)) {
          console.error(`[VIOLATION] Line ${idx + 1}: ${name}`);
          violations++;
        }
      }
    });
  }

  // 2. Extract and verify backticked file:line citations
  // Match patterns like `path/to/file.ext:123` or `file.ext:123-145`
  const citationRegex = /`([a-zA-Z0-9_\-./\\]+\.[a-zA-Z0-9]+):(\d+)(?:-\d+)?`/g;
  let match;
  let citationsChecked = 0;

  while ((match = citationRegex.exec(content)) !== null) {
    const citedFile = match[1];
    const citedLine = parseInt(match[2], 10);
    const candidatePath = path.resolve(ROOT_DIR, citedFile);

    if (fs.existsSync(candidatePath) && !fs.statSync(candidatePath).isDirectory()) {
      citationsChecked++;
      const fileContent = fs.readFileSync(candidatePath, 'utf8');
      const totalLines = fileContent.split('\n').length;
      if (citedLine > totalLines) {
        console.error(`[FAIL] In-tree citation \`${citedFile}:${citedLine}\` exceeds total lines (${totalLines}).`);
        violations++;
      }
    }
  }

  console.log(`=== VERIFY CITATIONS & AST SEAMS: ${reportPath} ===`);
  console.log(`In-tree file:line citations verified: ${citationsChecked}`);
  console.log(`Violations detected: ${violations}`);

  if (violations > 0) {
    console.error(`FAIL: ${violations} citation or short-circuiting violation(s) found in ${reportPath}.`);
    process.exit(1);
  }

  console.log(`[OK] ${reportPath} passed citation and anti-short-circuiting verification.`);
  process.exit(0);
}

function main() {
  const args = process.argv.slice(2);
  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    printUsage();
    process.exit(0);
  }

  if (args[0] === '--check-tuple') {
    if (!args[1]) {
      console.error('[ERROR] Missing tuple argument for --check-tuple.');
      process.exit(1);
    }
    verifyTuple(args[1]);
  } else {
    verifyMarkdownReport(args[0]);
  }
}

main();
