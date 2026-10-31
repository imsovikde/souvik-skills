#!/usr/bin/env python3
"""
Test Suite for Gemini Skill Packager
Automated regression and compliance tests verifying ingestion, lossless transpilation,
rejection matrix validation, deterministic ZIP packaging, and typography standards.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent

class TestGeminiSkillPackager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="gemini_test_"))
        
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_typography_and_repo_standards(self):
        """Verify zero em-dashes, zero en-dashes, and zero ASCII box drawings."""
        forbidden_chars = [("\u2014", "em-dash"), ("\u2013", "en-dash")]
        # Box drawing characters in unicode range \u2500 - \u257F
        violations = []
        
        for file_path in SKILL_DIR.rglob("*"):
            if file_path.is_file() and file_path.suffix in [".md", ".py", ".yaml", ".json", ".txt"]:
                text = file_path.read_text(encoding="utf-8", errors="replace")
                for char, name in forbidden_chars:
                    if char in text:
                        violations.append(f"{file_path.relative_to(SKILL_DIR)} contains {name}")
                if file_path.name != "test_gemini_skill_packager.py":
                    for c in text:
                        if 0x2500 <= ord(c) <= 0x257F:
                            violations.append(f"{file_path.relative_to(SKILL_DIR)} contains decorative box drawing")
                            break
                        
        self.assertEqual(violations, [], f"Typography violations found: {violations}")

    def test_02_skill_md_structure(self):
        """Verify SKILL.md line count, frontmatter keys, and required sections."""
        skill_md = SKILL_DIR / "SKILL.md"
        self.assertTrue(skill_md.exists(), "SKILL.md must exist")
        
        lines = skill_md.read_text(encoding="utf-8").splitlines()
        self.assertLess(len(lines), 450, f"SKILL.md must be under 450 lines (got {len(lines)})")
        
        # Verify strict frontmatter
        self.assertEqual(lines[0], "---")
        fm_lines = []
        idx = 1
        while idx < len(lines) and lines[idx] != "---":
            fm_lines.append(lines[idx])
            idx += 1
        
        fm_keys = [l.split(":", 1)[0].strip() for l in fm_lines if ":" in l]
        self.assertIn("name", fm_keys)
        self.assertIn("description", fm_keys)
        self.assertEqual(len(fm_keys), 2, "SKILL.md frontmatter must contain only name and description")

    def test_03_ingestion_and_clutter_purging(self):
        """Test ingest_skill_source.py with mock nested multi-agent structure."""
        src_mock = self.temp_dir / "src_repo"
        skill_sub = src_mock / ".claude" / "skills" / "demo-complex-skill"
        skill_sub.mkdir(parents=True)
        (src_mock / ".git").mkdir()
        (src_mock / ".DS_Store").write_text("clutter", encoding="utf-8")
        
        mock_skill_md = (
            "---\n"
            "name: demo-complex-skill\n"
            "description: Multi-agent complex skill. Use when testing ingestion.\n"
            "---\n"
            "# Demo Complex Skill\n"
            "Test body.\n"
        )
        (skill_sub / "SKILL.md").write_text(mock_skill_md, encoding="utf-8")
        (skill_sub / "helper.py").write_text("print('hello')", encoding="utf-8")

        staging = self.temp_dir / "staging"
        ingest_script = SKILL_DIR / "scripts" / "ingest_skill_source.py"
        
        cmd = [sys.executable, str(ingest_script), str(src_mock), "-o", str(staging)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Ingest failed: {proc.stderr}")
        
        self.assertTrue((staging / "SKILL.md").exists())
        self.assertTrue((staging / "helper.py").exists())
        self.assertFalse((staging / ".git").exists())
        self.assertFalse((staging / ".DS_Store").exists())

    def test_04_lossless_transpilation_and_frontmatter_preservation(self):
        """Test lossless_gemini_transpiler.py stripping proprietary keys and migrating them."""
        staging = self.temp_dir / "stage_transpile"
        staging.mkdir(parents=True)
        
        raw_skill = (
            "---\n"
            "name: Raw-Skill_Name\n"
            "description: Performs complex tasks.\n"
            "disable-model-invocation: true\n"
            "user-invocable: true\n"
            "version: 1.4.2\n"
            "tools: [search, bash]\n"
            "---\n"
            "# Raw Skill Title\n\n"
            "Run script [types](references/types.ts) and config [schema](schema.sql).\n"
        )
        (staging / "SKILL.md").write_text(raw_skill, encoding="utf-8")
        
        ref_dir = staging / "references"
        ref_dir.mkdir()
        (ref_dir / "types.ts").write_text("export type TaskId = string;\n", encoding="utf-8")
        (staging / "schema.sql").write_text("CREATE TABLE test (id INT);\n", encoding="utf-8")
        
        transpile_script = SKILL_DIR / "scripts" / "lossless_gemini_transpiler.py"
        cmd = [sys.executable, str(transpile_script), str(staging)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Transpilation failed: {proc.stderr}")
        
        # Verify transformed SKILL.md
        new_md = (staging / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: raw-skill-name", new_md)
        self.assertIn("Preserved Platform Metadata & Trigger Contract", new_md)
        self.assertIn("disable-model-invocation", new_md)
        self.assertIn("1.4.2", new_md)
        
        # Verify renamed extensions
        self.assertTrue((ref_dir / "types.ts.txt").exists())
        self.assertTrue((staging / "schema.sql.txt").exists())
        self.assertIn("types.ts.txt", new_md)
        self.assertIn("schema.sql.txt", new_md)

    def test_05_package_and_zip_validation(self):
        """Test validate_and_package_zip.py produces compliant zip."""
        staging = self.temp_dir / "stage_pkg"
        staging.mkdir(parents=True)
        
        clean_skill = (
            "---\n"
            "name: test-valid-skill\n"
            "description: Processes valid test flows cleanly. Use when testing packaging.\n"
            "---\n"
            "# Valid Skill\n\n"
            "Execution instructions.\n"
        )
        (staging / "SKILL.md").write_text(clean_skill, encoding="utf-8")
        scripts_dir = staging / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "run.py").write_text("print('OK')\n", encoding="utf-8")
        
        zip_out = self.temp_dir / "test-valid-skill.zip"
        pkg_script = SKILL_DIR / "scripts" / "validate_and_package_zip.py"
        
        cmd = [sys.executable, str(pkg_script), str(staging), "-o", str(zip_out)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Packaging failed: {proc.stderr}")
        
        self.assertTrue(zip_out.exists())
        with zipfile.ZipFile(zip_out, "r") as zf:
            names = zf.namelist()
            self.assertIn("SKILL.md", names)
            self.assertIn("scripts/run.py", names)
            self.assertIsNone(zf.testzip())

    def test_06_ultra_safe_consolidation_mode(self):
        """Test ultra-safe mode collapses reference files to comply with <= 10 files."""
        staging = self.temp_dir / "stage_ultra"
        staging.mkdir(parents=True)
        
        (staging / "SKILL.md").write_text(
            "---\nname: ultra-skill\ndescription: Test ultra safe consolidation. Use when testing file ceilings.\n---\n# Ultra\n",
            encoding="utf-8"
        )
        ref_dir = staging / "references"
        ref_dir.mkdir()
        for i in range(12):
            (ref_dir / f"ref_{i}.md").write_text(f"# Reference {i}\nDetails {i}\n", encoding="utf-8")
            
        transpile_script = SKILL_DIR / "scripts" / "lossless_gemini_transpiler.py"
        cmd = [sys.executable, str(transpile_script), str(staging), "--ultra-safe"]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Ultra safe failed: {proc.stderr}")
        
        self.assertTrue((ref_dir / "consolidated-references.md").exists())
        self.assertFalse((ref_dir / "ref_0.md").exists())
        
        # Verify file count <= 10
        total_files = list(staging.rglob("*"))
        file_count = len([f for f in total_files if f.is_file()])
        self.assertLessEqual(file_count, 10)

    def test_07_strict_losslessness_and_offline_gate(self):
        """Test strict losslessness gate catches unhandled network calls."""
        staging = self.temp_dir / "stage_strict"
        staging.mkdir(parents=True)
        (staging / "SKILL.md").write_text(
            "---\nname: strict-skill\ndescription: Test strict losslessness. Use when validating offline compliance.\n---\n# Strict\n",
            encoding="utf-8"
        )
        scripts_dir = staging / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "bad_call.js").write_text("const ep = 'https://api.external.com/v1';", encoding="utf-8")
        
        pkg_script = SKILL_DIR / "scripts" / "validate_and_package_zip.py"
        cmd = [sys.executable, str(pkg_script), str(staging), "--strict-lossless"]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0, "Strict losslessness must fail when unhandled external network calls exist")
        self.assertIn("external network endpoints", proc.stderr + proc.stdout)

    def test_08_kebab_case_hyphen_enforcement(self):
        """Test validator rejects single-word unhyphenated name, and transpiler fixes it."""
        staging = self.temp_dir / "stage_single_word"
        staging.mkdir(parents=True)
        (staging / "SKILL.md").write_text(
            "---\nname: hallmark\ndescription: Anti-slop frontend web design skill. Use when building UI.\n---\n# Single Word\n",
            encoding="utf-8"
        )
        pkg_script = SKILL_DIR / "scripts" / "validate_and_package_zip.py"
        proc = subprocess.run([sys.executable, str(pkg_script), str(staging)], capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0, "Validator must reject single-word unhyphenated name")
        self.assertIn("violates kebab-case regex", proc.stderr + proc.stdout)

        # Transpiler must fix it by adding hyphenated suffix
        transpile_script = SKILL_DIR / "scripts" / "lossless_gemini_transpiler.py"
        proc_trans = subprocess.run([sys.executable, str(transpile_script), str(staging)], capture_output=True, text=True)
        self.assertEqual(proc_trans.returncode, 0)
        
        # Now validator must pass
        proc_pass = subprocess.run([sys.executable, str(pkg_script), str(staging)], capture_output=True, text=True)
        self.assertEqual(proc_pass.returncode, 0, f"Validator should pass after transpiler fix: {proc_pass.stderr}")

    def test_09_file_count_ceiling_and_automatic_lossless_consolidation(self):
        """Test validator rejects > 100 files, and transpiler consolidates subdirectories to <= 100 files without dropping media."""
        staging = self.temp_dir / "stage_100_files"
        staging.mkdir(parents=True)
        (staging / "SKILL.md").write_text(
            "---\nname: mega-skill\ndescription: Test 100 file limit gate. Use when testing file count constraints.\n---\n# Mega\n",
            encoding="utf-8"
        )
        themes_dir = staging / "references" / "themes"
        themes_dir.mkdir(parents=True)
        # Create 60 theme md files and 60 image files
        for i in range(60):
            (themes_dir / f"theme_{i}.md").write_text(f"Theme {i} definition with full color tokens.\n", encoding="utf-8")
            (themes_dir / f"theme_{i}.jpg").write_bytes(b"\xff\xd8\xff\xe0" + b"\x00"*20) # minimal mock jpeg header
            
        pkg_script = SKILL_DIR / "scripts" / "validate_and_package_zip.py"
        # Total files is > 120 -> validator must fail
        proc = subprocess.run([sys.executable, str(pkg_script), str(staging)], capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0, "Validator must reject > 100 files")
        self.assertIn("exceeds Gemini maximum ceiling of 100 files", proc.stderr + proc.stdout)

        # Run transpiler
        transpile_script = SKILL_DIR / "scripts" / "lossless_gemini_transpiler.py"
        proc_trans = subprocess.run([sys.executable, str(transpile_script), str(staging)], capture_output=True, text=True)
        self.assertEqual(proc_trans.returncode, 0, f"Transpiler failed: {proc_trans.stderr}")

        # Check all 60 JPG photos are STILL there!
        jpgs = list(themes_dir.glob("*.jpg"))
        self.assertEqual(len(jpgs), 60, "All 60 theme photos must be 100% retained!")

        # Check themes-catalog.md exists and contains theme content
        catalog = staging / "references" / "themes-catalog.md"
        self.assertTrue(catalog.exists(), "themes-catalog.md must exist")
        self.assertIn("Theme 0 definition", catalog.read_text(encoding="utf-8"))

        # Validator must now pass because file count is <= 100
        proc_pass = subprocess.run([sys.executable, str(pkg_script), str(staging)], capture_output=True, text=True)
        self.assertEqual(proc_pass.returncode, 0, f"Validator should pass: {proc_pass.stderr}")

if __name__ == "__main__":
    unittest.main()
