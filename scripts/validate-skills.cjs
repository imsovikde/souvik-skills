#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const rootDir = path.resolve(__dirname, "..");
const skillsDir = path.join(rootDir, "skills");
const readmePath = path.join(rootDir, "README.md");
const packageJsonPath = path.join(rootDir, "package.json");
const marketplacePath = path.join(rootDir, ".claude-plugin", "marketplace.json");
const rootPluginManifestPath = path.join(rootDir, ".claude-plugin", "plugin.json");
const codexManifestPath = path.join(rootDir, "codex-plugin.json");
const repositorySource = "imsovikde/souvik-skills";
const namePattern = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

function fail(message) {
  console.error(`ERROR: ${message}`);
  process.exitCode = 1;
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
    const value = line.slice(separator + 1).trim().replace(/^"|"$/g, "");
    fields[key] = value;
  }
  return fields;
}

function findContextFiles(dir) {
  const matches = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name === ".git" || entry.name === "node_modules") {
        continue;
      }
      matches.push(...findContextFiles(fullPath));
    } else if (entry.name.toLowerCase() === "context.md") {
      matches.push(fullPath);
    }
  }
  return matches;
}

function validateSkill(skillName) {
  const skillDir = path.join(skillsDir, skillName);
  const skillMd = path.join(skillDir, "SKILL.md");
  const openaiYaml = path.join(skillDir, "agents", "openai.yaml");

  if (!namePattern.test(skillName) || skillName.length > 63) {
    fail(`${skillName}: folder name must be lowercase hyphen-case and under 64 characters.`);
  }

  if (!fs.existsSync(skillMd)) {
    fail(`${skillName}: missing SKILL.md.`);
    return;
  }

  const frontmatter = parseFrontmatter(readFile(skillMd));
  if (!frontmatter) {
    fail(`${skillName}: SKILL.md must start with YAML frontmatter.`);
    return;
  }

  const keys = Object.keys(frontmatter).sort();
  const allowed = ["description", "name"];
  if (keys.join(",") !== allowed.join(",")) {
    fail(`${skillName}: SKILL.md frontmatter must contain only name and description.`);
  }

  if (frontmatter.name !== skillName) {
    fail(`${skillName}: frontmatter name must match folder name.`);
  }

  if (!frontmatter.description || frontmatter.description.length < 40) {
    fail(`${skillName}: description must clearly explain when to use the skill.`);
  }

  if (!fs.existsSync(openaiYaml)) {
    fail(`${skillName}: missing agents/openai.yaml.`);
    return;
  }

  const yaml = readFile(openaiYaml);
  for (const field of ["display_name", "short_description", "default_prompt"]) {
    if (!yaml.includes(`${field}:`)) {
      fail(`${skillName}: agents/openai.yaml missing interface.${field}.`);
    }
  }

  if (!yaml.includes(`$${skillName}`)) {
    fail(`${skillName}: default_prompt must mention $${skillName}.`);
  }
}

function validateReadmeInstallMatrix(skills) {
  if (!fs.existsSync(readmePath)) {
    fail("Missing README.md.");
    return;
  }

  const readme = readFile(readmePath);
  for (const skillName of skills) {
    if (!readme.includes(`\`${skillName}\``)) {
      fail(`${skillName}: README.md must include a catalog entry for this skill.`);
    }

    if (!readme.includes(`npx -y skills add ${repositorySource} --skill ${skillName} --agent <agent>`)) {
      fail(`${skillName}: README.md must include the project-only cross-agent install command.`);
    }

    if (!readme.includes(`npx -y skills add ${repositorySource} --skill ${skillName} --agent <agent> -g`)) {
      fail(`${skillName}: README.md must include the global cross-agent install command.`);
    }

    if (!readme.includes(`npx -y skills use ${repositorySource}@${skillName} | <agent-cli>`)) {
      fail(`${skillName}: README.md must include the try-once cross-agent command.`);
    }

    if (!readme.includes(`$${skillName}`)) {
      fail(`${skillName}: README.md must include an example prompt that mentions $${skillName}.`);
    }
  }
}

