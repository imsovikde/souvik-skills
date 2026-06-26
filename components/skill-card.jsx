"use client";

import { motion } from "motion/react";
import { ArrowUpRight, FileCode2 } from "lucide-react";
import Link from "next/link";
import { commandFor } from "@/lib/agents";
import { CopyButton } from "./copy-button";

function shortCode(name) {
  return name
    .split("-")
    .map((part) => part[0])
    .join("")
    .slice(0, 4)
    .toUpperCase();
}

export function SkillCard({ skill, index = 0 }) {
  const command = commandFor(skill.name, "project", "claude-code");

  return (
    <motion.article
      className="skill-card"
      layout
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: Math.min(index * 0.035, 0.22) }}
      whileHover={{ y: -4, scale: 1.01 }}
    >
      <div className="mac-toolbar">
        <span className="traffic red" />
        <span className="traffic amber" />
        <span className="traffic green" />
        <span className="mac-title">[{shortCode(skill.name)}]</span>
      </div>
      <div className="skill-card-body">
        <div className="card-meta">
          <span className="badge">{skill.category}</span>
          {skill.hasResources ? <span className="badge">resources</span> : null}
        </div>
        <h3>{skill.displayName}</h3>
        <p className="description">{skill.description}</p>
        <div className="command-strip">
          <code>{command}</code>
          <CopyButton value={command} label={`Copy install command for ${skill.name}`} />
        </div>
        <div className="card-actions">
          <Link className="text-link" href={`/skills/${skill.name}`}>
            Skill page <ArrowUpRight size={16} aria-hidden="true" />
          </Link>
          <a className="text-link" href={`https://github.com/imsovikde/souvik-skills/tree/main/skills/${skill.name}`} target="_blank" rel="noreferrer">
            Source <FileCode2 size={16} aria-hidden="true" />
          </a>
        </div>
      </div>
    </motion.article>
  );
}
