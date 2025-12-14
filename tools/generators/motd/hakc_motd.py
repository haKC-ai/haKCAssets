#!/usr/bin/env python3
"""
haKC MOTD Manager - Message of the Day in true BBS style
The Pinnacle of Hakcing Quality

Usage:
  hakc_motd.py              # Random MOTD
  hakc_motd.py --daily      # Daily MOTD (same for the whole day)
  hakc_motd.py --greet      # Random greet
  hakc_motd.py --fu         # Random FU to lamerz
  hakc_motd.py --sig        # Random signature
  hakc_motd.py --full       # Full MOTD with greet + message + sig
  hakc_motd.py --add "msg"  # Add a new MOTD to the JSON
  hakc_motd.py --list       # List all MOTDs
  hakc_motd.py --json       # Output as JSON for scripting
  hakc_motd.py --ansi       # Add ANSI color styling

signed, /dev/haKCØRY.23
"""

import argparse
import json
import random
import sys
from datetime import datetime
from pathlib import Path

# Find the MOTD JSON relative to this script
SCRIPT_DIR = Path(__file__).parent
MOTD_FILE = SCRIPT_DIR / "motd.json"

# ANSI color codes for that retro vibe
COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "cyan": "\033[36m",
    "magenta": "\033[35m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "red": "\033[31m",
    "white": "\033[37m",
}

GRADIENTS = [
    ["cyan", "blue", "magenta"],
    ["green", "cyan", "blue"],
    ["magenta", "red", "yellow"],
    ["yellow", "green", "cyan"],
]


def load_motd_data() -> dict:
    """Load the MOTD JSON file."""
    if not MOTD_FILE.exists():
        return {
            "version": "1.0",
            "motd": ["Welcome to haKC.ai - MOTD file not found!"],
            "categories": {"greets": [], "fus": [], "signatures": []},
        }

    with open(MOTD_FILE, "r") as f:
        return json.load(f)


