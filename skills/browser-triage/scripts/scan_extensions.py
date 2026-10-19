#!/usr/bin/env python3
"""
scan_extensions.py - Automated Static Analysis Scanner for Browser Extensions
Detects capture-phase event hijacking, propagation arrest, and event handler nulling.
"""

import os
import sys
import json
import re
import argparse

SUSPICIOUS_PATTERNS = {
    'capture_listener': re.compile(
        r"addEventListener\s*\(\s*['\"](?:click|mousedown|mouseup|pointerdown|pointerup)['\"].*?,\s*(?:true|\{\s*capture\s*:\s*true)",
        re.IGNORECASE
    ),
    'stop_immediate_prop': re.compile(r"\.stopImmediatePropagation\s*\(", re.IGNORECASE),
    'stop_propagation': re.compile(r"\.stopPropagation\s*\(", re.IGNORECASE),
    'prevent_default': re.compile(r"\.preventDefault\s*\(", re.IGNORECASE),
    'handler_nulling': re.compile(
        r"(?:document|body|window)\s*\.\s*(?:onmousedown|onmouseup|onclick|oncontextmenu|onselectstart)\s*=\s*null",
        re.IGNORECASE
    )
}

def locate_extension_dirs(browser_name, profile="Default"):
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    paths = {
        "brave": os.path.join(local_app_data, "BraveSoftware", "Brave-Browser", "User Data", profile, "Extensions"),
        "chrome": os.path.join(local_app_data, "Google", "Chrome", "User Data", profile, "Extensions"),
        "edge": os.path.join(local_app_data, "Microsoft", "Edge", "User Data", profile, "Extensions"),
        "chromium": os.path.join(local_app_data, "Chromium", "User Data", profile, "Extensions"),
    }
    return paths.get(browser_name.lower())

def scan_extension(ext_dir, ext_id):
    versions = [v for v in os.listdir(ext_dir) if os.path.isdir(os.path.join(ext_dir, v))]
    if not versions:
        return None
    latest_ver = versions[-1]
    ver_path = os.path.join(ext_dir, latest_ver)
    manifest_path = os.path.join(ver_path, "manifest.json")

    name = ext_id
    matches_all_urls = False
    all_frames = False
    content_scripts = []

    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8", errors="ignore") as mf:
                mdata = json.load(mf)
                name = mdata.get("name", ext_id)
                if name.startswith("__MSG_"):
                    loc_file = os.path.join(ver_path, "_locales", "en", "messages.json")
                    if os.path.exists(loc_file):
                        with open(loc_file, "r", encoding="utf-8", errors="ignore") as lf:
                            ldata = json.load(lf)
                            key = name[6:-2]
                            name = ldata.get(key, {}).get("message", name)

                for cs in mdata.get("content_scripts", []):
                    matches = cs.get("matches", [])
                    if any("<all_urls>" in m or "*://*/*" in m or "https://*/*" in m for m in matches):
                        matches_all_urls = True
                    if cs.get("all_frames", False):
                        all_frames = True
                    content_scripts.extend(cs.get("js", []))
        except Exception:
            pass

    findings = {k: [] for k in SUSPICIOUS_PATTERNS}
    total_findings_count = 0

    for root, _, files in os.walk(ver_path):
        for f in files:
            if f.endswith(".js"):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, ver_path)
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as jf:
                        content = jf.read()
                        for pkey, pattern in SUSPICIOUS_PATTERNS.items():
                            hits = pattern.findall(content)
                            if hits:
                                findings[pkey].append({"file": rel_path, "hits": len(hits)})
                                total_findings_count += len(hits)
                except Exception:
                    pass

    # Risk scoring algorithm
    risk_score = 0
    if findings['capture_listener']:
        risk_score += 40
    if findings['handler_nulling']:
        risk_score += 35
    if findings['stop_immediate_prop']:
        risk_score += 25
    if matches_all_urls:
        risk_score = int(risk_score * 1.5)
    if all_frames:
        risk_score += 15

    risk_score = min(risk_score, 100)

    return {
        "id": ext_id,
        "name": name,
        "version": latest_ver,
        "matches_all_urls": matches_all_urls,
        "all_frames": all_frames,
        "risk_score": risk_score,
        "findings": findings,
        "total_hits": total_findings_count
    }

def main():
    parser = argparse.ArgumentParser(description="Scan browser extensions for event hijacking.")
    parser.add_argument("--browser", default="brave", choices=["brave", "chrome", "edge", "chromium"], help="Target browser")
    parser.add_argument("--path", help="Direct path to Extensions directory")
    parser.add_argument("--profile", default="Default", help="Profile directory name")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()

    detected_browser = args.browser
    ext_dir = args.path
    if not ext_dir:
        if args.profile and os.path.isabs(args.profile) and os.path.isdir(args.profile):
            p_lower = args.profile.lower()
            if "edge" in p_lower:
                detected_browser = "edge"
            elif "chrome" in p_lower:
                detected_browser = "chrome"
            elif "brave" in p_lower:
                detected_browser = "brave"

            if os.path.basename(args.profile).lower() == "extensions":
                ext_dir = args.profile
            else:
                ext_dir = os.path.join(args.profile, "Extensions")
        else:
            ext_dir = locate_extension_dirs(args.browser, args.profile)

    if not ext_dir or not os.path.isdir(ext_dir):
        print(f"Error: Extensions directory not found: {ext_dir}", file=sys.stderr)
        sys.exit(1)

    results = []
    for eid in os.listdir(ext_dir):
        epath = os.path.join(ext_dir, eid)
        if os.path.isdir(epath):
            res = scan_extension(epath, eid)
            if res:
                results.append(res)

    results.sort(key=lambda x: x["risk_score"], reverse=True)

    if args.json:
        print(json.dumps(results, indent=2))
        return

    print(f"=== BROWSER EXTENSION FORENSIC AUDIT ({detected_browser.upper()} - {len(results)} EXTENSIONS) ===\n")
    for r in results:
        status_tag = "[CRITICAL HIJACK RISK]" if r["risk_score"] >= 70 else ("[SUSPICIOUS]" if r["risk_score"] >= 40 else "[CLEAN]")
        if r["risk_score"] > 0:
            print(f"{status_tag} {r['name']} ({r['id']}) - Score: {r['risk_score']}/100")
            print(f"  All URLs: {r['matches_all_urls']} | All Frames: {r['all_frames']}")
            for pkey, items in r["findings"].items():
                if items:
                    files_str = ", ".join(f"{i['file']} ({i['hits']})" for i in items[:3])
                    print(f"  -> {pkey}: {files_str}")
            print()

if __name__ == "__main__":
    main()
