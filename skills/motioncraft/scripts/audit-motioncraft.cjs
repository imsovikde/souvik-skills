#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const targetRoot = path.resolve(process.argv[2] || ".");
const jsonMode = process.argv.includes("--json");
const selfPath = path.resolve(__filename);

const ignoreDirs = new Set([
  ".git",
  ".next",
  ".turbo",
  ".vercel",
  "coverage",
  "dist",
  "build",
  "node_modules",
  "out"
]);

const scanExtensions = new Set([
  ".css",
  ".scss",
  ".sass",
  ".less",
  ".html",
  ".js",
  ".jsx",
  ".ts",
  ".tsx",
  ".mjs",
  ".cjs"
]);

const checks = [
  {
    key: "motionTokens",
    label: "Motion tokens",
    weight: 16,
    good: true,
    pattern: /(--motion-|motionTokens|MotionConfig|duration.*motion|easing.*motion)/i,
    guidance: "Add centralized duration, easing, spring, distance, stagger, and reduced-motion tokens."
  },
  {
    key: "reducedMotion",
    label: "Reduced motion",
    weight: 18,
    good: true,
    pattern: /(prefers-reduced-motion|reducedMotion|useReducedMotion)/i,
    guidance: "Implement a reduced-motion design that disables parallax, smooth scroll, large transforms, autoplay, and loops."
  },
  {
    key: "transitionAll",
    label: "transition: all",
    weight: 18,
    good: false,
    pattern: /transition\s*:\s*all\b|className=["'`][^"'`]*\btransition-all\b/i,
    guidance: "Replace transition-all with explicit properties such as transform, opacity, color, background-color, and border-color."
  },
  {
    key: "layoutProperties",
    label: "Animated layout properties",
    weight: 14,
    good: false,
    pattern: /transition[^;\n{}]*(width|height|top|left|right|bottom|margin|padding)|animate\([^)]*(width|height|top|left|margin|padding)/i,
    guidance: "Avoid hot-path animation of layout properties. Prefer transform, opacity, FLIP, or measured layout springs."
  },
  {
    key: "expensiveEffects",
    label: "Expensive visual effects",
    weight: 8,
    good: false,
    pattern: /transition[^;\n{}]*(filter|backdrop-filter|box-shadow)|animation[^;\n{}]*(filter|backdrop-filter|box-shadow)/i,
    guidance: "Keep blur, backdrop-filter, and shadow animation short, subtle, and off hot paths, especially for Safari/mobile."
  },
  {
    key: "continuousLoops",
    label: "Continuous loops",
    weight: 8,
    good: false,
    pattern: /animation[^;\n{}]*infinite|animation-iteration-count\s*:\s*infinite|setInterval\s*\(|requestAnimationFrame\s*\(/i,
    guidance: "Pause or remove offscreen loops, gate ambient animation with IntersectionObserver, and disable loops for reduced motion."
  },
  {
    key: "scrollHijackRisk",
    label: "Scroll hijack risk",
    weight: 8,
    good: false,
    pattern: /(preventDefault\(\)[\s\S]{0,120}(wheel|touchmove)|(wheel|touchmove)[\s\S]{0,120}preventDefault\(\)|overflow\s*:\s*hidden[^;{}]*(body|html))/i,
    guidance: "Avoid scroll hijacking in docs, dashboards, forms, tables, and code-heavy workflows."
  },
  {
    key: "visibilityPause",
    label: "Offscreen pause support",
    weight: 10,
    good: true,
    pattern: /(IntersectionObserver|useInView|whileInView|content-visibility)/i,
    guidance: "Use IntersectionObserver, useInView, whileInView, or content-visibility to keep expensive motion from running offscreen."
  }
];

function fail(message) {
  console.error(`ERROR: ${message}`);
  process.exit(1);
}

function walk(dir, files = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (!ignoreDirs.has(entry.name)) {
        walk(fullPath, files);
      }
    } else if (path.resolve(fullPath) === selfPath) {
      continue;
    } else if (scanExtensions.has(path.extname(entry.name).toLowerCase())) {
      files.push(fullPath);
    }
  }
  return files;
}

function readPackageJson(root) {
  const packagePath = path.join(root, "package.json");
  if (!fs.existsSync(packagePath)) {
    return {};
  }
  try {
    return JSON.parse(fs.readFileSync(packagePath, "utf8"));
  } catch {
    return {};
  }
}

function detectLibraries(packageJson) {
  const deps = {
    ...packageJson.dependencies,
    ...packageJson.devDependencies
  };
  return [
    "motion",
    "framer-motion",
    "gsap",
    "lenis",
    "@studio-freight/lenis",
    "@react-spring/web",
    "react-spring"
  ].filter((name) => deps && deps[name]);
}

function lineNumber(text, index) {
  return text.slice(0, index).split(/\r?\n/).length;
}

function audit() {
  if (!fs.existsSync(targetRoot)) {
    fail(`Target does not exist: ${targetRoot}`);
  }

  const stat = fs.statSync(targetRoot);
  if (!stat.isDirectory()) {
    fail(`Target must be a directory: ${targetRoot}`);
  }

  const packageJson = readPackageJson(targetRoot);
  const libraries = detectLibraries(packageJson);
  const files = walk(targetRoot);
  const findings = Object.fromEntries(checks.map((check) => [check.key, []]));

  for (const file of files) {
    const text = fs.readFileSync(file, "utf8");
    for (const check of checks) {
      const match = text.match(check.pattern);
      if (match) {
        const index = match && typeof match.index === "number" ? match.index : 0;
        findings[check.key].push({
          file: path.relative(targetRoot, file),
          line: lineNumber(text, index)
        });
      }
    }
  }

  let score = 100;
  const summary = checks.map((check) => {
    const count = findings[check.key].length;
    const passed = check.good ? count > 0 : count === 0;
    if (!passed) {
      score -= check.weight;
    }
    return {
      key: check.key,
      label: check.label,
      passed,
      count,
      weight: check.weight,
      guidance: check.guidance,
      examples: findings[check.key].slice(0, 6)
    };
  });

  return {
    target: targetRoot,
    scannedFiles: files.length,
    libraries,
    score: Math.max(0, score),
    summary
  };
}

function printReport(result) {
  console.log("Motioncraft audit");
  console.log(`Target: ${result.target}`);
  console.log(`Scanned files: ${result.scannedFiles}`);
  console.log(`Animation libraries: ${result.libraries.length ? result.libraries.join(", ") : "none detected"}`);
  console.log(`Motion readiness score: ${result.score}/100`);
  console.log("");

  for (const item of result.summary) {
    const mark = item.passed ? "PASS" : "CHECK";
    console.log(`${mark} ${item.label} (${item.count} signal${item.count === 1 ? "" : "s"})`);
    if (!item.passed) {
      console.log(`  ${item.guidance}`);
    }
    for (const example of item.examples) {
      console.log(`  - ${example.file}:${example.line}`);
    }
  }

  console.log("");
  console.log("Use these findings to create a motion intent map before adding or changing animation.");
}

const result = audit();
if (jsonMode) {
  console.log(JSON.stringify(result, null, 2));
} else {
  printReport(result);
}
