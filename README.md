# Souvik Skills

Marketplace-ready agent skills by Souvik Dey.

[![CI](https://github.com/imsovikde/souvik-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/imsovikde/souvik-skills/actions/workflows/ci.yml)
[![CodeQL](https://github.com/imsovikde/souvik-skills/actions/workflows/codeql.yml/badge.svg)](https://github.com/imsovikde/souvik-skills/actions/workflows/codeql.yml)
[![npm version](https://img.shields.io/npm/v/%40imsovikde%2Fskills)](https://www.npmjs.com/package/@imsovikde/skills)
[![npm downloads](https://img.shields.io/npm/dm/%40imsovikde%2Fskills)](https://www.npmjs.com/package/@imsovikde/skills)
[![GitHub stars](https://img.shields.io/github/stars/imsovikde/souvik-skills?style=social)](https://github.com/imsovikde/souvik-skills/stargazers)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Souvik Skills is the public skill directory for reusable developer and research workflows created by [Souvik Dey](https://github.com/imsovikde). The repository is designed to work like a professional skill catalog: every skill is a self-contained folder with a `SKILL.md`, optional resources, agent UI metadata, and an NPM-ready installer path.

[Website](https://souvik-skills.vercel.app) · [Skills](https://souvik-skills.vercel.app/skills) · [Install](#cross-agent-install) · [Docs](https://souvik-skills.vercel.app/docs) · [Releases](https://github.com/imsovikde/souvik-skills/releases) · [NPM](https://www.npmjs.com/package/@imsovikde/skills)

## Marketplace Site

The repository includes a Vercel-ready and Cloudflare Pages-ready static Next.js marketplace:

- Vercel: [souvik-skills.vercel.app](https://souvik-skills.vercel.app)
- Cloudflare Pages: [souvik-skills.pages.dev](https://souvik-skills.pages.dev)
- `/` - product homepage
- `/skills` - searchable skill marketplace
- `/skills/<skill-name>` - independent page for every skill folder
- `/install` - cross-agent install matrix
- `/docs` - repository and skill standards
- `/motion` - motion-system examples

Run it locally:

```bash
npm run dev
```

Build the static export:

```bash
npm run build
```

## Skills

| Skill | Purpose |
| --- | --- |
| `delink-github` | Safely isolate copied repositories by removing Git history, GitHub workflow metadata, inherited license metadata, stale names, outside links, and author contacts before starting clean local history. |
| `gh-ready` | Make repositories SEO-friendly, package-ready, release-ready, badge-ready, secure, and professional for GitHub publication. |
| `magento-team-lead` | Lead Magento Open Source and Adobe Commerce architecture, reviews, debugging, delivery planning, and releases. |
| `motioncraft` | Design, audit, and implement project-specific premium motion systems with psychology, archetype playbooks, tokens, reduced motion, and browser verification. |
| `score2md` | Convert MusicXML, MXL, ABC, MIDI, score PDFs/images, audio, video, and YouTube sources into playable Markdown ABC with verification reports and guarded media preflight. |

## Cross-Agent Install

Use the `skills` CLI when installing directly from this GitHub repository into an agent. Replace `<agent>` with the agent slug you use, such as `codex`, `claude-code`, `cursor`, or `gemini-cli`. Replace `<agent-cli>` with the command that starts the agent when trying a skill once.

### Project Only

```bash
npx -y skills add imsovikde/souvik-skills --skill delink-github --agent <agent>
npx -y skills add imsovikde/souvik-skills --skill gh-ready --agent <agent>
npx -y skills add imsovikde/souvik-skills --skill magento-team-lead --agent <agent>
npx -y skills add imsovikde/souvik-skills --skill motioncraft --agent <agent>
npx -y skills add imsovikde/souvik-skills --skill score2md --agent <agent>
```

### Global

```bash
npx -y skills add imsovikde/souvik-skills --skill delink-github --agent <agent> -g
npx -y skills add imsovikde/souvik-skills --skill gh-ready --agent <agent> -g
npx -y skills add imsovikde/souvik-skills --skill magento-team-lead --agent <agent> -g
npx -y skills add imsovikde/souvik-skills --skill motioncraft --agent <agent> -g
npx -y skills add imsovikde/souvik-skills --skill score2md --agent <agent> -g
```

### Try Once

```bash
npx -y skills use imsovikde/souvik-skills@delink-github | <agent-cli>
npx -y skills use imsovikde/souvik-skills@gh-ready | <agent-cli>
npx -y skills use imsovikde/souvik-skills@magento-team-lead | <agent-cli>
npx -y skills use imsovikde/souvik-skills@motioncraft | <agent-cli>
npx -y skills use imsovikde/souvik-skills@score2md | <agent-cli>
```

## Claude Code Marketplace

Install these skills directly inside Claude Code as a plugin marketplace. Add the marketplace once,
then install any skill or the full bundle:

```text
/plugin marketplace add imsovikde/souvik-skills
/plugin install souvik-skills-all@souvik-skills
```

Install individual skills instead of the bundle:

```text
/plugin install delink-github@souvik-skills
/plugin install gh-ready@souvik-skills
/plugin install magento-team-lead@souvik-skills
/plugin install motioncraft@souvik-skills
/plugin install score2md@souvik-skills
```

Refresh to the latest catalog after new skills ship:

```text
/plugin marketplace update souvik-skills
```

The marketplace catalog is defined in `.claude-plugin/marketplace.json`; the OpenAI Codex discovery
manifest is `codex-plugin.json`.

## Codex Package Install

Install one skill into Codex from the NPM package:

```bash
npx @imsovikde/skills install delink-github
npx @imsovikde/skills install gh-ready
npx @imsovikde/skills install magento-team-lead
npx @imsovikde/skills install motioncraft
npx @imsovikde/skills install score2md
```

Install every skill:

```bash
npx @imsovikde/skills install all
```

List available skills:

```bash
npx @imsovikde/skills list
```

By default the installer copies skills into:

```text
%USERPROFILE%\.codex\skills
```

Set `CODEX_HOME` or pass `--dest <path>` to install elsewhere.

## Use

After installation, restart Codex so the new skill metadata is loaded.

Example prompts:

```text
Use $delink-github to safely detach, rename, clean inherited metadata, purge GitHub linkage, and start clean local Git history for this repository.
Use $gh-ready to make this project SEO-friendly, GitHub-ready, package-ready, and release-ready.
Use $magento-team-lead to lead this Adobe Commerce implementation review.
Use $motioncraft to design a project-specific premium motion system for this interface with a motion intent map, tokens, reduced-motion variants, and browser verification.
Use $score2md to convert this MusicXML score into a verified playable Markdown ABC file.
Use $score2md to convert this piano YouTube link only if the media preflight approves it, or explain how to override with --skip-preflight.
```

## Repository Standard

This repository follows the Souvik Skills standard:

- `guidance.md` defines the skill directory rules.
- `AGENTS.md` tells future agents how to create and maintain skills here.
- `NAMING.md` explains how skill and repository names are chosen.
- `LICENSE` grants MIT usage rights.
- `package.json` exposes the one-line NPM installer.

Do not create `context.md`. Use `guidance.md` as the durable repository guide.

## Development

Install dependencies, run the marketplace, and verify the repo:

```bash
npm install
npm run dev
npm run validate:skills
npm test
npm run build
```

Smoke-test the installer locally:

```bash
node bin/souvik-skills.cjs list
node bin/souvik-skills.cjs install all --dest ./tmp/codex-skills --force
npm run audit:motioncraft
```

## Deployment

See [`docs/deployment.md`](docs/deployment.md) for Vercel, Cloudflare Pages, and NPM release commands.

## Support And Troubleshooting

- If `npx -y skills add ...` fails, confirm GitHub can access `imsovikde/souvik-skills` and rerun the command.
- If `npx @imsovikde/skills ...` fails, verify the npm package with `npm view @imsovikde/skills version`.
- If Codex does not show a newly installed skill, restart Codex after installation.
- For bugs or feature requests, use the GitHub issue templates.
- For security concerns, follow `SECURITY.md` instead of opening a public issue.

## License

MIT. See `LICENSE`.
