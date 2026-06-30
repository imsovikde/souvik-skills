#!/usr/bin/env python3
import argparse
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


DEFAULT_AUTHOR_NAME = "Souvik Dey"
DEFAULT_AUTHOR_EMAIL = "imsovikde@gmail.com"
GITHUB_OWNER = "imsovikde"

SKIP_DIRECTORIES = {
    ".git",
    ".github",
    ".hg",
    ".svn",
    ".next",
    ".nuxt",
    ".turbo",
    ".vercel",
    ".wrangler",
    ".cache",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "venv",
    "node_modules",
    "bower_components",
    "__pycache__",
    "dist",
    "build",
    "out",
    "coverage",
}

SKIP_FILENAMES = {
    "package-lock.json",
    "npm-shrinkwrap.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "uv.lock",
    "poetry.lock",
    "pdm.lock",
    "Cargo.lock",
    "composer.lock",
}

BINARY_EXTENSIONS = {
    ".7z",
    ".avif",
    ".bmp",
    ".class",
    ".dll",
    ".doc",
    ".docx",
    ".exe",
    ".gif",
    ".gz",
    ".ico",
    ".jar",
    ".jpeg",
    ".jpg",
    ".mov",
    ".mp3",
    ".mp4",
    ".otf",
    ".pdf",
    ".png",
    ".ppt",
    ".pptx",
    ".pyc",
    ".rar",
    ".so",
    ".sqlite",
    ".tar",
    ".ttf",
    ".wasm",
    ".wav",
    ".webp",
    ".woff",
    ".woff2",
    ".xls",
    ".xlsx",
    ".zip",
}

EMAIL_RE = re.compile(r"(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}(?![\w.-])")
GITHUB_URL_RE = re.compile(
    r"(?P<prefix>git\+)?https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+"
    r"(?:\.git)?(?:/[^\s\]\)>'\"<]*)?"
)
LICENSE_META_RE = re.compile(
    r"^\s*(?:"
    r"['\"]?License\s+::|"
    r"license(?:_files?|[-_]files?|[-_]file)?\s*[:=]|"
    r"license-files\s*=|"
    r"license_file\s*=|"
    r"license_files\s*=|"
    r"['\"]license['\"]\s*:|"
    r"['\"]licenseFiles['\"]\s*:"
    r")",
    re.IGNORECASE,
)
LICENSE_BADGE_RE = re.compile(
    r"(?:!\[[^\]]*license[^\]]*\]|\[!\[[^\]]*license[^\]]*\])|"
    r"(?:img\.shields\.io/(?:badge/license|github/license)|license[-_ ]?:)",
    re.IGNORECASE,
)


class DelinkError(Exception):
    pass


@dataclass
class Identity:
    name: str
    email: str

    @property
    def full(self):
        return f"{self.name} <{self.email}>"


@dataclass
class CleanupReport:
    rewritten_files: list
    skipped_files: list
    removed_license_files: list
    renamed_directories: list
    root_rename: tuple | None


def clear_readonly_and_retry(func, path, exc_info):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except OSError:
        raise exc_info[1]


def resolve_target(raw_target):
    target = Path(raw_target).expanduser().resolve()
    if not target.exists():
        raise DelinkError(f"Target does not exist: {target}")
    if not target.is_dir():
        raise DelinkError(f"Target is not a directory: {target}")
    return target


def resolve_cli_target(args):
    positional = getattr(args, "target_path", None)
    flagged = getattr(args, "target", None)

    if positional and flagged and Path(positional).expanduser().resolve() != Path(flagged).expanduser().resolve():
        raise DelinkError("Use either positional target or --target, not both with different paths")

    return flagged or positional or "."


def ensure_safe_target(target):
    home = Path.home().resolve()
    root = Path(target.anchor).resolve()
    if target == root:
        raise DelinkError(f"Refusing to operate on filesystem root: {target}")
    if target == home:
        raise DelinkError(f"Refusing to operate on the user home directory: {target}")
    if target.parent == target:
        raise DelinkError(f"Refusing to operate on root-like path: {target}")


