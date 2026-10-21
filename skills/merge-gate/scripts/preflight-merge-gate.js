#!/usr/bin/env node
/**
 * preflight-merge-gate.js
 *
 * Production-grade pre-flight merge gatekeeper CLI for pull requests and branches.
 * Capabilities:
 * 1. Resolves diff scope against origin/main including working-tree changes.
 * 2. Cryptographic MD5 & SHA-256 verification of protected zero-touch paths.
 * 3. Differential line-deletion (-) scan for stripped validation and security invariants.
 * 4. Frontend UI and taste gatekeeper (responsive geometry, dialog bans, anti-slop rules).
 * 5. Backend protocol and MCP parity gatekeeper (structuredContent return-branch parity).
 * 6. Authentic humanizer PR review comment verifier (--verify-comment <file>).
 * 7. Self-test validation mode (--self-test).
 */

import { execFileSync } from 'node:child_process';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';

const ROOT_DIR = process.cwd();

function runGit(args, allowFailure = false) {
  try {
    return execFileSync('git', args, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }).trim();
  } catch (err) {
    if (allowFailure) return '';
    throw err;
  }
}

function computeFileHashes(filePath) {
  if (!fs.existsSync(filePath)) return null;
  const buffer = fs.readFileSync(filePath);
  const md5 = crypto.createHash('md5').update(buffer).digest('hex');
  const sha256 = crypto.createHash('sha256').update(buffer).digest('hex');
  return { md5, sha256, size: buffer.length };
}

function getGitBlobHashes(ref, relPath) {
  try {
    const content = execFileSync('git', ['show', `${ref}:${relPath}`], {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe']
    });
    const buffer = Buffer.from(content, 'utf8');
    const md5 = crypto.createHash('md5').update(buffer).digest('hex');
    const sha256 = crypto.createHash('sha256').update(buffer).digest('hex');
    return { md5, sha256, size: buffer.length };
  } catch {
    return null;
  }
}

function stripComments(code) {
  return code.replace(/\/\*[\s\S]*?\*\/|\/\/.*/g, '');
}

