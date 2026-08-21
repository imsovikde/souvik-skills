#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const targetDir = process.argv[2] || '.';
console.log(`Running Security Scan on: ${targetDir}`);

const secretPatterns = [
  /ghp_[0-9a-zA-Z]{36}/g,
  /gho_[0-9a-zA-Z]{36}/g,
  /sk-[0-9a-zA-Z]{48}/g,
  /xox[baprs]-[0-9a-zA-Z]{10,48}/g
];

let issues = 0;
function scan(dir) {
  for (const file of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, file.name);
    if (file.isDirectory() && file.name !== '.git' && file.name !== 'node_modules') {
      scan(full);
    } else if (file.isFile()) {
      const content = fs.readFileSync(full, 'utf8');
      for (const p of secretPatterns) {
        if (p.test(content)) {
          console.error(`SECURITY WARNING: Potential secret found in ${full}`);
          issues++;
        }
      }
    }
  }
}
scan(targetDir);
if (issues === 0) {
  console.log('Security Scan PASSED: No hardcoded credentials detected.');
} else {
  process.exit(1);
}
