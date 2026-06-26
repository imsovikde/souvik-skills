# Souvik Skills

Marketplace-ready agent skills by Souvik Dey.

Souvik Skills is the public skill directory for reusable developer and research workflows created by [Souvik Dey](https://github.com/imsovikde). The repository is designed to work like a professional skill catalog: every skill is a self-contained folder with a `SKILL.md`, optional resources, agent UI metadata, and an NPM-ready installer path.

## Marketplace Site

The repository includes a Vercel-ready and Cloudflare Pages-ready static Next.js marketplace:

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
| `delink-github` | Safely remove Git history, GitHub remotes, and root `.github` files before starting clean local history. |
| `gh-ready` | Prepare repositories for professional GitHub publication, open-source release, client delivery, or package distribution. |
| `magento-team-lead` | Lead Magento Open Source and Adobe Commerce architecture, reviews, debugging, delivery planning, and releases. |
| `motioncraft` | Design and implement premium, accessible, high-performance interface motion systems. |

## Cross-Agent Install

Use the `skills` CLI when installing directly from this GitHub repository into an agent. Replace `<agent>` with the agent slug you use, such as `codex`, `claude-code`, `cursor`, or `gemini-cli`. Replace `<agent-cli>` with the command that starts the agent when trying a skill once.

### Project Only

```bash
npx -y skills add imsovikde/souvik-skills --skill delink-github --agent <agent>
npx -y skills add imsovikde/souvik-skills --skill gh-ready --agent <agent>
npx -y skills add imsovikde/souvik-skills --skill magento-team-lead --agent <agent>
npx -y skills add imsovikde/souvik-skills --skill motioncraft --agent <agent>
```

### Global

```bash
npx -y skills add imsovikde/souvik-skills --skill delink-github --agent <agent> -g
npx -y skills add imsovikde/souvik-skills --skill gh-ready --agent <agent> -g
npx -y skills add imsovikde/souvik-skills --skill magento-team-lead --agent <agent> -g
npx -y skills add imsovikde/souvik-skills --skill motioncraft --agent <agent> -g
```

### Try Once

```bash
npx -y skills use imsovikde/souvik-skills@delink-github | <agent-cli>
npx -y skills use imsovikde/souvik-skills@gh-ready | <agent-cli>
npx -y skills use imsovikde/souvik-skills@magento-team-lead | <agent-cli>
npx -y skills use imsovikde/souvik-skills@motioncraft | <agent-cli>
```

## Codex Package Install

Install one skill into Codex from the NPM package:

```bash
npx @imsovikde/skills install delink-github
npx @imsovikde/skills install gh-ready
npx @imsovikde/skills install magento-team-lead
npx @imsovikde/skills install motioncraft
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
Use $delink-github to safely detach this repository from GitHub and start clean local Git history.
Use $gh-ready to make this project GitHub-ready and NPM-ready.
Use $magento-team-lead to lead this Adobe Commerce implementation review.
Use $motioncraft to add premium accessible motion to this interface.
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
```

## Deployment

See [`docs/deployment.md`](docs/deployment.md) for Vercel, Cloudflare Pages, and NPM release commands.

## License

MIT. See `LICENSE`.
