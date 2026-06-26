import Link from "next/link";

export default function NotFound() {
  return (
    <main id="content" className="section">
      <div className="container content-card">
        <p className="eyebrow">404</p>
        <h1 style={{ fontSize: "clamp(3rem, 8vw, 7rem)" }}>Page not found.</h1>
        <p className="lede" style={{ marginTop: 18 }}>
          This route does not exist in the Souvik Skills marketplace.
        </p>
        <Link className="button primary" href="/skills" style={{ marginTop: 24 }}>
          Browse skills
        </Link>
      </div>
    </main>
  );
}
