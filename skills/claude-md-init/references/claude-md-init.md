# Claude MD Init Reference

Deeper guidance for scaffolding or refreshing a project's `CLAUDE.md` with owner-locked, verified-commit rules. Read this before the first run in a new project.

## Why A Marker-Based Merge

A project's `CLAUDE.md` usually has content a human wrote: architecture notes, build commands, style rules. This skill must never overwrite that. `scripts/init-claude-md.cjs` only ever touches the block between:

```text
<!-- claude-md-init:start -->
...
<!-- claude-md-init:end -->
```

- If the file does not exist, it is created with a one-line title plus the managed block.
- If the file exists and has markers, only the text between them is replaced.
- If the file exists without markers, the managed block is appended once. It is never inserted a second time -- re-running the script always finds the markers after the first run.

Never hand-edit inside the markers; the next run will overwrite it. Put project-specific notes outside the markers.

## Determining Owner Identity

The email in the Commit Identity section becomes the address GitHub uses to attribute commits on the contribution graph. Get this right:

1. Prefer `git config user.name` / `git config user.email` already set in the target project.
2. If unset, ask the user directly for their name and the email verified on their GitHub account (Settings → Emails). Do not guess a personal email from a commit history or profile page.
3. Never fall back to a placeholder or an assistant's own identity.

## Cloud Vs Local Verified Commits

The generated block states both paths; understand why they differ before explaining it to a user:

- **Cloud sessions** (Claude Code on the web, or any container-based agent) have no private signing key. `git commit -S` in that environment either fails or silently produces an unsigned commit. The only way to get GitHub's Verified badge on work done in the cloud is to push a branch and merge it through the GitHub web UI or API -- GitHub signs the merge/squash commit with its own key.
- **Local sessions** run on a machine the user controls, so a real GPG or SSH signing key can live there. Once configured, `git commit` signs directly and shows Verified immediately, with no merge-through-UI step required.

Do not claim a direct cloud commit is signed. Do not tell a local user they must merge through the UI if they already have local signing configured -- that step is a cloud-only workaround.

## One-Time Local Signing Setup (Portable)

Give this to a user who wants direct local commits to show Verified. Replace `<name>` / `<email>` with their real values.

**SSH signing (recommended, matches modern GitHub defaults):**

```bash
ssh-keygen -t ed25519 -C "<email>" -f ~/.ssh/id_ed25519_signing
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519_signing.pub
git config --global commit.gpgsign true
```

Then add `~/.ssh/id_ed25519_signing.pub` on GitHub under Settings → SSH and GPG keys → New SSH key → key type **Signing Key**.

**GPG signing (alternative):**

```bash
gpg --full-generate-key
gpg --list-secret-keys --keyid-format=long
gpg --armor --export <KEY_ID>
git config --global user.signingkey <KEY_ID>
git config --global commit.gpgsign true
```

Add the exported public key on GitHub under Settings → SSH and GPG keys → New GPG key.

**Verify either path:**

```bash
git commit -S -m "test: verify signing"
git log -1 --show-signature
```

Then check the commit page on GitHub shows the green **Verified** badge.

## Stripping Default AI Attribution

Some harnesses append `Co-Authored-By: <assistant>` or a session-identity trailer by default. The managed block's rule 2 exists specifically to override that default: pass a clean commit message with no such trailer, regardless of what the harness would add automatically.