function readJson(filePath, label) {
  if (!fs.existsSync(filePath)) {
    fail(`Missing ${label} (${path.relative(rootDir, filePath)}).`);
    return null;
  }
  try {
    return JSON.parse(readFile(filePath));
  } catch (error) {
    fail(`${label} is not valid JSON: ${error.message}`);
    return null;
  }
}

function validateMarketplaceManifests(skills) {
  const pkg = readJson(packageJsonPath, "package.json");
  const marketplace = readJson(marketplacePath, "Claude Code marketplace manifest");
  const codexManifest = readJson(codexManifestPath, "Codex plugin manifest");
  const version = pkg ? pkg.version : null;

  if (fs.existsSync(rootPluginManifestPath)) {
    fail(
      "Remove .claude-plugin/plugin.json: the \"souvik-skills-all\" bundle entry sources from the " +
        "repo root (\"source\": \"./\"), so a root plugin.json would become the strict-mode component " +
        "authority for it and override its name/description. Marketplace entries must stay self-describing."
    );
  }

  if (marketplace) {
    const pluginEntries = Array.isArray(marketplace.plugins) ? marketplace.plugins : [];
    const bundleName = "souvik-skills-all";
    const bundle = pluginEntries.find((plugin) => plugin.name === bundleName);
    if (!bundle) {
      fail(`marketplace.json must include the "${bundleName}" bundle entry.`);
    } else if (bundle.source !== "./") {
      fail(`marketplace.json "${bundleName}" entry must keep "source": "./".`);
    }

    for (const skillName of skills) {
      const entry = pluginEntries.find((plugin) => plugin.name === skillName);
      if (!entry) {
        fail(`marketplace.json missing a plugin entry for skill "${skillName}".`);
        continue;
      }
      if (entry.source !== `./skills/${skillName}`) {
        fail(`marketplace.json entry "${skillName}" must set "source": "./skills/${skillName}" (its own folder, not a shared root) so it never shares a source with another entry.`);
      }
    }

    for (const entry of pluginEntries) {
      if (entry.name === bundleName) {
        continue;
      }
      if (!skills.includes(entry.name)) {
        fail(`marketplace.json entry "${entry.name}" does not correspond to a skill folder.`);
      }
      if (version && entry.version && entry.version !== version) {
        fail(`marketplace.json entry "${entry.name}" version ${entry.version} must match package version ${version}.`);
      }
    }

    if (version && marketplace.metadata && marketplace.metadata.version && marketplace.metadata.version !== version) {
      fail(`marketplace.json metadata.version ${marketplace.metadata.version} must match package version ${version}.`);
    }
  }

  if (codexManifest) {
    if (version && codexManifest.version !== version) {
      fail(`codex-plugin.json version ${codexManifest.version} must match package version ${version}.`);
    }
    const codexSkills = Array.isArray(codexManifest.skills)
      ? codexManifest.skills.map((skill) => (typeof skill === "string" ? skill : skill.name))
      : [];
    for (const skillName of skills) {
      if (!codexSkills.includes(skillName)) {
        fail(`codex-plugin.json missing skill "${skillName}".`);
      }
    }
    for (const skillName of codexSkills) {
      if (!skills.includes(skillName)) {
        fail(`codex-plugin.json lists "${skillName}", which is not a skill folder.`);
      }
    }
  }
}

if (!fs.existsSync(skillsDir)) {
  fail("Missing skills directory.");
} else {
  const skills = fs
    .readdirSync(skillsDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort();

  if (skills.length === 0) {
    fail("No skills found.");
  }

  for (const skill of skills) {
    validateSkill(skill);
  }

  validateReadmeInstallMatrix(skills);
  validateMarketplaceManifests(skills);
}

const contextFiles = findContextFiles(rootDir);
for (const filePath of contextFiles) {
  fail(`Remove context.md file: ${path.relative(rootDir, filePath)}`);
}

if (!process.exitCode) {
  console.log("Skill validation passed.");
}
