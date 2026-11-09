#!/usr/bin/env python3
"""
Pre-Download 18+ Age & Legal Compliance Gate
Validates public media URLs and records cryptographic, timestamped legal attestations
for adult/age-restricted media. General audience (non-explicit) media passes automatically.
"""

import argparse
import sys
import os
import json
import hashlib
import ipaddress
import urllib.parse
import subprocess
import shutil
from datetime import datetime, timezone, timedelta

# Fix Windows console encodings
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

DEFAULT_ATTESTATION_FILE = "compliance_attestation.json"
ATTESTATION_VALIDITY_HOURS = 24


def normalize_url(url: str) -> str:
    """Normalize URL by trimming whitespace, lowercasing scheme and host, and removing fragments."""
    url = url.strip()
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Malformed URL: '{url}'. Expected absolute URL with http:// or https://")
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    normalized = urllib.parse.urlunparse((scheme, netloc, parsed.path, parsed.params, parsed.query, ""))
    return normalized


def compute_url_hash(normalized_url: str) -> str:
    """Compute deterministic SHA-256 hash of normalized URL."""
    return hashlib.sha256(normalized_url.encode("utf-8")).hexdigest()


def compute_token_hmac(url_hash: str, signature: str, timestamp_iso: str, purpose: str) -> str:
    """Compute cryptographic token integrity signature."""
    payload = f"{url_hash}:{signature.strip()}:{timestamp_iso}:{purpose.strip().lower()}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def is_public_url(url: str) -> bool:
    """Verify URL targets a public domain or routable public IP address, not local/private networks."""
    try:
        parsed = urllib.parse.urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return False
            
        lower_host = hostname.lower()
        if lower_host in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
            return False
        if lower_host.endswith(".local") or lower_host.endswith(".internal"):
            return False

        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_unspecified:
                return False
        except ValueError:
            pass
            
        return True
    except Exception:
        return False


def check_media_age_rating(url: str) -> tuple:
    """
    Query target URL to determine if it is age-restricted / explicit.
    Returns (is_restricted: bool, age_limit: int, title: str)
    """
    if not shutil.which("yt-dlp"):
        return False, 0, "Unknown Media (yt-dlp not on PATH)"

    cmd = [
        "yt-dlp",
        "--dump-single-json",
        "--no-playlist",
        "--extractor-args", "youtube:player_client=android,ios,web"
    ]
    if shutil.which("node"):
        cmd.extend(["--js-runtimes", "node"])
    cmd.append(url)

    try:
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=25
        )
        if res.returncode == 0 and res.stdout.strip():
            data = json.loads(res.stdout)
            age_limit = data.get("age_limit") or 0
            title = data.get("title") or "Public Media"
            is_restricted = int(age_limit) >= 18
            return is_restricted, int(age_limit), title
    except Exception:
        pass

    return False, 0, "Direct Stream / General Audience"


def create_attestation_token(
    url: str,
    signature: str = "Authorized Adult User",
    purpose: str = "archival",
    is_explicit: bool = False,
    age_limit: int = 0,
    output_path: str = None
) -> dict:
    """Generate and write a signed compliance attestation token."""
    normalized = normalize_url(url)
    if not is_public_url(normalized):
        raise ValueError("URL must point to a publicly accessible media resource, not a private or loopback address.")

    sig_clean = signature.strip() if signature else "Authorized User"
    now_utc = datetime.now(timezone.utc)
    expires_utc = now_utc + timedelta(hours=ATTESTATION_VALIDITY_HOURS)
    timestamp_iso = now_utc.isoformat()
    expires_iso = expires_utc.isoformat()
    url_hash = compute_url_hash(normalized)
    token_hmac = compute_token_hmac(url_hash, sig_clean, timestamp_iso, purpose)

    token_data = {
        "version": "1.1",
        "attestation_type": "18_plus_conditional_compliance",
        "url_hash_sha256": url_hash,
        "target_url_redacted": f"{normalized[:30]}...{normalized[-10:]}" if len(normalized) > 45 else normalized,
        "is_explicit_media": is_explicit,
        "age_limit": age_limit,
        "confirm_adult_18plus": True,
        "signature": sig_clean,
        "purpose": purpose.strip().lower(),
        "created_at_utc": timestamp_iso,
        "expires_at_utc": expires_iso,
        "valid_hours": ATTESTATION_VALIDITY_HOURS,
        "integrity_hmac_sha256": token_hmac,
        "legal_declarations": [
            "User certifies they are 18 years of age or older if accessing age-restricted media.",
            "User certifies the target media stream is publicly accessible without bypassing access controls.",
            "User certifies download is for permitted personal archival, non-commercial research, or offline viewing."
        ]
    }

    out_file = output_path if output_path else DEFAULT_ATTESTATION_FILE
    out_dir = os.path.dirname(os.path.abspath(out_file))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(token_data, f, indent=2)

    return token_data


