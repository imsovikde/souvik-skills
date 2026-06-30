---
name: delink-github
description: Safely isolate a copied GitHub repository by removing Git history, GitHub workflow metadata, inherited license metadata, stale project names, outside repository links, and author contacts before starting clean local Git history.
---

# Delink GitHub

Use this skill when the user explicitly wants to detach, isolate, rename, clean, reinitialize, delink, disconnect, unpublish, or start fresh Git history for a repository copied from another GitHub project.

## Safety Rule

This workflow is destructive. Before running `reset`, confirm the user wants to permanently remove existing root `.git`, root `.github`, root `LICENSE*` or `COPYING*` files, inherited repository metadata, and stale project references. If the user already gave explicit approval in the current request, proceed with the guarded script command.

## Workflow

1. Identify the project root. Prefer an explicit absolute path or positional target.
2. Preview the destructive changes:

```bash
python <skill-dir>/scripts/delink.py plan <project-root> --rename-from old-project --rename-to new-project
```

3. If the plan matches the request, run the reset:

```bash
python <skill-dir>/scripts/delink.py reset <project-root> --rename-from old-project --rename-to new-project --yes
```

4. Verify the result:

```bash
git -C <final-project-root> remote -v
git -C <final-project-root> branch --show-current
git -C <final-project-root> log --oneline --max-count=3
```

The remote list should be empty, the branch should be `main` unless changed with `--branch`, and the new history should contain only the new local initial commit unless `--no-commit` was used.

## Script

Use `scripts/delink.py` for deterministic operations.

Commands:

- `plan`: print removals, rename variants, license cleanup, metadata rewrites, directory renames, and Git commands that would run.
- `reset`: remove root GitHub linkage, purge inherited metadata, optionally rename project references/directories, initialize Git, stage all files, and create an initial commit.

Target path:

- Positional target: `python delink.py plan C:\path\to\project`
- Backward-compatible flag: `python delink.py plan --target C:\path\to\project`
- Defaults to the current working directory when no target is supplied.

Useful options:

- `--rename-from <old>`: old project name to replace across source, config, and docs.
- `--rename-to <new>`: new project name and repository slug source.
- `--branch <name>`: initial branch name. Defaults to `main`.
- `--message <text>`: initial commit message. Defaults to `initial commit`.
- `--no-commit`: initialize and stage files without creating a commit.
- `--yes`: required for `reset`.

## Rename And Isolation Behavior

When `--rename-from` and `--rename-to` are provided, the script replaces dynamic casing variants:

- kebab-case: `old-project` to `new-project`
- snake_case: `old_project` to `new_project`
- PascalCase: `OldProject` to `NewProject`
- camelCase: `oldProject` to `newProject`
- UPPER_CASE: `OLD_PROJECT` to `NEW_PROJECT`
- uppercase compact: `OLDPROJECT` to `NEWPROJECT`
- lowercase compact: `oldproject` to `newproject`
- spaced words: `old project` to `new project`

The script skips lockfiles, dependency folders, generated folders, and binary assets to avoid breaking dependency resolution or media files.

It renames matching internal directories, including Python package folders such as `old_project`, and renames the root folder when its name matches a derived old-name variant.

## License And Metadata Cleanup

The script removes root `LICENSE*` and `COPYING*` files. It also strips common inherited license metadata from `README.md`, `setup.py`, `setup.cfg`, `pyproject.toml`, and `package.json`, including:

- license badges
- README license sections
- license classifiers
- `license`, `license_files`, and similar metadata lines
- `package.json` license fields

It rewrites contact metadata to the local Git identity, falling back to `Souvik Dey <imsovikde@gmail.com>`, and redirects GitHub repository URLs to:

```text
https://github.com/imsovikde/<new-repo-name>
```

## Guardrails

- Do not run this on a parent directory, home directory, drive root, or filesystem root.
- Do not run this to remove someone else's history unless the user owns the repository or has confirmed authority.
- Do not preserve GitHub Actions, issue templates, or pull request templates; the root `.github` directory is intentionally removed.
- Do not silently process only one rename option; `--rename-from` and `--rename-to` must be provided together.
- If `git commit` fails because identity is missing, configure `git config user.name` and `git config user.email`, then rerun or commit manually.

## Verification

When this skill changes, run:

```bash
python skills/delink-github/scripts/test_delink.py
npm run validate:skills
npm test
npm run build
node bin/souvik-skills.cjs install delink-github --force
```

After installing locally, restart Codex so the updated skill metadata loads.
