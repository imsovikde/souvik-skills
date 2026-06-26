"use client";

import { AnimatePresence, motion } from "motion/react";
import { Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";

function getPreferredTheme() {
  if (typeof window === "undefined") return "light";
  const stored = window.localStorage.getItem("souvik-skills-theme");
  if (stored === "dark" || stored === "light") return stored;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export function ThemeToggle() {
  const [theme, setTheme] = useState("light");

  useEffect(() => {
    const preferred = getPreferredTheme();
    setTheme(preferred);
    document.documentElement.dataset.theme = preferred;
  }, []);

  function toggleTheme() {
    const nextTheme = theme === "dark" ? "light" : "dark";
    setTheme(nextTheme);
    document.documentElement.dataset.theme = nextTheme;
    window.localStorage.setItem("souvik-skills-theme", nextTheme);
  }

  const isDark = theme === "dark";

  return (
    <motion.button
      className="theme-toggle"
      type="button"
      aria-label={`Switch to ${isDark ? "light" : "dark"} mode`}
      aria-pressed={isDark}
      onClick={toggleTheme}
      whileTap={{ scale: 0.96 }}
    >
      <span className="theme-track" aria-hidden="true">
        <motion.span className="theme-thumb" layout transition={{ type: "spring", visualDuration: 0.28, bounce: 0.12 }}>
          <AnimatePresence mode="wait" initial={false}>
            {isDark ? (
              <motion.span
                key="moon"
                initial={{ opacity: 0, rotate: -25, scale: 0.7 }}
                animate={{ opacity: 1, rotate: 0, scale: 1 }}
                exit={{ opacity: 0, rotate: 25, scale: 0.7 }}
              >
                <Moon size={15} />
              </motion.span>
            ) : (
              <motion.span
                key="sun"
                initial={{ opacity: 0, rotate: 25, scale: 0.7 }}
                animate={{ opacity: 1, rotate: 0, scale: 1 }}
                exit={{ opacity: 0, rotate: -25, scale: 0.7 }}
              >
                <Sun size={15} />
              </motion.span>
            )}
          </AnimatePresence>
        </motion.span>
      </span>
      <span className="theme-copy">{isDark ? "Dark" : "Light"}</span>
    </motion.button>
  );
}
