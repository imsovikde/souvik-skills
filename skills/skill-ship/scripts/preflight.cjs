#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");

const namePattern = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const ignoredDirectories = new Set([".git", "node_modules", "__pycache__", ".pytest_cache"]);
const textExtensions = new Set([
  ".md",
  ".js",
  ".cjs",
  ".mjs",
  ".ts",
  ".py",
  ".sh",
  ".yaml",
  ".yml",
  ".json",
  ".toml",
  ".txt"
]);

const failures = [];
const warnings = [];

function fail(message) {
  failures.push(message);
}

function warn(message) {
  warnings.push(message);
}

function readFile(filePath) {
  return fs.readFileSync(filePath, "utf8");
}

function parseFrontmatter(markdown) {
  const match = markdown.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
  if (!match) {
    return null;
  }

  const fields = {};
  for (const line of match[1].split(/\r?\n/)) {
    const separator = line.indexOf(":");
    if (separator === -1) {
      continue;
    }
    const key = line.slice(0, separator).trim();
    const value = line.slice(separator + 1).trim().replace(/^["']|["']$/g, "");
    fields[key] = value;
  }
  return fields;
}

function walk(dir, collected = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.isDirectory()) {
      if (ignoredDirectories.has(entry.name)) {
        continue;
      }
      walk(path.join(dir, entry.name), collected);
    } else if (entry.isFile()) {
      collected.push(path.join(dir, entry.name));
    }
  }
  return collected;
}

// Built from fragments so this scanner never flags its own source.
const secretPatterns = [
  { label: "npm access token", regex: new RegExp("npm" + "_[A-Za-z0-9]{36}") },
  { label: "GitHub personal access token", regex: new RegExp("ghp" + "_[A-Za-z0-9]{36}") },
  { label: "GitHub fine-grained token", regex: new RegExp("github" + "_pat_[A-Za-z0-9_]{22,}") },
  { label: "AWS access key id", regex: new RegExp("AKIA" + "[0-9A-Z]{16}") },
  { label: "OpenAI API key", regex: new RegExp("sk-" + "[A-Za-z0-9]{32,}") },
  { label: "private key block", regex: new RegExp("-----" + "BEGIN [A-Z ]+PRIVATE KEY") }
];

// Vendor names are assembled from fragments so this scanner never flags its own source.
const telemetryPatterns = [
  { label: "Google Analytics", regex: new RegExp("google-" + "analytics\\.com|gtag\\(|googletag" + "manager\\.com", "i") },
  { label: "Segment", regex: new RegExp("cdn\\.seg" + "ment\\.com|analytics\\.track\\s*\\(", "i") },
  { label: "Mix" + "panel", regex: new RegExp("mix" + "panel", "i") },
  { label: "Amplitude", regex: new RegExp("ampli" + "tude\\.com|ampli" + "tude\\.getInstance", "i") },
  { label: "Sentry error reporting", regex: new RegExp("sen" + "try\\.io|Sen" + "try\\.init", "i") },
  { label: "Post" + "Hog", regex: new RegExp("post" + "hog", "i") },
  { label: "Datadog", regex: new RegExp("datadog" + "hq\\.com|DD_API" + "_KEY", "i") },
  { label: "generic telemetry endpoint", regex: new RegExp("\\/(tele" + "metry|analytics|collect|beacon|track)\\b", "i") },
  { label: "usage ping", regex: new RegExp("\\bphone_?home\\b|\\busage_?ping\\b|\\btrack_?event\\b", "i") }
];

function scanContents(skillDir, skillName) {
  const files = walk(skillDir);

  for (const file of files) {
    const relative = path.relative(skillDir, file).split(path.sep).join("/");
    const extension = path.extname(file);

    if (path.basename(file).toLowerCase() === "context.md") {
      fail(`remove ${relative}: context.md is forbidden in this repository`);
    }

    if (!textExtensions.has(extension)) {
      continue;
    }

    let contents;
    try {
      contents = readFile(file);
    } catch {
      continue;
    }

    for (const { label, regex } of secretPatterns) {
      if (regex.test(contents)) {
        fail(`${relative}: possible hardcoded ${label} — remove it and rotate the credential`);
      }
    }

    for (const { label, regex } of telemetryPatterns) {
      if (regex.test(contents)) {
        warn(`${relative}: ${label} indicator found — confirm it is the skill's function, not tracking, and strip it if it is tracking`);
      }
    }
  }

  const licenseLike = files.some((file) => /^(licen[cs]e|notice)/i.test(path.basename(file)));
  if (licenseLike) {
    warn(
      `${skillName}: a licence or notice file is bundled — keep it, and record the upstream origin in references/ if this skill was adopted from elsewhere`
    );
  }
}

