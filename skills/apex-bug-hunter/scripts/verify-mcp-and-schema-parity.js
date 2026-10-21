#!/usr/bin/env node
/**
 * verify-mcp-and-schema-parity.js
 * Deterministic static & contract auditor for apex-bug-hunter.
 * Checks:
 * 1. Test harness initialization of client.listTools() before client.callTool()
 * 2. Tool handler return branches missing structuredContent when outputSchema is declared
 * 3. Unwired exported helper functions in src/utils or src/helpers
 * 4. In-place schema mutations lacking structuredClone()
 */

import fs from 'node:fs';
import path from 'node:path';

const ROOT_DIR = process.cwd();

function walkFiles(dir, fileList = []) {
  if (!fs.existsSync(dir)) return fileList;
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.name === 'node_modules' || entry.name === '.git' || entry.name === 'dist' || entry.name === 'build') {
      continue;
    }
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walkFiles(fullPath, fileList);
    } else if (/\.(ts|tsx|js|mjs|cjs)$/.test(entry.name)) {
      fileList.push(fullPath);
    }
  }
  return fileList;
}

function runAudit() {
  const allFiles = walkFiles(ROOT_DIR);
  const srcFiles = allFiles.filter((f) => !f.includes(`${path.sep}tests${path.sep}`) && !/\.(test|spec)\./.test(f));
  const testFiles = allFiles.filter((f) => f.includes(`${path.sep}tests${path.sep}`) || /\.(test|spec)\./.test(f));

  const findings = [];

  // 1. Check test files using callTool() without listTools()
  for (const testFile of testFiles) {
    const content = fs.readFileSync(testFile, 'utf8');
    if (content.includes('.callTool(') && !content.includes('.listTools(')) {
      findings.push({
        severity: 'P0 BLOCKER',
        pass: 'Pass 6 (Test-Harness Integrity)',
        file: path.relative(ROOT_DIR, testFile),
        message: 'Test file invokes client.callTool() without calling client.listTools() to initialize outputSchema validation.'
      });
    }
  }

  // 2. Check tool handlers declaring outputSchema for return paths lacking structuredContent
  for (const srcFile of srcFiles) {
    const content = fs.readFileSync(srcFile, 'utf8');
    if (content.includes('outputSchema') && content.includes('content:')) {
      const hasStructuredContent = content.includes('structuredContent');
      if (!hasStructuredContent) {
        findings.push({
          severity: 'P0 BLOCKER',
          pass: 'Pass 3 (Output Schema Parity)',
          file: path.relative(ROOT_DIR, srcFile),
          message: 'File declares outputSchema and returns content blocks, but never populates structuredContent.'
        });
      }
    }

    // 3. Check schema sanitizers mutating properties without structuredClone
    if (
      (content.includes('delete schema.') || content.includes('delete def.')) &&
      !content.includes('structuredClone(') &&
      !content.includes('JSON.parse(JSON.stringify(')
    ) {
      findings.push({
        severity: 'P1 CRITICAL',
        pass: 'Pass 3 (Multi-Client Schema Immutability)',
        file: path.relative(ROOT_DIR, srcFile),
        message: 'In-place property deletion on schema object detected without structuredClone() deep copy.'
      });
    }
  }

  // 4. Check exported helpers in utils/ or helpers/ that have zero production callers
  const helperFiles = srcFiles.filter((f) => /\/(utils|helpers)\//.test(f.replace(/\\/g, '/')));
  for (const helperFile of helperFiles) {
    const content = fs.readFileSync(helperFile, 'utf8');
    const exportRegex = /export\s+(?:async\s+)?function\s+([A-Za-z0-9_]+)/g;
    let match;
    while ((match = exportRegex.exec(content)) !== null) {
      const fnName = match[1];
      let usedInProd = false;
      for (const otherSrc of srcFiles) {
        if (otherSrc === helperFile) continue;
        const otherContent = fs.readFileSync(otherSrc, 'utf8');
        if (otherContent.includes(fnName)) {
          usedInProd = true;
          break;
        }
      }
      if (!usedInProd) {
        findings.push({
          severity: 'P1 CRITICAL',
          pass: 'Pass 2 (Unwired Dead Helper Code)',
          file: path.relative(ROOT_DIR, helperFile),
          message: `Exported helper function "${fnName}" has zero callers in production source files.`
        });
      }
    }
  }

  console.log('=== APEX BUG HUNTER: STATIC & MCP CONTRACT AUDIT ===');
  console.log(`Scanned ${srcFiles.length} source files and ${testFiles.length} test files.`);
  if (findings.length === 0) {
    console.log('[OK] Zero static contract or test-harness parity defects detected.');
    process.exit(0);
  } else {
    console.log(`[ALERT] Detected ${findings.length} potential contract/harness findings:`);
    for (const [idx, f] of findings.entries()) {
      console.log(`${idx + 1}. [${f.severity}] (${f.pass}) ${f.file}: ${f.message}`);
    }
    process.exit(1);
  }
}

runAudit();
