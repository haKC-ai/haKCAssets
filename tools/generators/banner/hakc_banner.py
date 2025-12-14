#!/usr/bin/env python3
"""
haKC Project Assets Generator - Generate banners, menus, and ASCII art for your projects
The Pinnacle of Hakcing Quality

Usage:
  hakc_banner.py --name "MyProject" --org "haKC-ai"
  hakc_banner.py --name "MyProject" --style warez
  hakc_banner.py --template banner_withvariables.txt    # Use template with {motd}, {greets}, etc.
  hakc_banner.py --template banner_withvariables.txt --output my_banner.txt
  hakc_banner.py --interactive

Styles:
  warez    - Classic NFO/warez scene style (default)
  minimal  - Clean, simple ASCII banners
  cyberpunk - Futuristic/synthwave vibes
  retro    - BBS era nostalgia
  modern   - Contemporary ASCII art

Template Variables (from motd.json):
  {motd}       - Random message of the day
  {greets}     - Random greets line
  {fus}        - Random FU line
  {signatures} - Random signature

signed, /dev/haKCØRY.23
"""

import argparse
import json
import random
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

# Script directory for relative imports
SCRIPT_DIR = Path(__file__).parent
MOTD_FILE = SCRIPT_DIR.parent / "motd" / "motd.json"

# Cache for MOTD data
_motd_data = None


def load_motd_data() -> dict:
    """Load MOTD data from motd.json."""
    global _motd_data
    if _motd_data is None:
        if MOTD_FILE.exists():
            _motd_data = json.loads(MOTD_FILE.read_text())
        else:
            # Fallback if motd.json not found
            _motd_data = {
                "motd": ["Welcome to haKC.ai - The Pinnacle of Hakcing Quality"],
                "categories": {
                    "greets": ["GR33TZ: SecKC, ACiD, iCE, badge lords"],
                    "fus": ["FU to lamerz who can't handle the ASCII"],
                    "signatures": ["───── ▓ signed, /dev/haKCØRY.23: ▓ ─────"],
                }
            }
    return _motd_data


def get_random_motd() -> str:
    """Get a random MOTD message."""
    data = load_motd_data()
    return random.choice(data.get("motd", ["Welcome to haKC.ai"]))


def get_random_greets() -> str:
    """Get a random greets line."""
    data = load_motd_data()
    return random.choice(data.get("categories", {}).get("greets", ["GR33TZ: haKC crew"]))


def get_random_fus() -> str:
    """Get a random FU line."""
    data = load_motd_data()
    return random.choice(data.get("categories", {}).get("fus", ["FU to lamerz"]))


def get_random_signature() -> str:
    """Get a random signature."""
    data = load_motd_data()
    return random.choice(data.get("categories", {}).get("signatures", ["- haKC.ai"]))


def render_template(template_path: Path, variables: Optional[dict] = None) -> str:
    """
    Render a template file with variables from motd.json.

    Supported variables:
      {motd}       - Random message of the day
      {greets}     - Random greets line
      {fus}        - Random FU line
      {signatures} - Random signature

    You can also pass custom variables dict to override.
    """
    template = template_path.read_text()

    # Default variable getters
    var_getters = {
        "motd": get_random_motd,
        "greets": get_random_greets,
        "fus": get_random_fus,
        "signatures": get_random_signature,
    }

    # Find all {variable} patterns
    pattern = r'\{(\w+)\}'

    def replace_var(match):
        var_name = match.group(1)
        # Check custom variables first
        if variables and var_name in variables:
            return variables[var_name]
        # Then check our getters
        if var_name in var_getters:
            return var_getters[var_name]()
        # Leave unknown variables as-is
        return match.group(0)

    return re.sub(pattern, replace_var, template)


def render_template_all_variants(template_path: Path, count: int = 5) -> list[str]:
    """
    Render multiple variants of a template with different random values.
    Useful for generating multiple banner options.
    """
    return [render_template(template_path) for _ in range(count)]


