#!/usr/bin/env python3
"""
haKCAssets Organizer - Automatically organize assets based on ruleset

Usage:
  python tools/organize.py                 # Dry run (show what would happen)
  python tools/organize.py --apply         # Actually move files
  python tools/organize.py --check         # Check for misplaced files (extension-based)
  python tools/organize.py --check --strict # Check using full ruleset
  python tools/organize.py --interactive   # Ask before each move
"""

import json
import os
import sys
import shutil
import argparse
from pathlib import Path
from typing import Optional

# ASCII art detection characters
ASCII_ART_CHARS = set("█▓▒░╔╗╚╝║═│─┌┐└┘├┤┬┴┼╭╮╯╰▀▄▌▐■□▪▫●○◆◇★☆")

# ANSI escape detection
ANSI_PATTERN = "\x1b["


class AssetOrganizer:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.rules_file = repo_root / "asset_rules.json"
        self.rules = self._load_rules()

    def _load_rules(self) -> dict:
        """Load rules from JSON file."""
        if not self.rules_file.exists():
            print(f"Error: {self.rules_file} not found")
            sys.exit(1)
        with open(self.rules_file) as f:
            return json.load(f)

    def _get_image_dimensions(self, filepath: Path) -> tuple[int, int]:
        """Get image dimensions using sips (macOS) or file inspection."""
        try:
            import subprocess
            result = subprocess.run(
                ["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(filepath)],
                capture_output=True, text=True
            )
            lines = result.stdout.strip().split('\n')
            width = height = 0
            for line in lines:
                if "pixelWidth" in line:
                    width = int(line.split()[-1])
                elif "pixelHeight" in line:
                    height = int(line.split()[-1])
            return (width, height)
        except Exception:
            return (0, 0)

    def _is_square(self, filepath: Path) -> bool:
        """Check if image is square (1:1 aspect ratio)."""
        w, h = self._get_image_dimensions(filepath)
        if w == 0 or h == 0:
            return False
        ratio = w / h
        return 0.9 <= ratio <= 1.1  # Allow 10% tolerance

    def _get_max_dimension(self, filepath: Path) -> int:
        """Get the larger dimension of an image."""
        w, h = self._get_image_dimensions(filepath)
        return max(w, h)

    def _contains_ascii_art(self, filepath: Path) -> bool:
        """Check if text file contains ASCII/ANSI art characters."""
        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore')
            # Check for ANSI escapes
            if ANSI_PATTERN in content:
                return True
            # Check for ASCII art characters
            return bool(ASCII_ART_CHARS & set(content))
        except Exception:
            return False

    def _name_contains(self, filepath: Path, patterns: list[str]) -> bool:
        """Check if filename contains any of the patterns."""
        name_lower = filepath.stem.lower()
        return any(p.lower() in name_lower for p in patterns)

    def _should_ignore(self, filepath: Path) -> bool:
        """Check if file should be ignored."""
        name = filepath.name
        for pattern in self.rules.get("ignore", []):
            if pattern.startswith("*."):
                if name.endswith(pattern[1:]):
                    return True
            elif name == pattern or str(filepath.relative_to(self.repo_root)).startswith(pattern):
                return True
        return False

    def _match_rule(self, filepath: Path, rule: dict) -> bool:
        """Check if a file matches a rule."""
        match = rule.get("match", {})
        ext = filepath.suffix.lower()

        # Check extension
        if "extensions" in match:
            if ext not in match["extensions"]:
                return False

        # Check aspect ratio
        if "aspect_ratio" in match:
            if match["aspect_ratio"] == "square" and not self._is_square(filepath):
                return False

        # Check max dimension
        if "max_dimension" in match:
            if self._get_max_dimension(filepath) > match["max_dimension"]:
                return False

        # Check name contains
        if "name_contains" in match:
            if not self._name_contains(filepath, match["name_contains"]):
                return False

        # Check content contains (for text files)
        if "content_contains" in match:
            if not self._contains_ascii_art(filepath):
                return False

        return True

    def get_destination(self, filepath: Path) -> Optional[str]:
        """Determine destination directory for a file based on rules."""
        if self._should_ignore(filepath):
            return None

        # Sort rules by priority
        sorted_rules = sorted(self.rules.get("rules", []), key=lambda r: r.get("priority", 99))

        for rule in sorted_rules:
            if self._match_rule(filepath, rule):
                return rule.get("destination")

        return None

    def get_root_files(self) -> list[Path]:
        """Get all files in repo root (not in subdirectories)."""
        files = []
        for item in self.repo_root.iterdir():
            if item.is_file() and not self._should_ignore(item):
                files.append(item)
        return files

    def check_misplaced(self, strict: bool = False) -> list[tuple[Path, str, str]]:
        """Check for files that might be in the wrong directory.

        In normal mode, only checks if file extension matches directory purpose.
        In strict mode, re-runs all rules to suggest better placement.
        """
        misplaced = []

        for dir_name, dir_info in self.rules.get("directories", {}).items():
            dir_path = self.repo_root / dir_name
            if not dir_path.exists():
                continue

            allowed_exts = dir_info.get("extensions", [])

            for filepath in dir_path.iterdir():
                if filepath.is_file() and not self._should_ignore(filepath):
                    ext = filepath.suffix.lower()

                    if strict:
                        # Re-run all rules to check placement
                        suggested = self.get_destination(filepath)
                        if suggested and suggested != dir_name:
                            misplaced.append((filepath, dir_name, suggested))
                    else:
                        # Just check if extension is valid for this directory
                        if allowed_exts and ext not in allowed_exts:
                            # Find where it should go
                            suggested = self.get_destination(filepath)
                            if suggested:
                                misplaced.append((filepath, dir_name, suggested))

        return misplaced

    def organize(self, dry_run: bool = True, interactive: bool = False) -> list[tuple[Path, Path]]:
        """Organize files in repo root to appropriate directories."""
        moves = []

        for filepath in self.get_root_files():
            dest_dir = self.get_destination(filepath)
            if dest_dir:
                dest_path = self.repo_root / dest_dir / filepath.name

                if interactive:
                    response = input(f"Move {filepath.name} → {dest_dir}/? [y/N] ").strip().lower()
                    if response != 'y':
                        print(f"  Skipped: {filepath.name}")
                        continue

                if dry_run:
                    print(f"  Would move: {filepath.name} → {dest_dir}/")
                else:
                    # Create directory if needed
                    dest_path.parent.mkdir(exist_ok=True)
                    shutil.move(str(filepath), str(dest_path))
                    print(f"  Moved: {filepath.name} → {dest_dir}/")

                moves.append((filepath, dest_path))

        return moves


def main():
    parser = argparse.ArgumentParser(description="Organize haKCAssets repository")
    parser.add_argument("--apply", action="store_true", help="Actually move files (default is dry run)")
    parser.add_argument("--check", action="store_true", help="Check for misplaced files in subdirectories")
    parser.add_argument("--strict", action="store_true", help="Strict mode: re-run all rules on existing files")
    parser.add_argument("--interactive", "-i", action="store_true", help="Ask before each move")
    args = parser.parse_args()

    # Find repo root (where asset_rules.json is)
    repo_root = Path(__file__).parent.parent
    if not (repo_root / "asset_rules.json").exists():
        repo_root = Path.cwd()

    organizer = AssetOrganizer(repo_root)

    print(f"\n{'─' * 50}")
    print("  haKCAssets Organizer")
    print(f"{'─' * 50}\n")

    if args.check:
        mode = "strict" if args.strict else "normal"
        print(f"Checking for misplaced files ({mode} mode)...\n")
        misplaced = organizer.check_misplaced(strict=args.strict)
        if misplaced:
            print("Potentially misplaced files:")
            for filepath, current, suggested in misplaced:
                print(f"  {filepath.name}: {current}/ → {suggested}/?")
        else:
            print("All files appear to be in correct directories.")
        return

    root_files = organizer.get_root_files()

    if not root_files:
        print("No files to organize in repo root.")
        return

    print(f"Found {len(root_files)} file(s) in repo root:\n")

    if args.apply:
        print("Organizing files...\n")
        moves = organizer.organize(dry_run=False, interactive=args.interactive)
        print(f"\nMoved {len(moves)} file(s).")
    elif args.interactive:
        print("Interactive mode...\n")
        moves = organizer.organize(dry_run=False, interactive=True)
        print(f"\nMoved {len(moves)} file(s).")
    else:
        print("Dry run (use --apply to actually move files):\n")
        moves = organizer.organize(dry_run=True)
        if moves:
            print(f"\nWould move {len(moves)} file(s). Run with --apply to execute.")
        else:
            print("No files matched any rules.")


if __name__ == "__main__":
    main()
