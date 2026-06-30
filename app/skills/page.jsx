import { MarketplaceBrowser } from "@/components/marketplace-browser";
import { getSkills } from "@/lib/skills";

export const metadata = {
  title: "Skills",
  description: "Browse every Souvik Skills workflow."
};

export default function SkillsPage() {
  const skills = getSkills();

  return (
    <div id="content">
      <section className="section">
        <div className="container">
          <div className="section-heading">
            <p className="eyebrow">Skill marketplace</p>
            <div>
              <h1 className="page-title">Every skill gets a page.</h1>
              <p className="lede" style={{ marginTop: 18 }}>
                Search the catalog, compare workflows, and open a complete page for installation and source context.
              </p>
            </div>
          </div>
          <MarketplaceBrowser skills={skills} />
        </div>
      </section>
    </div>
  );
}
