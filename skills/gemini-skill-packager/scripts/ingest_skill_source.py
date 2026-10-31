#!/usr/bin/env python3
"""
Ingest Skill Source for Gemini Skill Packager
Normalizes, extracts, and inventories any skill source (directory, .zip, .tar.gz, monorepo)
while purging OS/VCS clutter and resolving skill root boundaries.
"""

import argparse
import json
import os
import re
import shutil
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path

CLUTTER_PATTERNS = {
    ".git", ".github", ".gitignore", ".gitattributes",
    ".DS_Store", "__MACOSX", "Thumbs.db", "desktop.ini",
    ".vscode", ".idea", ".pytest_cache", "__pycache__",
    "node_modules", ".coverage", ".mypy_cache"
}

def is_clutter(path: Path) -> bool:
    for part in path.parts:
        if part in CLUTTER_PATTERNS or part.endswith(".pyc") or part.endswith(".pyo"):
            return True
    return False

def extract_archive_if_needed(source_path: Path, extract_dir: Path) -> Path:
    if source_path.is_file():
        suffix = source_path.suffix.lower()
        if suffix == ".zip":
            with zipfile.ZipFile(source_path, 'r') as zf:
                zf.extractall(extract_dir)
            return extract_dir
        elif suffix in [".tar", ".gz", ".tgz", ".bz2", ".xz"]:
            with tarfile.open(source_path, 'r:*') as tf:
                tf.extractall(extract_dir)
            return extract_dir
        else:
            raise ValueError(f"Unsupported archive format: {source_path}")
    return source_path

def find_candidate_skills(root_dir: Path) -> list[dict]:
    candidates = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dp = Path(dirpath)
        if is_clutter(dp):
            dirnames[:] = []
            continue
        
        for f in filenames:
            if f.lower() == "skill.md":
                skill_md_path = dp / f
                name_match = None
                try:
                    content = skill_md_path.read_text(encoding="utf-8", errors="replace")
                    fm_match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
                    if fm_match:
                        for line in fm_match.group(1).splitlines():
                            if line.strip().startswith("name:"):
                                name_match = line.split(":", 1)[1].strip().strip('"\'')
                                break
                except Exception:
                    pass
                
                candidates.append({
                    "skill_dir": dp,
                    "skill_md_path": skill_md_path,
                    "folder_name": dp.name,
                    "frontmatter_name": name_match,
                    "depth": len(dp.relative_to(root_dir).parts)
                })
    return candidates

def ingest(source: str, output_dir: str, target_skill_name: str | None = None) -> dict:
    src_path = Path(source).resolve()
    if not src_path.exists():
        raise FileNotFoundError(f"Source not found: {source}")

    temp_extract = Path(tempfile.mkdtemp(prefix="gemini_ingest_"))
    try:
        working_root = extract_archive_if_needed(src_path, temp_extract)
        candidates = find_candidate_skills(working_root)

        if not candidates:
            raise ValueError(f"No SKILL.md found in source: {source}")

        selected = None
        if target_skill_name:
            for c in candidates:
                if c["frontmatter_name"] == target_skill_name or c["folder_name"] == target_skill_name:
                    selected = c
                    break
            if not selected:
                available = [c["frontmatter_name"] or c["folder_name"] for c in candidates]
                raise ValueError(f"Requested skill '{target_skill_name}' not found. Available: {available}")
        elif len(candidates) == 1:
            selected = candidates[0]
        else:
            candidates.sort(key=lambda c: c["depth"])
            selected = candidates[0]

        target_skill_dir = selected["skill_dir"]
        out_path = Path(output_dir).resolve()
        if out_path.exists():
            shutil.rmtree(out_path)
        out_path.mkdir(parents=True, exist_ok=True)

        copied_files = []
        purged_files = []

        for dirpath, dirnames, filenames in os.walk(target_skill_dir):
            dp = Path(dirpath)
            rel_dir = dp.relative_to(target_skill_dir)

            if is_clutter(rel_dir):
                for f in filenames:
                    purged_files.append(str(rel_dir / f))
                dirnames[:] = []
                continue

            dest_dir = out_path / rel_dir
            dest_dir.mkdir(parents=True, exist_ok=True)

            for f in filenames:
                file_rel = rel_dir / f
                if is_clutter(file_rel):
                    purged_files.append(str(file_rel))
                    continue

                src_file = dp / f
                dest_file = dest_dir / f
                shutil.copy2(src_file, dest_file)
                copied_files.append({
                    "relative_path": str(file_rel).replace("\\", "/"),
                    "size_bytes": dest_file.stat().st_size,
                    "extension": dest_file.suffix.lower()
                })

        manifest = {
            "source": str(src_path),
            "selected_skill_folder": selected["folder_name"],
            "frontmatter_name": selected["frontmatter_name"],
            "staging_path": str(out_path),
            "file_count": len(copied_files),
            "purged_count": len(purged_files),
            "files": copied_files,
            "purged": purged_files
        }

        manifest_file = out_path / "ingestion_manifest.json"
        manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return manifest

    finally:
        shutil.rmtree(temp_extract, ignore_errors=True)

def main():
    parser = argparse.ArgumentParser(description="Ingest and normalize skill sources for Gemini packaging.")
    parser.add_argument("source", help="Path to skill directory or archive (.zip, .tar.gz)")
    parser.add_argument("--output-dir", "-o", required=True, help="Target staging directory")
    parser.add_argument("--skill-name", "-n", default=None, help="Specific skill name if source is a multi-skill repo")
    parser.add_argument("--json", action="store_true", help="Print manifest as JSON")

    args = parser.parse_args()
    try:
        manifest = ingest(args.source, args.output_dir, args.skill_name)
        if args.json:
            print(json.dumps(manifest, indent=2))
        else:
            print(f"Ingested '{manifest['selected_skill_folder']}' successfully.")
            print(f"Files staged: {manifest['file_count']} (Purged {manifest['purged_count']} clutter files)")
            print(f"Staged at: {manifest['staging_path']}")
    except Exception as e:
        print(f"Ingestion error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
