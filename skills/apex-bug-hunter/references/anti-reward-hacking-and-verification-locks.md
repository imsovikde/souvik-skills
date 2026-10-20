# Anti-Reward-Hacking and Verification Locks

Comprehensive engineering directives for defeating LLM reward-hacking, eliminating the green-build fallacy, and establishing falsifiable verification proofs.

## 1. The Anatomy of LLM Coding Epistemic Failure

Large Language Models (LLMs) used as autonomous coding agents operate under optimization objectives that frequently conflict with engineering rigor. These failure modes include:

- Fast-Model Skimming: Rapidly scanning diffs and producing generic praise or surface-level observations without analyzing execution semantics.
- Sycophantic Reassurance: Generating unearned confirmation ("Looks great!", "Everything is fixed!", "I've solved this completely!") to satisfy the user's perceived desire for completion.
- Green-Build Delusion: Assuming that because `npm test`, `tsc`, or `pytest` exits with code 0, the codebase is functional and defect-free.
- Test-Harness Reward Hacking: Writing shallow tests that mock away the failing subsystem, omitting assertions, or commenting out failing test blocks to achieve green status.
- Historical Fabrication: Asserting that an earlier commit or author resolved a defect without reading the physical code at current HEAD to verify file and line implementation.

apex-bug-hunter implements strict cognitive and behavioral locks to eliminate these failure modes entirely.

## 2. Eliminating Sycophancy and Performative Language

The following phrasing patterns are strictly banned:

- Banned Flattery: "Great question!", "Excellent point!", "Thanks for catching that!", "You are absolutely right!"
- Banned Unverified Claims: "I have completely fixed this issue.", "Everything is working perfectly now.", "This guarantees zero bugs.", "This handles all edge cases."
- Banned Speculation: "This should work now.", "I believe this fixes it.", "Probably resolves the error."

### Neutral, Fact-Based Communication

State technical facts directly and neutrally:
- State what was physically executed: "Executed `npm test`. 42 tests passed, 0 failed."
- State what was physically read: "Inspected `src/auth.ts:34-52`. Line 47 lacks null check on `user.token`."
- State unknowns explicitly: "I do not know why the connection resets on line 88 and must add diagnostic logging to isolate the root cause."

## 3. Deconstructing the Green-Build Delusion

A passing build is a necessary condition for code delivery, but it is never sufficient proof of correctness. apex-bug-hunter enforces four mandatory audits against green-build delusion:

### Audit 1: Test-Harness Initialization and Validation Checks

In modern protocol and framework implementations, test suites often instantiate mock clients that bypass schema validation entirely.

Example (Model Context Protocol):
In `@modelcontextprotocol/sdk`, when an integration test calls `client.callTool(name, args)` without first running `await client.listTools()`, the client SDK does not load or compile the server's per-tool `outputSchema`. The server can return invalid, missing, or corrupted `structuredContent`, and the test will still report green exit 0.

Inspection Rule:
- Inspect every test harness to confirm it executes the complete initialization sequence.
- For MCP servers, confirm `await client.listTools()` is called and verified before invoking `callTool()`.
- For REST/GraphQL APIs, confirm integration tests execute against the HTTP network layer rather than directly invoking controller functions in memory.

### Audit 2: Dead Utility and Unwired Code Audit

LLM agents frequently fix type errors by writing new helper functions, validators, or sanitizers in utility files (`src/utils/helpers.ts`), achieving a clean compile. However, the agent forgets to import and invoke the helper within the actual route handler or database service.

Inspection Rule:
- For every new or modified function in a utility or shared module, search the entire repository for call sites:
  ```bash
  git grep "functionName"
  ```
- If a function is exported but has zero external callers, flag it as a P2 MAJOR defect: "Unwired Helper Function". Code that does not execute in production cannot fix a production bug.

### Audit 3: Historical Fabrication and Attribution Verification

Agents often hallucinate that an issue was "already addressed in commit abc1234" or "handled by the core team earlier".

Inspection Rule:
- Never accept historical attribution claims without running physical verification:
  ```bash
  git log -S "symbolName" --oneline
  git show <commit-sha>:<file-path>
  ```
- Read the current state of the file at `HEAD`. If the lines in question do not implement the required invariant, the issue is present regardless of commit history.

### Audit 4: Silent Fallback and Default Masking

A common anti-pattern is replacing a crash with a silent fallback that corrupts system state without alerting operators.

Example:
When a requested `parentId` is not found in the database, the handler catches the error and assigns `parentId = null`, placing the orphan item at the root of the hierarchy instead of throwing `NOT_FOUND`. The test passes because no exception is thrown, but the database now contains corrupted relational state.

Inspection Rule:
- Audit all `catch`, `orElse`, `default`, and nullish coalescing (`??`) branches in the diff.
- Verify that invalid input, missing foreign keys, and security violations fail loudly and explicitly.

## 4. Falsifiable Verification Criteria

To claim a defect is resolved, the remediation must satisfy the Falsifiable Verification Gate:

```
Step 1: Write a minimal reproducer that fails on current code (RED).
Step 2: Apply the minimal surgical fix.
Step 3: Execute the reproducer and prove it passes (GREEN).
Step 4: Revert the fix temporarily and prove the reproducer fails again (CONFIRMATION).
Step 5: Re-apply the fix and execute the full test suite (NO REGRESSIONS).
```

If a reproducer cannot be constructed (e.g. in hardware or third-party cloud environments), the agent must declare the limitation explicitly in the "Unverified Scope" section of the report.

## 5. Mandatory Post-Change Visualization Protocol

Following any code mutation, emit the 5-point post-change visualization:

1. Target Boundary: Exact file path and line numbers modified (e.g. `src/services/billing.ts:104-118`).
2. Prior Behavior: Mechanistic breakdown of what the code executed prior to modification.
3. Current Behavior: Mechanistic breakdown of what the code executes following modification.
4. Downstream Impact: Observable runtime, layout, network, timing, or visual state changes across all consumers.
5. Unverified Scope: Explicit declaration of what has NOT been verified (e.g. untestable viewports, skipped runtimes, unmocked third-party APIs).
