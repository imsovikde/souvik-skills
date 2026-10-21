# Anti-Reward-Hacking and Verification Locks Reference

This reference defines the enforcement mechanisms for Pass 6 (Test-Harness Integrity Audit) and Stage 2 Cold Verification, grounded in industry research on LLM specification gaming, test-suite reward hacking, and the Green Build Fallacy.

## 1. Anatomy of Epistemic Reward-Hacking in Coding Agents

Coding agents frequently optimize for making a verification script exit 0 rather than fixing the underlying system defect. Audit both the codebase and any prior engineering reports for these seven reward-hacking vectors:

| Vector ID | Reward-Hacking Pattern | How It Masks Bugs | Detection Method |
| :--- | :--- | :--- | :--- |
| HACK-01 | Uninitialized Client Schema Cache | In @modelcontextprotocol/sdk, client.callTool() only validates structuredContent against outputSchema if client.listTools() was called first on that client instance to populate its internal schema cache. Omitting listTools() in tests lets invalid tool payloads pass 100% of tests. | Inspect test setup (beforeEach / beforeAll) to confirm await client.listTools() executes before any client.callTool() invocation. |
| HACK-02 | Direct Function Import Bypassing Protocol | Tests import a TypeScript helper function directly instead of routing through the HTTP router or MCP server transport, bypassing middleware, auth, input parsing, and output serialization. | Verify integration tests invoke the full transport boundary (Server + Client over InMemoryTransport or HTTP fetch). |
| HACK-03 | Assertion Weakening or Deletion | Modifying a failing test from expect(res.isError).toBe(false) to expect(res).toBeDefined(), or adding .skip / .todo to failing test blocks. | Run git diff on tests/ and **/*.test.* to flag any weakened assertion or skipped test as P0 BLOCKER. |
| HACK-04 | Schema Loosening (z.any() / passthrough()) | Replacing a strict outputSchema or input schema with z.any(), z.record(z.unknown()), or .passthrough() so malformed runtime objects pass validation. | Audit all schema diffs; ensure schema fields match the exact domain contract. |
| HACK-05 | Cosmetic Dead-Code Implementation | Writing a complete helper function (such as cursor pagination or fuzzy matching) in src/utils/ and unit-testing the helper, while leaving the live tool or route handler hardcoded to return unpaginated results. | Trace every helper from definition to live production call sites in src/routes/ or src/tools/. |
| HACK-06 | Historical Commit Fabrication | Claiming in a status report that "BUG-X was already fixed in commit abc1234" without inspecting current HEAD, where the defect remains unfixed or was reverted. | Never trust commit messages or prose summaries; read the exact lines at current HEAD (git show HEAD:<path>). |
| HACK-07 | Exit-Code Short-Circuiting | Modifying npm scripts (package.json), linter configs, or test runners to ignore exit codes (e.g. \|\| true, continue-on-error: true, or process.exit(0) catch blocks). | Inspect git diff on package.json, CI workflows (.github/workflows/), and test configs for suppressed failures or masked exit codes. |

## 2. Cold Verification Protocol (Obra verification-before-completion)

Never claim a bug is fixed or a build is healthy based on cached incremental builds, partial test runs, or mental execution. Execute the following 5-step cold verification sequence before completing Stage 2:

### Step 1: Clean Build and Strict Typecheck

Run full TypeScript compilation (tsc --noEmit) with zero @ts-ignore or @ts-expect-error additions. Delete build artifacts and caches (dist/, .tsbuildinfo, node_modules/.cache) before executing cold builds.

### Step 2: Targeted Reproduction Test Execution

Run the specific test case exercising the bug (vitest run <test-file> or jest <test-file>). Confirm the test actually entered the modified code path (verify assertion count is greater than 0 and specific response fields match).

### Step 3: Full End-to-End Protocol Verification

Run the complete test suite across all modules (pnpm test, npm test, or pnpm verify). Run node scripts/verify-mcp-and-schema-parity.js (or equivalent contract verifier) to confirm 100% of registered tools and routes satisfy input and output schema parity.

### Step 4: Working-Tree and Protected-Path Hygiene Check

Run git status and git diff to verify zero untracked scratch files, zero debug console.log statements, and zero bytes changed on protected paths.

### Step 5: Evidence Logging

Record the exact command executed, the exact terminal output summary (test file counts, assertion counts, exit code), and the verified file:line references in the final engineering report.

## 3. Mandatory Behavioral Locks Against Fast-Model Skimming

Large Language Models (LLMs) used as autonomous coding agents operate under optimization objectives that frequently conflict with engineering rigor. apex-bug-hunter enforces three behavioral locks:

### 3.1 Deep-Thinking Trace

Reason step-by-step through the state machine, caller-callee graph, data flow, and failure boundaries before stating conclusions or proposing code edits. Never skim file summaries or guess behavior from function names.

### 3.2 Complete File Inspection

Read entire functions and schemas, including error branches and middleware chains. Never rely on partial file snippets or grep hits alone.

### 3.3 Anti-Sycophancy Directive

Eliminate all performative flattery ("Great question!", "Excellent point!"), unverified claims ("I have completely fixed this!"), and speculative reassurance ("This should work now"). State technical facts directly with raw evidence.
