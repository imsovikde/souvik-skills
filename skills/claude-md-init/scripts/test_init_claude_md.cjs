#!/usr/bin/env node
"use strict";

const fs = require("fs");
const os = require("os");
const path = require("path");
const assert = require("assert");
const { execFileSync } = require("child_process");

const scriptPath = path.join(__dirname, "init-claude-md.cjs");

function withTempDir(fn) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "claude-md-init-test-"));
  try {
    fn(dir);
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
}

function run(args, cwd, env) {
  return execFileSync(process.execPath, [scriptPath, ...args], {
    cwd,
    encoding: "utf8",
    env: env || process.env
  });
}

function testCreatesClaudeMdWhenMissing() {
  withTempDir((dir) => {
    run(["--name", "Test Owner", "--email", "owner@example.com", dir], dir);
    const content = fs.readFileSync(path.join(dir, "CLAUDE.md"), "utf8");
    assert.ok(content.includes("Test Owner <owner@example.com>"), "expected owner identity in output");
    assert.ok(content.includes("<!-- claude-md-init:start -->"), "expected start marker");
    assert.ok(content.includes("<!-- claude-md-init:end -->"), "expected end marker");
  });
  console.log("PASS: creates CLAUDE.md when missing");
}

function testUpdateIsIdempotentAndPreservesUserContent() {
  withTempDir((dir) => {
    fs.writeFileSync(path.join(dir, "CLAUDE.md"), "# My Project\n\nHand-written notes stay here.\n");
    run(["--name", "Test Owner", "--email", "owner@example.com", dir], dir);
    const first = fs.readFileSync(path.join(dir, "CLAUDE.md"), "utf8");
    assert.ok(first.includes("Hand-written notes stay here."), "expected human content preserved on create");

    run(["--name", "Test Owner", "--email", "owner@example.com", dir], dir);
    const second = fs.readFileSync(path.join(dir, "CLAUDE.md"), "utf8");
    assert.strictEqual(first, second, "second run should not change output");

    const starts = second.split("<!-- claude-md-init:start -->").length - 1;
    assert.strictEqual(starts, 1, "expected exactly one managed block after two runs");
    assert.ok(second.includes("Hand-written notes stay here."), "expected human content preserved on update");
  });
  console.log("PASS: update is idempotent and preserves user content");
}

function testRequiresIdentityWhenUndetectable() {
  withTempDir((dir) => {
    const isolatedHome = fs.mkdtempSync(path.join(os.tmpdir(), "claude-md-init-home-"));
    const env = {
      ...process.env,
      HOME: isolatedHome,
      GIT_CONFIG_NOSYSTEM: "1",
      GIT_CONFIG_GLOBAL: path.join(isolatedHome, "does-not-exist")
    };

    let threw = false;
    try {
      run([dir], dir, env);
    } catch (error) {
      threw = true;
      const message = String(error.stderr || error.message);
      assert.ok(message.includes("owner name/email"), "expected identity error message");
    } finally {
      fs.rmSync(isolatedHome, { recursive: true, force: true });
    }

    assert.ok(threw, "expected script to fail without a discoverable identity");
  });
  console.log("PASS: fails without a discoverable owner identity");
}

testCreatesClaudeMdWhenMissing();
testUpdateIsIdempotentAndPreservesUserContent();
testRequiresIdentityWhenUndetectable();
console.log("All claude-md-init tests passed.");
