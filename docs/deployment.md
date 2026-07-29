# Deployment

Souvik Skills is a static Next.js App Router site. `next.config.mjs` uses `output: "export"`, so `npm run build` creates the deployable `out/` directory.

Production deployments:

- Vercel: <https://souvik-skills.vercel.app>
- Cloudflare Pages: <https://souvik-skills.pages.dev>

## Required checks

Run these before deploying:

```bash
npm run validate:skills
npm test
npm run build
```

When a public skill is added, removed, renamed, published, or materially updated, deploy both hosted marketplaces and verify the new catalog state on:

- `https://souvik-skills.vercel.app`
- `https://souvik-skills.pages.dev`

Required verification routes:

- `/`
- `/skills`
- `/skills/<skill-name>`
- `/install`
- `/docs`

## Vercel

Vercel can build the project from source:

```bash
vercel --prod
```

For a stale production site, force a fresh production deployment from the current `main` build:

```bash
vercel --prod --force
```

Expected settings:

- Framework: Next.js
- Build command: `npm run build`
- Output directory: `out`
- Node.js: 22 or any version satisfying `>=20.9.0`

## Cloudflare Pages

Use Wrangler direct upload after a successful build:

```bash
npx wrangler pages deploy out --project-name souvik-skills
```

For public skill catalog changes, deploy the current `out/` directory to the production branch:

```bash
npx wrangler pages deploy out --project-name souvik-skills --branch main
```

Expected settings for a Git-connected Pages project:

- Build command: `npm run build`
- Build output directory: `out`
- Node.js compatibility: `>=20.9.0`

## NPM package

The package exposes the `souvik-skills` CLI and ships only the skill/source files listed in `package.json`.

Dry-run before publishing:

```bash
npm pack --dry-run
```

## Release automation

This repository uses Release Please for versioning and changelog management:

1. Conventional commits land on `main`.
2. `.github/workflows/release-please.yml` opens or updates a release PR.
3. The release PR updates `package.json`, `package-lock.json`, `.release-please-manifest.json`, and `CHANGELOG.md`.
4. Merging the release PR creates a GitHub Release and tag, and the same workflow's `publish-npm` and
   `publish-github-packages` jobs run immediately after (gated on `releases_created`), checking out
   the release commit, validating, testing, building, and publishing.

The publish jobs intentionally use npm trusted publishing and provenance instead of an npm token in
repository secrets. Trusted publishing (OIDC) requires npm CLI 11.5.1 or later; both publish
workflows explicitly run `npm install -g npm@latest` before publishing because the npm CLI bundled
with `actions/setup-node`'s Node 22 can be older than that, in which case OIDC auth is silently
skipped and the publish fails with a generic `404 Not Found` rather than an auth error.

`.github/workflows/npm-publish.yml` duplicates the same publish steps and triggers on
`release: published`, but GitHub does not dispatch further workflow-triggering events for a release
created using the default `GITHUB_TOKEN` (release-please's release is created this way), so this
workflow does not currently fire as part of the release flow above. It only runs if a release is
published through some other path, such as the GitHub web UI with a personal account.

## NPM trusted publishing setup

Configure this once in the npm package settings for `@imsovikde/skills`:

- Publisher: GitHub Actions
- GitHub owner: `imsovikde`
- Repository: `souvik-skills`
- Workflow file: `.github/workflows/npm-publish.yml`
- Environment: leave blank unless a protected GitHub environment is later added

After trusted publishing is configured, the publish workflow can run:

```bash
npm publish --access public --provenance
```

GitHub Packages uses the workflow `GITHUB_TOKEN` and publishes the same scoped package to `https://npm.pkg.github.com` on each GitHub Release.

Manual publishing remains available only when release notes and version are ready:

```bash
npm publish --access public
```

Never commit NPM, GitHub, Vercel, or Cloudflare tokens.
