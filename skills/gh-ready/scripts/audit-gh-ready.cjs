#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const targetDir = path.resolve(process.argv[2] || ".");
const ignoreDirs = new Set([
  ".git",
  ".next",
  ".turbo",
  ".wrangler",
  "coverage",
  "dist",
  "node_modules",
  "out",
  "tmp"
]);

function rel(...parts) {
  return path.join(targetDir, ...parts);
}

function exists(...parts) {
  return fs.existsSync(rel(...parts));
}

function readText(...parts) {
  const file = rel(...parts);
  if (!fs.existsSync(file)) {
    return "";
  }
  return fs.readFileSync(file, "utf8");
}

function readJson(...parts) {
  try {
    return JSON.parse(readText(...parts));
  } catch {
    return null;
  }
}

function hasSection(markdown, heading) {
  return new RegExp(`^#{1,3}\\s+${escapeRegExp(heading)}\\b`, "im").test(markdown);
}

function hasAny(text, patterns) {
  return patterns.some((pattern) => pattern.test(text));
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function listFiles(dir = targetDir, collected = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (ignoreDirs.has(entry.name)) {
      continue;
    }

    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      listFiles(fullPath, collected);
    } else {
      collected.push(fullPath);
    }
  }
  return collected;
}

function findFiles(pattern) {
  return listFiles().filter((file) => pattern.test(path.relative(targetDir, file).replace(/\\/g, "/")));
}

function scoreCategory(name, checks) {
  const passed = checks.filter((check) => check.pass).length;
  const score = Math.round((passed / checks.length) * 5);
  const missing = checks.filter((check) => !check.pass).map((check) => check.label);
  return { name, score, passed, total: checks.length, missing };
}

function detectPrivateTraceHints(files) {
  const hints = [];
  const riskyName = /(^|\/)(\.env(\.|$)|\.npmrc$|id_rsa|.*\.(pem|p12|key|crt|log)$)/i;
  const riskyContent = [
    /npm_[A-Za-z0-9]{20,}/,
    /gh[pousr]_[A-Za-z0-9_]{20,}/,
    /AKIA[0-9A-Z]{16}/,
    /-----BEGIN (RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----/,
    /C:\\Users\\/i,
    /\/Users\/[^/\s]+\/(Desktop|Downloads|Projects)\//i
  ];

  for (const file of files) {
    const relative = path.relative(targetDir, file).replace(/\\/g, "/");
    if (/(^|\/)\.env\.example$/i.test(relative)) {
      continue;
    }
    if (riskyName.test(relative)) {
      hints.push(`${relative}: sensitive-looking filename`);
      continue;
    }

    const stat = fs.statSync(file);
    if (stat.size > 250_000) {
      continue;
    }

    let body = "";
    try {
      body = fs.readFileSync(file, "utf8");
    } catch {
      continue;
    }

    if (hasAny(body, riskyContent)) {
      hints.push(`${relative}: sensitive-looking content or local path`);
    }
  }

  return hints;
}

if (!fs.existsSync(targetDir) || !fs.statSync(targetDir).isDirectory()) {
  console.error(`Target is not a directory: ${targetDir}`);
  process.exit(1);
}

const files = listFiles();
const readme = readText("README.md");
const pkg = readJson("package.json");
const workflows = findFiles(/^\.github\/workflows\/.*\.ya?ml$/);
const issueTemplates = findFiles(/^\.github\/ISSUE_TEMPLATE\/.*\.ya?ml$/);
const codeql = workflows.some((file) => /codeql/i.test(path.basename(file)) || /codeql-action/i.test(readText(path.relative(targetDir, file))));
const hasCi = workflows.some((file) => /(ci|test|build)/i.test(path.basename(file)) || /npm (test|run build|run validate)/i.test(readText(path.relative(targetDir, file))));
const hasBadge = /\[!\[[^\]]+\]\([^)]+\)\]\([^)]+\)|!\[[^\]]+\]\([^)]+\)/.test(readme);
const privateHints = detectPrivateTraceHints(files);

