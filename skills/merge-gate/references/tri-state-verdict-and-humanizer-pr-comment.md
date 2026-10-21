# Tri-State Verdict and Humanizer PR Comment Reference

This reference establishes the normative rules for determining the tri-state pre-merge verdict, publishing authentic review reports to GitHub pull request comment threads, scrubbing AI prose tells using Wikipedia's 33 humanizer principles, and executing single-command surgical remediation.

## 1. The Tri-State Pre-Merge Verdict System

Every evaluated pull request or branch is assigned exactly one authoritative verdict:

```
                            [ Pre-Flight Merge Gate ]
                                        |
             +--------------------------+--------------------------+
             |                                                     |
             v                                                     v
    [ Fatal Blocker? ]                                   [ Meets All Invariants? ]
    (Crash, Security, Protected Path)                    (Clean Cold Build, 100% Tests)
             |                                                     |
      YES: VERDICT 3                                        YES: VERDICT 1
   [ HALT - DO NOT MERGE ]                               [ APPROVED FOR MERGE ]
             |                                                     |
             +--------------------------+--------------------------+
                                        |
                                  NO TO BOTH:
                                   VERDICT 2
                        [ PARTIAL / NEEDS IMPROVEMENT ]
```

### 1.1 VERDICT 1: APPROVED FOR MERGE (SAFE TO MERGE INTO MAIN)
- **Qualifying Criteria:**
  - The PR completely resolves its target objective formulated in Stage 1.
  - Introduces zero frontend/UI defects, zero backend logic errors, zero MCP contract drift, and zero security vulnerabilities.
  - Passes full cold test, lint, and build suites (`npm test`, `npm run build`, `pnpm verify`).
  - Passes cryptographic MD5 and SHA-256 protected-path checks against `origin/main`.
- **Gatekeeper Action:**
  - Post the humanized approval report to the GitHub PR comment thread.
  - HALT execution and wait for the user's explicit final merge confirmation (`gh pr merge` or `git merge`). Never auto-merge without final human approval.

### 1.2 VERDICT 2: PARTIAL / NEEDS IMPROVEMENT BEFORE MERGE
- **Qualifying Criteria:**
  - Zero fatal crashes, data loss risks, or security holes.
  - The PR introduces incomplete edge-case handling, missing empty/loading UI states, architectural coupling, suboptimal query patterns, or non-critical code smells.
- **Gatekeeper Action:**
  - Post the detailed improvement report to the GitHub PR comment thread explaining what works, what remains incomplete, and recommended surgical diffs.
  - Halt and wait for user direction: the user may command surgical remediation or choose to merge as-is.

### 1.3 VERDICT 3: HALT - DO NOT MERGE (BLOCKING DEFECTS FOUND)
- **Qualifying Criteria:**
  - Any fatal crash, unhandled rejection, data corruption, or broken tenant boundary.
  - Any missing `structuredContent` on non-error MCP return branches.
  - Any modified byte on protected zero-touch paths (MD5/SHA-256 mismatch).
  - Any test-harness reward-hacking (`HACK-01` through `HACK-12`) or suppressed tests (`.skip`, `.only`).
- **Gatekeeper Action:**
  - Immediately halt the merge pipeline.
  - Post the forensic blocking report to the GitHub PR comment thread with reproduction steps and exact `file:line` citations.
  - Present the Zero-Regression Fix Blueprint and wait for the user's execution command.

## 2. Authentic Human PR Review Comments (Wikipedia 33 Humanizer Principles)

When reviewing code, AI agents often produce sycophantic, wordy, and robotic reviews that irritate software engineers. All review comments posted to GitHub must adhere to the humanizer directives:

### 2.1 The Voice of a Senior Staff Engineer
- Write in the direct, concise, and pragmatic voice of an experienced engineer reviewing a teammate's pull request.
- Focus strictly on physical execution semantics: runtime errors, memory leaks, layout overflow at 320px, and missing test assertions.
- Skip conversational pleasantries: open directly with the verdict and key findings.

### 2.2 Strict Prohibition of Banned AI Vocabulary
The following words and phrases are banned from all PR review comments:

- Banned Words: `delve`, `pivotal`, `tapestry`, `testament`, `underscores`, `vital`, `seamless`, `holistic`, `paradigm`, `synergistic`, `beacon`, `embark`, `navigate`, `revolutionize`, `empower`, `foster`, `bolster`, `harness`, `catalyst`, `nuanced`, `vibrant`, `relentless`.
- Banned Theatrical Openers: "Here is the thing", "Let us dive in", "Certainly!", "Great work on this PR!", "Thanks for opening this PR!".
- Banned Superficial Participle Tails: "...highlighting the importance of...", "...ensuring that...", "...serving as a testament to...".
- Banned Not-X-But-Y Contrasts: "It is not just a feature, it is an architectural shift." State the technical fact directly.
- Banned Punctuation: Em-dashes (Unicode U+2014) and en-dashes (Unicode U+2013) are completely forbidden. Use colons, commas, or standard ASCII hyphens.

### 2.3 Automated Comment Validation
Before posting any review comment, the gatekeeper runs:

```bash
node scripts/preflight-merge-gate.js --verify-comment <comment-draft.md>
```

If the draft contains any em-dash, en-dash, banned AI vocabulary word, or UTF-8 BOM, the script exits with code 1 and blocks publication until the prose is cleansed.

### 2.4 GitHub PR Comment Publication
Publish verified comments directly to GitHub using the GitHub CLI:

```bash
gh pr comment <PR_NUMBER> --body-file <verified-comment.md>
```

## 3. Single-Command Surgical Auto-Remediation Protocol

When the user responds to Verdict 2 or Verdict 3 with a command to "Fix it", "Remediate", or "Execute fixes":

1. **Agree on Test Seams:** Identify public boundary seams for regression testing; avoid internal-module mocking.
2. **Author Failing Reproducer:** Write minimal reproduction test cases that fail cold on current code.
3. **Apply Minimal Fixes:** Implement surgical changes at the originating boundary adhering to Karpathy's 4 Surgical Coding Laws:
   - Law 1: Think before coding (surface hidden assumptions).
   - Law 2: Simplicity first (smallest change that solves root cause).
   - Law 3: Surgical changes (touch only necessary lines; zero reformatting).
   - Law 4: Goal-driven execution (concrete falsifiable completion criteria).
4. **Remove Debug Artifacts:** Confirm 100% of temporary `[DEBUG-xxxx]` probes and console logs are stripped.
5. **Cold Verification:** Run full test suites (`npm test`), build validation (`npm run build`), and the preflight scanner (`node scripts/preflight-merge-gate.js`).
6. **Granular Signed Commits:** Package fixes into conventional commits with GPG signing (`git commit -S -m "fix(<scope>): <summary> (BUG-XX)"`) with zero AI attribution trailers (`Co-authored-by`).
7. **Re-Evaluate Verdict:** Run the pre-flight gate again. Upon reaching Verdict 1, present the approval report to the user and prompt for final merge confirmation.
