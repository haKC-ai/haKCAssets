#!/usr/bin/env python3
"""
Artscene MOTD - Index and display random ASCII/NFO art from textfiles.com

Features:
- Indexes http://artscene.textfiles.com/asciiart/NFOS/
- Stores index locally with checksums for change detection
- Resumable downloads (tracks progress)
- Random MOTD display from cached files
- Efficient SQLite storage for fast lookups

Usage:
  python artscene_motd.py              # Show random MOTD
  python artscene_motd.py sync         # Sync/update index
  python artscene_motd.py sync --full  # Force full resync
  python artscene_motd.py list         # List all indexed files
  python artscene_motd.py show <name>  # Show specific file
  python artscene_motd.py stats        # Show index statistics
"""

import sqlite3
import hashlib
import random
import re
import sys
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
from html.parser import HTMLParser
from typing import Optional

BASE_URL = "http://artscene.textfiles.com/asciiart/NFOS/"
ARTSCENE_DIR = Path(__file__).parent
DEFAULT_DB = ARTSCENE_DIR / "index.db"
CACHE_DIR = ARTSCENE_DIR / "cache"


class DirectoryParser(HTMLParser):
    """Parse Apache directory listing for .nfo/.txt files."""

    def __init__(self):
        super().__init__()
        self.files = []
        self.in_link = False
        self.current_href = None

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for name, value in attrs:
                if name == 'href' and value and not value.startswith('?') and not value.startswith('/'):
                    # Filter for NFO/TXT/ASC files
                    if value.lower().endswith(('.nfo', '.txt', '.asc', '.ans')):
                        self.files.append(value)


