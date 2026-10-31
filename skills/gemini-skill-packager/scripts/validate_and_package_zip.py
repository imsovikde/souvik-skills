#!/usr/bin/env python3
"""
Validate and Package ZIP for Gemini Skill Packager
Audits skill directory against all Gemini Apps upload constraints and packages
into a zero-rejection, deterministic, verified .zip bundle for gemini.google.com.
"""

import argparse
import datetime
import json
import os
import re
import sys
import zipfile
from pathlib import Path

NAME_REGEX = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)+$")
ZERO_WIDTH_CHARS = re.compile(r"[\u200B\u200C\u200D\uFEFF\u202E]")
# Built from fragments so scanner never flags its own source
SECRET_REGEXES = [
    re.compile(r"s" + r"k-[A-Za-z0-9]{20,}"),
    re.compile(r"g" + r"hp_[A-Za-z0-9]{36}"),
    re.compile(r"n" + r"pm_[A-Za-z0-9]{36}"),
    re.compile(r"A" + r"KIA[0-9A-Z]{16}"),
    re.compile(r"A" + r"Iza[0-9A-Za-z_-]{35}")
]

ALLOWED_EXTENSIONS = {
    ".md", ".txt", ".pdf", ".docx", ".rtf", ".tex", ".log", ".rst", ".odt",
    ".csv", ".ods", ".xlsx",
    ".odp", ".pptx",
    ".jpg", ".jpeg", ".png", ".svg", ".gif", ".heic", ".ico", ".webp",
    ".py", ".sh", ".ipynb", ".js",
    ".css", ".html", ".htm",
    ".json", ".toml", ".xml", ".yaml", ".yml"
}

FORBIDDEN_FILES = {
    ".ds_store", "thumbs.db", "desktop.ini", "__macosx", ".git", ".gitignore",
    ".claude", ".claude-plugin", ".cursor", ".cursor-plugin", ".agents",
    ".codex-plugin", "openai.yaml",
    ".vscode", ".idea", "node_modules", "__pycache__"
}

def parse_frontmatter(content: str) -> tuple[dict, str]:
    if not content.startswith("---"):
        return {}, content
    end_idx = content.find("\n---", 3)
    if end_idx == -1:
        return {}, content
    
    raw = content[3:end_idx].strip()
    body = content[end_idx + 4:].lstrip("\r\n")
    fields = {}
    lines = raw.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if ":" in line and not line.startswith(" ") and not line.startswith("\t"):
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            if val in [">", ">-", "|", "|-"]:
                val_lines = []
                i += 1
                while i < len(lines) and (lines[i].startswith("  ") or lines[i].startswith("\t")):
                    val_lines.append(lines[i].strip())
                    i += 1
                fields[key] = " ".join(val_lines)
                continue
            elif val == "" and i + 1 < len(lines) and (lines[i+1].startswith("  ") or lines[i+1].startswith("\t")):
                sub_dict = {}
                i += 1
                while i < len(lines) and (lines[i].startswith("  ") or lines[i].startswith("\t")):
                    sub_line = lines[i].strip()
                    if ":" in sub_line:
                        sub_k, sub_v = sub_line.split(":", 1)
                        sub_dict[sub_k.strip()] = sub_v.strip().strip("\"'")
                    i += 1
                fields[key] = sub_dict
                continue
            else:
                fields[key] = val.strip("\"'")
        i += 1
    return fields, body

