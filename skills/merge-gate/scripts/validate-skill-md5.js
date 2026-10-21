#!/usr/bin/env node
/**
 * validate-skill-md5.js
 *
 * Strict Node.js skill integrity and MD5/SHA-256 manifest verifier for merge-gate.
 * Checks:
 * 1. SKILL.md frontmatter, description length, and < 450 line limit.
 * 2. Completeness of all reference and script files.
 * 3. Node.js syntax checking (node --check) on JavaScript CLI scripts.
 * 4. Zero em-dashes (\u2014) and zero en-dashes (\u2013) across the entire skill tree.
 * 5. Computes MD5 and SHA-256 checksums for every file and generates SKILL_MANIFEST.json.
 */

import { execFileSync } from 'node:child_process';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const SKILL_DIR = path.resolve(__dirname, '..');
const MANIFEST_PATH = path.join(SKILL_DIR, 'SKILL_MANIFEST.json');

console.log('====================================================');
console.log('     MERGE GATE: SKILL INTEGRITY & MD5 VALIDATOR    ');
console.log('====================================================');
console.log(`Auditing Directory: ${SKILL_DIR}`);

let passed = 0;
let failed = 0;

function assert(condition, message) {
  if (condition) {
    console.log(`[PASS] ${message}`);
    passed++;
  } else {
    console.error(`[FAIL] ${message}`);
    failed++;
  }
}

// 1. Required Files Anatomy
const requiredFiles = [
  'SKILL.md',
  '.claude-plugin/plugin.json',
  'agents/openai.yaml',
  'references/whole-project-main-diff-engine.md',
  'references/frontend-ui-and-taste-gate.md',
  'references/backend-security-and-mcp-gate.md',
  'references/tri-state-verdict-and-humanizer-pr-comment.md',
  'scripts/preflight-merge-gate.js',
  'scripts/validate-skill-md5.js'
];

for (const rel of requiredFiles) {
  const full = path.join(SKILL_DIR, rel);
  assert(fs.existsSync(full), `Required file exists: ${rel}`);
}

// 2. SKILL.md Frontmatter and Line Limits
const skillMdPath = path.join(SKILL_DIR, 'SKILL.md');
if (fs.existsSync(skillMdPath)) {
  const content = fs.readFileSync(skillMdPath, 'utf8');
  const lines = content.split(/\r?\n/);

  assert(lines.length < 450, `SKILL.md is under 450 lines (actual: ${lines.length})`);

  const fmMatch = content.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
  assert(Boolean(fmMatch), 'SKILL.md contains valid YAML frontmatter');

  if (fmMatch) {
    const rawFm = fmMatch[1];
    const nameMatch = rawFm.match(/^name:\s*(.+)$/m);
    const descMatch = rawFm.match(/^description:\s*(.+)$/m);

    assert(Boolean(nameMatch && nameMatch[1].trim() === 'merge-gate'), "Frontmatter name is 'merge-gate'");
    assert(Boolean(descMatch && descMatch[1].trim().length >= 40), 'Frontmatter description is >= 40 chars');
    assert(Boolean(descMatch && descMatch[1].trim().length < 1024), 'Frontmatter description is < 1024 chars');
  }

  assert(content.includes('Tri-State'), 'SKILL.md covers Tri-State Pre-Merge Verdicts');
  assert(content.includes('Whole-Project') || content.includes('whole-project'), 'SKILL.md covers Whole-Project comparison');
  assert(content.includes('humanizer'), 'SKILL.md covers humanizer review comments');
  assert(content.includes('preflight-merge-gate'), 'SKILL.md references preflight-merge-gate.js');
}

// 3. Syntax Validation on JavaScript Scripts
const jsScripts = ['scripts/preflight-merge-gate.js', 'scripts/validate-skill-md5.js'];
for (const rel of jsScripts) {
  const scriptPath = path.join(SKILL_DIR, rel);
  try {
    execFileSync(process.execPath, ['--check', scriptPath], { stdio: 'ignore' });
    assert(true, `Syntax valid (node --check): ${rel}`);
  } catch (err) {
    assert(false, `Syntax check failed on ${rel}: ${err.message}`);
  }
}

// 4. Recursive Walk, Zero-Dash Verification, and MD5 / SHA-256 Checksum Calculation
function walkFiles(dir, fileList = []) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.name === 'node_modules' || entry.name === '.git' || entry.name === 'SKILL_MANIFEST.json') {
      continue;
    }
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walkFiles(full, fileList);
    } else {
      fileList.push(full);
    }
  }
  return fileList;
}

const allSkillFiles = walkFiles(SKILL_DIR);
const manifestEntries = [];

let dashViolations = 0;
for (const filePath of allSkillFiles) {
  const relPath = path.relative(SKILL_DIR, filePath).split(path.sep).join('/');
  const buffer = fs.readFileSync(filePath);

  // Check text files for dashes
  if (/\.(md|js|json|yaml|yml|sh|cjs)$/.test(filePath)) {
    const text = buffer.toString('utf8');
    const dashes = text.match(/[\u2013\u2014]/g);
    if (dashes) {
      console.error(`[FAIL] File '${relPath}' contains ${dashes.length} forbidden em/en-dash(es).`);
      dashViolations++;
    }
  }

  const md5 = crypto.createHash('md5').update(buffer).digest('hex');
  const sha256 = crypto.createHash('sha256').update(buffer).digest('hex');

  manifestEntries.push({
    file: relPath,
    bytes: buffer.length,
    md5,
    sha256
  });
}

assert(dashViolations === 0, `Zero em-dashes and en-dashes across all files (${dashViolations} violations)`);

// 5. Generate and Write SKILL_MANIFEST.json
manifestEntries.sort((a, b) => a.file.localeCompare(b.file));
const manifestData = {
  skill: 'merge-gate',
  version: '0.14.0',
  generatedAt: new Date().toISOString(),
  fileCount: manifestEntries.length,
  files: manifestEntries
};

fs.writeFileSync(MANIFEST_PATH, JSON.stringify(manifestData, null, 2) + '\n', 'utf8');
assert(fs.existsSync(MANIFEST_PATH), `Generated cryptographic manifest: SKILL_MANIFEST.json (${manifestEntries.length} files tracked)`);

console.log('----------------------------------------------------');
console.log(`Summary: ${passed} passed, ${failed} failed`);
console.log('----------------------------------------------------');

if (failed > 0) {
  console.error('[FAIL] Skill integrity check failed.');
  process.exit(1);
}

console.log('[SUCCESS] merge-gate conforms to all cryptographic and architectural standards.');
process.exit(0);