# Box drawing characters
BOX = {
    "single": {"tl": "┌", "tr": "┐", "bl": "└", "br": "┘", "h": "─", "v": "│"},
    "double": {"tl": "╔", "tr": "╗", "bl": "╚", "br": "╝", "h": "═", "v": "║"},
    "round": {"tl": "╭", "tr": "╮", "bl": "╰", "br": "╯", "h": "─", "v": "│"},
    "heavy": {"tl": "┏", "tr": "┓", "bl": "┗", "br": "┛", "h": "━", "v": "┃"},
    "ascii": {"tl": "+", "tr": "+", "bl": "+", "br": "+", "h": "-", "v": "|"},
}

# Decorative elements
DECORATIONS = {
    "stars": ["★", "✧", "✦", "·", "∙", "◦", "◆", "◇"],
    "arrows": ["/\\", "\\/", ">>", "<<", "->", "<-", "═>", "<="],
    "lines": [
        "*~'`^`'~*-,._.,-*~'`^`'~*-,._.,-*~'`^`'~*",
        "═══════════════════════════════════════════",
        "───────────────────────────────────────────",
        "·∙∙·▫▫ᵒᴼᵒ▫ₒₒ▫ᵒᴼ¯`·.¸¸.·´¯`·.¸¸.·`¯ᴼᵒ▫ₒₒ▫ᵒᴼᵒ▫▫·∙∙",
        "▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓",
    ],
    "blocks": ["█", "▓", "▒", "░"],
}

# Big text alphabet using ASCII art
BIG_LETTERS = {
    "A": ["  ▄▄  ", " █  █ ", " ████ ", " █  █ ", " █  █ "],
    "B": [" ███▄ ", " █  █ ", " ███▄ ", " █  █ ", " ███▀ "],
    "C": [" ▄███ ", " █    ", " █    ", " █    ", " ▀███ "],
    "D": [" ███▄ ", " █  █ ", " █  █ ", " █  █ ", " ███▀ "],
    "E": [" ████ ", " █    ", " ███  ", " █    ", " ████ "],
    "F": [" ████ ", " █    ", " ███  ", " █    ", " █    "],
    "G": [" ▄███ ", " █    ", " █ ██ ", " █  █ ", " ▀███ "],
    "H": [" █  █ ", " █  █ ", " ████ ", " █  █ ", " █  █ "],
    "I": [" ███ ", "  █  ", "  █  ", "  █  ", " ███ "],
    "J": ["  ███ ", "   █  ", "   █  ", " █ █  ", " ▀█▀  "],
    "K": [" █ ▄█ ", " █▀█  ", " ██   ", " █▀█  ", " █ ▀█ "],
    "L": [" █    ", " █    ", " █    ", " █    ", " ████ "],
    "M": [" █▄▄█ ", " █▀▀█ ", " █  █ ", " █  █ ", " █  █ "],
    "N": [" █▄ █ ", " █▀██ ", " █ ▀█ ", " █  █ ", " █  █ "],
    "O": [" ▄██▄ ", " █  █ ", " █  █ ", " █  █ ", " ▀██▀ "],
    "P": [" ███▄ ", " █  █ ", " ███▀ ", " █    ", " █    "],
    "Q": [" ▄██▄ ", " █  █ ", " █  █ ", " █ ▀█ ", " ▀██▄ "],
    "R": [" ███▄ ", " █  █ ", " ███▀ ", " █▀█  ", " █ ▀█ "],
    "S": [" ▄███ ", " █    ", " ▀██▄ ", "   █  ", " ███▀ "],
    "T": [" ████ ", "  █   ", "  █   ", "  █   ", "  █   "],
    "U": [" █  █ ", " █  █ ", " █  █ ", " █  █ ", " ▀██▀ "],
    "V": [" █  █ ", " █  █ ", " █  █ ", " ▀▄▄▀ ", "  ▀▀  "],
    "W": [" █  █ ", " █  █ ", " █  █ ", " █▄▄█ ", " █▀▀█ "],
    "X": [" █  █ ", " ▀▄▄▀ ", "  ██  ", " ▄▀▀▄ ", " █  █ "],
    "Y": [" █  █ ", " ▀▄▄▀ ", "  █   ", "  █   ", "  █   "],
    "Z": [" ████ ", "   █▀ ", "  █▀  ", " █▀   ", " ████ "],
    " ": ["      ", "      ", "      ", "      ", "      "],
    "-": ["      ", "      ", " ──── ", "      ", "      "],
    ".": ["    ", "    ", "    ", "    ", " ▄  "],
    "_": ["      ", "      ", "      ", "      ", " ──── "],
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
    " ": ["   ", "   ", "   "],
    "-": ["   ", "▀▀▀", "   "],
    ".": ["  ", "  ", "▄ "],
    "_": ["   ", "   ", "▀▀▀"],
}