def require_rename_pair(rename_from, rename_to):
    if bool(rename_from) != bool(rename_to):
        raise DelinkError("--rename-from and --rename-to must be provided together")


def path_status(path):
    if path.exists() or path.is_symlink():
        return "present"
    return "absent"


def remove_path(path):
    if not path.exists() and not path.is_symlink():
        return False
    if path.is_symlink() or path.is_file():
        path.unlink()
        return True
    shutil.rmtree(path, onerror=clear_readonly_and_retry)
    return True


def run_git(target, args, check=True):
    result = subprocess.run(
        ["git", *args],
        cwd=str(target),
        capture_output=True,
        text=True,
        check=False,
    )
    if check and result.returncode != 0:
        command = "git " + " ".join(args)
        details = result.stderr.strip() or result.stdout.strip()
        raise DelinkError(f"{command} failed with exit code {result.returncode}: {details}")
    return result


def init_repository(target, branch):
    result = run_git(target, ["init", "--initial-branch", branch], check=False)
    if result.returncode == 0:
        return
    run_git(target, ["init"])
    run_git(target, ["symbolic-ref", "HEAD", f"refs/heads/{branch}"])


def git_config_value(key):
    result = subprocess.run(["git", "config", "--get", key], capture_output=True, text=True, check=False)
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    return None


def get_git_identity():
    return Identity(
        name=git_config_value("user.name") or DEFAULT_AUTHOR_NAME,
        email=git_config_value("user.email") or DEFAULT_AUTHOR_EMAIL,
    )


def split_words(value):
    value = value.strip()
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value)
    value = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", value)
    value = re.sub(r"[-_.\s]+", " ", value)
    words = re.findall(r"[A-Za-z0-9]+", value)
    return [word.lower() for word in words if word]


def pascal_case(words):
    return "".join(word[:1].upper() + word[1:] for word in words)


def camel_case(words):
    if not words:
        return ""
    return words[0] + pascal_case(words[1:])


def build_name_variants(value):
    words = split_words(value)
    if not words:
        raise DelinkError(f"Cannot derive name variants from {value!r}")

    kebab = "-".join(words)
    snake = "_".join(words)
    compact = "".join(words)
    title_words = " ".join(word[:1].upper() + word[1:] for word in words)
    lower_words = " ".join(words)

    return {
        "raw": value,
        "kebab": kebab,
        "snake": snake,
        "pascal": pascal_case(words),
        "camel": camel_case(words),
        "upper_snake": snake.upper(),
        "upper_kebab": kebab.upper(),
        "upper_compact": compact.upper(),
        "lower_compact": compact,
        "lower_words": lower_words,
        "title_words": title_words,
    }


def build_variant_map(rename_from, rename_to):
    old_variants = build_name_variants(rename_from)
    new_variants = build_name_variants(rename_to)
    variant_map = {}

    for key, old_value in old_variants.items():
        new_value = new_variants.get(key, rename_to)
        if old_value and old_value != new_value:
            variant_map[old_value] = new_value

    variant_map[rename_from] = rename_to
    return dict(sorted(variant_map.items(), key=lambda item: len(item[0]), reverse=True))


def kebab_name(value):
    return build_name_variants(value)["kebab"]


def should_skip_directory(path):
    return path.name in SKIP_DIRECTORIES


def should_skip_file(path):
    return path.name in SKIP_FILENAMES or path.suffix.lower() in BINARY_EXTENSIONS


def is_within_skipped_directory(path, target):
    try:
        relative = path.relative_to(target)
    except ValueError:
        return True
    return any(part in SKIP_DIRECTORIES for part in relative.parts[:-1])


def iter_candidate_files(target):
    for path in target.rglob("*"):
        if not path.is_file():
            continue
        if is_within_skipped_directory(path, target):
            continue
        yield path


def read_text(path):
    raw = path.read_bytes()
    if b"\0" in raw[:8192]:
        return None
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return None


def write_text(path, text):
    path.write_text(text, encoding="utf-8", newline="")


def apply_name_replacements(text, variant_map):
    for old, new in variant_map.items():
        text = text.replace(old, new)
    return text


