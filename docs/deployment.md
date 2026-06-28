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

## Vercel

Vercel can build the project from source:

```bash
vercel --prod
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
4. Merging the release PR creates a GitHub Release and tag.
5. `.github/workflows/npm-publish.yml` checks out that tag, runs validation/build/package dry-run, publishes to npm, and publishes the same package version to GitHub Packages.

The publish workflow intentionally uses npm trusted publishing and provenance instead of an npm token in repository secrets.

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
