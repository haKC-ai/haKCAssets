#!/usr/bin/env python3
"""
haKCAssets Manager - Unified asset management for haKC-ai organization

Commands:
  hakc_assets.py organize              # Organize local files in repo root
  hakc_assets.py sync                  # Sync assets from all org repos
  hakc_assets.py watch                 # Watch for changes (local + remote)
  hakc_assets.py status                # Show current state
  hakc_assets.py list-repos            # List all org repos
  hakc_assets.py scan [repo]           # Scan repo(s) for assets
  hakc_assets.py manifest              # Show/rebuild manifests

Options:
  --apply          Actually make changes (default is dry run)
  --interval N     Watch interval in minutes (default: 30)
  --verbose        Show detailed output
"""

import json
import os
import sys
import subprocess
import shutil
import base64
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field, asdict

# ─────────────────────────────────────────────────────────────
#  Configuration
# ─────────────────────────────────────────────────────────────

ASCII_ART_CHARS = set("█▓▒░╔╗╚╝║═│─┌┐└┘├┤┬┴┼╭╮╯╰▀▄▌▐■□▪▫●○◆◇★☆")
ANSI_PATTERN = "\x1b["

# New structure: repos/{type}/{repo}/{file}
ASSET_TYPE_DIRS = {
    "images": "images",
    "media": "media",
    "banners": "banners",
    "icons": "icons",
    "slidedecks": "slidedecks"
}


@dataclass
class AssetEntry:
    """Entry in a manifest."""
    filename: str
    source_repo: str
    source_path: str
    sha: str
    size: int
    synced_at: str
    download_url: str


@dataclass
class Asset:
    """Represents a discovered asset."""
    source: str
    path: str
    name: str
    size: int = 0
    sha: str = ""
    download_url: str = ""
    asset_type: str = "other"
    local_path: Optional[Path] = None
    extracted_content: Optional[str] = None  # For banners extracted from READMEs


@dataclass
class SyncState:
    """Tracks sync state."""
    last_sync: str = ""
    last_organize: str = ""
    assets: dict = field(default_factory=dict)  # "type/repo/file" -> sha


