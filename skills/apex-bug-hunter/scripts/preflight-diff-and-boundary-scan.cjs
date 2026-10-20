#!/usr/bin/env node
/**
 * apex-bug-hunter: Cross-platform Preflight Differential & Boundary Scanner
 * Deterministically audits git diff for deleted invariants, stripped boundaries, and test masks.
 */

const { execSync } = require("child_process");

const targetBase = process.argv[2] || "origin/main";
const targetHead = process.argv[3] || "HEAD";
const protectedPathsEnv = process.env.PROTECTED_PATHS || "";

console.log("==========================================================");
console.log("  Apex Bug Hunter: Cross-Platform Preflight Boundary Scan");
console.log("==========================================================");
console.log(`Comparison: ${targetBase}...${targetHead}`);

let violations = 0;
let warnings = 0;

function runGit(cmd) {
  try {
    return execSync(`git ${cmd}`, { encoding: "utf8", stdio: ["pipe", "pipe", "ignore"] });
  } catch {
    return "";
  }
}

// Check inside git repository
const isInsideRepo = runGit("rev-parse --is-inside-work-tree").trim();
if (isInsideRepo !== "true") {
  console.error("ERROR: Not inside a valid git repository.");
  process.exit(1);
}

// 1. Protected Zero-Touch Path Guard
if (protectedPathsEnv) {
  console.log("[1/4] Checking protected zero-touch paths...");
  const paths = protectedPathsEnv.split(",").map((p) => p.trim()).filter(Boolean);
  for (const p of paths) {
    const diff = runGit(`diff ${targetBase}...${targetHead} -- "${p}"`);
    if (diff.trim().length > 0) {
      console.log(`  [VIOLATION] Protected path '${p}' has modifications.`);
      violations++;
    } else {
      console.log(`  [PASS] Protected path '${p}' is untouched.`);
    }
  }
} else {
  console.log("[1/4] No protected paths configured. Skipping zero-touch path guard.");
}

// 2. Differential Line-Deletion (-) Audit
console.log("[2/4] Auditing deleted lines (-) for stripped invariants...");
const rawDiff = runGit(`diff ${targetBase}...${targetHead}`);
const diffLines = rawDiff.split("\n");
const deletedLines = diffLines.filter((l) => l.startsWith("-") && !l.startsWith("---"));

if (deletedLines.length > 0) {
  const valRegex = /(safeParse|validate|assert|z\.object|schema\.parse)/i;
  const authRegex = /(tenant_?id|owner_?id|requireAuth|checkPermission|verifyToken)/i;
  const txRegex = /(transaction|beginTransaction|commit|rollback)/i;

  const deletedVal = deletedLines.filter((l) => valRegex.test(l));
  if (deletedVal.length > 0) {
    console.log(`  [WARNING] Detected ${deletedVal.length} deleted validation line(s):`);
    deletedVal.slice(0, 5).forEach((l) => console.log(`    ${l}`));
    warnings++;
  }

  const deletedAuth = deletedLines.filter((l) => authRegex.test(l));
  if (deletedAuth.length > 0) {
    console.log(`  [WARNING] Detected ${deletedAuth.length} deleted auth/tenant line(s):`);
    deletedAuth.slice(0, 5).forEach((l) => console.log(`    ${l}`));
    warnings++;
  }

  const deletedTx = deletedLines.filter((l) => txRegex.test(l));
  if (deletedTx.length > 0) {
    console.log(`  [WARNING] Detected ${deletedTx.length} deleted transaction line(s):`);
    deletedTx.slice(0, 5).forEach((l) => console.log(`    ${l}`));
    warnings++;
  }
} else {
  console.log("  [PASS] No deleted lines detected in diff.");
}

// 3. Test-Harness Masking Audit
console.log("[3/4] Scanning for masked or skipped tests in added diff...");
const addedLines = diffLines.filter((l) => l.startsWith("+") && !l.startsWith("+++"));
const testMaskRegex = /(\.skip|\.only|describe\.skip|it\.skip|test\.skip|@unittest\.skip)/i;
const maskedLines = addedLines.filter((l) => testMaskRegex.test(l));

if (maskedLines.length > 0) {
  console.log(`  [VIOLATION] Detected test masking in added diff:`);
  maskedLines.slice(0, 5).forEach((l) => console.log(`    ${l}`));
  violations++;
} else {
  console.log("  [PASS] No test masking directives found.");
}

// 4. Summary and Exit Code
console.log("[4/4] Scan Summary:");
console.log(`  Violations: ${violations}`);
console.log(`  Warnings:   ${warnings}`);

if (violations > 0) {
  console.log(`FAIL: Preflight boundary scan failed with ${violations} violation(s).`);
  process.exit(1);
}

console.log("SUCCESS: Preflight boundary scan passed.");
process.exit(0);