class ArtsceneIndex:
    """Manages the artscene NFO index."""

    def __init__(self, db_path: Path = DEFAULT_DB, cache_dir: Path = CACHE_DIR):
        self.db_path = db_path
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY,
                    filename TEXT UNIQUE NOT NULL,
                    url TEXT NOT NULL,
                    size INTEGER,
                    checksum TEXT,
                    cached INTEGER DEFAULT 0,
                    last_seen TEXT,
                    added TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sync_state (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    last_sync TEXT,
                    last_full_sync TEXT,
                    files_total INTEGER DEFAULT 0,
                    files_cached INTEGER DEFAULT 0,
                    interrupted INTEGER DEFAULT 0,
                    resume_from TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_cached ON files(cached)
            """)
            # Initialize sync state if not exists
            conn.execute("""
                INSERT OR IGNORE INTO sync_state (id) VALUES (1)
            """)
            conn.commit()

    def _fetch_url(self, url: str, timeout: int = 30) -> Optional[bytes]:
        """Fetch URL content."""
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'haKCAssets/1.0'})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            print(f"  Error fetching {url}: {e}")
            return None

    def _get_remote_listing(self) -> list[str]:
        """Get list of files from remote directory."""
        print(f"  Fetching directory listing from {BASE_URL}...")
        content = self._fetch_url(BASE_URL)
        if not content:
            return []

        parser = DirectoryParser()
        parser.feed(content.decode('utf-8', errors='ignore'))
        return parser.files

    def _get_sync_state(self) -> dict:
        """Get current sync state."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM sync_state WHERE id = 1").fetchone()
            return dict(row) if row else {}

    def _update_sync_state(self, conn=None, **kwargs):
        """Update sync state."""
        close_conn = False
        if conn is None:
            conn = sqlite3.connect(self.db_path)
            close_conn = True

        sets = ", ".join(f"{k} = ?" for k in kwargs.keys())
        conn.execute(f"UPDATE sync_state SET {sets} WHERE id = 1", list(kwargs.values()))
        conn.commit()

        if close_conn:
            conn.close()

    def sync(self, full: bool = False, limit: int = None):
        """Sync index with remote directory."""
        state = self._get_sync_state()

        # Check if we're resuming
        resume_from = state.get('resume_from') if state.get('interrupted') else None
        if resume_from and not full:
            print(f"  Resuming from: {resume_from}")

        print(f"\n{'─' * 50}")
        print("  Artscene NFO Sync")
        print(f"{'─' * 50}\n")

        # Get remote file list
        remote_files = self._get_remote_listing()
        if not remote_files:
            print("  Failed to get remote listing.")
            return

        print(f"  Found {len(remote_files)} files in remote directory\n")

        # Update index
        with sqlite3.connect(self.db_path) as conn:
            now = datetime.now().isoformat()

            # Mark sync as in progress
            self._update_sync_state(conn=conn, interrupted=1)

            # Find resume point
            start_idx = 0
            if resume_from:
                try:
                    start_idx = remote_files.index(resume_from)
                    print(f"  Resuming from index {start_idx}")
                except ValueError:
                    start_idx = 0

            new_files = 0
            updated_files = 0

            files_to_process = remote_files[start_idx:]
            if limit:
                files_to_process = files_to_process[:limit]

            for i, filename in enumerate(files_to_process):
                url = BASE_URL + filename

                # Check if file exists in index
                existing = conn.execute(
                    "SELECT id, checksum FROM files WHERE filename = ?",
                    (filename,)
                ).fetchone()

                if existing:
                    # Update last_seen
                    conn.execute(
                        "UPDATE files SET last_seen = ? WHERE id = ?",
                        (now, existing[0])
                    )
                    updated_files += 1
                else:
                    # New file
                    conn.execute(
                        "INSERT INTO files (filename, url, last_seen) VALUES (?, ?, ?)",
                        (filename, url, now)
                    )
                    new_files += 1

                # Update resume point periodically
                if i % 100 == 0:
                    self._update_sync_state(conn=conn, resume_from=filename)
                    print(f"  Progress: {start_idx + i + 1}/{len(remote_files)} files indexed", end='\r')

            conn.commit()

            # Update totals
            total = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
            cached = conn.execute("SELECT COUNT(*) FROM files WHERE cached = 1").fetchone()[0]

            self._update_sync_state(
                conn=conn,
                last_sync=now,
                files_total=total,
                files_cached=cached,
                interrupted=0,
                resume_from=None
            )

            if full:
                self._update_sync_state(conn=conn, last_full_sync=now)

        print(f"\n  New files: {new_files}")
        print(f"  Updated: {updated_files}")
        print(f"  Total indexed: {total}")
        print(f"  Cached locally: {cached}")

    def cache_file(self, filename: str) -> Optional[str]:
        """Download and cache a file, return content."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT url FROM files WHERE filename = ?",
                (filename,)
            ).fetchone()

            if not row:
                return None

            url = row[0]
            cache_path = self.cache_dir / filename

            # Check if already cached
            if cache_path.exists():
                content = cache_path.read_text(encoding='utf-8', errors='ignore')
                return content

            # Download
            print(f"  Downloading {filename}...")
            data = self._fetch_url(url)
            if not data:
                return None

            content = data.decode('utf-8', errors='ignore')
            checksum = hashlib.md5(data).hexdigest()

            # Save to cache
            cache_path.write_bytes(data)

            # Update DB
            conn.execute(
                "UPDATE files SET cached = 1, checksum = ?, size = ? WHERE filename = ?",
                (checksum, len(data), filename)
            )
            conn.commit()

            # Update cached count
            cached = conn.execute("SELECT COUNT(*) FROM files WHERE cached = 1").fetchone()[0]
            self._update_sync_state(files_cached=cached)

            return content

    def get_random(self, prefer_cached: bool = True) -> Optional[tuple[str, str]]:
        """Get random file (filename, content)."""
        with sqlite3.connect(self.db_path) as conn:
            if prefer_cached:
                # Try cached first
                row = conn.execute(
                    "SELECT filename FROM files WHERE cached = 1 ORDER BY RANDOM() LIMIT 1"
                ).fetchone()

                if row:
                    filename = row[0]
                    cache_path = self.cache_dir / filename
                    if cache_path.exists():
                        return (filename, cache_path.read_text(encoding='utf-8', errors='ignore'))

            # Get any random file and cache it
            row = conn.execute(
                "SELECT filename FROM files ORDER BY RANDOM() LIMIT 1"
            ).fetchone()

            if row:
                filename = row[0]
                content = self.cache_file(filename)
                if content:
                    return (filename, content)

        return None

    def get_file(self, name: str) -> Optional[tuple[str, str]]:
        """Get specific file by name (partial match)."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT filename FROM files WHERE filename LIKE ? LIMIT 1",
                (f"%{name}%",)
            ).fetchone()

            if row:
                filename = row[0]
                content = self.cache_file(filename)
                if content:
                    return (filename, content)

        return None

    def list_files(self, pattern: str = None, cached_only: bool = False) -> list[dict]:
        """List indexed files."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            query = "SELECT filename, size, cached, added FROM files"
            params = []
            conditions = []

            if pattern:
                conditions.append("filename LIKE ?")
                params.append(f"%{pattern}%")

            if cached_only:
                conditions.append("cached = 1")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY filename"

            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def stats(self) -> dict:
        """Get index statistics."""
        with sqlite3.connect(self.db_path) as conn:
            state = self._get_sync_state()

            total = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
            cached = conn.execute("SELECT COUNT(*) FROM files WHERE cached = 1").fetchone()[0]
            total_size = conn.execute("SELECT SUM(size) FROM files WHERE size IS NOT NULL").fetchone()[0] or 0

            return {
                'total_files': total,
                'cached_files': cached,
                'total_size_mb': round(total_size / 1024 / 1024, 2),
                'last_sync': state.get('last_sync'),
                'last_full_sync': state.get('last_full_sync'),
                'interrupted': bool(state.get('interrupted')),
                'resume_from': state.get('resume_from')
            }


def display_motd(content: str, filename: str):
    """Display MOTD with header."""
    width = 80
    print()
    print("=" * width)
    print(f"  MOTD: {filename}")
    print(f"  Source: artscene.textfiles.com/asciiart/NFOS/")
    print("=" * width)
    print()
    print(content)
    print()
    print("=" * width)


def main():
    parser = argparse.ArgumentParser(
        description="Artscene NFO MOTD - Display random ASCII art",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("command", nargs="?", default="motd",
                        choices=["motd", "sync", "list", "show", "stats", "cache-all"],
                        help="Command to run")
    parser.add_argument("name", nargs="?", help="File name for 'show' command")
    parser.add_argument("--full", action="store_true", help="Force full resync")
    parser.add_argument("--limit", type=int, help="Limit files to process")
    parser.add_argument("--cached", action="store_true", help="Only show cached files")
    parser.add_argument("--pattern", "-p", type=str, help="Filter pattern for list")
    parser.add_argument("--db", type=str, help="Database path")

    args = parser.parse_args()

    db_path = Path(args.db) if args.db else DEFAULT_DB
    index = ArtsceneIndex(db_path=db_path)

    if args.command == "sync":
        index.sync(full=args.full, limit=args.limit)

    elif args.command == "list":
        files = index.list_files(pattern=args.pattern, cached_only=args.cached)
        if not files:
            print("No files found. Run 'sync' first.")
            return

        print(f"\n{'─' * 60}")
        print(f"  Indexed Files ({len(files)} total)")
        print(f"{'─' * 60}\n")

        for f in files[:50]:  # Limit display
            cached = "*" if f['cached'] else " "
            size = f"{f['size']:>8}" if f['size'] else "     N/A"
            print(f"  {cached} {f['filename']:<40} {size}")

        if len(files) > 50:
            print(f"\n  ... and {len(files) - 50} more")

    elif args.command == "show":
        if not args.name:
            print("Usage: artscene_motd.py show <filename>")
            return

        result = index.get_file(args.name)
        if result:
            display_motd(result[1], result[0])
        else:
            print(f"File not found: {args.name}")

    elif args.command == "stats":
        stats = index.stats()
        print(f"\n{'─' * 50}")
        print("  Artscene Index Statistics")
        print(f"{'─' * 50}\n")
        print(f"  Total files:     {stats['total_files']}")
        print(f"  Cached locally:  {stats['cached_files']}")
        print(f"  Cache size:      {stats['total_size_mb']} MB")
        print(f"  Last sync:       {stats['last_sync'] or 'Never'}")
        print(f"  Last full sync:  {stats['last_full_sync'] or 'Never'}")
        if stats['interrupted']:
            print(f"  Status:          INTERRUPTED (resume from: {stats['resume_from']})")

    elif args.command == "cache-all":
        files = index.list_files(cached_only=False)
        uncached = [f for f in files if not f['cached']]
        print(f"Caching {len(uncached)} files...")

        for i, f in enumerate(uncached):
            if args.limit and i >= args.limit:
                break
            index.cache_file(f['filename'])
            print(f"  {i+1}/{len(uncached)}: {f['filename']}", end='\r')

        print(f"\nDone.")

    else:  # motd
        stats = index.stats()
        if stats['total_files'] == 0:
            print("No files indexed. Run 'sync' first:")
            print("  python artscene_motd.py sync")
            return

        result = index.get_random()
        if result:
            display_motd(result[1], result[0])
        else:
            print("Failed to get MOTD. Try running 'sync' first.")


if __name__ == "__main__":
    main()
