# Scientific Root-Cause Analysis and Ponytail Surgical Fixes

Comprehensive reference for systematic root-cause tracing, 4-phase scientific debugging, Karpathy coding laws, and Ponytail minimal-remediation engineering.

## 1. The Iron Law of Debugging

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

Attempting to patch symptoms without proving the root cause is engineering malpractice. Symptom patches introduce technical debt, mask deeper structural defects, and create unpredictable regression cascades.

If you have not pinpointed the exact mechanistic trigger where valid state transitions into invalid state, you are forbidden from proposing or applying code modifications.

## 2. The 4-Phase Scientific Debugging Cycle

apex-bug-hunter enforces the 4-phase scientific debugging methodology:

### Phase 1: Root Cause Investigation

Execute five diagnostic steps before writing or modifying any code:

1. Read Error Artifacts Completely: Examine stack traces, line numbers, error codes, and stderr output in full. Never skim or truncate stack traces.
2. Build a Deterministic Reproducer: Create the minimal automated script or test case that triggers the defect with 100% reliability. If the issue cannot be reproduced deterministically, gather additional telemetry instead of guessing.
3. Inspect Recent Changes: Check `git log` and `git diff` for recent commits, dependency upgrades, environment shifts, or database migrations that altered assumptions.
4. Backward Data-Flow Tracing:
   - Identify the point of failure (the line where an exception is thrown or invalid state is detected).
   - Trace the offending variable backward to the function that passed it.
   - Continue tracing upward across layer boundaries until locating the original site of corruption.
   - Fix the defect at the source of invalid data, never at the point of symptom detection.
5. Multi-Component Boundary Logging: When an error spans multiple distributed services (e.g. CLI to Gateway to Database):
   - Instrument entry and exit points at each component boundary.
   - Run the reproducer once to isolate which boundary corrupts or drops data.
   - Focus investigation strictly on the failing boundary.

### Phase 2: Pattern Analysis

Before designing a solution:
1. Locate Working Counterparts: Find similar functionality in the same codebase that functions correctly.
2. Compare Implementations: Line by line, identify every difference between the working code and the broken code. Do not dismiss subtle differences in configuration, typing, or async handling.
3. Check Authoritative References: Compare the implementation against canonical documentation and official protocol specifications. Skimming documentation leads to flawed assumptions.

### Phase 3: Hypothesis and Minimal Testing

1. Formulate a Single Falsifiable Hypothesis: State clearly: "I hypothesize that defect X occurs because condition Y causes state Z."
2. Design a Minimal Test: Make the smallest possible modification or probe to test this hypothesis in isolation. Test one variable at a time.
3. Evaluate Results:
   - If evidence confirms the hypothesis, proceed to Phase 4.
   - If evidence refutes the hypothesis, revert changes and formulate a new hypothesis. Never layer fixes atop failed assumptions.

### Phase 4: Implementation and Cold Verification

1. Write a Failing Test First: Commit the minimal reproducing test in a failing state.
2. Apply the Surgical Fix: Implement the root-cause fix at the appropriate architectural layer.
3. Run Cold Verification: Execute the reproduction test to verify it passes. Run the entire test suite to ensure zero collateral regressions.
4. Document the Cause: Record the mechanistic breakdown of what failed and why the fix works.

## 3. The 3-Strike Architectural Halt Rule

If three successive remediation attempts fail to resolve a defect or introduce secondary regressions, stop immediately.

Do not attempt a fourth fix. A 3-strike failure indicates an architectural mismatch rather than a localized bug:
- The underlying state model may be inadequate for the concurrency or lifecycle requirements.
- The interface abstraction may leak internal state across module boundaries.
- Assumptions regarding data ownership or transaction boundaries may be invalid.

Halt all code mutations, document the three attempted approaches and their failure evidence, and present the findings to the human architect for design review.

## 4. Andrej Karpathy's 4 Surgical Coding Laws

When modifying code, adhere strictly to the four surgical coding laws:

### Law 1: Think Before Coding

Do not jump into editing files based on initial intuition. State all implicit assumptions explicitly:
- What assumptions does this module make about caller permissions?
- What invariants must remain true before and after this function runs?
- How does this code behave when input collections are empty, null, or exceeding limits?

### Law 2: Simplicity First

Always implement the simplest solution that completely resolves the root cause:
- No speculative features: Do not add flags or configurability for hypothetical future needs.
- No unneeded abstractions: Do not introduce factories, adapters, or visitor patterns when a simple pure function solves the issue.
- The Senior Engineer Test: If a seasoned developer would look at the code and say "this is overcomplicated", reject the design.

### Law 3: Surgical Changes

Touch only what is strictly necessary to resolve the root cause:
- Zero collateral damage: Do not reformat adjacent lines, reorder unrelated imports, or modify unrelated comments.
- One concern per change: Isolate bug fixes from refactoring and formatting changes.
- Traceability: Every changed line must map directly to the root cause identified in Phase 1.

### Law 4: Goal-Driven Execution

Never rely on vague completion goals like "improve validation" or "make it more robust":
- Formulate concrete, falsifiable criteria: "When an invalid UUID is passed to `/api/v1/items/:id`, the route returns HTTP 400 Bad Request with code `INVALID_IDENTIFIER` instead of HTTP 500."
- Execute the verification loop until this exact condition is confirmed with raw output.

## 5. Ponytail Minimal-Fix Engineering

The Ponytail engineering philosophy dictates: the smallest change that fully solves the task is the best change.

Every line of code added to a repository represents ongoing maintenance debt, test burden, and review overhead. Prefer solutions in this order:

1. Deletion: The best fix is deleting redundant, dead, or misconfigured code that should never have existed.
2. Standard Library Reuse: Replace hand-rolled parsers or complex utility functions with standard library primitives (such as `URL`, `crypto.randomUUID`, `path.resolve`, or `datetime.timezone`).
3. Targeted Correction: Fix the single incorrect operator, condition, or argument at the exact line of root cause.
4. Addition: Add new functions or modules only when existing infrastructure cannot express the required invariant.

### The Lean Review Checklist

Before finalizing any fix, review every line of the proposed diff:
- Can this be accomplished by deleting code instead of adding code?
- Does the codebase already contain a helper that performs this task? Name its exact path.
- Is there any speculative error handling for conditions that are mathematically or structurally impossible?
- Did this change add any dependency that could be handled natively?

If any proposed line fails this checklist, strip it immediately.
