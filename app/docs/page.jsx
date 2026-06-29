import { BookOpen, FileCheck2, FolderTree, ShieldCheck } from "lucide-react";
import { getSkills } from "@/lib/skills";

export const metadata = {
  title: "Docs",
  description: "Repository standards and frontend guidance for Souvik Skills."
};

const standards = [
  {
    icon: FolderTree,
    title: "Self-contained folders",
    body: "Each public workflow lives under skills/<skill-name> with its own SKILL.md and agent metadata."
  },
  {
    icon: FileCheck2,
    title: "Strict frontmatter",
    body: "SKILL.md frontmatter uses only name and description, and the name must match the folder."
  },
  {
    icon: BookOpen,
    title: "Progressive resources",
    body: "References, scripts, and assets stay inside the skill folder and load only when they help the workflow."
  },
  {
    icon: ShieldCheck,
    title: "Validation before release",
    body: "npm run validate:skills checks naming, metadata, README coverage, install commands, and context hygiene."
  }
];

export default function DocsPage() {
  const skills = getSkills();

  return (
    <div id="content">
      <section className="section">
        <div className="container">
          <div className="section-heading">
            <p className="eyebrow">Documentation</p>
            <div>
              <h1 style={{ fontSize: "clamp(3rem, 8vw, 7rem)" }}>A marketplace that documents itself.</h1>
              <p className="lede" style={{ marginTop: 18 }}>
                Souvik Skills uses repository rules, design rules, and motion rules so future frontend work remains
                consistent and mobile-safe.
              </p>
            </div>
          </div>

          <div className="route-grid">
            {standards.map((item) => {
              const Icon = item.icon;
              return (
                <article className="content-card" key={item.title}>
                  <Icon size={28} color="var(--coral-strong)" aria-hidden="true" />
                  <h3 style={{ marginTop: 16 }}>{item.title}</h3>
                  <p className="muted" style={{ marginTop: 10 }}>
                    {item.body}
                  </p>
                </article>
              );
            })}
          </div>
        </div>
      </section>

      <section className="section tight">
        <div className="container detail-grid">
          <div className="content-card dark">
            <h2 className="display">Frontend contract</h2>
            <ul className="list">
              <li>Read DESIGN.md before changing layout, color, typography, cards, or logo assets.</li>
              <li>Read MOTION.md before adding animation, transition, route motion, or gesture feedback.</li>
              <li>Keep all marketplace pages generated from skills/ at build time.</li>
              <li>After any public skill is added or updated, confirm the homepage, catalog, skill detail, install, and docs pages reflect it.</li>
              <li>Validate mobile at 360px, 390px, 430px, tablet, desktop, and wide desktop.</li>
            </ul>
          </div>

          <div className="content-card">
            <h2 className="display" style={{ fontSize: "clamp(2rem, 5vw, 4rem)" }}>
              Current catalog
            </h2>
            <ul className="list">
              {skills.map((skill) => (
                <li key={skill.name}>
                  <strong>{skill.name}</strong> - {skill.shortDescription}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>
    </div>
  );
}
