---
name: merge-gate
description: Pre-flight production merge gatekeeper for pull requests and branches. Performs full-project context comparison against main, whole-diff AST blast-radius auditing, frontend UI and taste checks, backend security and protocol parity, tri-state merge verdicts, and automated humanized PR review comments. Trigger automatically whenever the user provides a PR number (PR #N or PR URL), branch name, or asks for a pre-flight merge check, PR review, merge gate, merge verdict, or pre-merge audit against main.
---

# Merge Gate

A deterministic, full-stack pre-flight production merge gatekeeper. It unifies full-project context comparison against `main`, CodeRabbit and Qodo PR-Agent AST call-graph blast-radius traversal, Obra Superpowers systematic debugging (`systematic-debugging`, `defense-in-depth`, `condition-based-waiting`, `verification-before-completion`), tasteskill.dev frontend UI and anti-slop rules, Karpathy's 4 Surgical Coding Laws, and Wikipedia's 33 humanizer anti-AI-writing principles.

## When to Use

- Auditing a Pull Request (`PR #N` or PR URL) before merging into `main` or `production`

- Comparing a feature, fix, or release branch against `origin/main`

- Performing a pre-flight merge gatekeeper check on uncommitted working-tree changes

- Evaluating whether a PR completely resolves its target objective without collateral regressions

- Drafting and publishing an authentic human-voice GitHub PR review comment

- Generating an authoritative Tri-State Merge Verdict (`APPROVED`, `NEEDS IMPROVEMENT`, or `HALT - DO NOT MERGE`)

## 1. Cognitive Locks Against Epistemic Reward-Hacking and Premature Merges

Before inspecting any diff hunk or emitting any evaluation, engage all four cognitive locks:

### 1.1 Strict Prohibition of AI Sycophancy
- Ban all performative praise, conversational filler, and premature approval ("Great PR!", "Looks good to me!", "Code looks solid!").
- State technical findings, contract mismatches, responsive defects, and verification proofs plainly with exact `file:line` citations.

### 1.2 Whole-Project Context Over Flat Diffs
- Never evaluate a pull request as an isolated patch.
- Reconstruct full project context on `main` first: read `AGENTS.md`, `CLAUDE.md`, `INVARIANTS.md`, `HALL_OF_SHAME.md`, contract schemas, database models, and critical path callers.
- Compare what `main` expects against what the branch delivers.

### 1.3 Anti-Short-Circuiting and Zero Placeholder Code
- Never emit placeholder comments (`// ... existing code`, `/* rest of implementation */`, `// TODO`).
- Inspect 100% of changed files, routes, and components without skipping or early bailing.
- Record an explicit inspection receipt for every audited file before proceeding to the next.

### 1.4 Cryptographic Verification Over Assertion
- Verify protected zero-touch paths using cryptographic MD5 and SHA-256 hashes against `origin/main`.
- Any modification to protected paths (such as OAuth 2.1 routes or token authorities) triggers an immediate merge halt.

## 2. Universal Scope Resolution and Two-Stage Gate

Resolve the operational scope before executing inspection passes. Run `node scripts/preflight-merge-gate.js` to gather deterministic telemetry.

### 2.1 Three-Lane Scope Resolution

| Mode | Trigger Condition | Inspection Scope |
| :--- | :--- | :--- |
| **Pull Request Mode** | User provides `PR #N` or a PR URL | Fetch `git diff origin/main...HEAD`, PR commits, issue threads, and all upstream callers and downstream callees in the AST symbol graph |
| **Branch Comparison Mode** | User specifies a branch name | Audit `git diff origin/main...<branch>` plus all transitive call-graph dependencies |
| **Working-Tree Preflight Mode** | User requests pre-merge check on current work | Audit `git diff origin/main...HEAD` plus uncommitted staged and working-tree changes (`git diff HEAD` and `git status --porcelain`) |

### 2.2 Two-Stage Execution Gate

Operate in a strict two-stage gate unless the user explicitly commands immediate code mutation:

1. **Stage 1: Deep Audit, Tri-State Verdict, and PR Comment (Default):**
   - Execute the 4-Stage Pre-Flight Merge Pipeline across the resolved scope.
   - Run `node scripts/preflight-merge-gate.js` and `node scripts/validate-skill-md5.js`.
   - Determine the authoritative Tri-State Merge Verdict (`APPROVED`, `NEEDS IMPROVEMENT`, or `HALT`).
   - Draft the humanized review comment, verify it with `node scripts/preflight-merge-gate.js --verify-comment <draft-file>`, and post it to the GitHub PR thread (`gh pr comment <PR_NUMBER> --body-file <file>`).
   - HALT and wait for the user's explicit confirmation before merging or editing code.

2. **Stage 2: Surgical Auto-Remediation and Verified Merge (Triggered on User Command):**
   - When commanded to "Fix it" or "Execute fixes", apply approved surgical fixes adhering strictly to Karpathy's 4 laws.
   - Execute cold verification suites (`npm test`, `npm run build`, `npm run validate:skills`).
   - Commit fixes in granular GPG-signed commits (`git commit -S`) with zero AI attribution trailers.
   - If Verdict 1 is reached, merge the PR via `gh pr merge <PR_NUMBER> --squash` only after final user confirmation.

## 3. The 4-Stage Pre-Flight Merge Pipeline

Execute all four stages in sequence. Never skip stages even if an early blocker is discovered.

### Stage 1: Full-Project Context Reconstruction on `main`
- Understand the PR's stated objective from the title, PR description, linked issue, and commit history.
- Inspect `main` to identify existing domain models, schemas, and historical invariants.
- Determine whether the PR genuinely and completely solves the stated objective at runtime or introduces incomplete half-fixes.
- Consult `references/whole-project-main-diff-engine.md` for whole-project traversal rules.

### Stage 2: Whole-Diff AST & Security Blast-Radius Traversal
- Differential line-deletion (`-`) audit: verify deleted gates, schemas, `.refine()` constraints, or tenant predicates (`owner_id`, `tenant_id`).
- Bidirectional call-graph blast radius: traverse all upstream callers (fan-in) and downstream callees (fan-out) affected by modified symbols.
- Cryptographic zero-touch lock: verify MD5 and SHA-256 hashes of protected paths match `origin/main` byte-for-byte.
- Consult `references/whole-project-main-diff-engine.md` and `references/backend-security-and-mcp-gate.md`.

### Stage 3: Full-Stack Regression and Quality Gates
- **Frontend UI & Taste Gate:** Verify responsive collapse down to 320px viewport, complete interactive states (`loading`, `empty`, `error`, `disabled`, `focus-visible`), native dialog bans (`alert`, `confirm`, `prompt`), `dangerouslySetInnerHTML` ban, WCAG AA contrast (4.5:1), reduced-motion guards, and tasteskill.dev anti-slop rules. Consult `references/frontend-ui-and-taste-gate.md`.
- **Backend & Protocol Parity Gate:** Verify Model Context Protocol (MCP) per-return `outputSchema` vs `structuredContent` parity across 100% of branches, composite tenant isolation on database queries, atomic idempotency concurrency, zero unwired dead helpers, and zero test suppressions (`.skip`, `.only`, `.todo`). Consult `references/backend-security-and-mcp-gate.md`.

### Stage 4: Tri-State Verdict Determination & Humanized Review Publication
- Classify the PR into exactly one of three verdicts:
  1. `APPROVED FOR MERGE (SAFE TO MERGE INTO MAIN)`
  2. `PARTIAL / NEEDS IMPROVEMENT BEFORE MERGE`
  3. `HALT - DO NOT MERGE (BLOCKING DEFECTS FOUND)`
- Draft the review comment using Wikipedia's 33 humanizer principles (zero em/en-dashes, zero AI jargon, authentic veteran staff engineer voice).
- Run `node scripts/preflight-merge-gate.js --verify-comment <draft-file>`.
- Post the review comment directly to the GitHub PR thread (`gh pr comment <PR_NUMBER> --body-file <draft-file>`).
- Consult `references/tri-state-verdict-and-humanizer-pr-comment.md`.

## 4. The Tri-State Pre-Merge Verdict Matrix

| Verdict | Qualifying Criteria | Required Gatekeeper Action |
| :--- | :--- | :--- |
| **VERDICT 1: APPROVED FOR MERGE** | PR solves objective completely, introduces zero UI/security/protocol defects, passes cold builds and test suites, passes MD5/SHA-256 protected-path checks | Post humanized approval report to GitHub PR comment thread, HALT, and wait for user final merge command |
| **VERDICT 2: PARTIAL / NEEDS IMPROVEMENT** | Zero fatal crashes or security holes, but has incomplete edge-case handling, missing empty/loading states, architectural coupling, or code smells | Post improvement report to GitHub PR comment thread with surgical recommendations; wait for user direction |
| **VERDICT 3: HALT - DO NOT MERGE** | Any runtime crash, security breach, tenant leak, MCP schema drift, protected-path modification, or test reward-hacking detected | Immediately halt merge, post blocking report to GitHub PR comment thread, and present surgical fix blueprint |

## 5. Progressive Disclosure Reference Map

Load these auxiliary references when executing specific pipeline stages:

- `references/whole-project-main-diff-engine.md`: Protocol for reconstructing full repository context on `main`, mapping AST call-graph blast radius, line-deletion (`-`) analysis, and objective completion auditing.

- `references/frontend-ui-and-taste-gate.md`: Frontend UI checklist covering 320px responsive collapse, complete interactive states, native dialog bans, React state synchronization, WCAG AA contrast, and tasteskill.dev anti-slop rules.

- `references/backend-security-and-mcp-gate.md`: Backend checklist covering input and repository boundary validation, MCP outputSchema parity, database migration hygiene, composite tenant isolation, and test reward-hacking locks.

- `references/tri-state-verdict-and-humanizer-pr-comment.md`: Normative rules for the Tri-State Merge Verdict, automated GitHub PR comment posting, Wikipedia 33 humanizer rules, and surgical auto-remediation.

- `scripts/preflight-merge-gate.js`: Production-grade Node.js CLI scanner for cryptographic hash comparisons, diff parsing, UI anti-slop checks, MCP contract parity, and PR comment verification.

- `scripts/validate-skill-md5.js`: Node.js skill package integrity verifier and MD5/SHA-256 manifest generator.

## 6. Required Output Structure

### Stage 1 Output: Pre-Flight Merge Gate Report

```markdown
### Pre-Flight Merge Gate Evaluation: PR #<N>

**Verdict:** [ APPROVED FOR MERGE | PARTIAL / NEEDS IMPROVEMENT | HALT - DO NOT MERGE ]

#### 1. Target Objective Analysis
- Stated Objective: <concise summary of PR intent>
- Implementation Completeness: <Complete | Incomplete | Over-scoped>
- Edge Cases Handled / Missed: <mechanistic breakdown>

#### 2. AST Blast-Radius and Contract Verification
- Changed Components: <list of modified modules>
- Upstream Callers Affected: <verification of call sites>
- Protected Paths: <Untouched (MD5 match) | Modified (FAIL)>

#### 3. Frontend & Taste Findings
- 320px Viewport Compliance: <Pass | Defect file:line>
- Interactive UI States: <Complete | Missing states>
- Design Tokens & Anti-Slop: <Clean | Violations>

#### 4. Backend, Security & Protocol Findings
- Input & Boundary Validation: <Pass | Defect file:line>
- MCP Output Schema Parity: <100% Branches Verified | Defect file:line>
- Multi-Tenant Isolation: <Composite (owner_id, id) Bound | Leak Risk>

#### 5. Recommended Actions
- <Next step based on verdict>
```

### Stage 2 Output: Remediation and Merge Record

When commanded to execute fixes and merge:

1. **Commit Record:** Exact commit SHA, subject line, and `git show --stat` output.
2. **Cold Verification Evidence:** Raw terminal output from `npm test`, `npm run build`, and `node scripts/preflight-merge-gate.js`.
3. **Merge Evidence:** The exact `gh pr merge` output or squash commit SHA landing on `main`.
4. **Post-Change Visualization:** 5-point protocol: Target Boundary, Prior Behavior, Current Behavior, Downstream Impact, Unverified Scope.
