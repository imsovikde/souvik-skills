# Changelog

All notable changes to Souvik Skills are documented here.

## [0.6.0](https://github.com/imsovikde/souvik-skills/compare/v0.5.0...v0.6.0) (2026-06-30)


### Features

* guard score2md media transcription ([e862d21](https://github.com/imsovikde/souvik-skills/commit/e862d21bfc6ff4534dd257ad3e65fd94ff6e971c))
* upgrade delink-github isolation ([9a16c5a](https://github.com/imsovikde/souvik-skills/commit/9a16c5a92d85fbc92234709a8f0f0648e22d03e3))

## [0.5.0](https://github.com/imsovikde/souvik-skills/compare/v0.4.0...v0.5.0) (2026-06-30)


### Features

* harden score2md media conversion ([324c228](https://github.com/imsovikde/souvik-skills/commit/324c228db7b910c92d27a652657735015af017bd))


### Bug Fixes

* require hosted skill marketplace updates ([aa80157](https://github.com/imsovikde/souvik-skills/commit/aa801577ec938a6b4a64b4af3d70179e7e1739f3))
* require verified skill deployments ([91263ff](https://github.com/imsovikde/souvik-skills/commit/91263ffa1c5668ec5cdc245ef33dc4ba007adb91))

## [0.4.0](https://github.com/imsovikde/souvik-skills/compare/v0.3.0...v0.4.0) (2026-06-29)


### Features

* harden score2md marketplace release ([f86343a](https://github.com/imsovikde/souvik-skills/commit/f86343acd183000b94fb553a459c5829c99a7603))

## [0.3.0](https://github.com/imsovikde/souvik-skills/compare/v0.2.0...v0.3.0) (2026-06-29)


### Features

* document full agent sync protocol ([22648cc](https://github.com/imsovikde/souvik-skills/commit/22648ccb9a15105dd49902c5b5a737986d89b3cc))

## [0.2.0](https://github.com/imsovikde/souvik-skills/compare/v0.1.4...v0.2.0) (2026-06-29)


### Features

* upgrade motioncraft strategy system ([06390e1](https://github.com/imsovikde/souvik-skills/commit/06390e14980c1cea4299af7337e912bdd27a92d8))

## [0.1.4](https://github.com/imsovikde/souvik-skills/compare/v0.1.3...v0.1.4) (2026-06-28)


### Bug Fixes

* publish packages from release please ([665927d](https://github.com/imsovikde/souvik-skills/commit/665927d2208fb75d9cb3f2c1c855d053b006b9ac))

## [0.1.3](https://github.com/imsovikde/souvik-skills/compare/v0.1.2...v0.1.3) (2026-06-28)


### Bug Fixes

* support npm token publish fallback ([f1d184f](https://github.com/imsovikde/souvik-skills/commit/f1d184fac04640f29364eecf04d3e48541688159))

## 0.1.2 - 2026-06-28

- Upgraded `gh-ready` into a professional repository launch protocol covering SEO/AEO/GEO discoverability, package metadata, badges, releases, GitHub settings, provenance, and AI-agent readiness.
- Added a read-only `gh-ready` audit script and reusable community-file templates for repository readiness work.
- Added Release Please and npm trusted-publishing workflow files so GitHub releases can publish `@imsovikde/skills` without committed npm tokens.
- Added README visual and badge guidance for GitHub stars, npm downloads, quick links, feature-card tables, and hosted interactive docs/demo pages.
- Added GitHub Packages publishing on release alongside npm publishing.
- Enabled repository Actions workflow permissions for Release Please PR automation and updated workflows to current action major versions.

## 0.1.0 - 2026-06-26

- Added the Souvik Skills marketplace site as a static-export Next.js App Router project.
- Added independent routes for every skill under `skills/`.
- Added install cards for project, global, and try-once skill usage across the supported agent matrix.
- Added build-time skill metadata loading from `SKILL.md` and `agents/openai.yaml`.
- Added design and motion system guidance for future frontend work.
- Added GitHub-ready community, CI, security, and deployment documentation.
