# Deployment

Souvik Skills is a static Next.js App Router site. `next.config.mjs` uses `output: "export"`, so `npm run build` creates the deployable `out/` directory.

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

Publish when release notes and version are ready:

```bash
npm publish --access public
```

Never commit NPM, GitHub, Vercel, or Cloudflare tokens.