def save_motd_data(data: dict):
    """Save the MOTD JSON file."""
    with open(MOTD_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_daily_seed() -> int:
    """Get a seed based on today's date for consistent daily MOTD."""
    today = datetime.now().strftime("%Y-%m-%d")
    return hash(today) & 0xFFFFFFFF


def colorize(text: str, use_ansi: bool = True) -> str:
    """Apply ANSI coloring to text."""
    if not use_ansi:
        return text

    gradient = random.choice(GRADIENTS)
    result = []

    for i, char in enumerate(text):
        if char.strip():
            color = gradient[i % len(gradient)]
            result.append(f"{COLORS[color]}{char}")
        else:
            result.append(char)

    return "".join(result) + COLORS["reset"]


def format_box(text: str, use_ansi: bool = True) -> str:
    """Format text in a stylized box."""
    width = max(len(line) for line in text.split("\n")) + 4

    top = "╔" + "═" * width + "╗"
    bottom = "╚" + "═" * width + "╝"

    lines = []
    lines.append(top)
    for line in text.split("\n"):
        padding = width - len(line)
        lines.append(f"║  {line}{' ' * padding}║")
    lines.append(bottom)

    result = "\n".join(lines)

    if use_ansi:
        return f"{COLORS['cyan']}{result}{COLORS['reset']}"
    return result


def get_random_motd(data: dict, daily: bool = False) -> str:
    """Get a random MOTD."""
    motds = data.get("motd", ["No MOTDs found!"])

    if daily:
        random.seed(get_daily_seed())

    return random.choice(motds)


def get_random_greet(data: dict) -> str:
    """Get a random greet."""
    greets = data.get("categories", {}).get("greets", ["GR33TZ!"])
    return random.choice(greets)


def get_random_fu(data: dict) -> str:
    """Get a random FU to lamerz."""
    fus = data.get("categories", {}).get("fus", ["FU to nobody today."])
    return random.choice(fus)


def get_random_sig(data: dict) -> str:
    """Get a random signature."""
    sigs = data.get("categories", {}).get("signatures", ["- haKC.ai"])
    return random.choice(sigs)


def get_full_motd(data: dict, use_ansi: bool = True) -> str:
    """Get a full MOTD with greet, message, and signature."""
    parts = []

    # Header
    header = "THE PINNACLE OF HAKCING QUALITY"
    if use_ansi:
        header = f"{COLORS['bold']}{COLORS['magenta']}{header}{COLORS['reset']}"
    parts.append(header)
    parts.append("")

    # Greet
    greet = get_random_greet(data)
    if use_ansi:
        greet = f"{COLORS['green']}{greet}{COLORS['reset']}"
    parts.append(greet)
    parts.append("")

    # Main MOTD
    motd = get_random_motd(data)
    if use_ansi:
        motd = f"{COLORS['cyan']}{motd}{COLORS['reset']}"
    parts.append(motd)
    parts.append("")

    # FU (50% chance)
    if random.random() > 0.5:
        fu = get_random_fu(data)
        if use_ansi:
            fu = f"{COLORS['red']}{fu}{COLORS['reset']}"
        parts.append(fu)
        parts.append("")

    # Signature
    sig = get_random_sig(data)
    if use_ansi:
        sig = f"{COLORS['dim']}{sig}{COLORS['reset']}"
    parts.append(sig)

    return "\n".join(parts)


def add_motd(data: dict, message: str) -> bool:
    """Add a new MOTD to the JSON."""
    if message in data.get("motd", []):
        return False

    if "motd" not in data:
        data["motd"] = []

    data["motd"].append(message)
    save_motd_data(data)
    return True


def list_motds(data: dict, use_ansi: bool = True) -> str:
    """List all MOTDs."""
    motds = data.get("motd", [])
    lines = [f"=== haKC MOTDs ({len(motds)} total) ===", ""]

    for i, motd in enumerate(motds, 1):
        prefix = f"[{i:3d}] "
        if use_ansi:
            prefix = f"{COLORS['cyan']}{prefix}{COLORS['reset']}"
        lines.append(f"{prefix}{motd}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="haKC MOTD Manager - The Pinnacle of Hakcing Quality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  hakc_motd.py                  # Random MOTD
  hakc_motd.py --full --ansi    # Full styled MOTD
  hakc_motd.py --add "Your message here"

signed, /dev/haKCØRY.23
        """,
    )

    parser.add_argument("--daily", action="store_true", help="Get the daily MOTD (consistent for the day)")
    parser.add_argument("--greet", action="store_true", help="Get a random greet")
    parser.add_argument("--fu", action="store_true", help="Get a random FU to lamerz")
    parser.add_argument("--sig", action="store_true", help="Get a random signature")
    parser.add_argument("--full", action="store_true", help="Get full MOTD with greet + message + sig")
    parser.add_argument("--add", metavar="MSG", help="Add a new MOTD message")
    parser.add_argument("--list", action="store_true", help="List all MOTDs")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--ansi", action="store_true", help="Add ANSI color styling")
    parser.add_argument("--box", action="store_true", help="Display in a box")
    parser.add_argument("--count", action="store_true", help="Show MOTD count")

    args = parser.parse_args()

    data = load_motd_data()
    use_ansi = args.ansi

    if args.count:
        count = len(data.get("motd", []))
        print(f"{count} MOTDs loaded")
        return

    if args.add:
        if add_motd(data, args.add):
            print(f"Added: {args.add}")
        else:
            print("MOTD already exists!")
            sys.exit(1)
        return

    if args.list:
        print(list_motds(data, use_ansi))
        return

    # Get the appropriate output
    if args.full:
        output = get_full_motd(data, use_ansi)
    elif args.greet:
        output = get_random_greet(data)
        if use_ansi:
            output = colorize(output)
    elif args.fu:
        output = get_random_fu(data)
        if use_ansi:
            output = f"{COLORS['red']}{output}{COLORS['reset']}"
    elif args.sig:
        output = get_random_sig(data)
        if use_ansi:
            output = f"{COLORS['dim']}{output}{COLORS['reset']}"
    else:
        output = get_random_motd(data, daily=args.daily)
        if use_ansi:
            output = colorize(output)

    # Format output
    if args.json:
        print(json.dumps({"motd": output}))
    elif args.box:
        print(format_box(output, use_ansi))
    else:
        print(output)


if __name__ == "__main__":
    main()
