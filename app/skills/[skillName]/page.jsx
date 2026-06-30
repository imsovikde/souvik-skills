import { ArrowLeft, FileCode2 } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { CopyButton } from "@/components/copy-button";
import { InstallCard } from "@/components/install-card";
import { getSkill, getSkills, sourceUrl } from "@/lib/skills";

function plainLines(content) {
  return content
    .split(/\r?\n/)
    .map((line) => line.replace(/^[-*]\s+/, "").replace(/^\d+\.\s+/, "").replace(/`/g, "").trim())
    .filter(Boolean)
    .slice(0, 6);
}

export function generateStaticParams() {
  return getSkills().map((skill) => ({ skillName: skill.name }));
}

export async function generateMetadata({ params }) {
  const { skillName } = await params;
  const skill = getSkill(skillName);

  if (!skill) {
    return {
      title: "Skill not found"
    };
  }

  return {
    title: skill.displayName,
    description: skill.shortDescription || skill.description
  };
}

export default async function SkillPage({ params }) {
  const { skillName } = await params;
  const skill = getSkill(skillName);

  if (!skill) {
    notFound();
  }

  const sourceFiles = [...skill.sourceFiles, ...skill.references, ...skill.scripts, ...skill.assets];
  const sections = skill.sections.slice(0, 4);

  return (
    <div id="content">
      <section className="section">
        <div className="container">
          <Link className="button secondary" href="/skills" style={{ marginBottom: 28 }}>
            <ArrowLeft size={17} aria-hidden="true" /> All skills
          </Link>

          <div className="detail-grid">
            <div style={{ display: "grid", gap: 20, minWidth: 0 }}>
              <div className="content-card">
                <p className="eyebrow">{skill.category}</p>
                <h1 className="skill-title">{skill.displayName}</h1>
                <p className="lede" style={{ marginTop: 20 }}>
                  {skill.description}
                </p>
              </div>

              <div className="content-card dark">
                <h2 className="display compact">
                  What this skill adds
                </h2>
                <div className="markdown-snippet" style={{ marginTop: 18, color: "var(--panel-muted)" }}>
                  <p style={{ color: "var(--panel-muted)" }}>{skill.summary || skill.shortDescription}</p>
                  {sections.map((section) => (
                    <div key={section.title}>
                      <h3 style={{ marginBottom: 8 }}>{section.title}</h3>
                      <ul className="list">
                        {plainLines(section.content).map((line, index) => (
                          <li key={`${section.title}-${index}-${line}`}>{line}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>

              <div className="content-card">
                <h2 className="display compact">
                  Default agent prompt
                </h2>
                <div className="command-strip" style={{ marginTop: 18, background: "var(--panel)" }}>
                  <code>{skill.defaultPrompt}</code>
                  <CopyButton value={skill.defaultPrompt} label={`Copy default prompt for ${skill.name}`} />
                </div>
              </div>
            </div>

            <aside className="detail-aside">
              <InstallCard skillName={skill.name} title={skill.name} />

              <div className="content-card dark">
                <h3>Source files</h3>
                <ul className="list">
                  {sourceFiles.map((file) => (
                    <li key={file}>
                      <a href={sourceUrl(file)} target="_blank" rel="noreferrer">
                        <FileCode2 size={16} aria-hidden="true" /> {file}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            </aside>
          </div>
        </div>
      </section>
    </div>
  );
}
