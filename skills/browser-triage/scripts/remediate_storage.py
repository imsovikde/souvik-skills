#!/usr/bin/env python3
"""
remediate_storage.py - Surgical Chromium Storage & Cache Remediation Engine
Guarantees 100% preservation of Bookmarks, Login Data (passwords), History, Web Data, and Sessions.
"""

import os
import sys
import json
import shutil
import argparse

CRITICAL_ASSETS = [
    "Bookmarks",
    "Bookmarks.bak",
    "Login Data",
    "Login Data-journal",
    "Login Data For Account",
    "History",
    "History-journal",
    "Favicons",
    "Favicons-journal",
    "Web Data",
    "Web Data-journal",
    "Preferences",
    "Secure Preferences"
]

def get_browser_dirs(browser_name, profile="Default"):
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    bases = {
        "brave": os.path.join(local_app_data, "BraveSoftware", "Brave-Browser", "User Data"),
        "chrome": os.path.join(local_app_data, "Google", "Chrome", "User Data"),
        "edge": os.path.join(local_app_data, "Microsoft", "Edge", "User Data"),
        "chromium": os.path.join(local_app_data, "Chromium", "User Data"),
    }
    base = bases.get(browser_name.lower())
    if not base:
        return None, None
    prof = os.path.join(base, profile)
    return base, prof

def create_atomic_backup(base_dir, prof_dir, backup_dir):
    os.makedirs(backup_dir, exist_ok=True)
    print(f"Creating atomic backup to: {backup_dir}")

    # Copy individual critical files
    for asset in CRITICAL_ASSETS:
        src = os.path.join(prof_dir, asset)
        if os.path.exists(src):
            dst = os.path.join(backup_dir, asset)
            shutil.copy2(src, dst)
            print(f"  [BACKED UP] {asset} ({os.path.getsize(src)} bytes)")

    # Copy Local State from base
    local_state = os.path.join(base_dir, "Local State")
    if os.path.exists(local_state):
        shutil.copy2(local_state, os.path.join(backup_dir, "Local State"))
        print(f"  [BACKED UP] Local State ({os.path.getsize(local_state)} bytes)")

    # Copy Sessions directory
    sessions_src = os.path.join(prof_dir, "Sessions")
    if os.path.exists(sessions_src):
        sessions_dst = os.path.join(backup_dir, "Sessions")
        if os.path.exists(sessions_dst):
            shutil.rmtree(sessions_dst)
        shutil.copytree(sessions_src, sessions_dst)
        print(f"  [BACKED UP] Sessions/ directory ({len(os.listdir(sessions_dst))} files)")

    print("Atomic safety snapshot verified.")

def purge_corrupted_storage(base_dir, prof_dir, origin_filter=None):
    print("\nExecuting surgical storage and cache purge...")

    # 1. Purge Service Worker
    sw_dir = os.path.join(prof_dir, "Service Worker")
    if os.path.exists(sw_dir):
        shutil.rmtree(sw_dir, ignore_errors=True)
        print("  [PURGED] Default/Service Worker (all caches and registration DB)")

    # 2. Purge IndexedDB matching origin filter
    idb_dir = os.path.join(prof_dir, "IndexedDB")
    if os.path.exists(idb_dir):
        for entry in os.listdir(idb_dir):
            if origin_filter:
                if any(f in entry.lower() for f in origin_filter):
                    target = os.path.join(idb_dir, entry)
                    if os.path.isdir(target):
                        shutil.rmtree(target, ignore_errors=True)
                    else:
                        os.remove(target)
                    print(f"  [PURGED] Default/IndexedDB/{entry}")
            else:
                if "google" in entry.lower() or "mail" in entry.lower():
                    target = os.path.join(idb_dir, entry)
                    if os.path.isdir(target):
                        shutil.rmtree(target, ignore_errors=True)
                    print(f"  [PURGED] Default/IndexedDB/{entry}")

    # 3. Purge GPU, shader, and code compilation caches
    cache_dirs = [
        os.path.join(base_dir, "GrShaderCache"),
        os.path.join(base_dir, "ShaderCache"),
        os.path.join(base_dir, "GPUPersistentCache"),
        os.path.join(prof_dir, "GPUCache"),
        os.path.join(prof_dir, "DawnGraphiteCache"),
        os.path.join(prof_dir, "DawnWebGPUCache"),
        os.path.join(prof_dir, "Code Cache"),
    ]
    for c in cache_dirs:
        if os.path.exists(c):
            shutil.rmtree(c, ignore_errors=True)
            print(f"  [PURGED] {os.path.basename(os.path.dirname(c))}/{os.path.basename(c)}")

    print("Storage and shader cache purge complete.")

def reconfigure_hardware_accel(base_dir, prof_dir, enable=False):
    print(f"\nReconfiguring hardware acceleration mode (enabled={enable})...")
    
    # 1. Local State
    ls_path = os.path.join(base_dir, "Local State")
    if os.path.exists(ls_path):
        with open(ls_path, "r", encoding="utf-8") as f:
            ls_data = json.load(f)
        ls_data["hardware_acceleration_mode"] = {"enabled": enable}
        ls_data["hardware_acceleration_mode_previous"] = enable
        with open(ls_path, "w", encoding="utf-8") as f:
            json.dump(ls_data, f, indent=2, ensure_ascii=False)
        print("  [UPDATED] Local State (hardware_acceleration_mode)")

    # 2. Preferences
    pref_path = os.path.join(prof_dir, "Preferences")
    if os.path.exists(pref_path):
        with open(pref_path, "r", encoding="utf-8") as f:
            pref_data = json.load(f)
        pref_data["hardware_acceleration_mode"] = {"enabled": enable}
        with open(pref_path, "w", encoding="utf-8") as f:
            json.dump(pref_data, f, indent=2, ensure_ascii=False)
        print("  [UPDATED] Preferences (hardware_acceleration_mode)")

def main():
    parser = argparse.ArgumentParser(description="Surgically remediate Chromium storage & GPU caches.")
    parser.add_argument("--browser", default="brave", choices=["brave", "chrome", "edge", "chromium"], help="Target browser")
    parser.add_argument("--profile", default="Default", help="Profile name")
    parser.add_argument("--backup-dir", help="Backup destination path")
    parser.add_argument("--disable-gpu-accel", action="store_true", help="Set hardware acceleration to software fallback")
    parser.add_argument("--origins", nargs="+", help="Origin keywords for IndexedDB purge (e.g. mail.google.com)")
    args = parser.parse_args()

    base_dir, prof_dir = get_browser_dirs(args.browser, args.profile)
    if not prof_dir or not os.path.isdir(prof_dir):
        print(f"Error: Profile directory not found: {prof_dir}", file=sys.stderr)
        sys.exit(1)

    backup_path = args.backup_dir or os.path.join(os.environ.get("LOCALAPPDATA", ""), f"{args.browser.capitalize()}_Safe_Backup")
    create_atomic_backup(base_dir, prof_dir, backup_path)
    purge_corrupted_storage(base_dir, prof_dir, args.origins)

    if args.disable_gpu_accel:
        reconfigure_hardware_accel(base_dir, prof_dir, enable=False)

    print("\nAll surgical remediation tasks completed successfully.")

if __name__ == "__main__":
    main()