def strip_readme_license(text):
    lines = text.splitlines(keepends=True)
    output = []
    skipping = False
    skip_level = None

    for line in lines:
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if heading:
            level = len(heading.group(1))
            title = re.sub(r"[^a-z0-9 ]+", "", heading.group(2).strip().lower())
            if title == "license" or title.startswith("license "):
                skipping = True
                skip_level = level
                continue
            if skipping and level <= skip_level:
                skipping = False
                skip_level = None

        if skipping:
            continue
        if LICENSE_BADGE_RE.search(line):
            continue
        output.append(line)

    return "".join(output)


def strip_license_metadata(text, path):
    lowered = path.name.lower()

    if lowered.startswith("readme") and path.suffix.lower() in {".md", ".markdown", ".txt", ""}:
        return strip_readme_license(text)

    if lowered in {"setup.py", "pyproject.toml", "setup.cfg"}:
        lines = []
        for line in text.splitlines(keepends=True):
            if LICENSE_META_RE.search(line) or "License ::" in line:
                continue
            lines.append(line)
        return "".join(lines)

    return text


def rewrite_github_urls(text, repo_name):
    canonical = f"https://github.com/{GITHUB_OWNER}/{repo_name}"

    def replace(match):
        original = match.group(0)
        if original.startswith("git+"):
            return f"git+{canonical}.git"
        if original.endswith(".git"):
            return f"{canonical}.git"
        return canonical

    return GITHUB_URL_RE.sub(replace, text)


def rewrite_contact_metadata(text, path, identity):
    name = re.escape(path.name.lower())
    lowered = path.name.lower()

    if lowered == "setup.py":
        text = re.sub(
            r"(?m)^(\s*(?:author|maintainer)\s*=\s*)(['\"]).*?\2(,?)",
            rf"\1\"{identity.name}\"\3",
            text,
        )
        text = re.sub(
            r"(?m)^(\s*(?:author_email|maintainer_email|email|contact_email)\s*=\s*)(['\"]).*?\2(,?)",
            rf"\1\"{identity.email}\"\3",
            text,
        )
        return text

    if lowered in {"pyproject.toml", "setup.cfg"}:
        text = re.sub(r"(?m)^(\s*authors\s*=\s*).+$", rf'\1["{identity.full}"]', text)
        text = re.sub(r"(?m)^(\s*maintainers\s*=\s*).+$", rf'\1["{identity.full}"]', text)
        text = re.sub(r"(?m)^(\s*(?:author|maintainer)\s*=\s*)(['\"]).*?\2", rf'\1"{identity.name}"', text)
        text = re.sub(
            r"(?m)^(\s*(?:author_email|maintainer_email|email|contact_email|contact)\s*=\s*)(['\"]).*?\2",
            rf'\1"{identity.email}"',
            text,
        )
        return text

    return text


def update_package_json(text, identity, repo_name):
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return text

    canonical = f"https://github.com/{GITHUB_OWNER}/{repo_name}"
    changed = False

    for key in ["license", "licenses", "licenseFiles", "licenseFile"]:
        if key in data:
            data.pop(key, None)
            changed = True

    if data.get("author") != identity.full:
        data["author"] = identity.full
        changed = True

    target_repository = {"type": "git", "url": f"git+{canonical}.git"}
    if data.get("repository") != target_repository:
        data["repository"] = target_repository
        changed = True

    target_bugs = {"url": f"{canonical}/issues"}
    if data.get("bugs") != target_bugs:
        data["bugs"] = target_bugs
        changed = True

    if isinstance(data.get("homepage"), str) and "github.com" in data["homepage"].lower():
        data["homepage"] = canonical
        changed = True

    if not changed:
        return text

    return json.dumps(data, indent=2) + "\n"


def transform_text(path, text, variant_map, identity, repo_name):
    updated = text

    if variant_map:
        updated = apply_name_replacements(updated, variant_map)

    updated = strip_license_metadata(updated, path)
    updated = EMAIL_RE.sub(identity.email, updated)
    updated = rewrite_github_urls(updated, repo_name)
    updated = rewrite_contact_metadata(updated, path, identity)

    if path.name == "package.json":
        updated = update_package_json(updated, identity, repo_name)

    return updated