class Manifest:
    """Manages manifest files for asset tracking."""

    def __init__(self, manifest_path: Path):
        self.path = manifest_path
        self.entries: dict[str, AssetEntry] = {}
        self._load()

    def _load(self):
        """Load manifest from file."""
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text())
                for filename, entry_data in data.get("assets", {}).items():
                    self.entries[filename] = AssetEntry(**entry_data)
            except:
                pass

    def save(self):
        """Save manifest to file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "generated": datetime.now().isoformat(),
            "count": len(self.entries),
            "assets": {k: asdict(v) for k, v in self.entries.items()}
        }
        self.path.write_text(json.dumps(data, indent=2))

    def add(self, entry: AssetEntry):
        """Add or update an entry."""
        self.entries[entry.filename] = entry

    def get(self, filename: str) -> Optional[AssetEntry]:
        """Get entry by filename."""
        return self.entries.get(filename)

    def remove(self, filename: str):
        """Remove an entry."""
        self.entries.pop(filename, None)


class HaKCAssets:
    """Main asset manager class."""

    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or Path(__file__).parent.parent
        self.rules_file = self.repo_root / "asset_rules.json"
        self.state_file = self.repo_root / ".sync_state.json"
        self.repos_dir = self.repo_root / "repos"

        self.rules = self._load_rules()
        self.state = self._load_state()
        self.org = self.rules.get("org", "haKC-ai")

        # Manifests cache
        self._manifests: dict[str, Manifest] = {}

    def _load_rules(self) -> dict:
        """Load rules from JSON."""
        if self.rules_file.exists():
            return json.loads(self.rules_file.read_text())
        return {}

    def _load_state(self) -> SyncState:
        """Load sync state."""
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text())
                return SyncState(**data)
            except:
                pass
        return SyncState()

    def _save_state(self):
        """Save sync state."""
        self.state_file.write_text(json.dumps({
            "last_sync": self.state.last_sync,
            "last_organize": self.state.last_organize,
            "assets": self.state.assets
        }, indent=2))

    def _get_manifest(self, asset_type: str) -> Manifest:
        """Get or create manifest for asset type."""
        if asset_type not in self._manifests:
            manifest_path = self.repos_dir / asset_type / "manifest.json"
            self._manifests[asset_type] = Manifest(manifest_path)
        return self._manifests[asset_type]

    def _get_master_manifest_path(self) -> Path:
        """Get path to master manifest."""
        return self.repos_dir / "manifest.json"

    def _run_gh(self, *args) -> Optional[str]:
        """Run gh CLI command."""
        try:
            result = subprocess.run(
                ["gh", *args],
                capture_output=True, text=True, timeout=30
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except Exception:
            return None

    def _get_image_dimensions(self, filepath: Path) -> tuple:
        """Get image dimensions using sips."""
        try:
            result = subprocess.run(
                ["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(filepath)],
                capture_output=True, text=True
            )
            lines = result.stdout.strip().split('\n')
            w = h = 0
            for line in lines:
                if "pixelWidth" in line:
                    w = int(line.split()[-1])
                elif "pixelHeight" in line:
                    h = int(line.split()[-1])
            return (w, h)
        except:
            return (0, 0)

    def _is_square(self, filepath: Path) -> bool:
        """Check if image is square."""
        w, h = self._get_image_dimensions(filepath)
        if w == 0 or h == 0:
            return False
        return 0.9 <= w/h <= 1.1

    def _contains_ascii_art(self, filepath: Path) -> bool:
        """Check for ASCII art."""
        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore')
            return ANSI_PATTERN in content or bool(ASCII_ART_CHARS & set(content))
        except:
            return False

    def _should_ignore(self, filepath: Path) -> bool:
        """Check if file should be ignored."""
        name = filepath.name
        for pattern in self.rules.get("ignore", []):
            if pattern.startswith("*.") and name.endswith(pattern[1:]):
                return True
            if name == pattern:
                return True
        return False

    def _is_ascii_art(self, text: str) -> bool:
        """Check if text contains ASCII art characters."""
        if not text:
            return False
        return ANSI_PATTERN in text or bool(ASCII_ART_CHARS & set(text))

    def _extract_banners_from_readme(self, content: str, repo: str) -> list:
        """Extract ASCII banners from README code blocks."""
        import re
        banners = []

        # Match code blocks: ```...``` or indented blocks with ASCII art
        # Pattern for fenced code blocks (``` or ~~~)
        fenced_pattern = r'```[^\n]*\n(.*?)```'

        matches = re.findall(fenced_pattern, content, re.DOTALL)

        banner_num = 0
        for match in matches:
            block = match.strip()
            # Check if this block contains ASCII art
            if self._is_ascii_art(block) and len(block) > 20:
                # Skip blocks that look like code (contain common programming patterns)
                code_indicators = ['import ', 'def ', 'class ', 'function ', 'const ', 'let ', 'var ',
                                   'return ', 'if (', 'for (', '#!/', 'pip ', 'npm ', 'git ', 'python ',
                                   '$ ', '# Install', 'brew ', 'cargo ']
                if any(indicator in block for indicator in code_indicators):
                    continue

                banner_num += 1
                banners.append({
                    'content': block,
                    'name': f"readme_banner{'_' + str(banner_num) if banner_num > 1 else ''}.txt"
                })

        return banners

    def _get_asset_type(self, filepath: Path, content: str = None) -> str:
        """Determine asset type."""
        if self._should_ignore(filepath):
            return "other"

        ext = filepath.suffix.lower()
        name = filepath.stem.lower()

        # Icons detection
        if "icon" in name and ext in [".png", ".jpg", ".svg", ".ico"]:
            return "icons"

        # Media detection (videos)
        if ext in [".mp4", ".webm", ".mov", ".m4v"]:
            return "media"

        # Banner/ASCII detection
        if ext in [".txt", ".ans", ".asc", ".nfo", ""]:
            if any(p in name for p in ["banner", "ascii", "logo"]):
                return "banners"
            if content and any(c in content for c in "█▓▒░"):
                return "banners"
            return "other"

        # Images
        if ext in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"]:
            return "images"

        # Slidedecks (PDFs)
        if ext in [".pdf"]:
            return "slidedecks"

        return "other"

    def _match_rule(self, filepath: Path, rule: dict) -> bool:
        """Check if file matches a rule."""
        match = rule.get("match", {})
        ext = filepath.suffix.lower()

        if "extensions" in match and ext not in match["extensions"]:
            return False

        if "aspect_ratio" in match:
            if match["aspect_ratio"] == "square" and not self._is_square(filepath):
                return False

        if "max_dimension" in match:
            w, h = self._get_image_dimensions(filepath)
            if max(w, h) > match["max_dimension"]:
                return False

        if "name_contains" in match:
            name = filepath.stem.lower()
            if not any(p.lower() in name for p in match["name_contains"]):
                return False

        if "content_contains" in match:
            if not self._contains_ascii_art(filepath):
                return False

        return True

    def get_destination(self, filepath: Path) -> Optional[str]:
        """Get destination directory for a file."""
        if self._should_ignore(filepath):
            return None

        rules = sorted(self.rules.get("rules", []), key=lambda r: r.get("priority", 99))

        for rule in rules:
            if self._match_rule(filepath, rule):
                return rule.get("destination")

        return None

    # ─────────────────────────────────────────────────────────
    #  Local Organization
    # ─────────────────────────────────────────────────────────

    def get_root_files(self) -> list:
        """Get files in repo root."""
        files = []
        for item in self.repo_root.iterdir():
            if item.is_file() and not self._should_ignore(item):
                files.append(item)
        return files

    def organize(self, dry_run: bool = True, interactive: bool = False) -> list:
        """Organize files in repo root."""
        moves = []

        for filepath in self.get_root_files():
            dest_dir = self.get_destination(filepath)
            if dest_dir:
                dest_path = self.repo_root / dest_dir / filepath.name

                if interactive:
                    resp = input(f"Move {filepath.name} → {dest_dir}/? [y/N] ").strip().lower()
                    if resp != 'y':
                        continue

                if dry_run:
                    print(f"  Would move: {filepath.name} → {dest_dir}/")
                else:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(filepath), str(dest_path))
                    print(f"  Moved: {filepath.name} → {dest_dir}/")

                moves.append((filepath, dest_path))

        if not dry_run:
            self.state.last_organize = datetime.now().isoformat()
            self._save_state()

        return moves

    # ─────────────────────────────────────────────────────────
    #  Remote Sync (New Structure: repos/{type}/{repo}/{file})
    # ─────────────────────────────────────────────────────────

    def list_repos(self) -> list:
        """List org repos."""
        output = self._run_gh("repo", "list", self.org, "--json", "name,description,updatedAt", "--limit", "100")
        return json.loads(output) if output else []

    def scan_repo_contents(self, repo: str, path: str = "") -> list:
        """Get repo contents."""
        endpoint = f"repos/{self.org}/{repo}/contents/{path}".rstrip("/")
        output = self._run_gh("api", endpoint)
        if not output:
            return []
        try:
            items = json.loads(output)
            return [items] if isinstance(items, dict) else items
        except:
            return []

    def scan_repo(self, repo: str) -> list:
        """Scan repo for assets."""
        assets = []
        sync_config = self.rules.get("sync", {})
        source_dirs = sync_config.get("source_dirs", [])
        exclude = sync_config.get("exclude_repos", [])

        if repo in exclude:
            return []

        root_items = self.scan_repo_contents(repo)

        # Find asset directories and README files
        dirs_to_scan = []
        readme_item = None

        for item in root_items:
            name = item.get("name", "")
            if item.get("type") == "dir" and name.lower() in source_dirs:
                dirs_to_scan.append(name)
            elif item.get("type") == "file":
                # Check for README files to extract banners
                if name.lower() in ["readme.md", "readme.txt", "readme"]:
                    readme_item = item

                asset_type = self._get_asset_type(Path(name))
                if asset_type != "other":
                    assets.append(Asset(
                        source=repo, path=name, name=name,
                        size=item.get("size", 0),
                        sha=item.get("sha", ""),
                        download_url=item.get("download_url", ""),
                        asset_type=asset_type
                    ))

        # Extract banners from README
        if readme_item:
            readme_path = readme_item.get("path", readme_item.get("name", ""))
            content_data = self._run_gh("api", f"repos/{self.org}/{repo}/contents/{readme_path}")
            if content_data:
                try:
                    data = json.loads(content_data)
                    if data.get("encoding") == "base64":
                        readme_content = base64.b64decode(data.get("content", "")).decode("utf-8", errors="ignore")
                        banners = self._extract_banners_from_readme(readme_content, repo)
                        for banner in banners:
                            # Create a virtual asset for the extracted banner
                            assets.append(Asset(
                                source=repo,
                                path=f"README.md#{banner['name']}",
                                name=banner['name'],
                                size=len(banner['content']),
                                sha=readme_item.get("sha", "") + f"_{banner['name']}",
                                download_url="",  # No direct URL, content is extracted
                                asset_type="banners",
                                extracted_content=banner['content']
                            ))
                except:
                    pass

        # Scan asset directories
        for dir_name in dirs_to_scan:
            for item in self.scan_repo_contents(repo, dir_name):
                if item.get("type") == "file":
                    name = item.get("name", "")
                    path = item.get("path", "")

                    # Check content for text files
                    content = None
                    if Path(name).suffix.lower() in [".txt", ""] and item.get("size", 0) < 50000:
                        content_data = self._run_gh("api", f"repos/{self.org}/{repo}/contents/{path}")
                        if content_data:
                            try:
                                data = json.loads(content_data)
                                if data.get("encoding") == "base64":
                                    content = base64.b64decode(data.get("content", "")).decode("utf-8", errors="ignore")
                            except:
                                pass

                    asset_type = self._get_asset_type(Path(name), content)
                    if asset_type != "other":
                        assets.append(Asset(
                            source=repo, path=path, name=name,
                            size=item.get("size", 0),
                            sha=item.get("sha", ""),
                            download_url=item.get("download_url", ""),
                            asset_type=asset_type
                        ))

        return assets

    def scan_all_repos(self, specific_repo: str = None) -> list:
        """Scan all repos."""
        assets = []
        repos = [{"name": specific_repo}] if specific_repo else self.list_repos()

        print(f"Scanning {len(repos)} repo(s)...\n")

        for repo_info in repos:
            repo = repo_info["name"]
            if repo == "haKCAssets":
                continue

            print(f"  {repo}...", end=" ", flush=True)
            repo_assets = self.scan_repo(repo)
            assets.extend(repo_assets)
            print(f"{len(repo_assets)} asset(s)")

        return assets

    def get_sync_path(self, asset: Asset) -> Path:
        """Get local path: repos/{type}/{repo}/{file}"""
        return self.repos_dir / asset.asset_type / asset.source / asset.name

    def get_asset_key(self, asset: Asset) -> str:
        """Get unique key for state tracking."""
        return f"{asset.asset_type}/{asset.source}/{asset.name}"

    def needs_sync(self, asset: Asset) -> bool:
        """Check if asset needs syncing."""
        local = self.get_sync_path(asset)
        if not local.exists():
            return True

        key = self.get_asset_key(asset)
        return self.state.assets.get(key) != asset.sha

    def download_asset(self, asset: Asset) -> bool:
        """Download asset and update manifest."""
        local = self.get_sync_path(asset)
        local.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Handle extracted content (e.g., banners from READMEs)
            if asset.extracted_content:
                local.write_text(asset.extracted_content, encoding='utf-8')
                success = True
            else:
                # Normal download via curl
                result = subprocess.run(
                    ["curl", "-sL", "-o", str(local), asset.download_url],
                    capture_output=True, timeout=120
                )
                success = result.returncode == 0 and local.exists()

            if success:
                # Update state
                key = self.get_asset_key(asset)
                self.state.assets[key] = asset.sha

                # Update type manifest
                manifest = self._get_manifest(asset.asset_type)
                manifest.add(AssetEntry(
                    filename=asset.name,
                    source_repo=asset.source,
                    source_path=asset.path,
                    sha=asset.sha,
                    size=asset.size,
                    synced_at=datetime.now().isoformat(),
                    download_url=asset.download_url or "(extracted from README)"
                ))

                return True
        except Exception as e:
            print(f"    Error: {e}")
        return False

    def sync(self, assets: list, dry_run: bool = True) -> list:
        """Sync assets."""
        to_sync = [a for a in assets if self.needs_sync(a)]

        if not to_sync:
            print("\nAll assets up to date.")
            return []

        print(f"\n{len(to_sync)} asset(s) to sync:\n")

        synced = []
        for asset in to_sync:
            local = self.get_sync_path(asset)
            action = "new" if not local.exists() else "update"

            if dry_run:
                print(f"  [{action}] {asset.asset_type}/{asset.source}/{asset.name}")
            else:
                print(f"  Syncing {asset.source}/{asset.name}...", end=" ", flush=True)
                if self.download_asset(asset):
                    print("done")
                    synced.append(asset)
                else:
                    print("FAILED")

        if not dry_run and synced:
            # Save all manifests
            for manifest in self._manifests.values():
                manifest.save()

            # Update master manifest
            self._build_master_manifest()

            self.state.last_sync = datetime.now().isoformat()
            self._save_state()

        return synced

    def _build_master_manifest(self):
        """Build master manifest from all type manifests."""
        master = {
            "generated": datetime.now().isoformat(),
            "organization": self.org,
            "types": {},
            "by_repo": {},
            "total_assets": 0
        }

        # Scan all type directories
        if self.repos_dir.exists():
            for type_dir in self.repos_dir.iterdir():
                if type_dir.is_dir() and type_dir.name != ".git":
                    manifest_path = type_dir / "manifest.json"
                    if manifest_path.exists():
                        try:
                            data = json.loads(manifest_path.read_text())
                            type_name = type_dir.name
                            master["types"][type_name] = {
                                "count": data.get("count", 0),
                                "repos": {}
                            }

                            for filename, entry in data.get("assets", {}).items():
                                repo = entry.get("source_repo", "unknown")
                                if repo not in master["types"][type_name]["repos"]:
                                    master["types"][type_name]["repos"][repo] = []
                                master["types"][type_name]["repos"][repo].append(filename)

                                # Also build by_repo index
                                if repo not in master["by_repo"]:
                                    master["by_repo"][repo] = {}
                                if type_name not in master["by_repo"][repo]:
                                    master["by_repo"][repo][type_name] = []
                                master["by_repo"][repo][type_name].append(filename)

                                master["total_assets"] += 1
                        except:
                            pass

        self._get_master_manifest_path().write_text(json.dumps(master, indent=2))

    # ─────────────────────────────────────────────────────────
    #  Watch Mode
    # ─────────────────────────────────────────────────────────

    def watch(self, interval: int = 30):
        """Watch for changes."""
        print(f"Watching every {interval} minutes. Ctrl+C to stop.\n")

        try:
            while True:
                now = datetime.now().strftime('%H:%M:%S')
                print(f"\n[{now}] Checking...")

                # Check local files
                root_files = self.get_root_files()
                if root_files:
                    print(f"  Found {len(root_files)} local file(s) to organize")
                    self.organize(dry_run=False)

                # Check remote repos
                assets = self.scan_all_repos()
                synced = self.sync(assets, dry_run=False)
                if synced:
                    print(f"  Synced {len(synced)} asset(s)")

                print(f"  Next check in {interval} minutes...")
                time.sleep(interval * 60)

        except KeyboardInterrupt:
            print("\nStopped.")

    # ─────────────────────────────────────────────────────────
    #  Status & Manifests
    # ─────────────────────────────────────────────────────────

    def status(self):
        """Show current status."""
        print(f"\n{'─' * 50}")
        print("  haKCAssets Status")
        print(f"{'─' * 50}\n")

        print(f"  Organization: {self.org}")
        print(f"  Repo root: {self.repo_root}")
        print(f"  Last sync: {self.state.last_sync or 'Never'}")
        print(f"  Last organize: {self.state.last_organize or 'Never'}")

        # Count local assets
        counts = {}
        for dir_name in ["art", "avatars", "banners", "tools"]:
            dir_path = self.repo_root / dir_name
            if dir_path.exists():
                count = sum(1 for f in dir_path.rglob("*") if f.is_file())
                if count:
                    counts[dir_name] = count

        if counts:
            print(f"\n  Local assets:")
            for d, c in sorted(counts.items()):
                print(f"    {d}/: {c} file(s)")

        # Count synced assets by type
        if self.repos_dir.exists():
            print(f"\n  Synced assets (repos/):")
            for type_dir in sorted(self.repos_dir.iterdir()):
                if type_dir.is_dir() and type_dir.name not in [".git", "manifest.json"]:
                    count = sum(1 for f in type_dir.rglob("*") if f.is_file() and f.name != "manifest.json")
                    if count:
                        repos = [d.name for d in type_dir.iterdir() if d.is_dir()]
                        print(f"    {type_dir.name}/: {count} file(s) from {len(repos)} repo(s)")

        # Check for files to organize
        root_files = self.get_root_files()
        if root_files:
            print(f"\n  Pending: {len(root_files)} file(s) in root to organize")

    def show_manifest(self, asset_type: str = None):
        """Show manifest contents."""
        if asset_type:
            manifest_path = self.repos_dir / asset_type / "manifest.json"
            if manifest_path.exists():
                data = json.loads(manifest_path.read_text())
                print(f"\n{asset_type}/ manifest ({data.get('count', 0)} assets):\n")
                for filename, entry in data.get("assets", {}).items():
                    print(f"  {entry['source_repo']}/{filename}")
            else:
                print(f"No manifest for {asset_type}/")
        else:
            # Show master manifest
            master_path = self._get_master_manifest_path()
            if master_path.exists():
                data = json.loads(master_path.read_text())
                print(f"\nMaster Manifest ({data.get('total_assets', 0)} total assets):\n")

                for type_name, type_data in data.get("types", {}).items():
                    print(f"  {type_name}/: {type_data.get('count', 0)} assets")
                    for repo, files in type_data.get("repos", {}).items():
                        print(f"    └─ {repo}: {len(files)} file(s)")
            else:
                print("No master manifest. Run sync first.")


def main():
    parser = argparse.ArgumentParser(
        description="haKCAssets Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  organize      Organize local files in repo root
  sync          Sync assets from org repos
  watch         Watch for changes continuously
  status        Show current status
  list-repos    List all org repos
  scan          Scan repo(s) for assets
  manifest      Show manifest contents
        """
    )
    parser.add_argument("command", nargs="?", default="status",
                        choices=["organize", "sync", "watch", "status", "list-repos", "scan", "manifest"])
    parser.add_argument("--apply", action="store_true", help="Actually make changes")
    parser.add_argument("--interactive", "-i", action="store_true", help="Ask before changes")
    parser.add_argument("--interval", type=int, default=30, help="Watch interval (minutes)")
    parser.add_argument("--repo", type=str, help="Specific repo to scan")
    parser.add_argument("--type", type=str, help="Asset type for manifest command")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Find repo root
    repo_root = Path(__file__).parent.parent
    if not (repo_root / "asset_rules.json").exists():
        repo_root = Path.cwd()

    manager = HaKCAssets(repo_root)

    print(f"\n{'─' * 50}")
    print("  haKCAssets Manager")
    print(f"{'─' * 50}")

    if args.command == "status":
        manager.status()

    elif args.command == "organize":
        print("\nOrganizing local files...\n")
        moves = manager.organize(dry_run=not args.apply, interactive=args.interactive)
        if moves and not args.apply:
            print("\nRun with --apply to move files.")

    elif args.command == "sync":
        print(f"\nSyncing from {manager.org}...\n")
        assets = manager.scan_all_repos(specific_repo=args.repo)
        manager.sync(assets, dry_run=not args.apply)
        if not args.apply:
            print("\nRun with --apply to download assets.")

    elif args.command == "watch":
        manager.watch(interval=args.interval)

    elif args.command == "list-repos":
        repos = manager.list_repos()
        print(f"\n{len(repos)} repos in {manager.org}:\n")
        for r in repos:
            desc = (r.get("description") or "")[:40]
            print(f"  {r['name']:<35} {desc}")

    elif args.command == "scan":
        assets = manager.scan_all_repos(specific_repo=args.repo)
        print(f"\nFound {len(assets)} asset(s):\n")

        by_type = {}
        for a in assets:
            by_type.setdefault(a.asset_type, []).append(a)

        for asset_type, type_assets in sorted(by_type.items()):
            print(f"  {asset_type}/: {len(type_assets)}")
            if args.verbose:
                by_repo = {}
                for a in type_assets:
                    by_repo.setdefault(a.source, []).append(a)
                for repo, repo_assets in sorted(by_repo.items()):
                    print(f"    └─ {repo}: {len(repo_assets)}")

    elif args.command == "manifest":
        manager.show_manifest(asset_type=args.type)


if __name__ == "__main__":
    main()
