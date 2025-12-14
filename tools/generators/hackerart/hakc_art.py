#!/usr/bin/env python3
"""
haKC Art Generator - Generate ASCII art inspired by your banners and the artscene
The Pinnacle of Hakcing Quality

This generator:
1. Reads your existing banners from haKCAssets for style/vibe
2. Pulls inspiration from the artscene NFO index
3. Generates new ASCII art based on user input

Usage:
  hakc_art.py "MyProject"                    # Generate art for project
  hakc_art.py "MyProject" --style warez      # Specific style
  hakc_art.py --random                       # Random art from NFO collection
  hakc_art.py --inspire                      # Show inspiring art samples
  hakc_art.py --interactive                  # Interactive mode
  hakc_art.py --nfo                          # Show the full NFO banner
  hakc_art.py --nfo --animate                # Animated sparkle NFO banner
  hakc_art.py --nfo --typing                 # NFO with typing effect

signed, /dev/haKCØRY.23
"""

import argparse
import json
import os
import random
import sqlite3
import sys
from pathlib import Path
from typing import Optional

# Paths
SCRIPT_DIR = Path(__file__).parent
HAKC_ASSETS = SCRIPT_DIR.parent.parent.parent  # tools/generators/hackerart -> haKCAssets
BANNERS_DIR = HAKC_ASSETS / "banners"
ARTSCENE_DB = HAKC_ASSETS / "tools" / "artscene" / "index.db"
ARTSCENE_CACHE = HAKC_ASSETS / "tools" / "artscene" / "cache"

# Box drawing characters
BOX = {
    "single": {"tl": "┌", "tr": "┐", "bl": "└", "br": "┘", "h": "─", "v": "│"},
    "double": {"tl": "╔", "tr": "╗", "bl": "╚", "br": "╝", "h": "═", "v": "║"},
    "round": {"tl": "╭", "tr": "╮", "bl": "╰", "br": "╯", "h": "─", "v": "│"},
    "heavy": {"tl": "┏", "tr": "┓", "bl": "┗", "br": "┛", "h": "━", "v": "┃"},
}

# Decorative elements extracted from haKC banners
DECORATIONS = {
    "dividers": [
        "*~'`^`'~*-,._.,-*~'`^`'~*-,._.,-*~'`^`'~*-,._.,-*~'`^`'~*",
        "═══════════════════════════════════════════════════════════",
        "───────────────────────────────────────────────────────────",
        "·∙∙·▫▫ᵒᴼᵒ▫ₒₒ▫ᵒᴼ¯`·.¸¸.·´¯`·.¸¸.·`¯ᴼᵒ▫ₒₒ▫ᵒᴼᵒ▫▫·∙∙",
        "▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓",
        ".:/=================================================================\\:.",
    ],
    "corners": ["/\\", "\\/", "◆", "◇", "★", "✧", "✦"],
    "blocks": ["█", "▓", "▒", "░", "▄", "▀", "▌", "▐"],
    "lines": ["│", "║", "┃", "─", "═", "━"],
}

# Simple blocky letters (3 lines high)
SIMPLE_LETTERS = {
    "A": ["▄▀▄", "█▀█", "▀ ▀"],
    "B": ["█▀▄", "█▀▄", "▀▀ "],
    "C": ["▄▀▀", "█  ", "▀▀▀"],
    "D": ["█▀▄", "█ █", "▀▀ "],
    "E": ["█▀▀", "█▀▀", "▀▀▀"],
    "F": ["█▀▀", "█▀ ", "▀  "],
    "G": ["▄▀▀", "█ █", "▀▀▀"],
    "H": ["█ █", "█▀█", "▀ ▀"],
    "I": ["▀█▀", " █ ", "▀▀▀"],
    "J": [" ▀█", "  █", "▀▀ "],
    "K": ["█ █", "█▀▄", "▀ ▀"],
    "L": ["█  ", "█  ", "▀▀▀"],
    "M": ["█▄█", "█▀█", "▀ ▀"],
    "N": ["█▀█", "█ █", "▀ ▀"],
    "O": ["▄▀▄", "█ █", "▀▀▀"],
    "P": ["█▀▄", "█▀ ", "▀  "],
    "Q": ["▄▀▄", "█ █", "▀▀▄"],
    "R": ["█▀▄", "█▀▄", "▀ ▀"],
    "S": ["▄▀▀", "▀▀▄", "▀▀ "],
    "T": ["▀█▀", " █ ", " ▀ "],
    "U": ["█ █", "█ █", "▀▀▀"],
    "V": ["█ █", "█ █", " ▀ "],
    "W": ["█ █", "█▄█", "▀ ▀"],
    "X": ["▀▄▀", " █ ", "▀ ▀"],
    "Y": ["█ █", " █ ", " ▀ "],
    "Z": ["▀▀█", " █ ", "▀▀▀"],
    "0": ["▄▀▄", "█ █", "▀▀▀"],
    "1": ["▄█ ", " █ ", "▀▀▀"],
    "2": ["▀▀▄", " █ ", "▀▀▀"],
    "3": ["▀▀▄", " ▀▄", "▀▀ "],
    "4": ["█ █", "▀▀█", "  ▀"],
    "5": ["█▀▀", "▀▀▄", "▀▀ "],
    "6": ["▄▀ ", "█▀▄", "▀▀ "],
    "7": ["▀▀█", "  █", "  ▀"],
    "8": ["▄▀▄", "▄▀▄", "▀▀▀"],
    "9": ["▄▀▄", "▀▀█", "▀▀ "],
    " ": ["   ", "   ", "   "],
    "-": ["   ", "▀▀▀", "   "],
    ".": ["  ", "  ", "▄ "],
    "_": ["   ", "   ", "▀▀▀"],
    ":": [" ", "▄", "▄"],
}