function checkSkill(skillDir) {
  const skillName = path.basename(path.resolve(skillDir));

  if (!fs.existsSync(skillDir) || !fs.statSync(skillDir).isDirectory()) {
    fail(`${skillDir} is not a directory`);
    return skillName;
  }

  if (!namePattern.test(skillName) || skillName.length > 63) {
    fail(`folder name "${skillName}" must be lowercase kebab-case and under 64 characters`);
  }

  const skillMd = path.join(skillDir, "SKILL.md");
  if (!fs.existsSync(skillMd)) {
    fail("missing SKILL.md");
  } else {
    const frontmatter = parseFrontmatter(readFile(skillMd));
    if (!frontmatter) {
      fail("SKILL.md must start with YAML frontmatter");
    } else {
      const keys = Object.keys(frontmatter).sort();
      if (keys.join(",") !== "description,name") {
        fail(`SKILL.md frontmatter must contain only name and description (found: ${keys.join(", ") || "nothing"})`);
      }
      if (frontmatter.name !== skillName) {
        fail(`SKILL.md frontmatter name "${frontmatter.name}" must equal folder name "${skillName}"`);
      }
      if (!frontmatter.description || frontmatter.description.length < 40) {
        fail("SKILL.md description must be at least 40 characters and explain when to use the skill");
      }
    }
  }

  const openaiYaml = path.join(skillDir, "agents", "openai.yaml");
  if (!fs.existsSync(openaiYaml)) {
    fail("missing agents/openai.yaml");
  } else {
    const yaml = readFile(openaiYaml);
    for (const field of ["display_name", "short_description", "default_prompt"]) {
      if (!yaml.includes(`${field}:`)) {
        fail(`agents/openai.yaml missing interface.${field}`);
      }
    }
    if (!yaml.includes(`$${skillName}`)) {
      fail(`agents/openai.yaml default_prompt must mention $${skillName}`);
    }
  }

  const pluginJson = path.join(skillDir, ".claude-plugin", "plugin.json");
  if (!fs.existsSync(pluginJson)) {
    fail(
      "missing .claude-plugin/plugin.json — Cowork marketplace sync requires every plugin source directory to be self-describing"
    );
  } else {
    let manifest = null;
    try {
      manifest = JSON.parse(readFile(pluginJson));
    } catch (error) {
      fail(`.claude-plugin/plugin.json is not valid JSON: ${error.message}`);
    }
    if (manifest) {
      if (manifest.name !== skillName) {
        fail(`.claude-plugin/plugin.json name "${manifest.name}" must equal "${skillName}"`);
      }
      for (const field of ["version", "description"]) {
        if (!manifest[field]) {
          fail(`.claude-plugin/plugin.json missing ${field}`);
        }
      }
    }
  }

  scanContents(skillDir, skillName);
  return skillName;
}

function main() {
  const target = process.argv[2];
  if (!target) {
    console.error("Usage: node preflight.cjs <path-to-skill-folder>");
    process.exit(2);
  }

  const skillDir = path.resolve(target);
  const skillName = checkSkill(skillDir);

  console.log(`Preflight: ${skillName}`);

  if (warnings.length > 0) {
    console.log("\nWarnings (review, do not necessarily block):");
    for (const message of warnings) {
      console.log(`  ! ${message}`);
    }
  }

  if (failures.length > 0) {
    console.log("\nFailures:");
    for (const message of failures) {
      console.log(`  x ${message}`);
    }
    console.log(`\n${failures.length} failure(s). Fix them and re-run.`);
    process.exit(1);
  }

  console.log("\nAll required checks passed. Skill is marketplace-ready.");
}

main();