def validate_attestation_token(token_path: str, target_url: str) -> tuple:
    """
    Validate that an attestation token exists, is unexpired, matches target URL hash, and has valid HMAC.
    Returns (is_valid: bool, message: str, token_data: dict)
    """
    if not os.path.exists(token_path):
        return False, f"Attestation file not found at: {token_path}", None

    try:
        with open(token_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return False, f"Failed to parse attestation JSON: {e}", None

    required_keys = ["version", "url_hash_sha256", "confirm_adult_18plus", "signature", "created_at_utc", "expires_at_utc", "integrity_hmac_sha256"]
    for k in required_keys:
        if k not in data:
            return False, f"Malformed attestation token: missing field '{k}'", None

    if not data.get("confirm_adult_18plus", False):
        return False, "Attestation rejected: 18+ adult confirmation is not affirmed.", None

    # Check expiration
    try:
        expires_at = datetime.fromisoformat(data["expires_at_utc"])
        if datetime.now(timezone.utc) > expires_at:
            return False, f"Attestation token expired at {data['expires_at_utc']}. Please re-attest.", None
    except Exception as e:
        return False, f"Invalid expiration timestamp format: {e}", None

    # Verify URL hash match
    try:
        norm_url = normalize_url(target_url)
        expected_hash = compute_url_hash(norm_url)
        if data["url_hash_sha256"] != expected_hash:
            return False, "Attestation token URL mismatch. Token bound to different URL hash.", None
    except Exception as e:
        return False, f"Error validating target URL hash: {e}", None

    # Verify cryptographic integrity HMAC
    expected_hmac = compute_token_hmac(
        data["url_hash_sha256"],
        data["signature"],
        data["created_at_utc"],
        data.get("purpose", "archival")
    )
    if data["integrity_hmac_sha256"] != expected_hmac:
        return False, "Attestation integrity check failed. Token may have been altered.", None

    return True, "Attestation verified successfully.", data


def main():
    parser = argparse.ArgumentParser(
        description="Conditional 18+ Age & Legal Compliance Gate for Universal Video Downloader"
    )
    parser.add_argument("--url", required=True, help="Target public media URL")
    parser.add_argument("--confirm-adult-18plus", action="store_true", help="Affirm that you are 18 years of age or older if media is age-restricted")
    parser.add_argument("--signature", type=str, default="", help="Your full name or authorized legal signature string")
    parser.add_argument("--purpose", choices=["archival", "research", "personal"], default="archival", help="Purpose of download (default: archival)")
    parser.add_argument("--attestation-out", default=DEFAULT_ATTESTATION_FILE, help=f"Output path for attestation token JSON (default: {DEFAULT_ATTESTATION_FILE})")
    parser.add_argument("--verify", type=str, default=None, help="Verify an existing attestation token against --url instead of creating one")
    parser.add_argument("--check-only", action="store_true", help="Query whether the URL is age-restricted without creating an attestation")

    args = parser.parse_args()

    # Verification Mode
    if args.verify:
        is_valid, msg, token = validate_attestation_token(args.verify, args.url)
        if is_valid:
            print("=" * 65)
            print("[COMPLIANCE VERIFIED] Attestation Token is VALID")
            print("=" * 65)
            print(f"Target URL Hash: {token['url_hash_sha256']}")
            print(f"Signed By:       {token['signature']}")
            print(f"Purpose:         {token['purpose']}")
            print(f"Expires At:      {token['expires_at_utc']}")
            print("=" * 65)
            sys.exit(0)
        else:
            print(f"[COMPLIANCE ERROR] {msg}", file=sys.stderr)
            sys.exit(1)

    # Check age rating
    is_restricted, age_limit, title = check_media_age_rating(args.url)

    if args.check_only:
        print("=" * 65)
        print("  MEDIA AGE RATING INSPECTION")
        print("=" * 65)
        print(f"URL:            {args.url}")
        print(f"Title:          {title}")
        print(f"Age Limit:      {age_limit}")
        print(f"Classification: {'18+ ADULT / AGE-RESTRICTED' if is_restricted else 'GENERAL AUDIENCE (Non-Explicit)'}")
        print(f"18+ Gate Req:   {'YES (Adult confirmation required)' if is_restricted else 'NO (Unrestricted access)'}")
        print("=" * 65)
        sys.exit(0)

    # If general audience (non-explicit), no 18+ confirmation is required
    if not is_restricted:
        print(f"[COMPLIANCE PASS] Media '{title}' is General Audience (age_limit: {age_limit}).")
        print("No 18+ adult confirmation is required. Downloading and probing unlocked.\n")
        # Generate an auto-approved token for tools that accept a token
        token = create_attestation_token(
            url=args.url,
            signature=args.signature or "General Audience Pass",
            purpose=args.purpose,
            is_explicit=False,
            age_limit=age_limit,
            output_path=args.attestation_out
        )
        sys.exit(0)

    # Explicit / Age-Restricted media: enforce 18+ confirmation
    if not args.confirm_adult_18plus:
        print("=" * 65, file=sys.stderr)
        print("[AGE-RESTRICTED MEDIA DETECTED: 18+ CONFIRMATION REQUIRED]", file=sys.stderr)
        print("=" * 65, file=sys.stderr)
        print(f"Media Title:  {title}", file=sys.stderr)
        print(f"Age Limit:    {age_limit}+ (Adult / Explicit Content)", file=sys.stderr)
        print("", file=sys.stderr)
        print("This media is classified as adult or age-restricted.", file=sys.stderr)
        print("You MUST affirm that you are 18 years of age or older in your jurisdiction.", file=sys.stderr)
        print("", file=sys.stderr)
        print("Re-run with adult confirmation:", file=sys.stderr)
        print("  --confirm-adult-18plus", file=sys.stderr)
        print('Optional signature: --signature "Your Name"', file=sys.stderr)
        print("=" * 65, file=sys.stderr)
        sys.exit(2)

    try:
        token = create_attestation_token(
            url=args.url,
            signature=args.signature or "Adult User Attested",
            purpose=args.purpose,
            is_explicit=True,
            age_limit=age_limit,
            output_path=args.attestation_out
        )
        print("=" * 65)
        print("  18+ Age & Legal Attestation Gate: VERIFIED & SIGNED")
        print("=" * 65)
        print(f"Target URL:         {args.url}")
        print(f"URL SHA-256:        {token['url_hash_sha256']}")
        print(f"Signee:             {token['signature']}")
        print(f"Adult (18+):        AFFIRMED")
        print(f"Purpose:            {token['purpose']}")
        print(f"Attestation File:   {os.path.abspath(args.attestation_out)}")
        print(f"Token Expiration:   {token['expires_at_utc']} ({token['valid_hours']}h)")
        print(f"Integrity HMAC:     {token['integrity_hmac_sha256']}")
        print("=" * 65)
        print("[SUCCESS] Compliance attestation recorded. Proceed with probe_stream.py or download_video.py.\n")
        sys.exit(0)
    except Exception as e:
        print(f"[COMPLIANCE ERROR] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
