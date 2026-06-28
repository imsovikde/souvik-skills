export const repositorySource = "imsovikde/souvik-skills";
export const githubUrl = `https://github.com/${repositorySource}`;
export const npmPackage = "@imsovikde/skills";
export const npmUrl = `https://www.npmjs.com/package/${npmPackage}`;
export const siteUrl = "https://souvik-skills.vercel.app";

export const agents = [
  {
    id: "claude-code",
    label: "Claude Code",
    cli: "claude",
    destination: ".claude/skills"
  },
  {
    id: "codex",
    label: "Codex",
    cli: "codex",
    destination: ".codex/skills"
  },
  {
    id: "cursor",
    label: "Cursor",
    cli: "cursor",
    destination: ".cursor/skills"
  },
  {
    id: "gemini-cli",
    label: "Gemini CLI",
    cli: "gemini",
    destination: ".gemini/skills"
  },
  {
    id: "opencode",
    label: "OpenCode",
    cli: "opencode",
    destination: ".opencode/skills"
  },
  {
    id: "github-copilot",
    label: "GitHub Copilot",
    cli: null,
    destination: ".github/copilot/skills"
  }
];

export function commandFor(skillName, installMode, agentId) {
  const agent = agents.find((item) => item.id === agentId) || agents[0];

  if (installMode === "global") {
    return `npx -y skills add ${repositorySource} --skill ${skillName} --agent ${agent.id} -g`;
  }

  if (installMode === "try") {
    if (agent.cli) {
      return `npx -y skills use ${repositorySource}@${skillName} | ${agent.cli}`;
    }

    return `npx -y skills use ${repositorySource}@${skillName} --agent ${agent.id}`;
  }

  return `npx -y skills add ${repositorySource} --skill ${skillName} --agent ${agent.id}`;
}

export const installModes = [
  {
    id: "project",
    label: "Project",
    helper: (agent) => `Installs into ${agent.destination} of the current project.`
  },
  {
    id: "global",
    label: "Global",
    helper: () => "Installs user-wide for the selected agent."
  },
  {
    id: "try",
    label: "Try once",
    helper: (agent) =>
      agent.cli
        ? `Streams the skill prompt into ${agent.cli} without installing.`
        : "Streams the skill prompt for this agent without a permanent install."
  }
];
