#!/usr/bin/env node
/**
 * verify-mcp-and-schema-parity.js
 * Deterministic static & contract auditor for apex-bug-hunter v2.0.
 * Checks:
 * 1. Test harness initialization of client.listTools() before client.callTool()
 * 2. Tool handler per-return-branch structuredContent validation via balanced-brace parsing
 * 3. In-place schema mutations lacking structuredClone()
 * 4. Unwired exported helper functions in utils/ or helpers/ (comment-stripped caller scan)
 * 5. Internal-module mocking (HACK-08: vi.mock / jest.mock on relative paths)
 * 6. Tautological test assertions (HACK-09: expect(x).toBe(x))
 */

import fs from 'node:fs';
import path from 'node:path';

const ROOT_DIR = process.cwd();

function walkFiles(dir, fileList = []) {
  if (!fs.existsSync(dir)) return fileList;
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.name === 'node_modules' || entry.name === '.git' || entry.name === 'dist' || entry.name === 'build' || entry.name === '.next') {
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
        pass: 'Pass 7 (Test-Harness Integrity)',
        file: path.relative(ROOT_DIR, testFile),
        message: 'Test file invokes client.callTool() without calling client.listTools() to initialize outputSchema validation.'
      });
    }

    // 5. Internal-module mocking (HACK-08)
    const strippedTest = stripComments(content);
    const internalMockMatch = strippedTest.match(/(?:vi|jest)\.mock\s*\(\s*['"]\.\.?[\\/]/);
    if (internalMockMatch) {
      findings.push({
        severity: 'P1 CRITICAL',
        pass: 'Pass 7 (Internal-Module Mocking HACK-08)',
        file: path.relative(ROOT_DIR, testFile),
        message: 'Test file mocks internal relative module path rather than testing at public system boundaries.'
      });
    }

    // 6. Tautological assertions (HACK-09)
    const tautologicalMatch = strippedTest.match(/expect\s*\(\s*([a-zA-Z0-9_]+)\s*\)\.to(?:Be|Equal|StrictEqual)\s*\(\s*\1\s*\)/);
    if (tautologicalMatch) {
      findings.push({
        severity: 'P1 CRITICAL',
        pass: 'Pass 7 (Tautological Test Assertion HACK-09)',
        file: path.relative(ROOT_DIR, testFile),
        message: `Test contains circular tautological assertion: expect(${tautologicalMatch[1]}).toBe(${tautologicalMatch[1]}).`
      });
    }
  }

  // 2. Tool handler per-return-branch structuredContent validation
  for (const srcFile of srcFiles) {
    const rawContent = fs.readFileSync(srcFile, 'utf8');
    if (rawContent.includes('outputSchema')) {
      const cleanContent = stripComments(rawContent);
      const returnBlocks = extractReturnObjectBlocks(cleanContent);
      for (const block of returnBlocks) {
        if (block.text.includes('content:') && !block.text.includes('isError: true')) {
          if (!block.text.includes('structuredContent')) {
            findings.push({
              severity: 'P0 BLOCKER',
              pass: 'Pass 3 (Output Schema Return-Branch Parity)',
              file: `${path.relative(ROOT_DIR, srcFile)}:${block.line}`,
              message: 'Tool handler declares outputSchema and returns content, but this return branch lacks structuredContent.'
            });
          }
        }
      }
    }

    // 3. Check schema sanitizers mutating properties without structuredClone
    if (
      (rawContent.includes('delete schema.') || rawContent.includes('delete def.')) &&
      !rawContent.includes('structuredClone(') &&
      !rawContent.includes('JSON.parse(JSON.stringify(')
    ) {
      findings.push({
        severity: 'P1 CRITICAL',
        pass: 'Pass 3 (Multi-Client Schema Immutability)',
        file: path.relative(ROOT_DIR, srcFile),
        message: 'In-place property deletion on schema object detected without structuredClone() deep copy.'
      });
    }
  }

  // 4. Check exported helpers in utils/ or helpers/ with comment-stripped callers
  const helperFiles = srcFiles.filter((f) => /\/(utils|helpers)\//.test(f.replace(/\\/g, '/')));
  for (const helperFile of helperFiles) {
    const content = fs.readFileSync(helperFile, 'utf8');
    const cleanHelper = stripComments(content);
    const helperRegexes = [
      /export\s+(?:async\s+)?function\s+([A-Za-z0-9_]+)/g,
      /export\s+const\s+([A-Za-z0-9_]+)\s*=\s*(?:async\s+)?(?:\([^)]*\)|[A-Za-z0-9_]+)\s*=>/g,
      /export\s+const\s+([A-Za-z0-9_]+)\s*=\s*function/g
    ];

    for (const regex of helperRegexes) {
      let match;
      while ((match = regex.exec(cleanHelper)) !== null) {
        const fnName = match[1];
        let usedInProd = false;
        for (const otherSrc of srcFiles) {
          if (otherSrc === helperFile) continue;
          const otherContent = stripComments(fs.readFileSync(otherSrc, 'utf8'));
          if (otherContent.includes(fnName)) {
            usedInProd = true;
            break;
          }
        }
        if (!usedInProd) {
          findings.push({
            severity: 'P1 CRITICAL',
            pass: 'Pass 2 (Unwired Dead Helper Code HACK-05)',
            file: path.relative(ROOT_DIR, helperFile),
            message: `Exported helper "${fnName}" has zero callers in production source files (excluding comments).`
          });
        }
      }
    }
  }

  console.log('=== APEX BUG HUNTER: STATIC & MCP CONTRACT AUDIT (v2.0) ===');
  console.log(`Scanned ${srcFiles.length} source files and ${testFiles.length} test files.`);
  if (findings.length === 0) {
    console.log('[OK] Zero static contract, dead-code, or test-harness parity defects detected.');
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
