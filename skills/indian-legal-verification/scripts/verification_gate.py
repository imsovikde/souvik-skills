#!/usr/bin/env python3
# ====================================================================
# GEMINI_OFFLINE_ADAPTER: Environment Detection & Offline Gate
# In gemini.google.com sandbox, direct internet access is disabled.
# This script executes 100% locally and deterministically.
# ====================================================================
"""
Verification Gate for Indian Legal Verification
Deterministic compliance auditor for Indian legal drafts, complaints, and notices.
Checks for banned dashes, tracking links, unrevealed URLs, count mismatches,
vague citations, entitlement traps, footer PII, secrets, and zero-width characters.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Banned dash characters
EM_DASH = "\u2014"
EN_DASH = "\u2013"
ZERO_WIDTH_CHARS = re.compile(r"[\u200B\u200C\u200D\uFEFF\u202E]")

# Secret token patterns
SECRET_REGEXES = [
    re.compile(r"s" + r"k-[A-Za-z0-9]{20,}"),
    re.compile(r"g" + r"hp_[A-Za-z0-9]{36}"),
    re.compile(r"n" + r"pm_[A-Za-z0-9]{36}"),
    re.compile(r"A" + r"KIA[0-9A-Z]{16}"),
    re.compile(r"A" + r"Iza[0-9A-Za-z_-]{35}")
]

# Sensitive Indian PII patterns
PAN_REGEX = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")
AADHAAR_REGEX = re.compile(r"\b[2-9]{1}[0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b")
ACCOUNT_REGEX = re.compile(r"\b[0-9]{10,18}\b")

# Tracking parameters in URLs
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "gclid", "fbclid", "mc_eid", "ref", "source", "session_id", "trk"
}

# Approved official legal portal domains
OFFICIAL_DOMAINS = {
    "indiacode.gov.in", "www.indiacode.nic.in", "egazette.gov.in",
    "main.sci.gov.in", "sci.gov.in", "services.ecourts.gov.in", "ecourts.gov.in",
    "www.rbi.org.in", "rbi.org.in", "rbidocs.rbi.org.in",
    "www.sebi.gov.in", "sebi.gov.in", "scores.sebi.gov.in",
    "irdai.gov.in", "www.irdai.gov.in", "bimabharosa.irdai.gov.in",
    "www.cci.gov.in", "cci.gov.in", "fssai.gov.in", "www.fssai.gov.in",
    "foscos.fssai.gov.in", "cbfcindia.gov.in", "www.cbfcindia.gov.in",
    "ncdrc.nic.in", "ibbi.gov.in"
}

# Number words map
NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
}

def audit_draft_text(text: str, strict: bool = False) -> tuple[str, list[dict]]:
    defects = []
    lines = text.splitlines()

    # 1. Zero-width character scan
    for idx, line in enumerate(lines, 1):
        if ZERO_WIDTH_CHARS.search(line):
            defects.append({
                "code": "ZERO_WIDTH_UNICODE",
                "severity": "BLOCK",
                "line": idx,
                "message": "Hidden zero-width Unicode characters detected.",
                "fix": "Remove all hidden Unicode characters."
            })

    # 2. Banned dash scan (Em dash and En dash)
    for idx, line in enumerate(lines, 1):
        if EM_DASH in line or EN_DASH in line:
            defects.append({
                "code": "BANNED_DASH",
                "severity": "BLOCK",
                "line": idx,
                "message": "Banned punctuation detected (Em dash U+2014 or En dash U+2013).",
                "excerpt": line[:80],
                "fix": "Replace em dashes and en dashes with commas, hyphens (-), or periods."
            })

    # 3. Secret token scan
    for idx, line in enumerate(lines, 1):
        for sec_re in SECRET_REGEXES:
            if sec_re.search(line):
                defects.append({
                    "code": "SECRET_TOKEN",
                    "severity": "BLOCK",
                    "line": idx,
                    "message": "Potential exposed secret token detected.",
                    "fix": "Purge or redact secret credentials."
                })

    # 4. Hyperlink and URL integrity checks
    markdown_link_re = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    for idx, line in enumerate(lines, 1):
        for match in markdown_link_re.finditer(line):
            link_text = match.group(1).strip()
            url = match.group(2).strip()

            parsed = urlparse(url)
            if parsed.scheme in ["http", "https"]:
                # Check tracking parameters
                qs = parse_qs(parsed.query)
                found_tracking = [k for k in qs.keys() if k.lower() in TRACKING_PARAMS]
                if found_tracking:
                    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                    defects.append({
                        "code": "TRACKING_LINK",
                        "severity": "BLOCK",
                        "line": idx,
                        "message": f"URL contains tracking parameters: {', '.join(found_tracking)}",
                        "excerpt": url,
                        "fix": f"Strip tracking parameters. Use clean URL: {clean_url}"
                    })

                # Check dual display rule: clean URL must be visible in rendered text
                # It is visible if link text equals the URL, or if the URL appears visibly outside the markdown target
                line_outside_target = line[:match.start()] + link_text + line[match.end():]
                url_is_visible = (url in line_outside_target) or (link_text == url) or (parsed.netloc in link_text)
                if not url_is_visible:
                    defects.append({
                        "code": "HIDDEN_URL",
                        "severity": "BLOCK",
                        "line": idx,
                        "message": "Link target URL is hidden behind anchor text without visible URL.",
                        "excerpt": f"[{link_text}]({url})",
                        "fix": f"Display both text and URL visibly: [{link_text}]({url}) ({url})"
                    })

                # Check domain authority if citation relates to official rules
                domain = parsed.netloc.lower()
                if "gov.in" not in domain and "nic.in" not in domain and domain not in OFFICIAL_DOMAINS:
                    if any(term in line.lower() for term in ["circular", "act", "section", "ombudsman", "rule", "order"]):
                        defects.append({
                            "code": "UNOFFICIAL_DOMAIN",
                            "severity": "REVIEW",
                            "line": idx,
                            "message": f"Citation points to secondary/unofficial domain '{domain}'.",
                            "excerpt": url,
                            "fix": "Replace with official portal endpoint (.gov.in, .rbi.org.in, .sci.gov.in)."
                        })

    # 5. List enumeration count validation
    header_pattern = re.compile(
        r"\b(?:the\s+)?(?:following\s+)?(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+"
        r"(grounds|reasons|documents|communications|notices|points|violations|issues|facts|events|claims|annexures)"
        r"\s*(?::|\.)",
        re.IGNORECASE
    )

    for idx, line in enumerate(lines):
        m = header_pattern.search(line)
        if m:
            num_str = m.group(1).lower()
            stated_count = int(num_str) if num_str.isdigit() else NUMBER_WORDS.get(num_str, 0)
            subject = m.group(2)

            # Count following consecutive list items
            item_count = 0
            j = idx + 1
            while j < len(lines):
                cur = lines[j].strip()
                if not cur:
                    j += 1
                    continue
                # Match numbered list (1., 2., (i), (1)) or bullet list (- , * )
                if re.match(r"^(?:\d+[\.\)]|\([a-z0-9]+\)|[-*])\s+", cur):
                    item_count += 1
                    j += 1
                else:
                    # Break when list ends
                    break

            if item_count > 0 and stated_count != item_count:
                defects.append({
                    "code": "COUNT_MISMATCH",
                    "severity": "BLOCK",
                    "line": idx + 1,
                    "message": f"Stated count '{stated_count}' does not match actual listed items '{item_count}' for {subject}.",
                    "excerpt": line.strip(),
                    "fix": f"Synchronize stated count: change '{num_str}' to '{item_count}' or adjust listed items."
                })

    # 6. Vague Legal Attributions
    vague_patterns = [
        re.compile(r"\bas\s+per\s+law\b", re.IGNORECASE),
        re.compile(r"\bas\s+per\s+prevailing\s+laws\b", re.IGNORECASE),
        re.compile(r"\bunder\s+relevant\s+provisions\b", re.IGNORECASE),
        re.compile(r"\bas\s+per\s+rbi\s+guidelines\b", re.IGNORECASE),
        re.compile(r"\bas\s+per\s+rbi\s+rules\b", re.IGNORECASE),
        re.compile(r"\bas\s+per\s+irdai\s+regulations\b", re.IGNORECASE)
    ]

    for idx, line in enumerate(lines, 1):
        for vp in vague_patterns:
            if vp.search(line):
                # Check if specific instrument or circular number is also mentioned on the same line
                if not any(marker in line for marker in ["No.", "Act", "Circular", "Section", "Clause", "Regulation"]):
                    defects.append({
                        "code": "VAGUE_CITATION",
                        "severity": "BLOCK",
                        "line": idx,
                        "message": "Vague legal attribution without instrument title or section.",
                        "excerpt": line.strip()[:80],
                        "fix": "Name the specific Act/Circular, official number, date, and exact clause."
                    })

    # 7. Discretion vs Right & Ceiling vs Entitlement Traps
    ceiling_trap_re = re.compile(r"\b(?:entitled\s+to|debt\s+of|due\s+as\s+a\s+right)\s+(?:Rs\.?|INR)?\s*30[,0-9\s]*(?:lakh)?\b", re.IGNORECASE)
    discretion_trap_re = re.compile(r"\b(?:bound\s+to\s+award|must\s+award\s+interim\s+compensation\s+under\s+section\s+143a)\b", re.IGNORECASE)

    for idx, line in enumerate(lines, 1):
        if ceiling_trap_re.search(line) and "ombudsman" in text.lower():
            defects.append({
                "code": "CEILING_AS_ENTITLEMENT",
                "severity": "BLOCK",
                "line": idx,
                "message": "Award ceiling presented as automatic statutory entitlement.",
                "excerpt": line.strip()[:80],
                "fix": "Clarify that Rs 30 lakh is an Ombudsman discretionary award ceiling, not an automatic debt."
            })
        if discretion_trap_re.search(line):
            defects.append({
                "code": "DISCRETION_AS_RIGHT",
                "severity": "BLOCK",
                "line": idx,
                "message": "Discretionary statutory power presented as mandatory court obligation.",
                "excerpt": line.strip()[:80],
                "fix": "Reframe as discretionary relief under Section 143A NI Act."
            })

    # 8. Footer PII Check
    # Analyze the last 20% of lines as footer/closing section
    footer_start_idx = max(0, int(len(lines) * 0.8))
    for idx in range(footer_start_idx, len(lines)):
        line = lines[idx]
        # Ignore lines explicitly marked as redacted or masked (e.g. XXXX, ****)
        if "xxxx" in line.lower() or "****" in line:
            continue
        if PAN_REGEX.search(line):
            defects.append({
                "code": "FOOTER_PII",
                "severity": "BLOCK",
                "line": idx + 1,
                "message": "Unmasked Permanent Account Number (PAN) detected in footer.",
                "fix": "Redact PAN in footers and analysis copies (e.g. ABCDE****F)."
            })
        if AADHAAR_REGEX.search(line):
            defects.append({
                "code": "FOOTER_PII",
                "severity": "BLOCK",
                "line": idx + 1,
                "message": "Unmasked Aadhaar number detected in footer.",
                "fix": "Mask Aadhaar to last 4 digits (e.g. XXXX-XXXX-1234)."
            })

    # Determine overall status
    has_block = any(d["severity"] == "BLOCK" for d in defects)
    has_review = any(d["severity"] == "REVIEW" for d in defects)

    if has_block:
        verdict = "BLOCK"
    elif has_review:
        verdict = "REVIEW"
    else:
        verdict = "PASS"

    return verdict, defects

def main():
    parser = argparse.ArgumentParser(description="Audit Indian legal draft against mechanical verification gate.")
    parser.add_argument("file", nargs="?", help="Path to text or markdown draft file")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--strict", action="store_true", help="Treat REVIEW warnings as BLOCK")
    args = parser.parse_args()

    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File '{args.file}' not found.", file=sys.stderr)
            sys.exit(1)
        text = file_path.read_text(encoding="utf-8", errors="replace")
    else:
        text = sys.stdin.read()

    verdict, defects = audit_draft_text(text, strict=args.strict)

    if args.strict and verdict == "REVIEW":
        verdict = "BLOCK"

    if args.json:
        output = {
            "verdict": verdict,
            "total_defects": len(defects),
            "defects": defects
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"\n=======================================================")
        print(f" Indian Legal Verification Gate Audit Report")
        print(f"=======================================================")
        print(f" VERDICT: {verdict}")
        print(f" TOTAL DEFECTS DETECTED: {len(defects)}")
        print(f"-------------------------------------------------------")
        if not defects:
            print(" [PASS] Draft passed 100% of mechanical verification checks.")
            print(" - Zero banned em/en dashes")
            print(" - Zero tracking parameters")
            print(" - Zero hidden URLs")
            print(" - Zero enumeration count mismatches")
            print(" - Zero unverified vague citations")
            print(" - Zero sensitive footer PII")
        else:
            for idx, d in enumerate(defects, 1):
                sev = d['severity']
                code = d['code']
                line = d.get('line', '-')
                msg = d['message']
                fix = d.get('fix', '')
                print(f" [{idx}] [{sev}] Line {line} - {code}: {msg}")
                if "excerpt" in d:
                    print(f"     Excerpt: {d['excerpt']}")
                if fix:
                    print(f"     Required Fix: {fix}")
        print(f"=======================================================\n")

    if verdict == "BLOCK":
        sys.exit(1)
    elif verdict == "REVIEW":
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
