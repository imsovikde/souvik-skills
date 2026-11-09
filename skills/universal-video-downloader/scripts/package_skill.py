#!/usr/bin/env python3
"""
Skill Validator and Zero-Rejection Package Builder
Validates SKILL.md frontmatter, checks script compilability, executes smoke tests,
and builds portable .skill and .zip archives for Gemini and Antigravity.
"""

import sys
import os
import re
import zipfile
import py_compile
import subprocess
import argparse

# Configure console encoding
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

SKILL_NAME = "universal-video-downloader"
REQUIRED_SCRIPTS = [
    "verify_compliance.py",
    "probe_stream.py",
    "download_video.py",
    "package_skill.py"
]
REQUIRED_REFERENCES = [
    "evidence-and-probing.md",
    "quality-and-formats.md",
    "compliance-gate.md"
]


def validate_skill_md(skill_md_path: str) -> dict:
    """Validate SKILL.md frontmatter and structural rules."""
    if not os.path.exists(skill_md_path):
        raise FileNotFoundError(f"SKILL.md missing at {skill_md_path}")

    with open(skill_md_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    line_count = len(lines)
    if line_count > 500:
        raise ValueError(f"SKILL.md exceeds 500-line budget: {line_count} lines found.")

    if not content.startswith("---"):
        raise ValueError("SKILL.md must start with YAML frontmatter delimiters ('---') at byte 0.")

    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError("SKILL.md has unterminated YAML frontmatter.")

    fm_raw = parts[1].strip()
    name_match = re.search(r"^name:\s*([^\r\n]+)", fm_raw, re.MULTILINE)
    if not name_match:
        raise ValueError("SKILL.md frontmatter missing 'name:' field.")
    parsed_name = name_match.group(1).strip().strip('"').strip("'")
    if parsed_name != SKILL_NAME:
        raise ValueError(f"Frontmatter name '{parsed_name}' does not match expected '{SKILL_NAME}'.")

    desc_match = re.search(r"^description:\s*(.+?)(?=\n[a-zA-Z0-9_-]+:|$)", fm_raw, re.MULTILINE | re.DOTALL)
    if not desc_match:
        raise ValueError("SKILL.md frontmatter missing 'description:' field.")
    desc_val = desc_match.group(1).strip().strip('"').strip("'")
    if len(desc_val) > 1024:
        raise ValueError(f"Frontmatter description exceeds 1024 characters ({len(desc_val)} chars).")

    return {
        "name": parsed_name,
        "description_length": len(desc_val),
        "total_lines": line_count
    }


def validate_scripts(scripts_dir: str):
    """Compile and smoke-test all Python scripts."""
    print("Checking Python script integrity...")
    for sname in REQUIRED_SCRIPTS:
        spath = os.path.join(scripts_dir, sname)
        if not os.path.exists(spath):
            raise FileNotFoundError(f"Required script missing: {spath}")

        # 1. Bytecode compilation check
        try:
            py_compile.compile(spath, doraise=True)
            print(f"  [PASS] py_compile: {sname}")
        except py_compile.PyCompileError as e:
            raise RuntimeError(f"Script compilation failed for {sname}: {e}")

        # 2. Smoke test with --help (skip self to prevent recursive invocation)
        if sname != "package_skill.py":
            try:
                res = subprocess.run([sys.executable, spath, "--help"], capture_output=True, text=True, check=True)
                if "--help" in res.stdout or "usage:" in res.stdout.lower():
                    print(f"  [PASS] smoke test (--help): {sname}")
                else:
                    print(f"  [WARN] smoke test output non-standard for {sname}")
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Script --help smoke test failed for {sname}: {e}")


def validate_references(ref_dir: str):
    """Verify that all required reference markdown files exist and are populated."""
    print("Checking reference documents...")
    for rname in REQUIRED_REFERENCES:
        rpath = os.path.join(ref_dir, rname)
        if not os.path.exists(rpath):
            raise FileNotFoundError(f"Required reference document missing: {rpath}")
        size = os.path.getsize(rpath)
        if size < 50:
            raise ValueError(f"Reference document {rname} appears empty or truncated ({size} bytes).")
        print(f"  [PASS] reference verified: {rname} ({size} bytes)")


def create_package_archives(skill_root: str, out_dir: str = None) -> list:
    """Bundle skill package into portable .skill and .zip archives."""
    out_dir = out_dir or skill_root
    os.makedirs(out_dir, exist_ok=True)

    zip_filename = os.path.join(out_dir, f"{SKILL_NAME}.zip")
    skill_filename = os.path.join(out_dir, f"{SKILL_NAME}.skill")

    # Exclude development clutter
    ignore_patterns = re.compile(r"(__pycache__|\.pyc$|\.DS_Store|thumbs\.db|\.git)", re.IGNORECASE)

    archives = [zip_filename, skill_filename]
    for arch_path in archives:
        with zipfile.ZipFile(arch_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(skill_root):
                # Prune ignored directories
                dirs[:] = [d for d in dirs if not ignore_patterns.search(d)]
                for file in files:
                    if ignore_patterns.search(file):
                        continue
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, skill_root)
                    zf.write(full_path, arcname=rel_path)

    return archives


def main():
    parser = argparse.ArgumentParser(
        description="Validate and package universal-video-downloader into portable .skill and .zip archives"
    )
    parser.add_argument("--output-dir", default=None, help="Custom output directory for packages")
    parser.add_argument("--skip-tests", action="store_true", help="Skip script compile and smoke tests")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_root = os.path.abspath(os.path.join(script_dir, ".."))

    print("=" * 65)
    print("  Skill Package Validator & Archiver")
    print(f"  Target: {skill_root}")
    print("=" * 65)

    # 1. Validate SKILL.md
    skill_md = os.path.join(skill_root, "SKILL.md")
    fm_info = validate_skill_md(skill_md)
    print(f"[PASS] SKILL.md Validated: name={fm_info['name']} lines={fm_info['total_lines']} desc_len={fm_info['description_length']}")

    # 2. Validate Scripts
    if not args.skip_tests:
        scripts_dir = os.path.join(skill_root, "scripts")
        validate_scripts(scripts_dir)

    # 3. Validate References
    ref_dir = os.path.join(skill_root, "references")
    validate_references(ref_dir)

    # 4. Generate Packages
    archives = create_package_archives(skill_root, out_dir=args.output_dir)
    print("\n[SUCCESS] Skill Packages Generated:")
    for arch in archives:
        sz_kb = round(os.path.getsize(arch) / 1024, 2)
        print(f"  - {os.path.basename(arch)}: {sz_kb} KB ({arch})")

    print("=" * 65)
    print("Package verification passed with 100% fidelity.")


if __name__ == "__main__":
    main()