# haKC-style greets and phrases
HAKC_GREETS = [
    "GR33TZ: SecKC, CoWTownComputerCongress, ACiD, iCE, T$A, badge lords",
    "SHOUTZ: 14.4k Modem Jammers, MUD survivors, ANSI artists",
    "Big ups to everyone who still reads NFO files for fun.",
    "Greets to the real ones who know what a .diz file is.",
    "RESPECT: BBS sysops who kept the lights on.",
]

HAKC_SIGNATURES = [
    "───── ▓ signed, /dev/haKCØRY.23: ▓ ─────",
    "- /dev/CØR.23",
    "[ haKC.ai - The Pinnacle of Hakcing Quality ]",
    "*~'`^`'~*-,._.,-*~ haKC.ai ~*-,._.,-*~'`^`'~*",
    "< cory@haKC.ai | Drop a line on any fine BBS >",
]

HAKC_TAGLINES = [
    "THE PINNACLE OF HAKCING QUALITY",
    "nano > vim. come fight us.",
    "If your editor auto wraps lines, bounce now.",
    "FU to lamerz still using WordPad.",
    "Connection: 14.4k BLAZING FAST",
]


def text_to_art(text: str) -> list[str]:
    """Convert text to blocky ASCII art (3 lines high)."""
    text = text.upper()
    result = ["", "", ""]

    for char in text:
        if char in SIMPLE_LETTERS:
            for i, line in enumerate(SIMPLE_LETTERS[char]):
                result[i] += line
        else:
            for i in range(3):
                result[i] += " "

    return result