const categories = [
  scoreCategory("Identity and positioning", [
    { label: "README.md exists", pass: Boolean(readme) },
    { label: "README starts with an H1 title", pass: /^#\s+\S+/m.test(readme) },
    { label: "LICENSE exists", pass: exists("LICENSE") || exists("LICENSE.md") },
    { label: "package description or repo description is present", pass: Boolean(pkg?.description || /description/i.test(readme)) },
    { label: "repository/homepage metadata exists", pass: Boolean(pkg?.repository || pkg?.homepage || /https?:\/\/github\.com\//i.test(readme)) }
  ]),
  scoreCategory("README as product page", [
    { label: "what/value proposition appears early", pass: readme.slice(0, 1200).length > 100 },
    { label: "installation section exists", pass: hasSection(readme, "Installation") || /install/i.test(readme) },
    { label: "quick start or use section exists", pass: hasSection(readme, "Quick Start") || hasSection(readme, "Use") || /quick start/i.test(readme) },
    { label: "testing/development commands are documented", pass: /npm (test|run test|run build|run validate|run dev)|pytest|cargo test|go test/i.test(readme) },
    { label: "license section exists", pass: hasSection(readme, "License") || /license/i.test(readme) }
  ]),
  scoreCategory("SEO AEO GEO discoverability", [
    { label: "first paragraph is descriptive", pass: readme.split(/\r?\n\r?\n/).some((block) => block.length > 80 && !block.startsWith("#")) },
    { label: "package keywords exist", pass: Array.isArray(pkg?.keywords) && pkg.keywords.length >= 3 },
    { label: "canonical links exist", pass: /https?:\/\//.test(readme) },
    { label: "FAQ or troubleshooting appears", pass: /FAQ|Troubleshooting|Support/i.test(readme) },
    { label: "accurate badges are present", pass: hasBadge }
  ]),
  scoreCategory("Install and usage", [
    { label: "copyable command blocks exist", pass: /```[\s\S]*?(npm|npx|pnpm|yarn|git|gh|python|cargo|go)\b/i.test(readme) },
    { label: "common commands documented", pass: /commands|scripts|development|test|build/i.test(readme) },
    { label: "configuration or environment documented", pass: /config|environment|\.env|settings/i.test(readme) || exists(".env.example") },
    { label: "usage examples exist", pass: /example|usage|prompt/i.test(readme) },
    { label: "support/troubleshooting path exists", pass: exists("SUPPORT.md") || /support|troubleshooting/i.test(readme) }
  ]),
  scoreCategory("Package metadata", [
    { label: "package.json exists", pass: Boolean(pkg) },
    { label: "name/version/description/license exist", pass: Boolean(pkg?.name && pkg?.version && pkg?.description && pkg?.license) },
    { label: "repository and bugs metadata exist", pass: Boolean(pkg?.repository && pkg?.bugs) },
    { label: "files or exports/bin controls package contents", pass: Boolean(pkg?.files || pkg?.exports || pkg?.bin) },
    { label: "engines metadata exists", pass: Boolean(pkg?.engines) }
  ]),
  scoreCategory("CI and quality gates", [
    { label: "GitHub workflow exists", pass: workflows.length > 0 },
    { label: "CI/test/build workflow exists", pass: hasCi },
    { label: "package test script exists", pass: Boolean(pkg?.scripts?.test) },
    { label: "build or validation script exists", pass: Boolean(pkg?.scripts?.build || pkg?.scripts?.["validate:skills"] || pkg?.scripts?.lint) },
    { label: "CodeQL or security scan exists", pass: codeql }
  ]),
  scoreCategory("Security posture", [
    { label: "SECURITY.md exists", pass: exists("SECURITY.md") },
    { label: "Dependabot configured", pass: exists(".github", "dependabot.yml") || exists(".github", "dependabot.yaml") },
    { label: "CodeQL workflow exists", pass: codeql },
    { label: ".env.example exists when config is mentioned", pass: exists(".env.example") || !/\.env|environment/i.test(readme) },
    { label: "no obvious private trace hints", pass: privateHints.length === 0 }
  ]),
  scoreCategory("Community health", [
    { label: "CONTRIBUTING.md exists", pass: exists("CONTRIBUTING.md") },
    { label: "CODE_OF_CONDUCT.md exists", pass: exists("CODE_OF_CONDUCT.md") },
    { label: "SUPPORT.md exists", pass: exists("SUPPORT.md") },
    { label: "issue templates exist", pass: issueTemplates.length > 0 },
    { label: "PR template or CODEOWNERS exists", pass: exists(".github", "PULL_REQUEST_TEMPLATE.md") || exists(".github", "CODEOWNERS") }
  ]),
  scoreCategory("Release process", [
    { label: "CHANGELOG.md exists", pass: exists("CHANGELOG.md") },
    { label: "release workflow exists", pass: workflows.some((file) => /release|publish/i.test(path.basename(file))) },
    { label: "package version exists", pass: Boolean(pkg?.version) },
    { label: "publish config or release docs exist", pass: Boolean(pkg?.publishConfig) || /publish|release/i.test(readme) || exists("docs", "deployment.md") },
    { label: "package files are constrained", pass: Boolean(pkg?.files || exists(".npmignore")) }
  ]),
  scoreCategory("Docs examples and AI readiness", [
    { label: "docs directory or deeper docs exist", pass: exists("docs") || /docs\//i.test(readme) },
    { label: "examples or usage examples exist", pass: exists("examples") || /example/i.test(readme) },
    { label: "AGENTS.md exists", pass: exists("AGENTS.md") },
    { label: "architecture/deployment docs exist", pass: /architecture|deployment/i.test(readme) || exists("docs", "deployment.md") },
    { label: "verification checklist or commands exist", pass: /verify|validation|test|build/i.test(readme) }
  ])
];

const total = categories.reduce((sum, category) => sum + category.score, 0);
const status =
  privateHints.length > 0
    ? "unsafe to publish"
    : total >= 45
      ? "release-ready"
      : total >= 35
        ? "needs GitHub settings"
        : "needs implementation";

console.log(`GH Ready audit: ${targetDir}`);
console.log(`Score: ${total}/50`);
console.log(`Status: ${status}`);
console.log("");

for (const category of categories) {
  console.log(`${category.score}/5 ${category.name} (${category.passed}/${category.total})`);
  for (const missing of category.missing) {
    console.log(`  - Missing: ${missing}`);
  }
}

if (privateHints.length > 0) {
  console.log("");
  console.log("Private trace hints:");
  for (const hint of privateHints.slice(0, 20)) {
    console.log(`  - ${hint}`);
  }
  if (privateHints.length > 20) {
    console.log(`  - ...and ${privateHints.length - 20} more`);
  }
}

console.log("");
console.log("Next steps:");
if (total >= 45 && privateHints.length === 0) {
  console.log("- Keep trust signals current as the repository changes.");
} else {
  console.log("- Fix missing trust signals before publishing.");
}
console.log("- Run the repository's install, test, build, and package dry-run commands.");
console.log("- Configure live GitHub settings only after explicit approval.");
