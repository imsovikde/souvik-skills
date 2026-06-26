#!/usr/bin/env python3
import argparse
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path


class DelinkError(Exception):
    pass


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


def ensure_safe_target(target):
    home = Path.home().resolve()
    root = Path(target.anchor).resolve()
    if target == root:
        raise DelinkError(f"Refusing to operate on filesystem root: {target}")
    if target == home:
        raise DelinkError(f"Refusing to operate on the user home directory: {target}")
    if target.parent == target:
        raise DelinkError(f"Refusing to operate on root-like path: {target}")


def path_status(path):
    if path.exists() or path.is_symlink():
        return "present"
    return "absent"


def print_plan(target, branch, message, no_commit):
    git_dir = target / ".git"
    github_dir = target / ".github"
    print(f"Target: {target}")
    print("Planned removals:")
    print(f"  - {git_dir} ({path_status(git_dir)})")
    print(f"  - {github_dir} ({path_status(github_dir)})")
    print("Planned Git operations:")
    print(f"  - git init on branch {branch}")
    print("  - git add --all")
    if no_commit:
        print("  - skip commit (--no-commit)")
    else:
        print(f"  - git commit -m {message!r}")


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


def reset_repository(target, branch, message, no_commit):
    print(f"Target: {target}")
    for child_name in [".git", ".github"]:
        child = target / child_name
        if remove_path(child):
            print(f"Removed {child}")
        else:
            print(f"Skipped missing {child}")

    init_repository(target, branch)
    print(f"Initialized clean Git repository on branch {branch}")

    run_git(target, ["add", "--all"])
    print("Staged all files")

    if no_commit:
        print("Skipped commit because --no-commit was provided")
        return

    staged = run_git(target, ["diff", "--cached", "--quiet"], check=False)
    if staged.returncode == 0:
        print("No staged changes to commit")
        return

    try:
        run_git(target, ["commit", "-m", message])
    except DelinkError as error:
        raise DelinkError(
            f"{error}\nConfigure Git identity with `git config user.name` and "
            "`git config user.email`, or rerun with --no-commit."
        ) from error
    print(f"Created initial commit: {message}")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Remove GitHub linkage and start a clean local Git repository."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ["plan", "reset"]:
        subparser = subparsers.add_parser(command)
        subparser.add_argument(
            "--target",
            default=".",
            help="Project root to delink. Defaults to the current directory.",
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

    subparsers.choices["reset"].add_argument(
        "--yes",
        action="store_true",
        help="Confirm destructive removal of .git and .github.",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        target = resolve_target(args.target)
        ensure_safe_target(target)
        if args.command == "plan":
            print_plan(target, args.branch, args.message, args.no_commit)
            return
        if not args.yes:
            raise DelinkError("reset is destructive and requires --yes")
        reset_repository(target, args.branch, args.message, args.no_commit)
    except DelinkError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
