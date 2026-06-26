export function LogoMark({ className = "brand-mark" }) {
  return (
    <svg className={className} viewBox="0 0 64 64" role="img" aria-label="Souvik Skills mark">
      <rect x="4" y="4" width="56" height="56" rx="15" fill="#1c1c22" />
      <path d="M18 18h28v7H27v7h15v7H27v7h21v7H18V18z" fill="#f7f2e9" />
      <path d="M14 13h11v6h-5v26h5v6H14V13zm36 0v38H39v-6h5V19h-5v-6h11z" fill="#d87258" />
      <path d="M31 13h4v7h-4zm0 31h4v7h-4z" fill="#f0b85f" />
    </svg>
  );
}

export function GitHubIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <path
        fill="currentColor"
        d="M12 2.25a9.75 9.75 0 0 0-3.08 19c.49.09.67-.21.67-.47v-1.66c-2.72.59-3.29-1.17-3.29-1.17-.45-1.12-1.09-1.42-1.09-1.42-.88-.6.07-.59.07-.59.98.07 1.5 1 1.5 1 .87 1.49 2.29 1.06 2.85.81.09-.63.34-1.06.62-1.31-2.17-.25-4.46-1.09-4.46-4.84 0-1.07.38-1.95 1-2.63-.1-.25-.43-1.25.1-2.59 0 0 .82-.26 2.68 1a9.25 9.25 0 0 1 4.88 0c1.86-1.26 2.68-1 2.68-1 .53 1.34.2 2.34.1 2.59.62.68 1 1.56 1 2.63 0 3.76-2.29 4.58-4.47 4.83.35.31.67.91.67 1.83v2.72c0 .26.18.57.68.47A9.75 9.75 0 0 0 12 2.25Z"
      />
    </svg>
  );
}
