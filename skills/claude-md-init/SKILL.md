---
name: claude-md-init
description: Scaffold or update a project's root CLAUDE.md with a concise repo snapshot and hard commit rules -- author identity locked to the real repository owner, no AI co-author or session trailers, and every commit verified (GitHub-merge signing for cloud sessions, local GPG/SSH signing otherwise). Use when a user asks to set up, generate, initialize, or refresh a project's CLAUDE.md, wants commits attributed only to their own GitHub account with no Claude or AI attribution, wants every commit to show GitHub's Verified badge, or asks to apply "the same CLAUDE.md setup" used in another project.
---

# Claude MD Init

Create or refresh the root `CLAUDE.md` for the current project so any AI agent working here inherits the same repo snapshot and the same non-negotiable commit rules, without re-deriving them from scratch each time and without clobbering content a human already wrote.

## Required Reference

Read `references/claude-md-init.md` before the first run in a new project, especially for the marker-based merge strategy and the local commit-signing setup that the generated `CLAUDE.md` points to.

Bundled resources:

- `scripts/init-claude-md.cjs`: detects project facts (package manager, git remote, deploy config) and creates or updates the managed block of `CLAUDE.md` between markers.
- `scripts/test_init_claude_md.cjs`: verifies the script creates, updates idempotently, and preserves human-authored content.
- `assets/templates/claude-md-block.md`: the managed block template, for a manual fallback when the script cannot run.

## Workflow

1. Determine the repository owner's real name and GitHub-verified email. Prefer an existing `git config user.name`/`user.email`, otherwise ask the user directly. Never guess or invent an email -- an unverifiable email breaks GitHub's contribution-graph attribution.
2. Run the bundled script against the target project:

   ```bash
   node scripts/init-claude-md.cjs <target-dir> --name "<Owner Name>" --email "<owner@example.com>"
   ```

   Omit `--name`/`--email` when they can be auto-detected from `git config`.
3. If `CLAUDE.md` does not exist, the script creates it with a short repo snapshot plus the managed block.
4. If `CLAUDE.md` already exists, the script replaces only the content between the `<!-- claude-md-init:start -->` and `<!-- claude-md-init:end -->` markers, leaving everything else the human wrote untouched. If the markers are missing, it appends the managed block once instead of guessing where to merge.
5. Confirm the emitted commit-identity email matches a real GitHub-verified address on the owner's account -- this is what makes commits attributed to the right person on the contribution graph.
6. Tell the user plainly: cloud sessions cannot cryptographically sign commits because the container holds no private key, so the Verified badge on cloud work comes from merging the pushed branch through the GitHub UI/API, not from `git commit -S`. Local sessions should follow `references/claude-md-init.md` to set up real GPG or SSH commit signing once.
7. Re-run the script whenever repo facts change (new deploy target, renamed package, new owner email) to refresh the managed block without hand-editing it.

## The Managed Block

The block written into `CLAUDE.md` always contains:

- A short repo snapshot (package/repo name, package manager, deploy target) inferred from the current project, never copied from another repository.
- **Commit Identity & Attribution**: every commit uses the owner's real name and GitHub-verified email; no `Co-Authored-By` or session/assistant trailers, ever.
- **Verified Commits**: cloud commits land Verified via a GitHub-UI merge; local commits are signed with the owner's own GPG or SSH key.

Everything outside the markers belongs to the project and must be preserved exactly.

## Verification

- `CLAUDE.md` exists and contains exactly one managed block bounded by the start/end markers.
- The email in the Commit Identity section is a real address the user confirmed, not a placeholder.
- Running the script twice in a row changes nothing on the second run (idempotent) unless a detected fact changed.
- Content the user wrote outside the markers is byte-for-byte unchanged.
- `node scripts/test_init_claude_md.cjs` passes.
