#!/usr/bin/env python3
"""
manage_extension.py - Surgical Extension State Manager for Chromium Browsers
Safely disables, enables, or quarantines extensions via Secure Preferences & Preferences.
"""

import os
import sys
import json
import shutil
import argparse

def get_profile_dir(browser_name, profile="Default"):
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    bases = {
        "brave": os.path.join(local_app_data, "BraveSoftware", "Brave-Browser", "User Data", profile),
        "chrome": os.path.join(local_app_data, "Google", "Chrome", "User Data", profile),
        "edge": os.path.join(local_app_data, "Microsoft", "Edge", "User Data", profile),
        "chromium": os.path.join(local_app_data, "Chromium", "User Data", profile),
    }
    return bases.get(browser_name.lower())

def update_preferences_file(file_path, ext_id, action):
    if not os.path.exists(file_path):
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "extensions" not in data:
        data["extensions"] = {}
    if "settings" not in data["extensions"]:
        data["extensions"]["settings"] = {}

    settings = data["extensions"]["settings"]
    if ext_id not in settings:
        settings[ext_id] = {}

    if action == "disable":
        settings[ext_id]["disable_reasons"] = [1]
        settings[ext_id]["state"] = 0
    elif action == "enable":
        settings[ext_id]["disable_reasons"] = []
        settings[ext_id]["state"] = 1

    temp_path = file_path + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    shutil.move(temp_path, file_path)
    return True

def quarantine_extension(prof_dir, ext_id):
    ext_dir = os.path.join(prof_dir, "Extensions", ext_id)
    if not os.path.exists(ext_dir):
        print(f"Error: Extension folder not found: {ext_dir}", file=sys.stderr)
        return False
    quarantine_dir = os.path.join(prof_dir, "Extensions_Quarantine")
    os.makedirs(quarantine_dir, exist_ok=True)
    dst = os.path.join(quarantine_dir, ext_id)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.move(ext_dir, dst)
    print(f"Quarantined: {ext_dir} -> {dst}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Manage Chromium extension states.")
    parser.add_argument("extension_id", help="Target Extension ID")
    parser.add_argument("action", choices=["disable", "enable", "quarantine", "status"], help="Action to perform")
    parser.add_argument("--browser", default="brave", choices=["brave", "chrome", "edge", "chromium"], help="Target browser")
    parser.add_argument("--profile", default="Default", help="Profile name")
    args = parser.parse_args()

    prof_dir = get_profile_dir(args.browser, args.profile)
    if not prof_dir or not os.path.isdir(prof_dir):
        print(f"Error: Profile directory not found: {prof_dir}", file=sys.stderr)
        sys.exit(1)

    sec_pref = os.path.join(prof_dir, "Secure Preferences")
    pref = os.path.join(prof_dir, "Preferences")

    if args.action == "status":
        for label, path in [("Secure Preferences", sec_pref), ("Preferences", pref)]:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    d = json.load(f)
                info = d.get("extensions", {}).get("settings", {}).get(args.extension_id, {})
                print(f"[{label}] disable_reasons: {info.get('disable_reasons')} | state: {info.get('state')}")
        return

    if args.action == "quarantine":
        update_preferences_file(sec_pref, args.extension_id, "disable")
        update_preferences_file(pref, args.extension_id, "disable")
        quarantine_extension(prof_dir, args.extension_id)
        print(f"Extension {args.extension_id} successfully disabled and quarantined.")
        return

    # Disable or enable
    s1 = update_preferences_file(sec_pref, args.extension_id, args.action)
    s2 = update_preferences_file(pref, args.extension_id, args.action)
    print(f"Extension {args.extension_id} marked as {args.action.upper()} (Secure Prefs: {s1}, Prefs: {s2}).")

if __name__ == "__main__":
    main()