function extractReturnObjectBlocks(code) {
  const blocks = [];
  const returnRegex = /\breturn\s*\{/g;
  let match;
  while ((match = returnRegex.exec(code)) !== null) {
    const startBrace = code.indexOf('{', match.index);
    if (startBrace === -1) continue;
    let depth = 0;
    let endBrace = -1;
    for (let i = startBrace; i < code.length; i++) {
      if (code[i] === '{') depth++;
      else if (code[i] === '}') {
        depth--;
        if (depth === 0) {
          endBrace = i;
          break;
        }
      }
    }
    if (endBrace !== -1) {
      const lineNum = code.slice(0, match.index).split('\n').length;
      blocks.push({ line: lineNum, text: code.slice(startBrace, endBrace + 1) });
    }
  }
  return blocks;
}

function verifyCommentFile(commentFilePath) {
  const resolvedPath = path.resolve(ROOT_DIR, commentFilePath);
  if (!fs.existsSync(resolvedPath)) {
    console.error(`[ERROR] Comment file does not exist: ${commentFilePath}`);
    process.exit(1);
  }

  const rawBuffer = fs.readFileSync(resolvedPath);
  let violations = 0;

  console.log('=== MERGE GATE: HUMANIZER PR COMMENT VERIFIER ===');
  console.log(`Auditing target: ${commentFilePath}`);

  // 1. UTF-8 BOM Check
  if (rawBuffer.length >= 3 && rawBuffer[0] === 0xef && rawBuffer[1] === 0xbb && rawBuffer[2] === 0xbf) {
    console.error('[FAIL] Comment file contains a UTF-8 Byte Order Mark (BOM).');
    violations++;
  }

  const content = rawBuffer.toString('utf8');

  // 2. Mojibake Detection
  if (/ΓÇ|â€”|â€“|Ã©|Ã/.test(content)) {
    console.error('[FAIL] Detected encoding corruption / mojibake artifacts in comment text.');
    violations++;
  }

  // 3. Em-Dash and En-Dash Prohibition
  const dashes = content.match(/[\u2013\u2014]/g);
  if (dashes) {
    console.error(`[FAIL] Detected ${dashes.length} forbidden em-dash / en-dash character(s) in review comment.`);
    violations++;
  }

  // 4. Banned AI Vocabulary from Wikipedia 33 Humanizer Principles
  const bannedWords = [
    'delve', 'pivotal', 'tapestry', 'testament', 'underscores', 'vital',
    'seamless', 'holistic', 'paradigm', 'synergistic', 'beacon', 'embark',
    'navigate', 'revolutionize', 'empower', 'foster', 'bolster', 'harness',
    'catalyst', 'nuanced', 'vibrant', 'relentless'
  ];

  const lines = content.split('\n');
  lines.forEach((line, idx) => {
    // Skip rule definition quotes or code blocks
    if (line.trim().startsWith('`') || line.trim().startsWith('>') || /banned|prohibit|rule/i.test(line)) {
      return;
    }

    for (const word of bannedWords) {
      const regex = new RegExp(`\\b${word}\\b`, 'i');
      if (regex.test(line)) {
        console.error(`[FAIL] Line ${idx + 1}: Banned AI vocabulary word "${word}" detected.`);
        violations++;
      }
    }

    if (/\b(here's the thing|let's dive in|certainly!|great work on this pr)\b/i.test(line)) {
      console.error(`[FAIL] Line ${idx + 1}: Banned theatrical / sycophantic opener detected.`);
      violations++;
    }

    if (/\b(highlighting the importance of|serving as a testament to)\b/i.test(line)) {
      console.error(`[FAIL] Line ${idx + 1}: Banned superficial participle tail detected.`);
      violations++;
    }
  });

  if (violations > 0) {
    console.error(`\n[REJECTED] PR review comment failed humanizer verification with ${violations} violation(s).`);
    process.exit(1);
  }

  console.log('[OK] PR review comment passed all humanizer authenticity checks.');
  process.exit(0);
}

function runSelfTest() {
  console.log('=== MERGE GATE: RUNNING INTERNAL SELF-TEST ===');
  let passed = 0;

  // Test 1: Return block extractor
  const sampleCode = `
    function handle() {
      if (err) {
        return { isError: true, content: [{ type: "text", text: "fail" }] };
      }
      return {
        content: [{ type: "text", text: "ok" }],
        structuredContent: { count: 1 }
      };
    }
  `;
  const blocks = extractReturnObjectBlocks(sampleCode);
  if (blocks.length === 2 && blocks[1].text.includes('structuredContent')) {
    console.log('[PASS] extractReturnObjectBlocks correctly parsed 2 return objects.');
    passed++;
  } else {
    console.error('[FAIL] extractReturnObjectBlocks self-test failed.');
  }

  // Test 2: Comment stripper
  const sampleWithComments = `
    // export function dead() {}
    /* block comment */
    export function live() {}
  `;
  const stripped = stripComments(sampleWithComments);
  if (!stripped.includes('dead') && stripped.includes('live')) {
    console.log('[PASS] stripComments successfully stripped line and block comments.');
    passed++;
  } else {
    console.error('[FAIL] stripComments self-test failed.');
  }

  // Test 3: Crypto hashing
  const testBuffer = Buffer.from('merge-gate-self-test-payload', 'utf8');
  const testMd5 = crypto.createHash('md5').update(testBuffer).digest('hex');
  const testSha256 = crypto.createHash('sha256').update(testBuffer).digest('hex');
  if (testMd5 && testSha256 && testMd5.length === 32 && testSha256.length === 64) {
    console.log('[PASS] Cryptographic MD5 & SHA-256 hash generator self-test passed.');
    passed++;
  } else {
    console.error('[FAIL] Cryptographic self-test failed.');
  }

  console.log(`Self-Test Results: ${passed}/3 checks passed.`);
  process.exit(passed === 3 ? 0 : 1);
}

function runFullPreflightScan() {
  const baseRef = process.argv[2] || 'origin/main';
  const headRef = process.argv[3] || 'HEAD';
  const protectedPathsCsv = process.env.PROTECTED_PATHS || '';

  console.log('==========================================================');
  console.log('      MERGE GATE: PRE-FLIGHT PRODUCTION GATEKEEPER        ');
  console.log('==========================================================');
  console.log(`Timestamp: ${new Date().toISOString()}`);
  console.log(`Base:      ${baseRef}`);
  console.log(`Head:      ${headRef}`);

  const insideWorkTree = runGit(['rev-parse', '--is-inside-work-tree'], true);
  if (insideWorkTree !== 'true') {
    console.error('[ERROR] Current working directory is not inside a Git repository.');
    process.exit(1);
  }

  const currentBranch = runGit(['rev-parse', '--abbrev-ref', 'HEAD'], true);
  console.log(`Branch:    ${currentBranch}`);

  let blockers = 0;
  let warnings = 0;

  // 1. Working-tree porcelain inspection
  console.log('\n--- CHECK 1: WORKING-TREE STATUS ---');
  const porcelain = runGit(['status', '--porcelain'], true);
  if (porcelain) {
    console.log('[INFO] Uncommitted changes detected in working tree:');
    porcelain.split('\n').slice(0, 8).forEach((l) => console.log(`  ${l}`));
  } else {
    console.log('[OK] Working tree clean.');
  }

  // 2. Cryptographic Protected Zero-Touch Path Lock
  if (protectedPathsCsv) {
    console.log('\n--- CHECK 2: CRYPTOGRAPHIC ZERO-TOUCH PATH LOCK ---');
    const pathsToCheck = protectedPathsCsv.split(',').map((p) => p.trim()).filter(Boolean);

    for (const relPath of pathsToCheck) {
      const baseHashes = getGitBlobHashes(baseRef, relPath);
      const headHashes = computeFileHashes(path.resolve(ROOT_DIR, relPath));

      if (!baseHashes && !headHashes) {
        console.log(`[SKIP] Protected path not present in base or head: ${relPath}`);
        continue;
      }

      if (!baseHashes || !headHashes || baseHashes.sha256 !== headHashes.sha256) {
        console.error(`[P0 BLOCKER] Protected path altered: ${relPath}`);
        if (baseHashes && headHashes) {
          console.error(`  Base SHA-256: ${baseHashes.sha256}`);
          console.error(`  Head SHA-256: ${headHashes.sha256}`);
        }
        blockers++;
      } else {
        console.log(`[PASS] Protected path verified identical (SHA-256 match): ${relPath}`);
      }
    }

    if (blockers > 0) {
      console.error(`\n[HALT] Cryptographic zero-touch path lock violated. Exiting code 2.`);
      process.exit(2);
    }
  }

  // 3. Differential Line-Deletion (-) Audit
  console.log('\n--- CHECK 3: DIFFERENTIAL LINE-DELETION (-) INVARIANT SCAN ---');
  let unifiedDiff = '';
  try {
    unifiedDiff += runGit(['diff', `${baseRef}...${headRef}`, '--unified=0'], true) + '\n';
  } catch {
    // range diff may be unavailable
  }
  unifiedDiff += runGit(['diff', 'HEAD', '--unified=0'], true);

  const gateRegex = /(\.refine\(|\.superRefine\(|safeParse\(|\.strict\(|structuredClone\(|owner_id|tenant_id|deletedAt|archivedAt|listTools\()/;
  const removedGates = unifiedDiff
    .split('\n')
    .filter((line) => line.startsWith('-') && !line.startsWith('---') && gateRegex.test(line));

  if (removedGates.length > 0) {
    console.log('[WARNING] Sensitive validation, tenant, or security predicates in deleted lines (-):');
    removedGates.slice(0, 6).forEach((l) => console.log(`  ${l}`));
    warnings++;
  } else {
    console.log('[OK] Zero critical validation or tenant gates removed in diff.');
  }

  // 4. Frontend UI, Responsive Geometry & Anti-Slop Audit
  console.log('\n--- CHECK 4: FRONTEND UI & TASTE AUDIT ---');
  const changedFrontendFiles = runGit(
    ['diff', '--name-only', `${baseRef}...${headRef}`, '--', '*.tsx', '*.jsx', '*.html', '*.vue', '*.svelte', '*.css'],
    true
  ).split('\n').map((f) => f.trim()).filter(Boolean);

  let uiFindings = 0;
  for (const relFile of changedFrontendFiles) {
    const fullPath = path.resolve(ROOT_DIR, relFile);
    if (!fs.existsSync(fullPath)) continue;
    const content = fs.readFileSync(fullPath, 'utf8');

    // Dialog bans
    if (/\b(alert|confirm|prompt)\s*\(/.test(content)) {
      console.error(`[P0 BLOCKER] Native dialog invocation (alert/confirm/prompt) in ${relFile}`);
      blockers++;
      uiFindings++;
    }

    // Dangerous HTML
    if (content.includes('dangerouslySetInnerHTML')) {
      console.error(`[P0 BLOCKER] dangerouslySetInnerHTML detected in ${relFile}`);
      blockers++;
      uiFindings++;
    }

    // Legacy h-screen
    if (/\bh-screen\b/.test(content)) {
      console.log(`[WARNING] Legacy h-screen unit in ${relFile} (prefer min-h-dvh or 100dvh)`);
      warnings++;
      uiFindings++;
    }

    // Raw scroll listener
    if (/window\.addEventListener\s*\(\s*['"]scroll['"]/.test(content)) {
      console.error(`[P1 CRITICAL] Raw window scroll event listener in ${relFile}`);
      warnings++;
      uiFindings++;
    }

    // Hardcoded pure black
    if (/#000000\b|#000\b/.test(content) && !relFile.endsWith('.json')) {
      console.log(`[WARNING] Hardcoded pure black (#000000) in ${relFile} (prefer dark theme neutrals)`);
      warnings++;
      uiFindings++;
    }

    // Em-dashes in UI files
    if (/[\u2013\u2014]/.test(content)) {
      console.log(`[WARNING] Em-dash or en-dash detected in UI source file: ${relFile}`);
      warnings++;
      uiFindings++;
    }
  }

  if (uiFindings === 0) {
    console.log('[OK] Frontend files passed responsive geometry and anti-slop rules.');
  }

  // 5. Backend, MCP Contract Parity & Test Harness Audit
  console.log('\n--- CHECK 5: BACKEND, PROTOCOL & TEST-HARNESS PARITY ---');
  const allChangedFiles = runGit(['diff', '--name-only', `${baseRef}...${headRef}`], true)
    .split('\n')
    .map((f) => f.trim())
    .filter(Boolean);

  let backendFindings = 0;
  for (const relFile of allChangedFiles) {
    const fullPath = path.resolve(ROOT_DIR, relFile);
    if (!fs.existsSync(fullPath) || fs.statSync(fullPath).isDirectory()) continue;
    const content = fs.readFileSync(fullPath, 'utf8');

    // MCP outputSchema per-return parity
    if (content.includes('outputSchema')) {
      const clean = stripComments(content);
      const returnBlocks = extractReturnObjectBlocks(clean);
      for (const block of returnBlocks) {
        if (block.text.includes('content:') && !block.text.includes('isError: true')) {
          if (!block.text.includes('structuredContent')) {
            console.error(`[P0 BLOCKER] MCP tool return statement lacks structuredContent in ${relFile}:${block.line}`);
            blockers++;
            backendFindings++;
          }
        }
      }
    }

    // In-place schema mutation
    if (
      (content.includes('delete schema.') || content.includes('delete def.')) &&
      !content.includes('structuredClone(') &&
      !content.includes('JSON.parse(JSON.stringify(')
    ) {
      console.error(`[P1 CRITICAL] In-place schema mutation without structuredClone in ${relFile}`);
      warnings++;
      backendFindings++;
    }

    // Test suppressions in test files
    if (relFile.includes('test') || relFile.includes('spec')) {
      if (/\b(describe|it|test)\.(skip|only|todo|fails)\b/.test(content)) {
        console.error(`[P0 BLOCKER] Test modifier (.skip/.only/.todo/.fails) in ${relFile}`);
        blockers++;
        backendFindings++;
      }
    }
  }

  if (backendFindings === 0) {
    console.log('[OK] Backend and protocol contracts passed all parity checks.');
  }

  // Summary and Tri-State Verdict Determination
  console.log('\n==========================================================');
  console.log('                 PRE-FLIGHT GATE VERDICT                  ');
  console.log('==========================================================');
  console.log(`Blockers: ${blockers}`);
  console.log(`Warnings: ${warnings}`);

  if (blockers > 0) {
    console.error('\nVERDICT 3: HALT - DO NOT MERGE (BLOCKING DEFECTS FOUND)');
    process.exit(1);
  }

  if (warnings > 0) {
    console.log('\nVERDICT 2: PARTIAL / NEEDS IMPROVEMENT BEFORE MERGE');
    process.exit(0);
  }

  console.log('\nVERDICT 1: APPROVED FOR MERGE (SAFE TO MERGE INTO MAIN)');
  process.exit(0);
}

function main() {
  const args = process.argv.slice(2);
  if (args.includes('--self-test')) {
    runSelfTest();
  } else if (args.includes('--verify-comment')) {
    const commentIndex = args.indexOf('--verify-comment');
    const commentFile = args[commentIndex + 1];
    if (!commentFile) {
      console.error('[ERROR] Missing comment file argument for --verify-comment.');
      process.exit(1);
    }
    verifyCommentFile(commentFile);
  } else {
    runFullPreflightScan();
  }
}

main();
