"use client";

import { AnimatePresence, LayoutGroup, motion } from "motion/react";
import { Search } from "lucide-react";
import { useMemo, useState } from "react";
import { SkillCard } from "./skill-card";
import { SelectMenu } from "./select-menu";

export function MarketplaceBrowser({ skills }) {
  const categories = useMemo(() => ["All", ...Array.from(new Set(skills.map((skill) => skill.category))).sort()], [skills]);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("All");
  const [sortBy, setSortBy] = useState("name");
  const sortOptions = [
    { value: "name", label: "Name", meta: "A-Z" },
    { value: "category", label: "Category", meta: "Grouped" }
  ];

  const visibleSkills = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();

    return skills
      .filter((skill) => {
        const matchesCategory = category === "All" || skill.category === category;
        const matchesQuery =
          !normalizedQuery ||
          [skill.name, skill.displayName, skill.category, skill.description, skill.shortDescription]
            .join(" ")
            .toLowerCase()
            .includes(normalizedQuery);

        return matchesCategory && matchesQuery;
      })
      .sort((a, b) => {
        if (sortBy === "category") return a.category.localeCompare(b.category) || a.displayName.localeCompare(b.displayName);
        return a.displayName.localeCompare(b.displayName);
      });
  }, [category, query, skills, sortBy]);

  return (
    <div>
      <div className="filter-panel">
        <label style={{ position: "relative", minWidth: 0 }}>
          <span className="sr-only">Search skills</span>
          <Search
            size={18}
            aria-hidden="true"
            style={{ position: "absolute", left: 14, top: "50%", transform: "translateY(-50%)", color: "var(--muted)" }}
          />
          <input
            className="search-input"
            style={{ paddingLeft: 42, width: "100%" }}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search skills, agents, commands"
            type="search"
          />
        </label>
        <div className="chip-row" aria-label="Skill categories">
          {categories.map((item) => (
            <button
              key={item}
              type="button"
              className={`chip ${item === category ? "active" : ""}`}
              onClick={() => setCategory(item)}
            >
              {item}
            </button>
          ))}
        </div>
        <SelectMenu label="Sort" value={sortBy} options={sortOptions} onChange={setSortBy} className="sort-control" />
      </div>

      <LayoutGroup>
        <motion.div className="skill-grid" layout>
          <AnimatePresence mode="popLayout">
            {visibleSkills.map((skill, index) => (
              <SkillCard key={skill.name} skill={skill} index={index} />
            ))}
          </AnimatePresence>
        </motion.div>
      </LayoutGroup>
    </div>
  );
}