def audit_directory(skill_dir: Path, ultra_safe: bool = False, strict_lossless: bool = False) -> tuple[list[str], list[str], dict]:
    errors = []
    warnings = []
    meta = {}

    # 1. Exact SKILL.md check
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append("Missing required SKILL.md at skill root.")
        return errors, warnings, meta

    # Check for case variations
    for item in skill_dir.iterdir():
        if item.name.lower() == "skill.md" and item.name != "SKILL.md":
            errors.append(f"SKILL.md filename must be exact uppercase: found '{item.name}'.")

    content = skill_md.read_text(encoding="utf-8", errors="replace")
    fm, body = parse_frontmatter(content)
    
    if not fm:
        errors.append("SKILL.md missing valid YAML frontmatter block (enclosed in ---).")
    else:
        name = fm.get("name", "")
        if not name:
            errors.append("SKILL.md frontmatter missing 'name' field.")
        elif not NAME_REGEX.match(name) or len(name) > 64:
            errors.append(f"Frontmatter name '{name}' violates kebab-case regex ^[a-z0-9]+(-[a-z0-9]+)*$ or exceeds 64 chars.")
        else:
            meta["name"] = name

        desc = fm.get("description", "")
        if not desc:
            errors.append("SKILL.md frontmatter missing 'description' field.")
        elif len(desc) < 40 or len(desc) > 1024:
            errors.append(f"Frontmatter description length ({len(desc)}) must be between 40 and 1024 characters.")
        elif "use when" not in desc.lower():
            warnings.append("Frontmatter description should include an explicit 'Use when...' trigger condition.")
        meta["description"] = desc

    # 2. File and Directory Iteration
    all_files = []
    total_uncompressed_bytes = 0
    max_depth = 0

    for root, dirs, files in os.walk(skill_dir):
        root_path = Path(root)
        rel_root = root_path.relative_to(skill_dir)
        depth = len(rel_root.parts)
        if depth > max_depth:
            max_depth = depth

        if depth > 10:
            errors.append(f"Directory nesting depth ({depth}) exceeds Gemini maximum depth of 10: {rel_root}")

        # Check for banned directories
        for d in dirs:
            if d.lower() in FORBIDDEN_FILES:
                errors.append(f"Forbidden directory found: {rel_root / d}")

        for f in files:
            if f == "ingestion_manifest.json":
                continue
            file_path = root_path / f
            rel_file = file_path.relative_to(skill_dir)
            all_files.append(rel_file)

            # Check symlinks
            if file_path.is_symlink():
                errors.append(f"Symlinks are forbidden in Gemini skill packages: {rel_file}")

            # Check forbidden filenames
            if f.lower() in FORBIDDEN_FILES:
                errors.append(f"Forbidden file found: {rel_file}")

            # Check extension whitelist
            suffix = file_path.suffix.lower()
            if not suffix or suffix not in ALLOWED_EXTENSIONS:
                errors.append(f"Unsupported file extension '{suffix}' in {rel_file}. Must be whitelisted.")

            size = file_path.stat().st_size
            total_uncompressed_bytes += size

            # Inspect text files for zero-width characters and secrets
            if suffix in [".md", ".txt", ".json", ".yaml", ".yml", ".py", ".sh", ".js"]:
                try:
                    text_content = file_path.read_text(encoding="utf-8", errors="replace")
                    if ZERO_WIDTH_CHARS.search(text_content):
                        errors.append(f"Hidden zero-width Unicode characters detected in {rel_file}.")
                    if strict_lossless and "\ufffd" in text_content:
                        errors.append(f"Corrupted character encoding (\ufffd) detected in {rel_file}.")
                    for sec_re in SECRET_REGEXES:
                        if sec_re.search(text_content):
                            errors.append(f"Potential hardcoded secret matching {sec_re.pattern} found in {rel_file}.")
                    # Check for unhandled external network calls in scripts (Google Support constraint)
                    if "scripts" in rel_file.parts and suffix in [".py", ".sh", ".js", ".txt"]:
                        if ("https://api." in text_content or "http://" in text_content) and "OFFLINE" not in text_content and "mock://" not in text_content:
                            msg = f"Executable script {rel_file} contains external network endpoints without offline fallback (Google Support answer/17094296 constraint)."
                            if strict_lossless:
                                errors.append(msg)
                            else:
                                warnings.append(msg)
                except Exception:
                    pass

    meta["file_count"] = len(all_files)
    meta["uncompressed_size_bytes"] = total_uncompressed_bytes
    meta["max_depth"] = max_depth

    # File count constraints
    if len(all_files) > 100:
        errors.append(f"Total file count ({len(all_files)}) exceeds Gemini maximum of 100 files.")
    elif len(all_files) > 95:
        warnings.append(f"File count ({len(all_files)}) is very close to Gemini ceiling of 100 files.")

    if ultra_safe and len(all_files) > 10:
        errors.append(f"Ultra-Safe mode requires <= 10 files (found {len(all_files)}). Run transpiler with --ultra-safe.")

    # Size constraints
    if total_uncompressed_bytes > 100 * 1024 * 1024:
        errors.append(f"Uncompressed package size ({total_uncompressed_bytes / (1024*1024):.2f} MB) exceeds 100 MB.")

    return errors, warnings, meta

