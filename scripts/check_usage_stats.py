#!/usr/bin/env python3
"""
FLOW 8 Pro Studio Remote — GitHub Usage & Release Download Tracker
Queries the public GitHub API to display how many users have downloaded
FLOW8_Remote_Pro.exe, along with repository stars, forks, and watchers.
"""

import json
import urllib.request

REPO = "livezalaeveryday/Flow8-Remote-Pro"


def fetch_json(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Flow8-Remote-Pro-Stats-Checker/1.0",
            "Accept": "application/vnd.github+json",
        },
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    print("=" * 68)
    print(f"  FLOW 8 PRO STUDIO REMOTE — USAGE & DOWNLOAD ANALYTICS")
    print(f"  Repository: https://github.com/{REPO}")
    print("=" * 68)

    try:
        repo_info = fetch_json(f"https://api.github.com/repos/{REPO}")
        print(f"  * Stars (Stargazers) : {repo_info.get('stargazers_count', 0)}")
        print(f"  * Forks              : {repo_info.get('forks_count', 0)}")
        print(f"  * Subscribers/Watch  : {repo_info.get('subscribers_count', 0)}")
        print(f"  * Open Issues        : {repo_info.get('open_issues_count', 0)}")
    except Exception as e:
        print(f"  [!] Could not fetch repo info: {e}")

    print("-" * 68)
    try:
        releases = fetch_json(f"https://api.github.com/repos/{REPO}/releases")
        total_downloads = 0
        if not releases:
            print("  No releases published yet.")
        for rel in releases:
            tag = rel.get("tag_name", "unknown")
            name = rel.get("name") or tag
            pub = rel.get("published_at", "")[:10]
            print(f"  Release [{tag}] {name} (Published: {pub})")
            for asset in rel.get("assets", []):
                a_name = asset.get("name", "")
                dl_count = asset.get("download_count", 0)
                size_mb = asset.get("size", 0) / (1024 * 1024)
                total_downloads += dl_count
                print(f"    -> {a_name:<28} : {dl_count:>5} downloads ({size_mb:.2f} MB)")
        print("-" * 68)
        print(f"  TOTAL EXE / RELEASE DOWNLOADS : {total_downloads}")
    except Exception as e:
        print(f"  [!] Could not fetch release stats: {e}")
    print("=" * 68)


if __name__ == "__main__":
    main()