def center_text(lines: list[str], width: int = 70) -> list[str]:
    """Center lines within a width."""
    result = []
    for line in lines:
        pad = max(0, (width - len(line)) // 2)
        result.append(" " * pad + line)
    return result


def make_box(content: list[str], style: str = "double", width: int = 0) -> list[str]:
    """Wrap content in a box."""
    b = BOX.get(style, BOX["double"])
    if width == 0:
        width = max(len(line) for line in content) + 4

    result = []
    result.append(b["tl"] + b["h"] * (width - 2) + b["tr"])

    for line in content:
        pad_right = width - len(line) - 4
        result.append(f"{b['v']}  {line}{' ' * pad_right}  {b['v']}")

    result.append(b["bl"] + b["h"] * (width - 2) + b["br"])
    return result


def load_banner_vibes() -> dict:
    """Load existing banners to extract style/vibe patterns."""
    vibes = {
        "headers": [],
        "footers": [],
        "dividers": [],
        "patterns": [],
    }

    if not BANNERS_DIR.exists():
        return vibes

    for banner_file in BANNERS_DIR.glob("**/*.txt"):
        try:
            content = banner_file.read_text(errors="ignore")
            lines = content.split("\n")

            # Extract patterns
            for line in lines:
                # Headers typically have lots of blocks
                if line.count("█") > 5:
                    vibes["headers"].append(line)
                # Dividers are long lines of repeated chars
                elif len(line) > 30 and len(set(line.strip())) <= 5:
                    vibes["dividers"].append(line.strip())
                # Signatures
                elif "signed" in line.lower() or "/dev/" in line:
                    vibes["footers"].append(line.strip())

        except Exception:
            pass

    return vibes


def get_random_nfo() -> Optional[str]:
    """Get a random NFO from the artscene index."""
    if not ARTSCENE_DB.exists():
        return None

    try:
        conn = sqlite3.connect(ARTSCENE_DB)
        cursor = conn.cursor()

        # Get random file that's been downloaded
        cursor.execute(
            "SELECT filename FROM files WHERE downloaded = 1 ORDER BY RANDOM() LIMIT 1"
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            cache_path = ARTSCENE_CACHE / row[0]
            if cache_path.exists():
                return cache_path.read_text(errors="ignore")

    except Exception:
        pass

    return None


def get_nfo_by_pattern(pattern: str) -> list[str]:
    """Search NFOs by pattern."""
    results = []

    if not ARTSCENE_DB.exists():
        return results

    try:
        conn = sqlite3.connect(ARTSCENE_DB)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT filename FROM files WHERE downloaded = 1 AND filename LIKE ?",
            (f"%{pattern}%",),
        )
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            cache_path = ARTSCENE_CACHE / row[0]
            if cache_path.exists():
                results.append(cache_path.read_text(errors="ignore"))

    except Exception:
        pass

    return results


def generate_warez_art(name: str, tagline: str = "", include_greets: bool = True) -> str:
    """Generate warez-style ASCII art."""
    width = 70
    lines = []

    # Header with blocks
    lines.append("")
    lines.append(" " * 16 + "██████████")
    lines.append(" " * 15 + "█▓       ░██")

    # Tagline or default
    tag = tagline or random.choice(HAKC_TAGLINES)
    lines.append(" " * 15 + f"█▒        ██ {tag}")
    lines.append("    █████████████░        █████████████████ ████████████")

    # Big text
    big_text = text_to_art(name)
    lines.append("")
    lines.extend(center_text(big_text, width))
    lines.append("")

    # Divider
    lines.append(random.choice(DECORATIONS["dividers"]))
    lines.append("")

    # Greets
    if include_greets:
        lines.append("        " + random.choice(HAKC_GREETS))
        lines.append("")

    # Signature
    lines.append("                    " + random.choice(HAKC_SIGNATURES))
    lines.append("")

    return "\n".join(lines)


def generate_minimal_art(name: str) -> str:
    """Generate minimal ASCII art."""
    big_text = text_to_art(name)
    boxed = make_box(big_text, "round")
    return "\n".join(center_text(boxed, 60)) + "\n"


def generate_cyberpunk_art(name: str, status: str = "ONLINE") -> str:
    """Generate cyberpunk-style art."""
    width = 70
    lines = []

    # Glitch header
    lines.append("▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓")
    lines.append("")

    # Big text
    big_text = text_to_art(name)
    lines.extend(center_text(big_text, width))

    lines.append("")
    lines.append("▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓")
    lines.append("")

    # Status box
    lines.append("    ╔═══════════════════════════════════════════════════════╗")
    lines.append(f"    ║  SYSTEM: {name.upper().ljust(47)}║")
    lines.append(f"    ║  STATUS: {status.ljust(47)}║")
    lines.append("    ╚═══════════════════════════════════════════════════════╝")
    lines.append("")

    return "\n".join(lines)


def generate_bbs_art(name: str, sysop: str = "haKCer") -> str:
    """Generate BBS-style art."""
    width = 58
    lines = []

    lines.append("╔" + "═" * (width - 2) + "╗")
    lines.append("║" + f" {name} BBS ".center(width - 2, "═") + "║")
    lines.append("╠" + "═" * (width - 2) + "╣")
    lines.append("║" + "".center(width - 2) + "║")
    lines.append("║" + "WELCOME, CALLER!".center(width - 2) + "║")
    lines.append("║" + "".center(width - 2) + "║")
    lines.append("║" + f"  SysOp: {sysop}".ljust(width - 2) + "║")
    lines.append("║" + "  Connection: 14.4k BLAZING FAST".ljust(width - 2) + "║")
    lines.append("║" + "".center(width - 2) + "║")
    lines.append("╚" + "═" * (width - 2) + "╝")
    lines.append("")

    return "\n".join(lines)


def show_inspiration():
    """Show inspiring art from NFO collection and haKC banners."""
    print("\n" + "=" * 60)
    print("  haKC Art Inspiration - Samples from the scene")
    print("=" * 60 + "\n")

    # Load haKC banner vibes
    vibes = load_banner_vibes()

    if vibes["headers"]:
        print("=== haKC HEADERS ===\n")
        for header in vibes["headers"][:3]:
            print(header)
        print()

    if vibes["dividers"]:
        print("=== haKC DIVIDERS ===\n")
        for div in vibes["dividers"][:5]:
            print(div)
        print()

    # Show random NFO
    nfo = get_random_nfo()
    if nfo:
        print("=== RANDOM NFO FROM ARTSCENE ===\n")
        # Show first 30 lines
        for line in nfo.split("\n")[:30]:
            print(line)
        print("\n[...truncated...]\n")
    else:
        print("  (artscene index not available - run artscene/motd.py --sync first)\n")


def interactive_mode():
    """Interactive art generation wizard."""
    print("\n" + "=" * 60)
    print("  haKC Art Generator - Interactive Mode")
    print("  The Pinnacle of Hakcing Quality")
    print("=" * 60 + "\n")

    name = input("  What to generate art for: ").strip()
    if not name:
        name = "haKC"

    print("\n  Available styles:")
    print("    1. warez    - Classic NFO/warez scene style")
    print("    2. minimal  - Clean, simple ASCII art")
    print("    3. cyberpunk - Futuristic/synthwave vibes")
    print("    4. bbs      - BBS era nostalgia")

    style_choice = input("\n  Style [1]: ").strip()
    styles = {"1": "warez", "2": "minimal", "3": "cyberpunk", "4": "bbs"}
    style = styles.get(style_choice, "warez")

    print("\n" + "=" * 60 + "\n")

    if style == "warez":
        print(generate_warez_art(name))
    elif style == "minimal":
        print(generate_minimal_art(name))
    elif style == "cyberpunk":
        print(generate_cyberpunk_art(name))
    else:
        print(generate_bbs_art(name))

    # Offer to save
    save = input("  Save to file? [y/N]: ").strip().lower()
    if save == "y":
        filename = input(f"  Filename [{name.lower()}_art.txt]: ").strip()
        if not filename:
            filename = f"{name.lower()}_art.txt"

        with open(filename, "w") as f:
            if style == "warez":
                f.write(generate_warez_art(name))
            elif style == "minimal":
                f.write(generate_minimal_art(name))
            elif style == "cyberpunk":
                f.write(generate_cyberpunk_art(name))
            else:
                f.write(generate_bbs_art(name))

        print(f"  Saved to: {filename}")

    print("\n  ───── ▓ signed, /dev/haKCØRY.23: ▓ ─────\n")


def main():
    parser = argparse.ArgumentParser(
        description="haKC Art Generator - The Pinnacle of Hakcing Quality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Styles:
  warez     - Classic NFO/warez scene style (default)
  minimal   - Clean, simple ASCII art
  cyberpunk - Futuristic/synthwave vibes
  bbs       - BBS era nostalgia

Examples:
  hakc_art.py "MyProject"
  hakc_art.py "CoolTool" --style cyberpunk
  hakc_art.py --inspire
  hakc_art.py --random
  hakc_art.py --interactive

signed, /dev/haKCØRY.23
        """,
    )

    parser.add_argument("name", nargs="?", help="Name to generate art for")
    parser.add_argument(
        "--style", "-s",
        choices=["warez", "minimal", "cyberpunk", "bbs"],
        default="warez",
        help="Art style",
    )
    parser.add_argument("--tagline", "-t", help="Custom tagline")
    parser.add_argument("--output", "-o", help="Save to file")
    parser.add_argument("--random", "-r", action="store_true", help="Show random NFO from artscene")
    parser.add_argument("--inspire", action="store_true", help="Show inspiring art samples")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--no-greets", action="store_true", help="Skip greets section")
    parser.add_argument("--nfo", action="store_true", help="Show full haKC NFO banner")
    parser.add_argument("--animate", "-a", action="store_true", help="Enable sparkle animation (with --nfo)")
    parser.add_argument("--typing", action="store_true", help="Enable typing effect (with --nfo)")
    parser.add_argument("--frames", "-f", type=int, default=100, help="Animation frames (default: 100)")

    args = parser.parse_args()

    # NFO banner mode (uses nfo_effects module)
    if args.nfo:
        try:
            from nfo_effects import animate_sparkles, print_static, print_with_typing, clear_screen
            clear_screen()
            if args.animate:
                try:
                    animate_sparkles(iterations=args.frames)
                except KeyboardInterrupt:
                    pass
                finally:
                    clear_screen()
                    print_static()
            elif args.typing:
                print_with_typing()
            else:
                print_static()
        except ImportError:
            print("Error: nfo_effects.py not found in hackerart directory")
        return

    if args.inspire:
        show_inspiration()
        return

    if args.random:
        nfo = get_random_nfo()
        if nfo:
            print(nfo)
        else:
            print("No NFOs cached. Run: python artscene/motd.py --sync")
        return

    if args.interactive:
        interactive_mode()
        return

    if not args.name:
        print("Error: name required (or use --interactive)")
        parser.print_help()
        return

    # Generate art
    if args.style == "warez":
        art = generate_warez_art(args.name, args.tagline or "", not args.no_greets)
    elif args.style == "minimal":
        art = generate_minimal_art(args.name)
    elif args.style == "cyberpunk":
        art = generate_cyberpunk_art(args.name)
    else:
        art = generate_bbs_art(args.name)

    print(art)

    if args.output:
        with open(args.output, "w") as f:
            f.write(art)
        print(f"\n  Saved to: {args.output}")


if __name__ == "__main__":
    main()
