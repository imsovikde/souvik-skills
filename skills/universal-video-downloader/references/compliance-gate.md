# Conditional 18+ Compliance & Legal Attestation Protocol

This guide outlines the legal and technical requirements enforced by the `universal-video-downloader` compliance gate.

---

## 1. Compliance Scope & Legal Foundation

The `universal-video-downloader` skill operates strictly within the boundaries of applicable digital media laws and platform terms:

1. **Publicly Accessible Media Only**:
   - The tool operates exclusively on publicly accessible URLs and public media streams that require no authenticated bypass or session theft.
   - It **never** attempts to circumvent DRM systems (such as Google Widevine, Apple FairPlay, or Microsoft PlayReady).
   - It **never** bypasses subscriber paywalls, access control lists, or private authentication barriers.
2. **Permitted Use Cases**:
   - Time-shifting and offline viewing for personal use.
   - Archival of publicly released media, conferences, academic presentations, and tutorials.
   - Research and technical analysis of video compression codecs and adaptive streaming protocols.

---

## 2. Conditional 18+ Age Certification

Under the updated conditional policy:

- **General Audience Media (`age_limit < 18`)**:
  - General audience videos (e.g., standard YouTube tutorials, public music videos, Dailymotion clips, podcasts) bypass the 18+ gate completely.
  - The tools execute immediately without prompting for age certification.
- **Age-Restricted / Adult Media (`age_limit >= 18`)**:
  - If a media stream is classified as age-gated, explicit, or adult content, the user must confirm they are 18 years of age or older in their jurisdiction.
  - Confirmation can be provided directly via the `--confirm-adult-18plus` flag or via a signed `compliance_attestation.json` token.
  - If confirmation is missing on an explicit video, probing and downloading abort with **exit code 2**.

---

## 3. Cryptographic Token Specification

When compliance is affirmed for age-restricted media, `scripts/verify_compliance.py` creates a signed token (`compliance_attestation.json`):

```json
{
  "version": "1.1",
  "attestation_type": "18_plus_conditional_compliance",
  "url_hash_sha256": "4a7d...39b1",
  "target_url_redacted": "https://example.com/video",
  "is_explicit_media": true,
  "age_limit": 18,
  "confirm_adult_18plus": true,
  "signature": "Full Name",
  "purpose": "archival",
  "created_at_utc": "2026-11-09T05:00:00+00:00",
  "expires_at_utc": "2026-11-10T05:00:00+00:00",
  "valid_hours": 24,
  "integrity_hmac_sha256": "8f12...e4a7",
  "legal_declarations": [
    "User certifies they are 18 years of age or older if accessing age-restricted media.",
    "User certifies the target media stream is publicly accessible without bypassing access controls.",
    "User certifies download is for permitted personal archival, non-commercial research, or offline viewing."
  ]
}
```

### Verification Algorithm
When `probe_stream.py` or `download_video.py` is invoked:
1. The target URL is normalized (stripped of fragments, lowercasing scheme and host).
2. The SHA-256 hash of the normalized URL is calculated and compared against `url_hash_sha256`.
3. The expiration timestamp (`expires_at_utc`) is checked against current UTC time.
4. The token's integrity HMAC is recalculated using:
   $$\text{HMAC} = \text{SHA-256}(\text{url\_hash} : \text{signature} : \text{created\_at\_utc} : \text{purpose})$$
   and matched against `integrity_hmac_sha256`.

---

## 4. Operational Runbook

### Checking Media Age Rating
```bash
python scripts/verify_compliance.py --url "URL" --check-only
```

### Generating an Attestation Token for Explicit Media
```bash
python scripts/verify_compliance.py \
  --url "https://example.com/explicit-video" \
  --confirm-adult-18plus \
  --signature "Your Full Name" \
  --purpose archival \
  --attestation-out compliance_attestation.json
```

### Direct In-Prompt Confirmation
```bash
python scripts/download_video.py "https://example.com/explicit-video" --confirm-adult-18plus -q best -o "./downloads"
```
