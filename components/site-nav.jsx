"use client";

import { AnimatePresence, motion } from "motion/react";
import { Menu, X } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { GitHubIcon, LogoMark } from "./brand";
import { ThemeToggle } from "./theme-toggle";
import { githubUrl } from "@/lib/agents";

const links = [
  { href: "/", label: "Home" },
  { href: "/skills", label: "Skills" },
  { href: "/install", label: "Install" },
  { href: "/docs", label: "Docs" },
  { href: "/motion", label: "Motion" }
];

export function SiteNav() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const menuButtonRef = useRef(null);

  const isActive = (href) => (href === "/" ? pathname === href : pathname.startsWith(href));

  useEffect(() => {
    setOpen(false);
  }, [pathname]);

  useEffect(() => {
    if (!open) return;

    function handleKeyDown(event) {
      if (event.key === "Escape") {
        setOpen(false);
        menuButtonRef.current?.focus();
      }
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [open]);

  return (
    <header className="site-header">
      <a className="skip-link" href="#content">
        Skip to content
      </a>
      <nav className="nav container" aria-label="Primary navigation">
        <Link className="brand" href="/" onClick={() => setOpen(false)}>
          <LogoMark />
          <span className="brand-word">Souvik Skills</span>
        </Link>

        <div className="nav-links">
          {links.map((link) => (
            <Link key={link.href} className={isActive(link.href) ? "active" : ""} href={link.href}>
              {link.label}
            </Link>
          ))}
          <a href={githubUrl} target="_blank" rel="noreferrer">
            <GitHubIcon />
            GitHub
          </a>
          <ThemeToggle />
        </div>

        <div className="nav-controls">
          <ThemeToggle />
          <button
            ref={menuButtonRef}
            className="menu-button"
            type="button"
            aria-expanded={open}
            aria-controls="mobile-navigation"
            onClick={() => setOpen((value) => !value)}
          >
            {open ? <X size={21} aria-hidden="true" /> : <Menu size={21} aria-hidden="true" />}
            <span className="sr-only">Toggle navigation</span>
          </button>
        </div>
      </nav>

      <AnimatePresence>
        {open ? (
          <motion.div
            id="mobile-navigation"
            className="mobile-panel"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
          >
            {links.map((link) => (
              <Link key={link.href} href={link.href} onClick={() => setOpen(false)}>
                {link.label}
              </Link>
            ))}
            <a href={githubUrl} target="_blank" rel="noreferrer" onClick={() => setOpen(false)}>
              GitHub
            </a>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </header>
  );
}
