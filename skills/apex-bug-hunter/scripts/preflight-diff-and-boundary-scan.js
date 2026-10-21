#!/usr/bin/env node
/**
 * preflight-diff-and-boundary-scan.js
 * Cross-platform Node.js deterministic preflight scanner for apex-bug-hunter.
 * Resolves audit scope, enforces 0-byte diff on protected paths,
 * inspects deleted validation lines (-), checks UTF-8 BOM hygiene,
 * and flags test-suite reward-hacking modifiers (.skip, .only, .todo, .fails).
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

  console.log('=== APEX BUG HUNTER: PREFLIGHT DIFF & BOUNDARY SCAN (JS) ===');
  console.log(`Timestamp: ${new Date().toISOString()}`);

  const insideWorkTree = runGit(['rev-parse', '--is-inside-work-tree'], true);
  if (insideWorkTree !== 'true') {
    console.error('[ERROR] Current directory is not inside a Git repository.');
    process.exit(1);
  }

  const currentBranch = runGit(['rev-parse', '--abbrev-ref', 'HEAD']);
  const currentCommit = runGit(['rev-parse', '--short', 'HEAD']);
  console.log(`Current Branch: ${currentBranch} (${currentCommit})`);

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

  // 2. Protected Zero-Touch Path Lock
  if (protectedPathsCsv && diffRange) {
    console.log('\n--- PASS 0: PROTECTED ZERO-TOUCH PATH LOCK ---');
    const protectedPaths = protectedPathsCsv
      .split(',')
      .map((p) => p.trim())
      .filter(Boolean);

    for (const pPath of protectedPaths) {
      const diffOutput = runGit(['diff', diffRange, '--', pPath], true);
      const changedBytes = Buffer.byteLength(diffOutput, 'utf8');
      if (changedBytes !== 0) {
        console.error(`[P0 BLOCKER] Protected path modified (${changedBytes} diff bytes): ${pPath}`);
        process.exit(2);
      } else {
        console.log(`[OK] Protected path verified 0-byte diff: ${pPath}`);
      }
    }
  }

  // 3. Differential Line-Deletion (-) Scan for Validation and Security Gates
  if (diffRange) {
    console.log('\n--- PASS 2: DIFFERENTIAL LINE-DELETION (-) AUDIT ---');
    console.log(`Changed files in ${diffRange}:`);
    console.log(runGit(['diff', '--name-status', diffRange], true) || '(none)');

    const unifiedDiff = runGit(['diff', diffRange, '--unified=0'], true);
    const gateRegex = /(\.refine\(|\.superRefine\(|safeParse\(|\.strict\(|owner_id|tenant_id|deletedAt|archivedAt|listTools\()/;
    const removedGates = unifiedDiff
      .split('\n')
      .filter((line) => line.startsWith('-') && !line.startsWith('---') && gateRegex.test(line));

    console.log('\nScanning removed lines (-) for weakened validation, auth, or tenant predicates...');
    if (removedGates.length > 0) {
      console.log('[WARNING] Critical validation or state predicates found in deleted lines (-):');
      for (const line of removedGates) {
        console.log(`  ${line}`);
      }
    } else {
      console.log('[OK] No obvious validation or tenant predicates found in deleted lines.');
    }
  }

  // 4. UTF-8 BOM Check on Tracked Files
  console.log('\n--- PASS 3: UTF-8 BOM & MANIFEST HYGIENE SCAN ---');
  const trackedFiles = runGit(['ls-files'], true)
    .split('\n')
    .map((f) => f.trim())
    .filter(Boolean);

  const bomFiles = [];
  for (const relFile of trackedFiles) {
    const fullPath = path.resolve(process.cwd(), relFile);
    if (!fs.existsSync(fullPath) || fs.statSync(fullPath).isDirectory()) continue;
    const fd = fs.openSync(fullPath, 'r');
    const buf = Buffer.alloc(3);
    const bytesRead = fs.readSync(fd, buf, 0, 3, 0);
    fs.closeSync(fd);
    if (bytesRead === 3 && buf[0] === 0xef && buf[1] === 0xbb && buf[2] === 0xbf) {
      bomFiles.push(relFile);
    }
  }

  if (bomFiles.length > 0) {
    console.log('[P1 CRITICAL] UTF-8 BOM detected in tracked files:');
    for (const f of bomFiles) console.log(`  ${f}`);
  } else {
    console.log('[OK] Zero tracked files contain a UTF-8 Byte Order Mark (BOM).');
  }

  // 5. Test-Harness Reward-Hacking Scan (.skip, .only, .todo, .fails, @ts-ignore)
  console.log('\n--- PASS 6: TEST-HARNESS & SUPPRESSION AUDIT ---');
  const skippedTests = runGit(
    ['grep', '-nE', '\\b(describe|it|test)\\.(skip|only|todo|fails)\\b', '--', 'tests/', '*.test.*', '*.spec.*'],
    true
  );
  if (skippedTests) {
    console.log('[P1 CRITICAL] Skipped or focused tests detected in test suite:');
    console.log(skippedTests);
  } else {
    console.log('[OK] Zero .skip/.only/.todo/.fails modifiers detected in test files.');
  }

  const tsSuppressions = runGit(
    ['grep', '-nE', '(@ts-ignore|@ts-expect-error|eslint-disable)', '--', 'src/'],
    true
  );
  if (tsSuppressions) {
    console.log('[WARNING] Type or lint suppressions detected in src/ (verify each is justified):');
    console.log(tsSuppressions);
  } else {
    console.log('[OK] Zero @ts-ignore / @ts-expect-error / eslint-disable directives in src/.');
  }

  console.log('\n=== PREFLIGHT SCAN COMPLETE ===');
}

main();
