#!/usr/bin/env bash
# apex-bug-hunter: Preflight Differential & Boundary Scanner
# Scans git diff for deleted invariants, weakened schemas, and test masks.

set -euo pipefail

TARGET_BASE="${1:-origin/main}"
TARGET_HEAD="${2:-HEAD}"
PROTECTED_PATHS="${PROTECTED_PATHS:-}"

echo "=========================================================="
echo "  Apex Bug Hunter: Preflight Differential & Boundary Scan"
echo "=========================================================="
echo "Comparison: ${TARGET_BASE}...${TARGET_HEAD}"

# Verify git repository
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "ERROR: Not inside a valid git repository."
  exit 1
fi

VIOLATIONS=0
WARNINGS=0

# 1. Protected Zero-Touch Path Guard
if [ -n "$PROTECTED_PATHS" ]; then
  echo "[1/4] Checking protected zero-touch paths..."
  IFS=',' read -ra PATHS <<< "$PROTECTED_PATHS"
  for PPATH in "${PATHS[@]}"; do
    PPATH=$(echo "$PPATH" | xargs)
    DIFF_COUNT=$(git diff "${TARGET_BASE}...${TARGET_HEAD}" -- "$PPATH" 2>/dev/null | wc -l || true)
    if [ "$DIFF_COUNT" -gt 0 ]; then
      echo "  [VIOLATION] Protected path '$PPATH' has modifications (${DIFF_COUNT} diff lines)."
      VIOLATIONS=$((VIOLATIONS + 1))
    else
      echo "  [PASS] Protected path '$PPATH' is untouched (0-byte diff)."
    fi
  done
else
  echo "[1/4] No protected paths configured. Skipping zero-touch path guard."
fi

# 2. Differential Line-Deletion (-) Audit
echo "[2/4] Auditing deleted lines (-) for stripped invariants..."
DELETED_LINES=$(git diff "${TARGET_BASE}...${TARGET_HEAD}" 2>/dev/null | grep "^-" | grep -v "^---" || true)

if [ -n "$DELETED_LINES" ]; then
  # Check for deleted validation
  DELETED_VALIDATION=$(echo "$DELETED_LINES" | grep -Ei "(safeParse|validate|assert|z\.object|schema\.parse)" || true)
  if [ -n "$DELETED_VALIDATION" ]; then
    echo "  [WARNING] Detected deleted validation logic:"
    echo "$DELETED_VALIDATION" | head -n 5 | sed 's/^/    /'
    WARNINGS=$((WARNINGS + 1))
  fi

  # Check for deleted auth / tenant gates
  DELETED_AUTH=$(echo "$DELETED_LINES" | grep -Ei "(tenant_?id|owner_?id|requireAuth|checkPermission|verifyToken)" || true)
  if [ -n "$DELETED_AUTH" ]; then
    echo "  [WARNING] Detected deleted authorization or tenant boundary logic:"
    echo "$DELETED_AUTH" | head -n 5 | sed 's/^/    /'
    WARNINGS=$((WARNINGS + 1))
  fi

  # Check for deleted transactions
  DELETED_TX=$(echo "$DELETED_LINES" | grep -Ei "(transaction|beginTransaction|commit|rollback)" || true)
  if [ -n "$DELETED_TX" ]; then
    echo "  [WARNING] Detected deleted transaction wrapper:"
    echo "$DELETED_TX" | head -n 5 | sed 's/^/    /'
    WARNINGS=$((WARNINGS + 1))
  fi
else
  echo "  [PASS] No deleted lines detected in diff."
fi

# 3. Test-Harness Masking Audit
echo "[3/4] Scanning for masked or skipped tests in diff..."
ADDED_LINES=$(git diff "${TARGET_BASE}...${TARGET_HEAD}" 2>/dev/null | grep "^+" | grep -v "^+++" || true)

if [ -n "$ADDED_LINES" ]; then
  TEST_MASKS=$(echo "$ADDED_LINES" | grep -Ei "(\.skip|\.only|describe\.skip|it\.skip|test\.skip|@unittest\.skip)" || true)
  if [ -n "$TEST_MASKS" ]; then
    echo "  [VIOLATION] Detected test masking (.skip / .only) in added diff:"
    echo "$TEST_MASKS" | head -n 5 | sed 's/^/    /'
    VIOLATIONS=$((VIOLATIONS + 1))
  else
    echo "  [PASS] No test masking directives found."
  fi
else
  echo "  [PASS] No added lines in diff to scan."
fi

# 4. Summary and Exit Code
echo "[4/4] Scan Summary:"
echo "  Violations: $VIOLATIONS"
echo "  Warnings:   $WARNINGS"

if [ "$VIOLATIONS" -gt 0 ]; then
  echo "FAIL: Preflight boundary scan failed with $VIOLATIONS violation(s)."
  exit 1
fi

echo "SUCCESS: Preflight boundary scan passed."
exit 0
