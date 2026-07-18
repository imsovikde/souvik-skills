#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

const START_MARKER = "<!-- claude-md-init:start -->";
const END_MARKER = "<!-- claude-md-init:end -->";

function parseArgs(argv) {
  const args = { target: ".", name: null, email: null, repo: null };
  const positionals = [];

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--name") {
      args.name = argv[(index += 1)];
    } else if (arg === "--email") {
      args.email = argv[(index += 1)];
    } else if (arg === "--repo") {
      args.repo = argv[(index += 1)];
    } else {
      positionals.push(arg);
    }
  }

  if (positionals[0]) {
    args.target = positionals[0];
  }

  return args;
}

function run(command, cwd) {
  try {
    return execSync(command, { cwd, stdio: ["ignore", "pipe", "ignore"] }).toString().trim();
  } catch {
    return "";
  }
}

function detectGitIdentity(targetDir) {
  return {
    name: run("git config user.name", targetDir),
    email: run("git config user.email", targetDir)
  };
}

function detectRepoSlug(targetDir) {
  const remote = run("git remote get-url origin", targetDir);
  const match = remote.match(/github\.com[:/]+([^/]+)\/([^/.]+?)(?:\.git)?$/);
  return match ? `${match[1]}/${match[2]}` : null;
}

function readJson(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch {
    return null;
  }
}

function detectPackageManager(targetDir) {
  if (fs.existsSync(path.join(targetDir, "pnpm-lock.yaml"))) {
    return "pnpm";
  }
  if (fs.existsSync(path.join(targetDir, "yarn.lock"))) {
    return "yarn";
  }
  if (fs.existsSync(path.join(targetDir, "package-lock.json"))) {
    return "npm";
  }
  if (
    fs.existsSync(path.join(targetDir, "requirements.txt")) ||
    fs.existsSync(path.join(targetDir, "pyproject.toml"))
  ) {
    return "pip";
  }
  return null;
}

function detectDeployTarget(targetDir) {
  if (fs.existsSync(path.join(targetDir, "vercel.json"))) {
    return "Vercel";
  }
  if (fs.existsSync(path.join(targetDir, "wrangler.toml"))) {
    return "Cloudflare Pages";
  }
  if (fs.existsSync(path.join(targetDir, "netlify.toml"))) {
    return "Netlify";
  }
  return null;
}

function buildBlock({ name, email, repoSlug, pkgName, packageManager, deployTarget }) {
  const lines = [];

  lines.push(START_MARKER);
  lines.push("");
  lines.push("## Repo Snapshot");
  lines.push("");
  if (pkgName) {
    lines.push(`- Package: \`${pkgName}\``);
  }
  if (repoSlug) {
    lines.push(`- Repository: \`${repoSlug}\``);
  }
  if (packageManager) {
    lines.push(`- Package manager: ${packageManager}`);
  }
  if (deployTarget) {
    lines.push(`- Deploy target: ${deployTarget}`);
  }
  lines.push("");
  lines.push("## Commit Identity & Attribution (hard rule)");
  lines.push("");
  lines.push("Every commit in this repo -- from any environment (cloud, local, or CI) -- must satisfy:");
  lines.push("");
  lines.push(
    `1. **Author is only ${name}.** Use \`${name} <${email}>\` (the GitHub-verified email). Set at session start:`
  );
  lines.push("");
  lines.push("   ```bash");
  lines.push(`   git config user.name "${name}"`);
  lines.push(`   git config user.email "${email}"`);
  lines.push("   ```");
  lines.push("");
  lines.push("2. **No AI attribution.** Never add `Co-Authored-By:` trailers for Claude or any AI tool, and never add");
  lines.push(
    `   \`Claude-Session:\` or other assistant-identity trailers. Only ${name}'s name may appear on the GitHub`
  );
  lines.push("   contribution graph. Strip any trailer the harness would add by default.");
  lines.push("");
  lines.push("## Verified Commits (hard rule)");
  lines.push("");
  lines.push("Every commit that lands on the default branch must show GitHub's green **Verified** badge.");
  lines.push("");
  lines.push(
    "- **From cloud:** the container holds no private signing key, so a direct cloud commit cannot be"
  );
  lines.push(
    "  cryptographically signed. Commit to a feature branch with the identity above and a clean message, push,"
  );
  lines.push(
    "  then merge through the GitHub web UI/API -- GitHub signs the resulting commit, so it lands Verified."
  );
  lines.push(
    `- **From local:** sign with ${name}'s own GPG or SSH signing key (\`git config commit.gpgsign true\`),`
  );
  lines.push("  confirm `git log -1 --show-signature`, and confirm the GitHub commit page shows Verified after push.");
  lines.push("- Do not substitute an unsigned direct commit on the default branch when a verified commit was requested.");
  lines.push("");
  lines.push(END_MARKER);

  return lines.join("\n");
}

function mergeIntoClaudeMd(existing, block, pkgName) {
  if (existing === null) {
    const title = pkgName
      ? `# CLAUDE.md\n\nGuidance for Claude (and any AI agent) working in the ${pkgName} project.\n\n`
      : "# CLAUDE.md\n\n";
    return `${title}${block}\n`;
  }

  const startIndex = existing.indexOf(START_MARKER);
  const endIndex = existing.indexOf(END_MARKER);

  if (startIndex !== -1 && endIndex !== -1 && endIndex > startIndex) {
    const before = existing.slice(0, startIndex);
    const after = existing.slice(endIndex + END_MARKER.length);
    return `${before}${block}${after}`;
  }

  const separator = existing.endsWith("\n") ? "\n" : "\n\n";
  return `${existing}${separator}${block}\n`;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const targetDir = path.resolve(args.target);

  if (!fs.existsSync(targetDir)) {
    console.error(`ERROR: target directory does not exist: ${targetDir}`);
    process.exitCode = 1;
    return;
  }

  const gitIdentity = detectGitIdentity(targetDir);
  const name = args.name || gitIdentity.name;
  const email = args.email || gitIdentity.email;

  if (!name || !email) {
    console.error(
      "ERROR: could not determine owner name/email. Pass --name and --email, or set git config user.name/user.email."
    );
    process.exitCode = 1;
    return;
  }

  const repoSlug = args.repo || detectRepoSlug(targetDir);
  const pkg = readJson(path.join(targetDir, "package.json"));
  const pkgName = pkg ? pkg.name : null;
  const packageManager = detectPackageManager(targetDir);
  const deployTarget = detectDeployTarget(targetDir);

  const block = buildBlock({ name, email, repoSlug, pkgName, packageManager, deployTarget });
  const claudeMdPath = path.join(targetDir, "CLAUDE.md");
  const existing = fs.existsSync(claudeMdPath) ? fs.readFileSync(claudeMdPath, "utf8") : null;
  const updated = mergeIntoClaudeMd(existing, block, pkgName);

  fs.writeFileSync(claudeMdPath, updated);
  console.log(`${existing === null ? "Created" : "Updated"} ${path.relative(process.cwd(), claudeMdPath) || "CLAUDE.md"}`);
}

main();