def text_to_big(text: str, style: str = "big") -> list[str]:
    """Convert text to big ASCII art letters."""
    text = text.upper()
    letters = BIG_LETTERS if style == "big" else SIMPLE_LETTERS
    height = 5 if style == "big" else 3

    result = [""] * height

    for char in text:
        if char in letters:
            for i, line in enumerate(letters[char]):
                result[i] += line
        else:
            for i in range(height):
                result[i] += " "

    return result


def make_box(content: list[str], style: str = "double", padding: int = 2) -> list[str]:
    """Wrap content in a box."""
    b = BOX.get(style, BOX["double"])
    width = max(len(line) for line in content) + padding * 2

    result = []
    result.append(b["tl"] + b["h"] * width + b["tr"])

    for line in content:
        pad_right = width - len(line) - padding
        result.append(f"{b['v']}{' ' * padding}{line}{' ' * pad_right}{b['v']}")

    result.append(b["bl"] + b["h"] * width + b["br"])

    return result


def center_lines(lines: list[str], width: int = 80) -> list[str]:
    """Center a list of lines within a width."""
    result = []
    for line in lines:
        pad = (width - len(line)) // 2
        result.append(" " * pad + line)
    return result


def generate_warez_banner(
    name: str,
    org: str = "haKC.ai",
    tagline: str = "THE PINNACLE OF HAKCING QUALITY",
    author: str = "/dev/haKCØRY.23",
) -> str:
    """Generate a classic warez scene NFO-style banner."""
    width = 80

    lines = []

    # Top decoration
    lines.append("")
    lines.append(" " * 16 + "██████████")
    lines.append(" " * 15 + "█▓       ░██")
    lines.append(" " * 15 + f"█▒        ██ {tagline}")
    lines.append("    █████████████░        █████████████████ ████████████ ████████████")

    # Big text name
    big_name = text_to_big(name, "simple")
    lines.append("")
    for bl in center_lines(big_name, width):
        lines.append(bl)
    lines.append("")

    # Divider
    lines.append(".:/=" + "=" * 68 + "=\\:.")
    lines.append("")

    # Info section
    lines.append(f"        Name: {name.ljust(45)}")
    lines.append(f"        Org:  {org.ljust(45)}")
    lines.append(f"        Date: {datetime.now().strftime('%Y-%m-%d').ljust(45)}")
    lines.append("")

    # Decorative line
    lines.append("    " + random.choice(DECORATIONS["lines"]))
    lines.append("")

    # Greets section
    lines.append("        GR33TZ: SecKC, CoWTownComputerCongress, ACiD, iCE, badge lords")
    lines.append("        SHOUTZ: 14.4k Modem Jammers, MUD survivors, ANSI artists")
    lines.append("")

    # Footer
    lines.append("                    If your editor auto wraps lines, bounce now.")
    lines.append(f"                      ───── ▓ signed, {author}: ▓ ─────")
    lines.append('                            "nano > vim. come fight us."')
    lines.append("")

    return "\n".join(lines)


def generate_minimal_banner(name: str, org: str = "haKC.ai", tagline: str = "") -> str:
    """Generate a clean, minimal ASCII banner."""
    width = 60

    lines = []

    # Simple box with name
    big_name = text_to_big(name, "simple")
    boxed = make_box(big_name, "round")

    lines.extend(center_lines(boxed, width))
    lines.append("")

    if tagline:
        lines.append(tagline.center(width))
    else:
        lines.append(org.center(width))

    lines.append("─" * width)
    lines.append("")

    return "\n".join(lines)


