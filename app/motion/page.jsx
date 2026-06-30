import { Activity, MousePointerClick, PanelTopOpen, Sparkles } from "lucide-react";
import { CopyButton } from "@/components/copy-button";
import { InstallCard } from "@/components/install-card";
import { getSkills } from "@/lib/skills";

export const metadata = {
  title: "Motion",
  description: "Motion engineering standards for the Souvik Skills marketplace."
};

const moments = [
  {
    icon: MousePointerClick,
    title: "Immediate feedback",
    body: "Press and copy states respond inside the 50-160ms tactile window."
  },
  {
    icon: PanelTopOpen,
    title: "Tab continuity",
    body: "Install mode changes use a shared moving pill instead of a hard cut."
  },
  {
    icon: Activity,
    title: "Route presence",
    body: "Pages enter with low-distance opacity and y motion, then settle."
  },
  {
    icon: Sparkles,
    title: "Reduced motion",
    body: "Motion respects user preference and removes expressive movement."
  }
];

export default function MotionPage() {
  const skills = getSkills();
  const sampleSkill = skills.find((skill) => skill.name === "motioncraft") || skills[0];

  return (
    <div id="content">
      <section className="section">
        <div className="container">
          <div className="section-heading">
            <p className="eyebrow">Motion engineering</p>
            <div>
              <h1 className="page-title">Responsive, not noisy.</h1>
              <p className="lede" style={{ marginTop: 18 }}>
                Motion on this site exists to confirm input, preserve orientation, and make install actions feel precise.
              </p>
            </div>
          </div>

          <div className="route-grid">
            {moments.map((moment) => {
              const Icon = moment.icon;
              return (
                <article className="content-card" key={moment.title}>
                  <Icon size={28} color="var(--coral-strong)" aria-hidden="true" />
                  <h3 style={{ marginTop: 16 }}>{moment.title}</h3>
                  <p className="muted" style={{ marginTop: 10 }}>
                    {moment.body}
                  </p>
                </article>
              );
            })}
          </div>
        </div>
      </section>

      <section className="section tight">
        <div className="container detail-grid">
          <InstallCard skillName={sampleSkill?.name || "motioncraft"} title="motion demo" />
          <div className="content-card dark">
            <h2 className="display">Copy animation</h2>
            <p style={{ marginTop: 14, color: "var(--panel-muted)" }}>
              The copy button compresses on press, morphs to a check, and runs a restrained glow sweep.
            </p>
            <div className="install-command" style={{ marginTop: 20 }}>
              <code>npx @imsovikde/skills list</code>
              <CopyButton value="npx @imsovikde/skills list" label="Copy demo command" />
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