def remove_root_license_files(target):
    removed = []
    for child in target.iterdir():
        if not (child.is_file() or child.is_symlink()):
            continue
        upper = child.name.upper()
        if upper.startswith("LICENSE") or upper.startswith("COPYING"):
            remove_path(child)
            removed.append(child)
    return removed


def rewrite_project_files(target, variant_map, identity, repo_name):
    rewritten = []
    skipped = []

    for path in iter_candidate_files(target):
        if should_skip_file(path):
            skipped.append(path)
            continue

        text = read_text(path)
        if text is None:
            skipped.append(path)
            continue

        updated = transform_text(path, text, variant_map, identity, repo_name)
        if updated != text:
            write_text(path, updated)
            rewritten.append(path)

    return rewritten, skipped


def planned_directory_renames(target, variant_map):
    if not variant_map:
        return []

    planned = []
    directories = sorted([path for path in target.rglob("*") if path.is_dir()], key=lambda path: len(path.parts), reverse=True)

    for directory in directories:
        if is_within_skipped_directory(directory, target):
            continue
        if directory.name in variant_map:
            planned.append((directory, directory.with_name(variant_map[directory.name])))

    if target.name in variant_map:
        planned.append((target, target.with_name(variant_map[target.name])))

    return planned


def rename_matching_directories(target, variant_map):
    renamed = []
    if not variant_map:
        return target, renamed, None

    directories = sorted([path for path in target.rglob("*") if path.is_dir()], key=lambda path: len(path.parts), reverse=True)

    for directory in directories:
        if directory == target:
            continue
        if is_within_skipped_directory(directory, target):
            continue
        replacement = variant_map.get(directory.name)
        if not replacement or replacement == directory.name:
            continue
        destination = directory.with_name(replacement)
        if destination.exists():
            raise DelinkError(f"Cannot rename {directory} to {destination}: destination already exists")
        directory.rename(destination)
        renamed.append((directory, destination))

    root_rename = None
    root_replacement = variant_map.get(target.name)
    if root_replacement and root_replacement != target.name:
        destination = target.with_name(root_replacement)
        if destination.exists():
            raise DelinkError(f"Cannot rename {target} to {destination}: destination already exists")
        if Path.cwd().resolve() == target:
            os.chdir(target.parent)
        target.rename(destination)
        root_rename = (target, destination)
        target = destination

    return target, renamed, root_rename


def cleanup_project(target, rename_from, rename_to):
    require_rename_pair(rename_from, rename_to)

    identity = get_git_identity()
    variant_map = build_variant_map(rename_from, rename_to) if rename_from and rename_to else {}
    repo_name = kebab_name(rename_to or target.name)

    removed_license_files = remove_root_license_files(target)
    rewritten_files, skipped_files = rewrite_project_files(target, variant_map, identity, repo_name)
    target, renamed_directories, root_rename = rename_matching_directories(target, variant_map)

    return target, CleanupReport(
        rewritten_files=rewritten_files,
        skipped_files=skipped_files,
        removed_license_files=removed_license_files,
        renamed_directories=renamed_directories,
        root_rename=root_rename,
    )


