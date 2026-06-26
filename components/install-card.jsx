"use client";

import { motion } from "motion/react";
import { useMemo, useState } from "react";
import { agents, commandFor, installModes } from "@/lib/agents";
import { CopyButton } from "./copy-button";
import { SelectMenu } from "./select-menu";

export function InstallCard({ skillName, title = "Install skill" }) {
  const [agentId, setAgentId] = useState("claude-code");
  const [modeId, setModeId] = useState("project");

  const agent = agents.find((item) => item.id === agentId) || agents[0];
  const mode = installModes.find((item) => item.id === modeId) || installModes[0];
  const command = useMemo(() => commandFor(skillName, modeId, agentId), [skillName, modeId, agentId]);
  const agentOptions = useMemo(
    () => agents.map((item) => ({ value: item.id, label: item.label, meta: item.id })),
    []
  );

  return (
    <motion.section
      className="install-card"
      initial={{ opacity: 0, y: 14 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
    >
      <div className="install-inner">
        <div>
          <p className="install-label">Install {title}</p>
        </div>

        <SelectMenu label="Agent" value={agentId} options={agentOptions} onChange={setAgentId} className="agent-select" />

        <div className="install-tabs" role="tablist" aria-label="Install mode">
          {installModes.map((item) => (
            <button
              key={item.id}
              className={`install-tab ${item.id === modeId ? "active" : ""}`}
              type="button"
              role="tab"
              aria-selected={item.id === modeId}
              onClick={() => setModeId(item.id)}
            >
              {item.id === modeId ? <motion.span className="tab-pill" layoutId={`tab-pill-${skillName}`} /> : null}
              <span style={{ position: "relative", zIndex: 1 }}>{item.label}</span>
            </button>
          ))}
        </div>

        <div className="install-command">
          <code>{command}</code>
          <CopyButton value={command} label={`Copy ${mode.label} install command`} />
        </div>

        <p className="install-helper">{mode.helper(agent)}</p>
      </div>
    </motion.section>
  );
}