def generate_cyberpunk_banner(
    name: str, org: str = "haKC.ai", tagline: str = "NEURAL INTERFACE READY"
) -> str:
    """Generate a cyberpunk/synthwave style banner."""
    width = 80

    lines = []

    # Glitchy header
    lines.append("▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓")
    lines.append("")

    # Big name with effects
    big_name = text_to_big(name, "simple")
    lines.extend(center_lines(big_name, width))

    lines.append("")
    lines.append("▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓▒░▒▓")
    lines.append("")

    # Cyberpunk info
    lines.append(f"    ╔══════════════════════════════════════════════════════════════╗")
    lines.append(f"    ║  SYSTEM: {name.upper().ljust(55)}║")
    lines.append(f"    ║  ORG:    {org.ljust(55)}║")
    lines.append(f"    ║  STATUS: {tagline.ljust(55)}║")
    lines.append(f"    ╚══════════════════════════════════════════════════════════════╝")
    lines.append("")

    # Grid decoration
    lines.append("    ║" + "═" * 8 + "╬" + "═" * 8 + "╬" + "═" * 8 + "╬" + "═" * 8 + "║")
    lines.append("")

    return "\n".join(lines)


def generate_retro_banner(name: str, org: str = "haKC.ai", sysop: str = "haKCer") -> str:
    """Generate a BBS-era retro banner."""
    width = 60

    lines = []

    # BBS header
    lines.append("╔" + "═" * (width - 2) + "╗")
    lines.append("║" + f" {name} BBS ".center(width - 2, "═") + "║")
    lines.append("╠" + "═" * (width - 2) + "╣")

    # Welcome message
    lines.append("║" + "".center(width - 2) + "║")
    lines.append("║" + "WELCOME, CALLER!".center(width - 2) + "║")
    lines.append("║" + "".center(width - 2) + "║")

    # System info
    lines.append("║" + f"  SysOp: {sysop}".ljust(width - 2) + "║")
    lines.append("║" + f"  Org:   {org}".ljust(width - 2) + "║")
    lines.append("║" + f"  Node:  1 of 1".ljust(width - 2) + "║")
    lines.append("║" + "".center(width - 2) + "║")

    # Connection info
    lines.append("║" + "  ─────────────────────────────────────────────────".ljust(width - 2) + "║")
    lines.append("║" + "  Connection: 14.4k BLAZING FAST".ljust(width - 2) + "║")
    lines.append("║" + "  Protocol:   ZModem Ready".ljust(width - 2) + "║")
    lines.append("║" + "".center(width - 2) + "║")

    lines.append("╚" + "═" * (width - 2) + "╝")
    lines.append("")

    return "\n".join(lines)


def generate_modern_banner(name: str, org: str = "haKC.ai", version: str = "1.0.0") -> str:
    """Generate a modern, clean ASCII banner."""
    width = 50

    lines = []

    # Simple modern header
    lines.append("┌" + "─" * (width - 2) + "┐")
    lines.append("│" + "".center(width - 2) + "│")

    # Name
    big_name = text_to_big(name, "simple")
    for bl in big_name:
        centered = bl.center(width - 2)
        lines.append("│" + centered + "│")

    lines.append("│" + "".center(width - 2) + "│")
    lines.append("├" + "─" * (width - 2) + "┤")

    # Metadata
    lines.append("│" + f"  {org} | v{version}".ljust(width - 2) + "│")
    lines.append("└" + "─" * (width - 2) + "┘")
    lines.append("")

    return "\n".join(lines)


def generate_menu(name: str, options: list[str], style: str = "warez") -> str:
    """Generate a menu template."""
    width = 60

    lines = []

    if style == "warez":
        lines.append("╔" + "═" * (width - 2) + "╗")
        lines.append("║" + f" {name} MENU ".center(width - 2, "═") + "║")
        lines.append("╠" + "═" * (width - 2) + "╣")
        lines.append("║" + "".center(width - 2) + "║")

        for i, opt in enumerate(options, 1):
            line = f"  [{i}] {opt}"
            lines.append("║" + line.ljust(width - 2) + "║")

        lines.append("║" + "".center(width - 2) + "║")
        lines.append("║" + "  [Q] Quit".ljust(width - 2) + "║")
        lines.append("║" + "".center(width - 2) + "║")
        lines.append("╚" + "═" * (width - 2) + "╝")
    else:
        lines.append(f"── {name} ──")
        lines.append("")
        for i, opt in enumerate(options, 1):
            lines.append(f"  {i}. {opt}")
        lines.append("")
        lines.append("  q. Quit")

    lines.append("")

    return "\n".join(lines)


