#!/usr/bin/env python3
"""
haKC Menu Generator - Generate ASCII menu templates for CLI tools
The Pinnacle of Hakcing Quality

Usage:
  hakc_menu.py --name "MyTool" --options "Start,Config,Help,Quit"
  hakc_menu.py --name "MyTool" --style warez
  hakc_menu.py --interactive

Styles:
  warez    - Classic NFO/warez scene style (default)
  minimal  - Clean, simple menus
  bbs      - BBS era style
  modern   - Contemporary look

signed, /dev/haKCØRY.23
"""

import argparse
import sys
from pathlib import Path

# Add parent to path for lib import
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib import BOX, text_to_big, center_lines, random_decoration, get_signature


def generate_warez_menu(name: str, options: list[str], width: int = 60) -> str:
    """Generate warez-style menu."""
    lines = []

    lines.append("╔" + "═" * (width - 2) + "╗")
    lines.append("║" + f" {name} ".center(width - 2, "═") + "║")
    lines.append("╠" + "═" * (width - 2) + "╣")
    lines.append("║" + "".center(width - 2) + "║")

    for i, opt in enumerate(options, 1):
        key = str(i) if i < 10 else chr(ord('A') + i - 10)
        line = f"  [{key}] {opt}"
        lines.append("║" + line.ljust(width - 2) + "║")

    lines.append("║" + "".center(width - 2) + "║")
    lines.append("║" + "  [Q] Quit".ljust(width - 2) + "║")
    lines.append("║" + "".center(width - 2) + "║")
    lines.append("║" + "─" * (width - 4).center(width - 2) + "║")
    lines.append("║" + "  Select option: _".ljust(width - 2) + "║")
    lines.append("╚" + "═" * (width - 2) + "╝")
    lines.append("")

    return "\n".join(lines)


def generate_minimal_menu(name: str, options: list[str], width: int = 40) -> str:
    """Generate minimal-style menu."""
    lines = []

    lines.append("┌" + "─" * (width - 2) + "┐")
    lines.append("│" + name.center(width - 2) + "│")
    lines.append("├" + "─" * (width - 2) + "┤")

    for i, opt in enumerate(options, 1):
        line = f"  {i}. {opt}"
        lines.append("│" + line.ljust(width - 2) + "│")

    lines.append("│" + "".center(width - 2) + "│")
    lines.append("│" + "  q. Quit".ljust(width - 2) + "│")
    lines.append("└" + "─" * (width - 2) + "┘")
    lines.append("")

    return "\n".join(lines)


def generate_bbs_menu(name: str, options: list[str], width: int = 60) -> str:
    """Generate BBS-style menu."""
    lines = []

    lines.append("╔" + "═" * (width - 2) + "╗")
    lines.append("║" + f" ◄ {name} MENU ► ".center(width - 2, "═") + "║")
    lines.append("╠" + "═" * (width - 2) + "╣")
    lines.append("║" + "".center(width - 2) + "║")

    for i, opt in enumerate(options, 1):
        line = f"  <{i}> {opt}"
        lines.append("║" + line.ljust(width - 2) + "║")

    lines.append("║" + "".center(width - 2) + "║")
    lines.append("║" + "  <X> eXit to Main".ljust(width - 2) + "║")
    lines.append("║" + "".center(width - 2) + "║")
    lines.append("╟" + "─" * (width - 2) + "╢")
    lines.append("║" + "  Your choice? _".ljust(width - 2) + "║")
    lines.append("╚" + "═" * (width - 2) + "╝")
    lines.append("")

    return "\n".join(lines)


def generate_modern_menu(name: str, options: list[str], width: int = 50) -> str:
    """Generate modern-style menu."""
    lines = []

    lines.append("┏" + "━" * (width - 2) + "┓")
    lines.append("┃" + name.center(width - 2) + "┃")
    lines.append("┣" + "━" * (width - 2) + "┫")
    lines.append("┃" + "".center(width - 2) + "┃")

    for i, opt in enumerate(options, 1):
        line = f"  → {i}  {opt}"
        lines.append("┃" + line.ljust(width - 2) + "┃")

    lines.append("┃" + "".center(width - 2) + "┃")
    lines.append("┃" + "  → q  Exit".ljust(width - 2) + "┃")
    lines.append("┃" + "".center(width - 2) + "┃")
    lines.append("┗" + "━" * (width - 2) + "┛")
    lines.append("")

    return "\n".join(lines)


