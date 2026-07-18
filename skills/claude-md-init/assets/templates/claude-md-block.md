<!-- claude-md-init:start -->

## Repo Snapshot

- Package: `{{PKG_NAME}}`
- Repository: `{{REPO_SLUG}}`
- Package manager: {{PACKAGE_MANAGER}}
- Deploy target: {{DEPLOY_TARGET}}

## Commit Identity & Attribution (hard rule)

Every commit in this repo -- from any environment (cloud, local, or CI) -- must satisfy:

1. **Author is only {{OWNER_NAME}}.** Use `{{OWNER_NAME}} <{{OWNER_EMAIL}}>` (the GitHub-verified email). Set at session start:

   ```bash
   git config user.name "{{OWNER_NAME}}"
   git config user.email "{{OWNER_EMAIL}}"
   ```

2. **No AI attribution.** Never add `Co-Authored-By:` trailers for Claude or any AI tool, and never add
   `Claude-Session:` or other assistant-identity trailers. Only {{OWNER_NAME}}'s name may appear on the GitHub
   contribution graph. Strip any trailer the harness would add by default.

## Verified Commits (hard rule)

Every commit that lands on the default branch must show GitHub's green **Verified** badge.

- **From cloud:** the container holds no private signing key, so a direct cloud commit cannot be
  cryptographically signed. Commit to a feature branch with the identity above and a clean message, push,
  then merge through the GitHub web UI/API -- GitHub signs the resulting commit, so it lands Verified.
- **From local:** sign with {{OWNER_NAME}}'s own GPG or SSH signing key (`git config commit.gpgsign true`),
  confirm `git log -1 --show-signature`, and confirm the GitHub commit page shows Verified after push.
- Do not substitute an unsigned direct commit on the default branch when a verified commit was requested.

<!-- claude-md-init:end -->
