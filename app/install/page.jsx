import { InstallCard } from "@/components/install-card";
import { SkillCard } from "@/components/skill-card";
import { getSkills } from "@/lib/skills";

export const metadata = {
  title: "Install",
  description: "Copy Souvik Skills install commands for every supported agent."
};

export default function InstallPage() {
  const skills = getSkills();

  return (
    <div id="content">
      <section className="section">
        <div className="container">
          <div className="section-heading">
            <p className="eyebrow">Install matrix</p>
            <div>
              <h1 className="page-title">Project, global, or try once.</h1>
              <p className="lede" style={{ marginTop: 18 }}>
                Each skill gets the same macOS-style installer module with Core 6 agent support and animated copy actions.
              </p>
            </div>
          </div>

          <div className="install-matrix">
            {skills.map((skill) => (
              <InstallCard key={skill.name} skillName={skill.name} title={skill.name} />
            ))}
          </div>
        </div>
      </section>

      <section className="section tight">
        <div className="container">
          <div className="section-heading">
            <p className="eyebrow">Skill pages</p>
            <div>
              <h2>Open a page before copying.</h2>
              <p className="muted">The cards below link to the richer skill explanations and source file lists.</p>
            </div>
          </div>
          <div className="skill-grid">
            {skills.map((skill, index) => (
              <SkillCard key={skill.name} skill={skill} index={index} />
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