def generate_submenu(name: str, options: list[str], parent: str = "Main", style: str = "warez") -> str:
    """Generate a submenu with back option."""
    if style == "warez":
        menu = generate_warez_menu(name, options)
        # Replace quit with back
        menu = menu.replace("[Q] Quit", f"[B] Back to {parent}")
    elif style == "bbs":
        menu = generate_bbs_menu(name, options)
        menu = menu.replace("<X> eXit to Main", f"<B> Back to {parent}")
    else:
        menu = generate_minimal_menu(name, options) if style == "minimal" else generate_modern_menu(name, options)
        menu = menu.replace("q. Quit", f"b. Back to {parent}").replace("q  Exit", f"b  Back to {parent}")

    return menu


GENERATORS = {
    "warez": generate_warez_menu,
    "minimal": generate_minimal_menu,
    "bbs": generate_bbs_menu,
    "modern": generate_modern_menu,
}


def interactive_mode():
    """Interactive menu generation wizard."""
    print("\n" + "=" * 60)
    print("  haKC Menu Generator - Interactive Mode")
    print("  The Pinnacle of Hakcing Quality")
    print("=" * 60 + "\n")

    name = input("  Menu name: ").strip()
    if not name:
        name = "Main Menu"

    print("  Enter menu options (comma-separated):")
    options_str = input("  Options: ").strip()
    if not options_str:
        options = ["Start", "Settings", "Help", "About"]
    else:
        options = [o.strip() for o in options_str.split(",")]

    print("\n  Available styles:")
    print("    1. warez    - Classic NFO/warez scene style")
    print("    2. minimal  - Clean, simple menus")
    print("    3. bbs      - BBS era style")
    print("    4. modern   - Contemporary look")

    style_choice = input("\n  Style [1]: ").strip()
    styles = {"1": "warez", "2": "minimal", "3": "bbs", "4": "modern"}
    style = styles.get(style_choice, "warez")

    generator = GENERATORS.get(style, generate_warez_menu)
    menu = generator(name, options)

    print("\n" + "=" * 60 + "\n")
    print(menu)

    save = input("  Save to file? [y/N]: ").strip().lower()
    if save == "y":
        filename = input(f"  Filename [menu.txt]: ").strip()
        if not filename:
            filename = "menu.txt"

        with open(filename, "w") as f:
            f.write(menu)
        print(f"  Saved to: {filename}")

    print("\n  ───── ▓ signed, /dev/haKCØRY.23: ▓ ─────\n")


def main():
    parser = argparse.ArgumentParser(
        description="haKC Menu Generator - The Pinnacle of Hakcing Quality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Styles:
  warez     - Classic NFO/warez scene style (default)
  minimal   - Clean, simple menus
  bbs       - BBS era style
  modern    - Contemporary look

Examples:
  hakc_menu.py --name "MyTool" --options "Start,Config,Help"
  hakc_menu.py --name "Settings" --style bbs
  hakc_menu.py --interactive

signed, /dev/haKCØRY.23
        """,
    )

    parser.add_argument("--name", "-n", help="Menu name/title")
    parser.add_argument("--options", "-O", help="Comma-separated menu options")
    parser.add_argument(
        "--style", "-s",
        choices=["warez", "minimal", "bbs", "modern"],
        default="warez",
        help="Menu style",
    )
    parser.add_argument("--width", "-w", type=int, default=60, help="Menu width")
    parser.add_argument("--output", "-o", help="Save to file")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--submenu", action="store_true", help="Generate as submenu (with Back option)")
    parser.add_argument("--parent", "-p", default="Main", help="Parent menu name (for submenu)")

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        return

    if not args.name:
        print("Error: --name is required (or use --interactive)")
        parser.print_help()
        return

    # Parse options
    if args.options:
        options = [o.strip() for o in args.options.split(",")]
    else:
        options = ["Option 1", "Option 2", "Option 3"]

    # Generate menu
    if args.submenu:
        menu = generate_submenu(args.name, options, args.parent, args.style)
    else:
        generator = GENERATORS.get(args.style, generate_warez_menu)
        menu = generator(args.name, options, args.width)

    print(menu)

    if args.output:
        with open(args.output, "w") as f:
            f.write(menu)
        print(f"\n  Saved to: {args.output}")


if __name__ == "__main__":
    main()
