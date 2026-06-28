"use client";

import { motion, useScroll, useSpring, useTransform } from "motion/react";
import Link from "next/link";
import { usePathname } from "next/navigation";
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
  const { scrollY } = useScroll();
  const rawProgress = useTransform(scrollY, [0, 128], [0, 1], { clamp: true });
  const headerProgress = useSpring(rawProgress, {
    stiffness: 420,
    damping: 42,
    mass: 0.7
  });
  const headerWidth = useTransform(headerProgress, [0, 1], ["1200px", "860px"]);
  const headerMinHeight = useTransform(headerProgress, [0, 1], ["76px", "68px"]);
  const headerRadius = useTransform(headerProgress, [0, 1], ["22px", "999px"]);
  const headerPaddingY = useTransform(headerProgress, [0, 1], ["12px", "9px"]);
  const headerPaddingX = useTransform(headerProgress, [0, 1], ["15px", "13px"]);
  const headerShadowY = useTransform(headerProgress, [0, 1], ["0px", "16px"]);
  const headerShadowBlur = useTransform(headerProgress, [0, 1], ["0px", "44px"]);
  const headerShadowAlpha = useTransform(headerProgress, [0, 1], [0, 0.14]);
  const mobileGutter = useTransform(headerProgress, [0, 1], ["32px", "20px"]);
  const mobileRadius = useTransform(headerProgress, [0, 1], ["18px", "26px"]);
  const mobilePaddingY = useTransform(headerProgress, [0, 1], ["10px", "9px"]);
  const mobilePaddingX = useTransform(headerProgress, [0, 1], ["10px", "9px"]);

  const isActive = (href) => (href === "/" ? pathname === href : pathname.startsWith(href));

  return (
    <header className="site-header">
      <a className="skip-link" href="#content">
        Skip to content
      </a>
      <motion.nav
        className="nav-shell"
        aria-label="Primary navigation"
        style={{
          "--header-width": headerWidth,
          "--header-min-height": headerMinHeight,
          "--header-radius": headerRadius,
          "--header-padding-y": headerPaddingY,
          "--header-padding-x": headerPaddingX,
          "--header-shadow-y": headerShadowY,
          "--header-shadow-blur": headerShadowBlur,
          "--header-shadow-alpha": headerShadowAlpha,
          "--header-mobile-gutter": mobileGutter,
          "--header-mobile-radius": mobileRadius,
          "--header-mobile-padding-y": mobilePaddingY,
          "--header-mobile-padding-x": mobilePaddingX
        }}
      >
        <Link className="brand" href="/">
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
        </div>

        <div className="nav-theme">
          <ThemeToggle />
        </div>
      </motion.nav>
    </header>
  );
}
