#!/usr/bin/env node
/**
 * preflight-diff-and-boundary-scan.js
 * Cross-platform Node.js deterministic preflight scanner for apex-bug-hunter v2.0.
 * Resolves audit scope, inspects uncommitted staged/working-tree diffs,
 * enforces 0-byte diff on protected paths, checks deleted validation lines (-),
 * detects leftover [DEBUG-xxxx] probes, flags flaky test sleeps, scans for leaked secrets,
 * checks UTF-8 BOM hygiene, and flags test-suite reward-hacking modifiers.
 */

import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

function runGit(args, allowFailure = false) {
  try {
    return execFileSync('git', args, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }).trim();
  } catch (err) {
    if (allowFailure) return '';
    throw err;
  }
}

function main() {
  const baseRef = process.argv[2] || '';
  const headRef = process.argv[3] || 'HEAD';
  const protectedPathsCsv = process.env.PROTECTED_PATHS || '';

  console.log('=== APEX BUG HUNTER: PREFLIGHT DIFF & BOUNDARY SCAN (JS v2.0) ===');
  console.log(`Timestamp: ${new Date().toISOString()}`);

  const insideWorkTree = runGit(['rev-parse', '--is-inside-work-tree'], true);
  if (insideWorkTree !== 'true') {
    console.error('[ERROR] Current directory is not inside a Git repository.');
    process.exit(1);
  }

  const currentBranch = runGit(['rev-parse', '--abbrev-ref', 'HEAD'], true);
  const currentCommit = runGit(['rev-parse', '--short', 'HEAD'], true);
  console.log(`Current Branch: ${currentBranch} (${currentCommit})`);

  let violations = 0;
  let warnings = 0;

  // 1. Resolve Scope
  let diffRange = '';
  const hasOriginMain = Boolean(runGit(['show-ref', '--verify', 'refs/remotes/origin/main'], true));

  if (baseRef) {
    diffRange = `${baseRef}...${headRef}`;
    console.log(`Resolved Scope: Differential Audit (${diffRange})`);
  } else if (hasOriginMain && currentBranch !== 'main') {
    diffRange = `origin/main...${headRef}`;
    console.log(`Resolved Scope: Branch Comparison (${diffRange})`);
  } else {
    console.log(`Resolved Scope: Whole-Branch / Full-Repository Audit (${currentBranch})`);
  }

  // 2. Uncommitted Working-Tree Status
  console.log('\n--- PASS 0: WORKING-TREE STATUS ---');
  const porcelain = runGit(['status', '--porcelain'], true);
  if (porcelain) {
    console.log('[INFO] Uncommitted changes detected in working tree:');
    const lines = porcelain.split('\n').slice(0, 10);
    for (const line of lines) console.log(`  ${line}`);
  } else {
    console.log('[OK] Working tree clean.');
  }

  // 3. Protected Zero-Touch Path Lock (Range + Working Tree)
  if (protectedPathsCsv) {
    console.log('\n--- PASS 1: PROTECTED ZERO-TOUCH PATH LOCK ---');
    const protectedPaths = protectedPathsCsv
      .split(',')
      .map((p) => p.trim())
      .filter(Boolean);

    for (const pPath of protectedPaths) {
      let rangeDiff = '';
      if (diffRange) {
        rangeDiff = runGit(['diff', diffRange, '--', pPath], true);
      }
      const wipDiff = runGit(['diff', 'HEAD', '--', pPath], true);
      const totalBytes = Buffer.byteLength(rangeDiff + wipDiff, 'utf8');

      if (totalBytes !== 0) {
        console.error(`[P0 BLOCKER] Protected path modified (${totalBytes} diff bytes): ${pPath}`);
        violations++;
      } else {
        console.log(`[OK] Protected path verified 0-byte diff: ${pPath}`);
      }
    }
  }

  // 4. Differential Line-Deletion (-) Scan for Validation and Security Gates
  console.log('\n--- PASS 2: DIFFERENTIAL LINE-DELETION (-) AUDIT ---');
  let diffText = '';
  if (diffRange) {
    diffText += runGit(['diff', diffRange, '--unified=0'], true) + '\n';
  }
  diffText += runGit(['diff', 'HEAD', '--unified=0'], true);

  const gateRegex = /(\.refine\(|\.superRefine\(|safeParse\(|\.strict\(|structuredClone\(|FOR UPDATE|owner_id|tenant_id|deletedAt|archivedAt|listTools\()/;
  const removedGates = diffText
    .split('\n')
    .filter((line) => line.startsWith('-') && !line.startsWith('---') && gateRegex.test(line));

  if (removedGates.length > 0) {
    console.log('[WARNING] Critical validation, auth, or tenant predicates found in deleted lines (-):');
    for (const line of removedGates.slice(0, 8)) {
      console.log(`  ${line}`);
    }
    warnings++;
  } else {
    console.log('[OK] Zero critical validation or tenant predicates detected in deleted lines.');
  }

  // 5. UTF-8 BOM Check on Tracked Files
  console.log('\n--- PASS 3: UTF-8 BOM & MANIFEST HYGIENE SCAN ---');
  const trackedFiles = runGit(['ls-files'], true)
    .split('\n')
    .map((f) => f.trim())
    .filter(Boolean);

  const bomFiles = [];
  for (const relFile of trackedFiles) {
    const fullPath = path.resolve(process.cwd(), relFile);
    if (!fs.existsSync(fullPath) || fs.statSync(fullPath).isDirectory()) continue;
    try {
      const fd = fs.openSync(fullPath, 'r');
      const buf = Buffer.alloc(3);
      const bytesRead = fs.readSync(fd, buf, 0, 3, 0);
      fs.closeSync(fd);
      if (bytesRead === 3 && buf[0] === 0xef && buf[1] === 0xbb && buf[2] === 0xbf) {
        bomFiles.push(relFile);
      }
    } catch {
      // ignore unreadable files
    }
  }

  if (bomFiles.length > 0) {
    console.log('[P1 CRITICAL] UTF-8 BOM detected in tracked files:');
    for (const f of bomFiles) console.log(`  ${f}`);
    violations++;
  } else {
    console.log('[OK] Zero tracked files contain a UTF-8 Byte Order Mark (BOM).');
  }

  // 6. Test-Harness Reward-Hacking Scan (.skip, .only, .todo, .fails)
  console.log('\n--- PASS 6: TEST-HARNESS & SUPPRESSION AUDIT ---');
  const skippedTests = runGit(
    ['grep', '-nE', '\\b(describe|it|test)\\.(skip|only|todo|fails)\\b', '--', 'tests/', '*.test.*', '*.spec.*'],
    true
  );
  if (skippedTests) {
    console.log('[P1 CRITICAL] Skipped or focused tests detected:');
    console.log(skippedTests.split('\n').slice(0, 5).join('\n'));
    violations++;
  } else {
    console.log('[OK] Zero .skip/.only/.todo/.fails modifiers detected in test files.');
  }

  // 7. Leftover Debug Probes [DEBUG-xxxx]
  console.log('\n--- PASS 7: DIAGNOSTIC PROBE RESIDUE SCAN ---');
  const debugProbes = runGit(
    ['grep', '-nE', '\\[DEBUG-[a-f0-9]{4}\\]', '--', 'src/', 'tests/'],
    true
  );
  if (debugProbes) {
    console.log('[VIOLATION] Leftover [DEBUG-xxxx] probes detected in source or tests:');
    console.log(debugProbes.split('\n').slice(0, 5).join('\n'));
    violations++;
  } else {
    console.log('[OK] Zero leftover [DEBUG-xxxx] diagnostic probes detected.');
  }

  // 8. Arbitrary Sleep / Timeout Detection
  const flakySleeps = runGit(
    ['grep', '-nE', '\\b(waitForTimeout|setTimeout)\\(', '--', 'tests/'],
    true
  );
  if (flakySleeps) {
    console.log('[WARNING] Arbitrary sleep/timeout detected in test files (consider condition-based-waiting):');
    console.log(flakySleeps.split('\n').slice(0, 5).join('\n'));
    warnings++;
  } else {
    console.log('[OK] Zero arbitrary waitForTimeout calls detected in tests.');
  }

  // 9. Leaked Secrets & API Keys (REDACT-01)
  console.log('\n--- PASS 8: SECRET & API KEY SCAN (REDACT-01) ---');
  const secretLeaks = runGit(
    ['grep', '-nE', '(ghp_[A-Za-z0-9_]{36}|sk-[A-Za-z0-9]{32,}|xoxb-[A-Za-z0-9-]{20,}|-----BEGIN (RSA|EC|OPENSSH|PRIVATE) KEY-----)', '--', 'src/', 'tests/'],
    true
  );
  if (secretLeaks) {
    console.log('[VIOLATION] Hardcoded secret or private key found:');
    console.log(secretLeaks.split('\n').slice(0, 5).join('\n'));
    violations++;
  } else {
    console.log('[OK] Zero hardcoded API keys or private keys found.');
  }

  console.log('\n=== PREFLIGHT SCAN SUMMARY ===');
  console.log(`Violations: ${violations}`);
  console.log(`Warnings:   ${warnings}`);

  if (violations > 0) {
    console.error(`FAIL: Preflight boundary scan failed with ${violations} violation(s).`);
    process.exit(1);
  }

  console.log('SUCCESS: Preflight boundary scan passed.');
  process.exit(0);
}

main();