def generate_footer(author: str = "/dev/haKCØRY.23", style: str = "warez") -> str:
    """Generate a footer/signature."""
    if style == "warez":
        return f"""
    *~'`^`'~*-,._.,-*~'`^`'~*-,._.,-*~'`^`'~*-,._.,-*~'`^`'~*
               ───── ▓ signed, {author}: ▓ ─────
                     "nano > vim. come fight us."
"""
    else:
        return f"\n─ {author}\n"


def generate_all_assets(name: str, org: str, style: str, output_dir: Path):
    """Generate all assets for a project."""
    output_dir.mkdir(parents=True, exist_ok=True)

    assets = {}

    # Main banner
    if style == "warez":
        assets["banner.txt"] = generate_warez_banner(name, org)
    elif style == "minimal":
        assets["banner.txt"] = generate_minimal_banner(name, org)
    elif style == "cyberpunk":
        assets["banner.txt"] = generate_cyberpunk_banner(name, org)
    elif style == "retro":
        assets["banner.txt"] = generate_retro_banner(name, org)
    else:  # modern
        assets["banner.txt"] = generate_modern_banner(name, org)

    # Menu template
    default_options = ["Start", "Settings", "Help", "About"]
    assets["menu.txt"] = generate_menu(name, default_options, style)

    # Footer/signature
    assets["footer.txt"] = generate_footer(style=style)

    # Big text versions
    big_name = "\n".join(text_to_big(name, "big"))
    assets["name_big.txt"] = big_name

    simple_name = "\n".join(text_to_big(name, "simple"))
    assets["name_simple.txt"] = simple_name

    # Write all assets
    for filename, content in assets.items():
        filepath = output_dir / filename
        filepath.write_text(content)
        print(f"  Created: {filepath}")

    # Write metadata
    metadata = {
        "project": name,
        "org": org,
        "style": style,
        "generated": datetime.now().isoformat(),
        "generator": "haKC Project Assets Generator",
        "files": list(assets.keys()),
    }

    (output_dir / "manifest.json").write_text(json.dumps(metadata, indent=2))
    print(f"  Created: {output_dir / 'manifest.json'}")


def interactive_mode():
    """Interactive wizard for generating assets."""
    print("\n" + "=" * 60)
    print("  haKC Project Assets Generator - Interactive Mode")
    print("  The Pinnacle of Hakcing Quality")
    print("=" * 60 + "\n")

    name = input("  Project name: ").strip()
    if not name:
        name = "MyProject"

    org = input("  Organization [haKC.ai]: ").strip()
    if not org:
        org = "haKC.ai"

    print("\n  Available styles:")
    print("    1. warez    - Classic NFO/warez scene style")
    print("    2. minimal  - Clean, simple ASCII banners")
    print("    3. cyberpunk - Futuristic/synthwave vibes")
    print("    4. retro    - BBS era nostalgia")
    print("    5. modern   - Contemporary ASCII art")

    style_choice = input("\n  Style [1]: ").strip()
    styles = {"1": "warez", "2": "minimal", "3": "cyberpunk", "4": "retro", "5": "modern"}
    style = styles.get(style_choice, "warez")

    output = input(f"  Output directory [{name.lower()}_assets]: ").strip()
    if not output:
        output = f"{name.lower()}_assets"

    output_dir = Path(output)

    print(f"\n  Generating {style} assets for '{name}'...")
    print()

    generate_all_assets(name, org, style, output_dir)

    print(f"\n  Done! Assets saved to: {output_dir.absolute()}")
    print("  ───── ▓ signed, /dev/haKCØRY.23: ▓ ─────\n")


