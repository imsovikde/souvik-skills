#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().with_name("delink.py")


class DelinkScriptTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="delink-test-"))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def run_script(self, *args, cwd=None):
        env = os.environ.copy()
        env.update(
            {
                "GIT_AUTHOR_NAME": "Souvik Dey",
                "GIT_AUTHOR_EMAIL": "imsovikde@gmail.com",
                "GIT_COMMITTER_NAME": "Souvik Dey",
                "GIT_COMMITTER_EMAIL": "imsovikde@gmail.com",
            }
        )
        return subprocess.run(
            [sys.executable, str(SCRIPT), *map(str, args)],
            cwd=str(cwd or self.temp_dir),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    def make_project(self):
        project = self.temp_dir / "old-project"
        project.mkdir()
        (project / ".github").mkdir()
        (project / ".github" / "workflows").mkdir()
        (project / ".github" / "workflows" / "ci.yml").write_text("name: OldProject\n", encoding="utf-8")
        (project / "LICENSE").write_text("MIT License\n", encoding="utf-8")
        (project / "README.md").write_text(
            "\n".join(
                [
                    "# OldProject",
                    "",
                    "[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)",
                    "",
                    "Contact old@example.com and see https://github.com/original-owner/old-project.",
                    "",
                    "## License",
                    "",
                    "MIT.",
                    "",
                    "## Usage",
                    "",
                    "Use old-project, old_project, OldProject, oldProject, OLD_PROJECT, OLDPROJECT, and oldproject.",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (project / "pyproject.toml").write_text(
            "\n".join(
                [
                    "[project]",
                    'name = "old-project"',
                    'authors = ["Original Author <old@example.com>"]',
                    'license = "MIT"',
                    'classifiers = ["License :: OSI Approved :: MIT License"]',
                    "",
                    "[project.urls]",
                    'Repository = "https://github.com/original-owner/old-project"',
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (project / "package.json").write_text(
            json.dumps(
                {
                    "name": "old-project",
                    "version": "1.0.0",
                    "license": "MIT",
                    "author": "Original Author <old@example.com>",
                    "repository": {
                        "type": "git",
                        "url": "git+https://github.com/original-owner/old-project.git",
                    },
                    "bugs": {"url": "https://github.com/original-owner/old-project/issues"},
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (project / "package-lock.json").write_text('{"name":"old-project"}\n', encoding="utf-8")
        package_dir = project / "old_project"
        package_dir.mkdir()
        (package_dir / "__init__.py").write_text(
            "class OldProject:\n    NAME = 'OLD_PROJECT'\n    slug = 'old-project'\n",
            encoding="utf-8",
        )
        (project / "logo.png").write_bytes(b"\x89PNG\r\n\x1a\n\0old-project")
        subprocess.run(["git", "init"], cwd=str(project), capture_output=True, text=True, check=False)
        return project

    def test_reset_supports_positional_target_rename_cleanup_and_commit(self):
        project = self.make_project()

        result = self.run_script(
            "reset",
            project,
            "--rename-from",
            "old-project",
            "--rename-to",
            "fresh-skill",
            "--yes",
        )

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        final_project = self.temp_dir / "fresh-skill"
        self.assertTrue(final_project.exists())
        self.assertFalse((final_project / ".github").exists())
        self.assertFalse((final_project / "LICENSE").exists())
        self.assertTrue((final_project / ".git").exists())
        self.assertTrue((final_project / "fresh_skill").is_dir())

        readme = (final_project / "README.md").read_text(encoding="utf-8")
        self.assertIn("fresh-skill", readme)
        self.assertIn("fresh_skill", readme)
        self.assertIn("FreshSkill", readme)
        self.assertIn("freshSkill", readme)
        self.assertIn("FRESH_SKILL", readme)
        self.assertIn("FRESHSKILL", readme)
        self.assertIn("imsovikde@gmail.com", readme)
        self.assertIn("https://github.com/imsovikde/fresh-skill", readme)
        self.assertNotIn("License: MIT", readme)
        self.assertNotIn("## License", readme)
        self.assertNotIn("old-project", readme)

        package_json = json.loads((final_project / "package.json").read_text(encoding="utf-8"))
        self.assertNotIn("license", package_json)
        self.assertEqual(package_json["author"], "Souvik Dey <imsovikde@gmail.com>")
        self.assertEqual(package_json["repository"]["url"], "git+https://github.com/imsovikde/fresh-skill.git")
        self.assertEqual(package_json["bugs"]["url"], "https://github.com/imsovikde/fresh-skill/issues")

        pyproject = (final_project / "pyproject.toml").read_text(encoding="utf-8")
        self.assertNotIn("License ::", pyproject)
        self.assertNotIn('license = "MIT"', pyproject)
        self.assertIn('authors = ["Souvik Dey <imsovikde@gmail.com>"]', pyproject)

        lockfile = (final_project / "package-lock.json").read_text(encoding="utf-8")
        self.assertIn("old-project", lockfile)
        self.assertIn(b"old-project", (final_project / "logo.png").read_bytes())

        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=str(final_project),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(branch.stdout.strip(), "main")
        log = subprocess.run(
            ["git", "log", "--oneline", "--max-count=1"],
            cwd=str(final_project),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertIn("initial commit", log.stdout)
        remotes = subprocess.run(
            ["git", "remote", "-v"],
            cwd=str(final_project),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(remotes.stdout.strip(), "")

    def test_plan_keeps_backward_compatible_target_flag(self):
        project = self.make_project()
        result = self.run_script("plan", "--target", project, "--rename-from", "old-project", "--rename-to", "fresh-skill")

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("Planned repository isolation", result.stdout)
        self.assertIn("old-project", result.stdout)
        self.assertIn("fresh-skill", result.stdout)

    def test_reset_requires_rename_pair(self):
        project = self.make_project()
        result = self.run_script("reset", project, "--rename-from", "old-project", "--yes")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--rename-from and --rename-to", result.stderr)


if __name__ == "__main__":
    unittest.main()
