#!/usr/bin/env node
"use strict";

const fs = require("fs");
const os = require("os");
const path = require("path");
const assert = require("assert");
const { execFileSync } = require("child_process");

const scriptPath = path.join(__dirname, "preflight.cjs");
const repoRoot = path.resolve(__dirname, "..", "..", "..");

function withTempDir(fn) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "skill-ship-test-"));
  try {
    return fn(dir);
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
}

function run(skillDir) {
  try {
    const stdout = execFileSync(process.execPath, [scriptPath, skillDir], { encoding: "utf8" });
    return { code: 0, output: stdout };
  } catch (error) {
    return { code: error.status, output: String(error.stdout || "") + String(error.stderr || "") };
  }
}

function makeValidSkill(root, name) {
  const dir = path.join(root, name);
  fs.mkdirSync(path.join(dir, "agents"), { recursive: true });
  fs.mkdirSync(path.join(dir, ".claude-plugin"), { recursive: true });
  fs.writeFileSync(
    path.join(dir, "SKILL.md"),
    `---\nname: ${name}\ndescription: A sufficiently detailed description explaining exactly when an agent should reach for this test skill.\n---\n\n# Test\n\nBody.\n`
  );
  fs.writeFileSync(
    path.join(dir, "agents", "openai.yaml"),
    `interface:\n  display_name: "Test"\n  short_description: "Test skill"\n  default_prompt: "Use $${name} to do the thing."\n`
  );
  fs.writeFileSync(
    path.join(dir, ".claude-plugin", "plugin.json"),
    JSON.stringify({ name, version: "0.6.0", description: "Test skill" }, null, 2)
  );
  return dir;
}

function testValidSkillPasses() {
  withTempDir((root) => {
    const dir = makeValidSkill(root, "sample-skill");
    const result = run(dir);
    assert.strictEqual(result.code, 0, `expected pass, got:\n${result.output}`);
    assert.ok(result.output.includes("marketplace-ready"), "expected ready message");
  });
  console.log("PASS: compliant skill passes preflight");
}

function testMissingPluginJsonFails() {
  withTempDir((root) => {
    const dir = makeValidSkill(root, "sample-skill");
    fs.rmSync(path.join(dir, ".claude-plugin"), { recursive: true, force: true });
    const result = run(dir);
    assert.strictEqual(result.code, 1, "expected failure without plugin.json");
    assert.ok(result.output.includes("plugin.json"), "expected plugin.json failure message");
  });
  console.log("PASS: missing .claude-plugin/plugin.json fails");
}

function testNameMismatchFails() {
  withTempDir((root) => {
    const dir = makeValidSkill(root, "sample-skill");
    fs.writeFileSync(
      path.join(dir, "SKILL.md"),
      "---\nname: wrong-name\ndescription: A sufficiently detailed description explaining exactly when an agent should reach for this test skill.\n---\n\n# Test\n"
    );
    const result = run(dir);
    assert.strictEqual(result.code, 1, "expected failure on name mismatch");
    assert.ok(result.output.includes("must equal folder name"), "expected name mismatch message");
  });
  console.log("PASS: frontmatter name mismatch fails");
}

function testHardcodedSecretFails() {
  withTempDir((root) => {
    const dir = makeValidSkill(root, "sample-skill");
    fs.mkdirSync(path.join(dir, "scripts"), { recursive: true });
    const fakeToken = "npm" + "_" + "a".repeat(36);
    fs.writeFileSync(path.join(dir, "scripts", "leak.js"), `const token = "${fakeToken}";\n`);
    const result = run(dir);
    assert.strictEqual(result.code, 1, "expected failure on hardcoded secret");
    assert.ok(result.output.includes("hardcoded"), "expected secret failure message");
  });
  console.log("PASS: hardcoded credential fails");
}

function testTelemetryWarns() {
  withTempDir((root) => {
    const dir = makeValidSkill(root, "sample-skill");
    fs.mkdirSync(path.join(dir, "scripts"), { recursive: true });
    const vendor = "mix" + "panel";
    fs.writeFileSync(path.join(dir, "scripts", "t.js"), `${vendor}.track('used');\n`);
    const result = run(dir);
    assert.strictEqual(result.code, 0, "telemetry should warn, not block");
    assert.ok(result.output.includes("Mix" + "panel"), "expected telemetry warning");
  });
  console.log("PASS: telemetry indicator warns without blocking");
}

function testRepoSkillsAllPass() {
  const skillsDir = path.join(repoRoot, "skills");
  const names = fs
    .readdirSync(skillsDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name);

  assert.ok(names.length > 0, "expected skills in repository");

  for (const name of names) {
    const result = run(path.join(skillsDir, name));
    assert.strictEqual(result.code, 0, `${name} failed preflight:\n${result.output}`);
  }
  console.log(`PASS: all ${names.length} repository skills pass preflight`);
}

testValidSkillPasses();
testMissingPluginJsonFails();
testNameMismatchFails();
testHardcodedSecretFails();
testTelemetryWarns();
testRepoSkillsAllPass();
console.log("All skill-ship tests passed.");