def main():
    parser = argparse.ArgumentParser(
        description="haKC Project Assets Generator - The Pinnacle of Hakcing Quality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Styles:
  warez     - Classic NFO/warez scene style (default)
  minimal   - Clean, simple ASCII banners
  cyberpunk - Futuristic/synthwave vibes
  retro     - BBS era nostalgia
  modern    - Contemporary ASCII art

Template Variables (from motd.json):
  {motd}       - Random message of the day
  {greets}     - Random greets line
  {fus}        - Random FU line
  {signatures} - Random signature

Examples:
  hakc_banner.py --name "MyProject" --org "haKC-ai"
  hakc_banner.py --name "CoolTool" --style cyberpunk
  hakc_banner.py --template banner_withvariables.txt
  hakc_banner.py --template banner_withvariables.txt --output my_banner.txt
  hakc_banner.py --template banner_withvariables.txt --count 5  # Generate 5 variants
  hakc_banner.py --interactive

signed, /dev/haKCØRY.23
        """,
    )

    parser.add_argument("--name", "-n", help="Project name")
    parser.add_argument("--org", "-o", default="haKC.ai", help="Organization name")
    parser.add_argument(
        "--style",
        "-s",
        choices=["warez", "minimal", "cyberpunk", "retro", "modern"],
        default="warez",
        help="Banner style",
    )
    parser.add_argument("--output", "-d", help="Output file or directory")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--preview", "-p", action="store_true", help="Preview banner only")
    parser.add_argument("--template", "-t", help="Template file with {motd}, {greets}, {fus}, {signatures} variables")
    parser.add_argument("--count", "-c", type=int, default=1, help="Number of variants to generate (with --template)")
    parser.add_argument("--motd", help="Override {motd} variable")
    parser.add_argument("--greets", help="Override {greets} variable")
    parser.add_argument("--fus", help="Override {fus} variable")
    parser.add_argument("--sig", help="Override {signatures} variable")

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        return

    # Template mode - render template with variables from motd.json
    if args.template:
        template_path = Path(args.template)
        if not template_path.exists():
            # Try relative to script dir
            template_path = SCRIPT_DIR / args.template
        if not template_path.exists():
            print(f"Error: Template file not found: {args.template}")
            return

        # Build custom variables from args
        custom_vars = {}
        if args.motd:
            custom_vars["motd"] = args.motd
        if args.greets:
            custom_vars["greets"] = args.greets
        if args.fus:
            custom_vars["fus"] = args.fus
        if args.sig:
            custom_vars["signatures"] = args.sig

        if args.count > 1:
            # Generate multiple variants
            print(f"\n  Generating {args.count} banner variants from template...\n")
            variants = []
            for i in range(args.count):
                rendered = render_template(template_path, custom_vars if custom_vars else None)
                variants.append(rendered)
                if args.output:
                    # Save each variant
                    output_path = Path(args.output)
                    if output_path.suffix:
                        # Has extension - insert number before it
                        out_file = output_path.parent / f"{output_path.stem}_{i+1}{output_path.suffix}"
                    else:
                        out_file = Path(f"{args.output}_{i+1}.txt")
                    out_file.write_text(rendered)
                    print(f"  Saved: {out_file}")
                else:
                    print(f"═══════════════════ Variant {i+1} ═══════════════════")
                    print(rendered)
            print(f"\n  Generated {args.count} variants.")
        else:
            # Single render
            rendered = render_template(template_path, custom_vars if custom_vars else None)
            if args.output:
                Path(args.output).write_text(rendered)
                print(f"\n  Saved: {args.output}")
            else:
                print(rendered)
        print("  ───── ▓ signed, /dev/haKCØRY.23: ▓ ─────\n")
        return

    if not args.name:
        print("Error: --name is required (or use --interactive or --template)")
        parser.print_help()
        return

    # Preview mode
    if args.preview:
        if args.style == "warez":
            print(generate_warez_banner(args.name, args.org))
        elif args.style == "minimal":
            print(generate_minimal_banner(args.name, args.org))
        elif args.style == "cyberpunk":
            print(generate_cyberpunk_banner(args.name, args.org))
        elif args.style == "retro":
            print(generate_retro_banner(args.name, args.org))
        else:
            print(generate_modern_banner(args.name, args.org))
        return

    # Generate all assets
    output_dir = Path(args.output) if args.output else Path(f"{args.name.lower()}_assets")

    print(f"\n  Generating {args.style} assets for '{args.name}'...")
    print()

    generate_all_assets(args.name, args.org, args.style, output_dir)

    print(f"\n  Done! Assets saved to: {output_dir.absolute()}")
    print("  ───── ▓ signed, /dev/haKCØRY.23: ▓ ─────\n")


if __name__ == "__main__":
    main()
