import { ArrowRight, Boxes, Code2, Sparkles } from "lucide-react";
import Link from "next/link";
import { CopyButton } from "@/components/copy-button";
import { InstallCard } from "@/components/install-card";
import { SkillCard } from "@/components/skill-card";
import { getSkills } from "@/lib/skills";
import { npmPackage, repositorySource } from "@/lib/agents";

export default function HomePage() {
  const skills = getSkills();
  const featured = skills.slice(0, 3);

  return (
    <div id="content">
      <section className="hero">
        <div className="container hero-grid">
          <div className="hero-copy">
            <p className="eyebrow">Souvik Skills / agent marketplace</p>
            <h1>Souvik Skills</h1>
            <p className="lede">Marketplace-ready agent skills by Souvik Dey, generated from the repository itself.</p>
            <p className="muted">
              Browse independent skill pages, copy install commands for multiple agents, and understand exactly what each
              workflow adds before installing it.
            </p>
            <div className="hero-actions">
              <Link className="button primary" href="/skills">
                Browse skills <ArrowRight size={18} aria-hidden="true" />
              </Link>
              <Link className="button secondary" href="/install">
                Install matrix
              </Link>
            </div>
            <dl className="stats-grid">
              <div className="stat">
                <dt>Skills</dt>
                <dd>{skills.length}</dd>
              </div>
              <div className="stat">
                <dt>Package</dt>
                <dd>{npmPackage}</dd>
              </div>
              <div className="stat">
                <dt>Repository</dt>
                <dd>{repositorySource}</dd>
              </div>
              <div className="stat">
                <dt>License</dt>
                <dd>MIT</dd>
              </div>
            </dl>
          </div>

          <article className="mac-card">
            <div className="mac-toolbar">
              <span className="traffic red" />
              <span className="traffic amber" />
              <span className="traffic green" />
              <span className="mac-title">souvik-skills.app</span>
            </div>
            <div className="terminal-preview">
              <div className="terminal-line">
                <span className="terminal-prompt">$</span>
                <span>npx @imsovikde/skills install all</span>
              </div>
              <div className="terminal-line">
                <span className="terminal-prompt">scan</span>
                <span>skills/*/SKILL.md + agents/openai.yaml</span>
              </div>
              <div className="terminal-line">
                <span className="terminal-prompt">build</span>
                <span>{skills.length} independent marketplace pages</span>
              </div>
              <div className="command-strip">
                <code>npx @imsovikde/skills install all</code>
                <CopyButton value="npx @imsovikde/skills install all" label="Copy install all command" />
              </div>
              <div className="ascii-panel">{`[ Souvik Skills ]
  ├─ project install
  ├─ global install
  └─ try once`}</div>
            </div>
          </article>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="section-heading">
            <p className="eyebrow">Featured skills</p>
            <div>
              <h2>Mac-style cards for real skill pages.</h2>
              <p className="muted">Every card links to a dedicated page with its own install panel and source metadata.</p>
            </div>
          </div>
          <div className="skill-grid">
            {featured.map((skill, index) => (
              <SkillCard key={skill.name} skill={skill} index={index} />
            ))}
          </div>
        </div>
      </section>

      <section className="section tight">
        <div className="container detail-grid">
          <div className="content-card">
            <p className="eyebrow">What changed</p>
            <h2 className="display">No drawer trap. Real pages.</h2>
            <p className="muted" style={{ marginTop: 16 }}>
              The marketplace now behaves like a site: routable pages, static build output, no ugly inner scrollbars, and
              mobile layouts designed first.
            </p>
            <div className="route-grid" style={{ marginTop: 22 }}>
              <div className="stat">
                <dt>
                  <Boxes size={15} aria-hidden="true" /> Catalog
                </dt>
                <dd>/skills</dd>
              </div>
              <div className="stat">
                <dt>
                  <Code2 size={15} aria-hidden="true" /> Detail
                </dt>
                <dd>/skills/name</dd>
              </div>
              <div className="stat">
                <dt>
                  <Sparkles size={15} aria-hidden="true" /> Motion
                </dt>
                <dd>/motion</dd>
              </div>
            </div>
          </div>
          <InstallCard skillName={skills[0]?.name || "motioncraft"} title="sample" />
        </div>
      </section>
    </div>
  );
}
