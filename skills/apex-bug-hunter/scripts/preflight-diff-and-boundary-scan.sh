#!/usr/bin/env bash
# apex-bug-hunter: Preflight Differential & Boundary Scanner (v2.0)
# Scans git diff, working-tree changes, deleted invariants, leftover probes, and secret leaks.

set -euo pipefail

TARGET_BASE="${1:-origin/main}"
TARGET_HEAD="${2:-HEAD}"
PROTECTED_PATHS="${PROTECTED_PATHS:-}"

echo "=========================================================="
echo "  Apex Bug Hunter: Preflight Differential & Boundary Scan"
echo "=========================================================="
echo "Comparison Range: ${TARGET_BASE}...${TARGET_HEAD}"

# Verify git repository
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "ERROR: Not inside a valid git repository."
  exit 1
fi

VIOLATIONS=0
WARNINGS=0

# 1. Protected Zero-Touch Path Guard (Committed + Working Tree)
if [ -n "$PROTECTED_PATHS" ]; then
  echo "[1/6] Checking protected zero-touch paths..."
  IFS=',' read -ra PATHS <<< "$PROTECTED_PATHS"
  for PPATH in "${PATHS[@]}"; do
    PPATH=$(echo "$PPATH" | xargs)
    RANGE_DIFF=$(git diff "${TARGET_BASE}...${TARGET_HEAD}" -- "$PPATH" 2>/dev/null | wc -l || true)
    WIP_DIFF=$(git diff HEAD -- "$PPATH" 2>/dev/null | wc -l || true)
    TOTAL_DIFF=$((RANGE_DIFF + WIP_DIFF))
    if [ "$TOTAL_DIFF" -gt 0 ]; then
      echo "  [VIOLATION] Protected path '$PPATH' has modifications (${TOTAL_DIFF} diff lines)."
      VIOLATIONS=$((VIOLATIONS + 1))
    else
      echo "  [PASS] Protected path '$PPATH' is untouched (0-byte diff)."
    fi
  done
else
  echo "[1/6] No protected paths configured. Skipping zero-touch path guard."
fi

# 2. Uncommitted Working-Tree Diff Inspection
echo "[2/6] Inspecting uncommitted working-tree changes..."
PORCELAIN=$(git status --porcelain 2>/dev/null || true)
if [ -n "$PORCELAIN" ]; then
  echo "  [INFO] Uncommitted changes detected in working tree:"
  echo "$PORCELAIN" | head -n 10 | sed 's/^/    /'
else
  echo "  [PASS] Working tree clean."
fi

# 3. Differential Line-Deletion (-) Audit (Range + Working Tree)
echo "[3/6] Auditing deleted lines (-) for stripped invariants..."
DELETED_LINES=$( { git diff "${TARGET_BASE}...${TARGET_HEAD}" 2>/dev/null || true; git diff HEAD 2>/dev/null || true; } | grep "^-" | grep -v "^---" || true )

if [ -n "$DELETED_LINES" ]; then
  GATE_REGEX="(\.refine\(|\.superRefine\(|safeParse\(|\.strict\(|structuredClone\(|FOR UPDATE|owner_id|tenant_id|deletedAt|archivedAt|listTools\()"
  DELETED_GATES=$(echo "$DELETED_LINES" | grep -Ei "$GATE_REGEX" || true)
  if [ -n "$DELETED_GATES" ]; then
    echo "  [WARNING] Critical validation or state predicates found in deleted lines (-):"
    echo "$DELETED_GATES" | head -n 5 | sed 's/^/    /'
    WARNINGS=$((WARNINGS + 1))
  else
    echo "  [PASS] No critical validation or tenant predicates detected in deleted lines."
  fi
else
  echo "  [PASS] No deleted lines detected in diff."
fi

# 4. Test-Harness Masking Audit (.skip, .only, .todo)
echo "[4/6] Scanning for masked or skipped tests in diff and test files..."
ADDED_LINES=$( { git diff "${TARGET_BASE}...${TARGET_HEAD}" 2>/dev/null || true; git diff HEAD 2>/dev/null || true; } | grep "^+" | grep -v "^+++" || true )

if [ -n "$ADDED_LINES" ]; then
  TEST_MASKS=$(echo "$ADDED_LINES" | grep -Ei "(\.skip|\.only|\.todo|\.fails|describe\.skip|it\.skip|test\.skip|@unittest\.skip)" || true)
  if [ -n "$TEST_MASKS" ]; then
    echo "  [VIOLATION] Detected test masking in added diff:"
    echo "$TEST_MASKS" | head -n 5 | sed 's/^/    /'
    VIOLATIONS=$((VIOLATIONS + 1))
  else
    echo "  [PASS] No test masking directives found in added diff."
  fi
else
  echo "  [PASS] No added lines in diff to scan."
fi

# 5. Diagnostic Probe Residue & Sleep Scanner
echo "[5/6] Scanning for leftover [DEBUG-xxxx] probes and flaky sleeps..."
DEBUG_PROBES=$(git grep -nE "\[DEBUG-[a-f0-9]{4}\]" -- "src/" "tests/" 2>/dev/null || true)
if [ -n "$DEBUG_PROBES" ]; then
  echo "  [VIOLATION] Leftover [DEBUG-xxxx] probes detected:"
  echo "$DEBUG_PROBES" | head -n 5 | sed 's/^/    /'
  VIOLATIONS=$((VIOLATIONS + 1))
else
  echo "  [PASS] Zero leftover [DEBUG-xxxx] probes found."
fi

FLAKY_SLEEPS=$(git grep -nE "(waitForTimeout\(|setTimeout\()" -- "tests/" 2>/dev/null || true)
if [ -n "$FLAKY_SLEEPS" ]; then
  echo "  [WARNING] Arbitrary sleep/timeout detected in tests (consider condition-based-waiting):"
  echo "$FLAKY_SLEEPS" | head -n 5 | sed 's/^/    /'
  WARNINGS=$((WARNINGS + 1))
else
  echo "  [PASS] Zero arbitrary waitForTimeout calls detected."
fi

# 6. Hardcoded Secret & Token Leak Scanner (REDACT-01)
echo "[6/6] Scanning for hardcoded tokens and leaked private keys..."
SECRET_LEAKS=$(git grep -nE "(ghp_[A-Za-z0-9_]{36}|sk-[A-Za-z0-9]{32,}|xoxb-[A-Za-z0-9-]{20,}|-----BEGIN (RSA|EC|OPENSSH|PRIVATE) KEY-----)" -- "src/" "tests/" 2>/dev/null || true)
if [ -n "$SECRET_LEAKS" ]; then
  echo "  [VIOLATION] Potential hardcoded API secret or private key found:"
  echo "$SECRET_LEAKS" | head -n 5 | sed 's/^/    /'
  VIOLATIONS=$((VIOLATIONS + 1))
else
  echo "  [PASS] Zero hardcoded API keys or private keys found."
fi

echo "=========================================================="
echo "Scan Summary:"
echo "  Violations: $VIOLATIONS"
echo "  Warnings:   $WARNINGS"
echo "=========================================================="

if [ "$VIOLATIONS" -gt 0 ]; then
  echo "FAIL: Preflight boundary scan failed with $VIOLATIONS violation(s)."
  exit 1
fi

echo "SUCCESS: Preflight boundary scan passed."
exit 0
