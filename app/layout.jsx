import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { SiteNav } from "@/components/site-nav";
import { PageTransition } from "@/components/page-transition";
import { LogoMark } from "@/components/brand";
import { githubUrl, npmUrl, siteUrl } from "@/lib/agents";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"]
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"]
});

export const metadata = {
  title: {
    default: "Souvik Skills",
    template: "%s | Souvik Skills"
  },
  description: "Marketplace-ready agent skills by Souvik Dey.",
  metadataBase: new URL(siteUrl),
  icons: {
    icon: [
      { url: "/favicon.ico", sizes: "any" },
      { url: "/icon.svg", type: "image/svg+xml" },
      { url: "/icon-192.png", type: "image/png", sizes: "192x192" }
    ],
    shortcut: "/favicon.ico",
    apple: [{ url: "/apple-icon.png", type: "image/png", sizes: "180x180" }]
  }
};

const themeScript = `
(() => {
  try {
    const stored = localStorage.getItem("souvik-skills-theme");
    const theme = stored === "dark" || stored === "light"
      ? stored
      : (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    const root = document.documentElement;
    root.classList.remove("light", "dark");
    root.classList.add(theme);
    root.dataset.theme = theme;
    root.style.colorScheme = theme;
  } catch {
    const root = document.documentElement;
    root.classList.add("light");
    root.dataset.theme = "light";
    root.style.colorScheme = "light";
  }
})();
`;

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable} light`} suppressHydrationWarning>
      <body>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
        <SiteNav />
        <PageTransition>{children}</PageTransition>
        <footer className="section" style={{ background: "var(--panel)", color: "var(--panel-muted)" }}>
          <div className="container" style={{ display: "grid", gap: 22 }}>
            <LogoMark />
            <p style={{ maxWidth: 620 }}>
              Souvik Skills is a public skill marketplace for reusable agent workflows, maintained by Souvik Dey and
              distributed through GitHub and NPM.
            </p>
            <div className="button-row">
              <a className="button dark" href={githubUrl} target="_blank" rel="noreferrer">
                GitHub repository
              </a>
              <a className="button dark" href={npmUrl} target="_blank" rel="noreferrer">
                NPM package
              </a>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
