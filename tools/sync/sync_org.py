#!/usr/bin/env python3
"""
haKCAssets Org Sync - Scan and sync assets from all haKC-ai repos

Usage:
  python tools/sync_org.py                    # Scan all repos, show what would be synced
  python tools/sync_org.py --apply            # Actually download and organize assets
  python tools/sync_org.py --watch            # Watch for changes (runs every N minutes)
  python tools/sync_org.py --repo hakcer      # Scan specific repo only
  python tools/sync_org.py --list             # List all repos and their asset counts
"""

import json
import os
import sys
import subprocess
import base64
import hashlib
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field

# Asset file patterns to look for
ASSET_EXTENSIONS = {
    "images": [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico"],
    "banners": [".txt", ".ans", ".asc", ".nfo"],
    "media": [".mp4", ".gif", ".webm", ".mov"],
    "docs": [".pdf"],
}

# Common asset directories in repos
ASSET_DIRS = ["media", "img", "images", "assets", "icons", "banner", "banners", "art", "screenshots", "docs"]

# Files that are likely banners (ASCII art)
BANNER_PATTERNS = ["banner", "ascii", "logo.txt", "header.txt"]


@dataclass
class Asset:
    """Represents a discovered asset."""
    repo: str
    path: str
    name: str
    size: int
    sha: str
    download_url: str
    asset_type: str  # images, banners, media, docs
    local_path: Optional[Path] = None


@dataclass
class SyncState:
    """Tracks sync state for incremental updates."""
    last_sync: str = ""
    repos: dict = field(default_factory=dict)  # repo -> {sha: local_path}


class OrgScanner:
    def __init__(self, org: str = "haKC-ai", repo_root: Path = None):
        self.org = org
        self.repo_root = repo_root or Path(__file__).parent.parent
        self.state_file = self.repo_root / ".sync_state.json"
        self.state = self._load_state()
        self.assets: list[Asset] = []

    def _load_state(self) -> SyncState:
        """Load sync state from file."""
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text())
                return SyncState(**data)
            except:
                pass
        return SyncState()

    def _save_state(self):
        """Save sync state to file."""
        self.state_file.write_text(json.dumps({
            "last_sync": self.state.last_sync,
            "repos": self.state.repos
        }, indent=2))

    def _run_gh(self, *args) -> Optional[str]:
        """Run gh CLI command and return output."""
        try:
            result = subprocess.run(
                ["gh", *args],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception as e:
            print(f"  Error running gh: {e}")
            return None

    def _get_file_type(self, filename: str, content: str = None) -> str:
        """Determine asset type from filename/content."""
        ext = Path(filename).suffix.lower()
        name_lower = filename.lower()

        # Check extension
        for asset_type, extensions in ASSET_EXTENSIONS.items():
            if ext in extensions:
                # Special case: .txt files might be banners
                if ext == ".txt":
                    if any(p in name_lower for p in BANNER_PATTERNS):
                        return "banners"
                    # Check content for ASCII art characters
                    if content and any(c in content for c in "█▓▒░╔╗╚╝│─"):
                        return "banners"
                return asset_type

        # Check if it's a banner file without extension
        if any(p in name_lower for p in BANNER_PATTERNS):
            return "banners"

        return "other"

    def list_repos(self) -> list[dict]:
        """List all repos in the org."""
        output = self._run_gh("repo", "list", self.org, "--json", "name,description,updatedAt", "--limit", "100")
        if output:
            return json.loads(output)
        return []

    def scan_repo_contents(self, repo: str, path: str = "") -> list[dict]:
        """Recursively scan repo contents for assets."""
        endpoint = f"repos/{self.org}/{repo}/contents/{path}".rstrip("/")
        output = self._run_gh("api", endpoint, "--jq", ".")

        if not output:
            return []

        try:
            items = json.loads(output)
            if isinstance(items, dict):  # Single file
                items = [items]
            return items
        except:
            return []

    def scan_repo(self, repo: str) -> list[Asset]:
        """Scan a single repo for assets."""
        assets = []

        # First, get root contents
        root_items = self.scan_repo_contents(repo)

        # Look for asset directories
        dirs_to_scan = []
        for item in root_items:
            name = item.get("name", "")
            item_type = item.get("type", "")

            if item_type == "dir" and name.lower() in ASSET_DIRS:
                dirs_to_scan.append(name)
            elif item_type == "file":
                # Check if it's an asset file in root
                asset_type = self._get_file_type(name)
                if asset_type != "other":
                    assets.append(Asset(
                        repo=repo,
                        path=name,
                        name=name,
                        size=item.get("size", 0),
                        sha=item.get("sha", ""),
                        download_url=item.get("download_url", ""),
                        asset_type=asset_type
                    ))

        # Scan asset directories
        for dir_name in dirs_to_scan:
            dir_items = self.scan_repo_contents(repo, dir_name)
            for item in dir_items:
                if item.get("type") == "file":
                    name = item.get("name", "")
                    path = item.get("path", "")

                    # For banners, try to peek at content
                    content = None
                    if Path(name).suffix.lower() in [".txt", ""] and item.get("size", 0) < 50000:
                        # Fetch content for ASCII detection
                        content_data = self._run_gh("api", f"repos/{self.org}/{repo}/contents/{path}")
                        if content_data:
                            try:
                                data = json.loads(content_data)
                                if data.get("encoding") == "base64":
                                    content = base64.b64decode(data.get("content", "")).decode("utf-8", errors="ignore")
                            except:
                                pass

                    asset_type = self._get_file_type(name, content)
                    if asset_type != "other":
                        assets.append(Asset(
                            repo=repo,
                            path=path,
                            name=name,
                            size=item.get("size", 0),
                            sha=item.get("sha", ""),
                            download_url=item.get("download_url", ""),
                            asset_type=asset_type
                        ))

        return assets

    def scan_all(self, specific_repo: str = None) -> list[Asset]:
        """Scan all repos (or specific repo) for assets."""
        self.assets = []

        if specific_repo:
            repos = [{"name": specific_repo}]
        else:
            repos = self.list_repos()

        print(f"Scanning {len(repos)} repo(s)...\n")

        for repo_info in repos:
            repo_name = repo_info["name"]

            # Skip haKCAssets itself
            if repo_name == "haKCAssets":
                continue

            print(f"  Scanning {repo_name}...", end=" ", flush=True)
            assets = self.scan_repo(repo_name)
            self.assets.extend(assets)
            print(f"found {len(assets)} asset(s)")

        return self.assets

    def get_local_path(self, asset: Asset) -> Path:
        """Determine local path for an asset based on rules."""
        # Organize by repo, then by type
        repo_dir = self.repo_root / "repos" / asset.repo

        if asset.asset_type == "images":
            return repo_dir / "images" / asset.name
        elif asset.asset_type == "banners":
            return repo_dir / "banners" / asset.name
        elif asset.asset_type == "media":
            return repo_dir / "media" / asset.name
        elif asset.asset_type == "docs":
            return repo_dir / "docs" / asset.name
        else:
            return repo_dir / "other" / asset.name

    def needs_sync(self, asset: Asset) -> bool:
        """Check if asset needs to be synced."""
        local_path = self.get_local_path(asset)

        # Check if file exists
        if not local_path.exists():
            return True

        # Check if SHA changed
        repo_state = self.state.repos.get(asset.repo, {})
        stored_sha = repo_state.get(asset.path)

        return stored_sha != asset.sha

    def download_asset(self, asset: Asset) -> bool:
        """Download an asset to local storage."""
        local_path = self.get_local_path(asset)
        local_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Use curl to download
            result = subprocess.run(
                ["curl", "-sL", "-o", str(local_path), asset.download_url],
                capture_output=True, timeout=60
            )

            if result.returncode == 0 and local_path.exists():
                # Update state
                if asset.repo not in self.state.repos:
                    self.state.repos[asset.repo] = {}
                self.state.repos[asset.repo][asset.path] = asset.sha
                return True
        except Exception as e:
            print(f"    Error downloading {asset.name}: {e}")

        return False

    def sync(self, dry_run: bool = True) -> list[Asset]:
        """Sync assets that need updating."""
        to_sync = [a for a in self.assets if self.needs_sync(a)]

        if not to_sync:
            print("\nAll assets are up to date.")
            return []

        print(f"\n{len(to_sync)} asset(s) need syncing:\n")

        for asset in to_sync:
            local_path = self.get_local_path(asset)
            action = "new" if not local_path.exists() else "update"

            if dry_run:
                print(f"  [{action}] {asset.repo}/{asset.path} → {local_path.relative_to(self.repo_root)}")
            else:
                print(f"  Syncing {asset.repo}/{asset.path}...", end=" ", flush=True)
                if self.download_asset(asset):
                    print("done")
                else:
                    print("FAILED")

        if not dry_run:
            self.state.last_sync = datetime.now().isoformat()
            self._save_state()

        return to_sync

    def watch(self, interval_minutes: int = 30):
        """Watch for changes and sync periodically."""
        print(f"Watching for changes every {interval_minutes} minutes...")
        print("Press Ctrl+C to stop.\n")

        try:
            while True:
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Scanning...")
                self.scan_all()
                synced = self.sync(dry_run=False)

                if synced:
                    print(f"Synced {len(synced)} asset(s)")
                else:
                    print("No changes detected")

                print(f"Next scan in {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
        except KeyboardInterrupt:
            print("\nStopped watching.")


def print_summary(scanner: OrgScanner):
    """Print a summary of discovered assets."""
    if not scanner.assets:
        print("\nNo assets found.")
        return

    # Group by repo
    by_repo = {}
    for asset in scanner.assets:
        if asset.repo not in by_repo:
            by_repo[asset.repo] = {"images": [], "banners": [], "media": [], "docs": []}
        by_repo[asset.repo][asset.asset_type].append(asset)

    print(f"\n{'─' * 60}")
    print(f"  Found {len(scanner.assets)} assets across {len(by_repo)} repos")
    print(f"{'─' * 60}\n")

    for repo, types in sorted(by_repo.items()):
        total = sum(len(v) for v in types.values())
        print(f"  {repo}: {total} asset(s)")
        for asset_type, assets in types.items():
            if assets:
                print(f"    {asset_type}: {len(assets)}")
                for a in assets[:3]:  # Show first 3
                    print(f"      - {a.name}")
                if len(assets) > 3:
                    print(f"      ... and {len(assets) - 3} more")


def main():
    parser = argparse.ArgumentParser(description="Sync assets from haKC-ai org repos")
    parser.add_argument("--apply", action="store_true", help="Actually download assets (default is dry run)")
    parser.add_argument("--watch", action="store_true", help="Watch for changes continuously")
    parser.add_argument("--interval", type=int, default=30, help="Watch interval in minutes (default: 30)")
    parser.add_argument("--repo", type=str, help="Scan specific repo only")
    parser.add_argument("--list", action="store_true", help="Just list repos and exit")
    parser.add_argument("--org", type=str, default="haKC-ai", help="GitHub org to scan")
    args = parser.parse_args()

    # Find repo root
    repo_root = Path(__file__).parent.parent
    if not (repo_root / "asset_rules.json").exists():
        repo_root = Path.cwd()

    scanner = OrgScanner(org=args.org, repo_root=repo_root)

    print(f"\n{'─' * 60}")
    print(f"  haKCAssets Org Sync")
    print(f"  Organization: {args.org}")
    print(f"{'─' * 60}\n")

    if args.list:
        repos = scanner.list_repos()
        print(f"Found {len(repos)} repos:\n")
        for repo in repos:
            desc = repo.get("description", "")[:50]
            print(f"  {repo['name']:<30} {desc}")
        return

    if args.watch:
        scanner.scan_all(specific_repo=args.repo)
        scanner.watch(interval_minutes=args.interval)
        return

    # Regular scan
    scanner.scan_all(specific_repo=args.repo)
    print_summary(scanner)

    if scanner.assets:
        print()
        scanner.sync(dry_run=not args.apply)

        if not args.apply and any(scanner.needs_sync(a) for a in scanner.assets):
            print("\nRun with --apply to download assets.")


if __name__ == "__main__":
    main()