def print_plan(target, args):
    require_rename_pair(args.rename_from, args.rename_to)
    identity = get_git_identity()
    variant_map = build_variant_map(args.rename_from, args.rename_to) if args.rename_from else {}
    repo_name = kebab_name(args.rename_to or target.name)
    license_files = [
        child
        for child in target.iterdir()
        if (child.is_file() or child.is_symlink())
        and (child.name.upper().startswith("LICENSE") or child.name.upper().startswith("COPYING"))
    ]
    directory_renames = planned_directory_renames(target, variant_map)

    print(f"Target: {target}")
    print("Planned removals:")
    print(f"  - {target / '.git'} ({path_status(target / '.git')})")
    print(f"  - {target / '.github'} ({path_status(target / '.github')})")
    if license_files:
        for path in license_files:
            print(f"  - {path} (root license file)")
    else:
        print("  - root LICENSE*/COPYING* files (none found)")

    print("Planned repository isolation:")
    if args.rename_from:
        print(f"  - rename references from {args.rename_from!r} to {args.rename_to!r}")
        print("  - variants: kebab-case, snake_case, PascalCase, camelCase, UPPER_CASE, uppercase, lowercase")
    else:
        print("  - no project rename requested")
    print(f"  - rewrite contact metadata to {identity.full}")
    print(f"  - redirect GitHub repository URLs to https://github.com/{GITHUB_OWNER}/{repo_name}")
    print("  - strip license classifiers, license metadata lines, license badges, and README license sections")
    print("  - skip lockfiles, dependency folders, generated folders, and binary assets")

    print("Planned directory renames:")
    if directory_renames:
        for source, destination in directory_renames:
            print(f"  - {source} -> {destination}")
    else:
        print("  - none")

    print("Planned Git operations:")
    print(f"  - git init on branch {args.branch}")
    print("  - git add --all")
    if args.no_commit:
        print("  - skip commit (--no-commit)")
    else:
        print(f"  - git commit -m {args.message!r}")


def reset_repository(target, args):
    print(f"Target: {target}")
    for child_name in [".git", ".github"]:
        child = target / child_name
        if remove_path(child):
            print(f"Removed {child}")
        else:
            print(f"Skipped missing {child}")

    target, report = cleanup_project(target, args.rename_from, args.rename_to)

    for path in report.removed_license_files:
        print(f"Removed license file {path}")
    for source, destination in report.renamed_directories:
        print(f"Renamed directory {source} -> {destination}")
    if report.root_rename:
        print(f"Renamed root {report.root_rename[0]} -> {report.root_rename[1]}")
    print(f"Rewritten files: {len(report.rewritten_files)}")
    print(f"Skipped lock/binary/generated files: {len(report.skipped_files)}")

    init_repository(target, args.branch)
    print(f"Initialized clean Git repository on branch {args.branch}")

    run_git(target, ["add", "--all"])
    print("Staged all files")

    if args.no_commit:
        print("Skipped commit because --no-commit was provided")
        return target

    staged = run_git(target, ["diff", "--cached", "--quiet"], check=False)
    if staged.returncode == 0:
        print("No staged changes to commit")
        return target

    try:
        run_git(target, ["commit", "-m", args.message])
    except DelinkError as error:
        raise DelinkError(
            f"{error}\nConfigure Git identity with `git config user.name` and "
            "`git config user.email`, or rerun with --no-commit."
        ) from error
    print(f"Created initial commit: {args.message}")
    return target


def add_common_arguments(subparser):
    subparser.add_argument(
        "target_path",
        nargs="?",
        help="Project root to delink. Defaults to the current directory.",
    )
    subparser.add_argument(
        "--target",
        help="Project root to delink. Kept for backward compatibility.",
    )
    subparser.add_argument(
        "--rename-from",
        help="Old project name to replace across source, config, and docs.",
    )
    subparser.add_argument(
        "--rename-to",
        help="New project name to use for replacement and directory renames.",
    )
    subparser.add_argument(
        "--branch",
        default="main",
        help="Initial branch name for the clean repository.",
    )
    subparser.add_argument(
        "--message",
        default="initial commit",
        help="Initial commit message.",
    )
    subparser.add_argument(
        "--no-commit",
        action="store_true",
        help="Initialize and stage files without creating a commit.",
    )


def build_parser():
    parser = argparse.ArgumentParser(
        description="Remove GitHub linkage, purge inherited repository metadata, and start a clean local Git repository."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ["plan", "reset"]:
        subparser = subparsers.add_parser(command)
        add_common_arguments(subparser)

    subparsers.choices["reset"].add_argument(
        "--yes",
        action="store_true",
        help="Confirm destructive removal of .git, .github, license files, and inherited metadata.",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        target = resolve_target(resolve_cli_target(args))
        ensure_safe_target(target)
        require_rename_pair(args.rename_from, args.rename_to)
        if args.command == "plan":
            print_plan(target, args)
            return
        if not args.yes:
            raise DelinkError("reset is destructive and requires --yes")
        final_target = reset_repository(target, args)
        print(f"Final target: {final_target}")
    except DelinkError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