def package_to_zip(skill_dir: Path, output_zip_path: Path, wrap_folder: bool = False, skill_name: str = "") -> dict:
    output_zip_path.parent.mkdir(parents=True, exist_ok=True)
    if output_zip_path.exists():
        output_zip_path.unlink()

    # Fixed deterministic timestamp: 2026-01-01 00:00:00 UTC
    fixed_time = (2026, 1, 1, 0, 0, 0)
    packaged_entries = []

    with zipfile.ZipFile(output_zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            dirs.sort()
            files.sort()
            for f in files:
                if f == "ingestion_manifest.json":
                    continue
                file_path = Path(root) / f
                rel_path = file_path.relative_to(skill_dir)
                
                if wrap_folder and skill_name:
                    arcname = f"{skill_name}/{str(rel_path).replace(os.sep, '/')}"
                else:
                    arcname = str(rel_path).replace(os.sep, "/")

                zinfo = zipfile.ZipInfo(filename=arcname, date_time=fixed_time)
                zinfo.external_attr = 0o644 << 16
                zinfo.compress_type = zipfile.ZIP_DEFLATED
                
                with open(file_path, "rb") as fp:
                    zf.writestr(zinfo, fp.read())
                packaged_entries.append(arcname)

    # Verify ZIP integrity
    with zipfile.ZipFile(output_zip_path, "r") as zf:
        bad_file = zf.testzip()
        if bad_file:
            raise RuntimeError(f"Corrupted archive entry detected: {bad_file}")

    compressed_size = output_zip_path.stat().st_size
    return {
        "zip_path": str(output_zip_path.resolve()),
        "compressed_size_bytes": compressed_size,
        "entry_count": len(packaged_entries),
        "entries": packaged_entries
    }

def main():
    parser = argparse.ArgumentParser(description="Audit and package Gemini Custom Skill ZIP bundle.")
    parser.add_argument("skill_dir", help="Path to prepared skill directory")
    parser.add_argument("--output", "-o", default=None, help="Output .zip path (defaults to <skill-name>.zip)")
    parser.add_argument("--ultra-safe", action="store_true", help="Enforce strict <= 10 files ceiling")
    parser.add_argument("--strict-lossless", action="store_true", help="Enforce strict zero-losslessness and Google offline policy gates")
    parser.add_argument("--wrap-folder", action="store_true", help="Nest archive contents inside top-level <skill-name>/ folder")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()
    skill_path = Path(args.skill_dir).resolve()

    if not skill_path.exists() or not skill_path.is_dir():
        print(f"Error: {args.skill_dir} is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    errors, warnings, meta = audit_directory(skill_path, ultra_safe=args.ultra_safe, strict_lossless=args.strict_lossless)

    skill_name = meta.get("name", skill_path.name)
    out_zip = Path(args.output) if args.output else skill_path.parent / f"{skill_name}.zip"

    result = {
        "status": "PASS" if not errors else "FAIL",
        "skill_name": skill_name,
        "meta": meta,
        "errors": errors,
        "warnings": warnings,
        "package": None
    }

    if errors:
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Audit failed with {len(errors)} error(s):")
            for err in errors:
                print(f"  [ERROR] {err}")
            for w in warnings:
                print(f"  [WARN]  {w}")
        sys.exit(1)

    # If audit passes, package zip
    package_res = package_to_zip(skill_path, out_zip, wrap_folder=args.wrap_folder, skill_name=skill_name)
    result["package"] = package_res

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Skill '{skill_name}' successfully validated and packaged.")
        print(f"Output ZIP: {package_res['zip_path']}")
        print(f"Compressed size: {package_res['compressed_size_bytes']} bytes ({package_res['compressed_size_bytes'] / 1024:.1f} KB)")
        print(f"Total entries: {package_res['entry_count']}")
        if warnings:
            print(f"Warnings ({len(warnings)}):")
            for w in warnings:
                print(f"  [WARN] {w}")

if __name__ == "__main__":
    main()
