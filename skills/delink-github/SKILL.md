---
name: delink-github
description: Safely detach a local project from GitHub by removing Git history, remotes, and the root .github directory, then creating a fresh local Git repository. Use only when the user explicitly wants to delink, disconnect, unpublish, reinitialize, remove GitHub linkage, erase Git history, or start clean Git history for a repository.
---

# Delink GitHub

Use this skill to reset a project from an existing GitHub-linked repository into a clean local Git repository.

## Safety Rule

This workflow is destructive. Before running `reset`, confirm the user wants to permanently remove the existing `.git` directory, all commit history, configured remotes, and the root `.github` directory. If the user already gave explicit approval in the current request, proceed with the guarded script command.

## Workflow

1. Identify the project root to delink. Prefer an explicit absolute `--target` path.
2. Run a preview first:

```bash
python <skill-dir>/scripts/delink.py plan --target <project-root>
```

3. If the plan matches the request, run the reset with explicit confirmation:

```bash
python <skill-dir>/scripts/delink.py reset --target <project-root> --yes
```

4. Verify the result:

```bash
git -C <project-root> remote -v
git -C <project-root> log --oneline --max-count=3
```

The remote list should be empty and the new history should contain only the new local initial commit, unless `--no-commit` was used.

## Script

Use `scripts/delink.py` for deterministic operations.

Commands:

- `plan`: print the target path, files that would be removed, and Git commands that would run.
- `reset`: remove root-level `.git` and `.github`, initialize a new Git repository, stage files, and create an initial commit.

Useful options:

- `--target <path>`: project root to operate on. Defaults to the current working directory.
- `--branch <name>`: initial branch name. Defaults to `main`.
- `--message <text>`: initial commit message. Defaults to `initial commit`.
- `--no-commit`: initialize and stage files without committing.
- `--yes`: required for `reset`.

## Guardrails

- Do not run this on a parent directory, home directory, drive root, or filesystem root.
- Do not run this to remove someone else's history unless the user owns the repository or has confirmed authority.
- Do not preserve GitHub Actions, issue templates, or pull request templates; this skill intentionally removes the root `.github` directory.
- Do not set Git user identity automatically. If `git commit` fails because identity is missing, tell the user to configure `git config user.name` and `git config user.email`, then rerun or commit manually.
