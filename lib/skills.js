import fs from "node:fs";
import path from "node:path";

const rootDir = process.cwd();
const skillsDir = path.join(rootDir, "skills");

function readFileIfExists(filePath) {
  if (!fs.existsSync(filePath)) {
    return "";
  }

  return fs.readFileSync(filePath, "utf8");
}

function parseFrontmatter(markdown) {
  const match = markdown.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
  if (!match) {
    return {};
  }

  const fields = {};
  const lines = match[1].split(/\r?\n/);

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    const separator = line.indexOf(":");

    if (separator === -1) {
      continue;
    }

    const key = line.slice(0, separator).trim();
    let value = line.slice(separator + 1).trim();

    if (value === "|" || value === ">") {
      const block = [];

      for (let blockIndex = index + 1; blockIndex < lines.length; blockIndex += 1) {
        const blockLine = lines[blockIndex];

        if (/^[a-zA-Z0-9_-]+:/.test(blockLine)) {
          break;
        }

        block.push(blockLine.trim());
        index = blockIndex;
      }

      value = block.join(" ");
    }

    fields[key] = value.replace(/^["']|["']$/g, "").trim();
  }

  return fields;
}

function parseOpenAiYaml(yaml) {
  const field = (name) => {
    const match = yaml.match(new RegExp(`${name}:\\s*(.+)`));
    return match ? match[1].replace(/^["']|["']$/g, "").trim() : "";
  };

  return {
    displayName: field("display_name"),
    shortDescription: field("short_description"),
    defaultPrompt: field("default_prompt")
  };
}

function stripFrontmatter(markdown) {
  return markdown.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/, "").trim();
}

function extractSummary(body) {
  const paragraphs = body
    .split(/\r?\n\r?\n/)
    .map((section) => section.trim())
    .filter(Boolean)
    .filter((section) => !section.startsWith("#") && !section.startsWith("```"));

  return paragraphs[0] || "";
}

function extractSections(body) {
  const sections = [];
  const matches = Array.from(body.matchAll(/^##\s+(.+)$/gm));

  for (let index = 0; index < matches.length; index += 1) {
    const match = matches[index];
    const next = matches[index + 1];
    const title = match[1].trim();
    const contentStart = match.index + match[0].length;
    const contentEnd = next ? next.index : body.length;
    const content = body.slice(contentStart, contentEnd).trim();

    sections.push({
      title,
      content
    });
  }

  return sections;
}

function firstSentence(text) {
  const sentence = text.match(/^[\s\S]*?[.!?](\s|$)/);
  return (sentence ? sentence[0] : text).trim();
}

function inferCategory(name, description) {
  const source = `${name} ${description}`.toLowerCase();

  if (
    source.includes("music") ||
    source.includes("score") ||
    source.includes("notation") ||
    source.includes("musicxml") ||
    source.includes("midi") ||
    source.includes("abc")
  ) {
    return "Music Conversion";
  }

  if (source.includes("motion") || source.includes("animation") || source.includes("interface")) {
    return "Interface Motion";
  }

  if (source.includes("magento") || source.includes("commerce") || source.includes("ecommerce")) {
    return "Commerce Leadership";
  }

  if (source.includes("detach") || source.includes("delink") || source.includes("reset")) {
    return "Repository Safety";
  }

  if (source.includes("github") || source.includes("repository") || source.includes("release")) {
    return "Release Readiness";
  }

  if (source.includes("doc") || source.includes("readme")) {
    return "Documentation";
  }

  return "Agent Workflow";
}

function listFolderFiles(folderPath, relativePrefix) {
  if (!fs.existsSync(folderPath)) {
    return [];
  }

  const ignoredDirectories = new Set(["__pycache__", ".pytest_cache"]);
  const ignoredExtensions = new Set([".pyc", ".pyo"]);
  const files = [];

  function walk(currentFolder) {
    for (const entry of fs.readdirSync(currentFolder, { withFileTypes: true })) {
      if (entry.isDirectory() && ignoredDirectories.has(entry.name)) {
        continue;
      }

      const absolutePath = path.join(currentFolder, entry.name);

      if (entry.isDirectory()) {
        walk(absolutePath);
        continue;
      }

      if (!entry.isFile()) {
        continue;
      }

      if (ignoredExtensions.has(path.extname(entry.name))) {
        continue;
      }

      const relativePath = path.relative(folderPath, absolutePath).split(path.sep).join("/");
      files.push(`${relativePrefix}/${relativePath}`);
    }
  }

  walk(folderPath);
  return files.sort();
}

function readSkill(skillName) {
  const skillDir = path.join(skillsDir, skillName);
  const skillMdPath = path.join(skillDir, "SKILL.md");
  const openAiYamlPath = path.join(skillDir, "agents", "openai.yaml");
  const markdown = readFileIfExists(skillMdPath);
  const body = stripFrontmatter(markdown);
  const frontmatter = parseFrontmatter(markdown);
  const openAi = parseOpenAiYaml(readFileIfExists(openAiYamlPath));
  const description = frontmatter.description || "";
  const name = frontmatter.name || skillName;
  const references = listFolderFiles(path.join(skillDir, "references"), `skills/${name}/references`);
  const scripts = listFolderFiles(path.join(skillDir, "scripts"), `skills/${name}/scripts`);
  const assets = listFolderFiles(path.join(skillDir, "assets"), `skills/${name}/assets`);
  const resourceCount = references.length + scripts.length + assets.length;

  return {
    name,
    displayName: openAi.displayName || name,
    shortDescription: openAi.shortDescription || firstSentence(description),
    defaultPrompt: openAi.defaultPrompt || `Use $${name} for this workflow.`,
    description,
    summary: extractSummary(body),
    sections: extractSections(body),
    category: inferCategory(name, description),
    sourceFiles: [`skills/${name}/SKILL.md`, `skills/${name}/agents/openai.yaml`],
    references,
    scripts,
    assets,
    resourceCount,
    hasResources: resourceCount > 0
  };
}

export function getSkills() {
  if (!fs.existsSync(skillsDir)) {
    return [];
  }

  return fs
    .readdirSync(skillsDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .filter((skillName) => fs.existsSync(path.join(skillsDir, skillName, "SKILL.md")))
    .map(readSkill)
    .sort((a, b) => a.name.localeCompare(b.name));
}

export function getSkill(skillName) {
  return getSkills().find((skill) => skill.name === skillName) || null;
}

export function getCategories() {
  return Array.from(new Set(getSkills().map((skill) => skill.category))).sort();
}

export function sourceUrl(filePath) {
  return `https://github.com/imsovikde/souvik-skills/blob/main/${filePath}`;
}
