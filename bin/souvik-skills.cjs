#!/usr/bin/env node

const fs = require("fs");
const os = require("os");
const path = require("path");

const rootDir = path.resolve(__dirname, "..");
const sourceSkillsDir = path.join(rootDir, "skills");

function readSkillNames() {
  if (!fs.existsSync(sourceSkillsDir)) {
    return [];
  }

  return fs
    .readdirSync(sourceSkillsDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .filter((name) => fs.existsSync(path.join(sourceSkillsDir, name, "SKILL.md")))
    .sort();
}

function defaultDestination() {
  const codexHome = process.env.CODEX_HOME;
  if (codexHome) {
    return path.join(codexHome, "skills");
  }
  return path.join(os.homedir(), ".codex", "skills");
}

function parseOptions(args) {
  const options = {
    dest: defaultDestination(),
    force: false
  };
  const positionals = [];

  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];
    if (arg === "--force") {
      options.force = true;
    } else if (arg === "--dest") {
      const value = args[index + 1];
      if (!value) {
        throw new Error("Missing value after --dest");
      }
      options.dest = path.resolve(value);
      index += 1;
    } else {
      positionals.push(arg);
    }
  }

  return { options, positionals };
}

function copyDirectory(source, destination) {
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.cpSync(source, destination, { recursive: true });
}

function installSkill(skillName, options) {
  const available = readSkillNames();
  if (!available.includes(skillName)) {
    throw new Error(`Unknown skill "${skillName}". Available skills: ${available.join(", ")}`);
  }

  const source = path.join(sourceSkillsDir, skillName);
  const destination = path.join(options.dest, skillName);

  if (fs.existsSync(destination)) {
    if (!options.force) {
      throw new Error(`Skill "${skillName}" already exists at ${destination}. Re-run with --force to overwrite it.`);
    }
    fs.rmSync(destination, { recursive: true, force: true });
  }

  copyDirectory(source, destination);
  console.log(`Installed ${skillName} to ${destination}`);
}

function printList() {
  const skills = readSkillNames();
  if (skills.length === 0) {
    console.log("No skills found.");
    return;
  }

  console.log("Souvik Skills:");
  for (const skill of skills) {
    console.log(`- ${skill}`);
  }
}

function printUsage() {
  console.log(`Souvik Skills

Usage:
  souvik-skills list
  souvik-skills install <skill-name|all> [--dest <path>] [--force]

Examples:
  npx @imsovikde/skills list
  npx @imsovikde/skills install gh-ready --force
  npx @imsovikde/skills install all --dest ./tmp/codex-skills
`);
}

function main() {
  const [command, ...rest] = process.argv.slice(2);

  if (!command || command === "help" || command === "--help" || command === "-h") {
    printUsage();
    return;
  }

  if (command === "list") {
    printList();
    return;
  }

  if (command === "install") {
    const { options, positionals } = parseOptions(rest);
    const target = positionals[0];
    if (!target) {
      throw new Error("Missing skill name. Use `souvik-skills list` to see available skills.");
    }

    const targets = target === "all" ? readSkillNames() : [target];
    for (const skillName of targets) {
      installSkill(skillName, options);
    }
    console.log("Restart Codex to pick up newly installed skills.");
    return;
  }

  throw new Error(`Unknown command "${command}".`);
}

try {
  main();
} catch (error) {
  console.error(`Error: ${error.message}`);
  process.exit(1);
}
