"use client";

import { motion } from "motion/react";
import { Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";

function getPreferredTheme() {
  if (typeof window === "undefined") return "light";
  const stored = window.localStorage.getItem("souvik-skills-theme");
  if (stored === "dark" || stored === "light") return stored;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function applyTheme(theme) {
  const root = document.documentElement;
  root.classList.remove("light", "dark");
  root.classList.add(theme);
  root.dataset.theme = theme;
  root.style.colorScheme = theme;
  window.localStorage.setItem("souvik-skills-theme", theme);
}

export function ThemeToggle() {
  const [theme, setTheme] = useState("light");
  const [transitioning, setTransitioning] = useState(false);

  useEffect(() => {
    const preferred = getPreferredTheme();
    setTheme(preferred);
    applyTheme(preferred);
  }, []);

  async function toggleTheme(event) {
    if (transitioning) return;

    const nextTheme = theme === "dark" ? "light" : "dark";
    const root = document.documentElement;
    const rect = event.currentTarget.getBoundingClientRect();
    const x = rect.left + rect.width / 2;
    const y = rect.top + rect.height / 2;

    setTransitioning(true);

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    if (!document.startViewTransition || reduceMotion) {
      applyTheme(nextTheme);
      setTheme(nextTheme);
      window.setTimeout(() => setTransitioning(false), 160);
      return;
    }

    root.classList.add("theme-reveal-running");

    const transition = document.startViewTransition(() => {
      applyTheme(nextTheme);
      setTheme(nextTheme);
    });

    try {
      await transition.ready;
      const endRadius = Math.hypot(
        Math.max(x, window.innerWidth - x),
        Math.max(y, window.innerHeight - y)
      );

      root.animate(
        {
          clipPath: [`circle(0px at ${x}px ${y}px)`, `circle(${endRadius}px at ${x}px ${y}px)`]
        },
        {
          duration: 520,
          easing: "cubic-bezier(0.16, 1, 0.3, 1)",
          pseudoElement: "::view-transition-new(root)"
        }
      );

      await transition.finished;
    } finally {
      root.classList.remove("theme-reveal-running");
      setTransitioning(false);
    }
  }

  const isDark = theme === "dark";

  return (
    <motion.button
      className="theme-toggle"
      type="button"
      aria-label={`Switch to ${isDark ? "light" : "dark"} mode`}
      aria-pressed={isDark}
      disabled={transitioning}
      onClick={toggleTheme}
      whileTap={{ scale: 0.96 }}
    >
      <motion.span
        className="theme-thumb"
        aria-hidden="true"
        animate={{ x: isDark ? 32 : 0 }}
        transition={{ type: "spring", stiffness: 420, damping: 42, mass: 0.7 }}
      />
      <span className="theme-cell" aria-hidden="true">
        <motion.span
          animate={{
            opacity: isDark ? 0.45 : 1,
            rotate: isDark ? -28 : 0,
            scale: isDark ? 0.82 : 1
          }}
          transition={{ duration: 0.18, ease: [0.16, 1, 0.3, 1] }}
        >
          <Sun size={16} />
        </motion.span>
      </span>
      <span className="theme-cell" aria-hidden="true">
        <motion.span
          animate={{
            opacity: isDark ? 1 : 0.45,
            rotate: isDark ? 0 : 28,
            scale: isDark ? 1 : 0.82
          }}
          transition={{ duration: 0.18, ease: [0.16, 1, 0.3, 1] }}
        >
          <Moon size={16} />
        </motion.span>
      </span>
    </motion.button>
  );
}
