#!/usr/bin/env python3
"""
haKC README Generator - Generate branded READMEs following haKC style guidelines
The Pinnacle of Hakcing Quality

Usage:
  hakc_readme.py --name "MyProject" --description "A cool tool"
  hakc_readme.py --name "MyProject" --template minimal
  hakc_readme.py --interactive
  hakc_readme.py --from-branding  # Use branding.json defaults

Templates:
  full     - Complete README with all sections
  minimal  - Basic README (description, install, usage)
  cli      - CLI tool focused README
  library  - Python library README

signed, /dev/haKCØRY.23
"""

import argparse
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Optional

# Script directory for relative imports
SCRIPT_DIR = Path(__file__).parent
BRANDING_FILE = SCRIPT_DIR.parent.parent.parent / "branding.json"
MOTD_FILE = SCRIPT_DIR.parent / "motd" / "motd.json"
BANNERS_DIR = SCRIPT_DIR.parent.parent.parent / "banners"

# Cache
_branding_data = None
_motd_data = None


def load_branding() -> dict:
    """Load branding guidelines from branding.json."""
    global _branding_data
    if _branding_data is None:
        if BRANDING_FILE.exists():
            _branding_data = json.loads(BRANDING_FILE.read_text())
        else:
            _branding_data = {
                "organization": "haKC.ai",
                "tagline": "THE PINNACLE OF HAKCING QUALITY",
                "shields": {"style": "for-the-badge"},
                "colors": {"palette": {"synthwave": {"primary": "#00D9FF", "secondary": "#FF10F0", "accent": "#7928CA"}}}
            }
    return _branding_data


def load_motd() -> dict:
    """Load MOTD data."""
    global _motd_data
    if _motd_data is None:
        if MOTD_FILE.exists():
            _motd_data = json.loads(MOTD_FILE.read_text())
        else:
            _motd_data = {"motd": [], "categories": {"signatures": []}}
    return _motd_data


def get_random_signature() -> str:
    """Get a random signature from MOTD."""
    data = load_motd()
    sigs = data.get("categories", {}).get("signatures", [])
    if sigs:
        return random.choice(sigs)
    return "───── ▓ signed, /dev/haKCØRY.23: ▓ ─────"


def get_banner_ascii() -> str:
    """Get the main haKC ASCII banner."""
    banner_file = BANNERS_DIR / "banner_component0.txt"
    if banner_file.exists():
        return banner_file.read_text()
    return """```
                 ██████████
                █▓       ░██
                █▒        ██ T H E   P I N N A C L E   O F   H A K C I N G   Q U A L I T Y
    █████████████░        █████████████████ ████████████ ████████████      ████████████
```"""


def generate_badges(
    name: str,
    org: str = "haKC-ai",
    python_version: str = "3.10+",
    license_type: str = "MIT",
    include_extras: bool = True
) -> str:
    """Generate shields.io badges."""
    branding = load_branding()
    colors = branding.get("colors", {}).get("palette", {}).get("synthwave", {})

    primary = colors.get("primary", "#00D9FF").replace("#", "")
    secondary = colors.get("secondary", "#FF10F0").replace("#", "")
    accent = colors.get("accent", "#7928CA").replace("#", "")

    badges = []

    # haKC quality badge
    badges.append(f"[![haKC](https://img.shields.io/badge/haKC-QUALITY-{accent}?style=for-the-badge)](https://github.com/{org})")

    # License
    badges.append(f"[![License](https://img.shields.io/badge/License-{license_type}-{primary}?style=for-the-badge)](LICENSE)")

    # Python
    badges.append(f"[![Python](https://img.shields.io/badge/Python-{python_version}-{secondary}?style=for-the-badge&logo=python&logoColor=white)](https://python.org)")

    if include_extras:
        # Terminal ready
        badges.append(f"[![Terminal](https://img.shields.io/badge/Terminal-Ready-00FF41?style=for-the-badge&logo=gnometerminal&logoColor=white)](.)")

    return "\n".join(badges)


def generate_full_readme(
    name: str,
    description: str,
    org: str = "haKC-ai",
    features: Optional[list] = None,
    install_cmd: Optional[str] = None,
    usage_examples: Optional[list] = None,
    python_version: str = "3.10+",
    license_type: str = "MIT",
    include_banner: bool = True,
) -> str:
    """Generate a full README with all sections."""

    lines = []

    # Banner
    if include_banner:
        lines.append("```")
        lines.append(f"{'█' * 60}")
        lines.append(f"  {name.upper()}")
        lines.append(f"  {description[:50]}...")
        lines.append(f"{'█' * 60}")
        lines.append("```")
        lines.append("")

    # Badges
    lines.append("<p align=\"center\">")
    lines.append("")
    lines.append(generate_badges(name, org, python_version, license_type))
    lines.append("")
    lines.append("</p>")
    lines.append("")

    # Description
    lines.append(f"<p align=\"center\">")
    lines.append(f"<strong>{description}</strong>")
    lines.append(f"</p>")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Features
    if features:
        lines.append("## Features")
        lines.append("")
        lines.append("```")
        for feat in features:
            lines.append(f"▸ {feat}")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

    # Installation
    lines.append("## Installation")
    lines.append("")
    if install_cmd:
        lines.append("```bash")
        lines.append(install_cmd)
        lines.append("```")
    else:
        lines.append("```bash")
        lines.append(f"pip install {name.lower().replace(' ', '-')}")
        lines.append("```")
        lines.append("")
        lines.append("Or from source:")
        lines.append("")
        lines.append("```bash")
        lines.append(f"git clone https://github.com/{org}/{name.lower().replace(' ', '-')}.git")
        lines.append(f"cd {name.lower().replace(' ', '-')}")
        lines.append("pip install -e .")
        lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Usage
    lines.append("## Usage")
    lines.append("")
    if usage_examples:
        lines.append("```bash")
        for example in usage_examples:
            lines.append(example)
        lines.append("```")
    else:
        lines.append("```bash")
        lines.append(f"# Basic usage")
        lines.append(f"{name.lower().replace(' ', '-')} --help")
        lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Contributing
    lines.append("## Contributing")
    lines.append("")
    lines.append("1. Fork it")
    lines.append("2. Create your feature branch (`git checkout -b feature/sick-feature`)")
    lines.append("3. Commit your changes (`git commit -am 'Add sick feature'`)")
    lines.append("4. Push to the branch (`git push origin feature/sick-feature`)")
    lines.append("5. Create a Pull Request")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Footer
    lines.append("<p align=\"center\">")
    lines.append("")
    lines.append("```")
    lines.append(get_random_signature())
    lines.append("\"nano > vim. come fight us.\"")
    lines.append("```")
    lines.append("")
    lines.append(f"**GR33TZ:** SecKC, LEGACY CoWTownComputerCongress, ACiD, iCE, T$A")
    lines.append("")
    lines.append("</p>")

    return "\n".join(lines)


def generate_minimal_readme(
    name: str,
    description: str,
    org: str = "haKC-ai",
    install_cmd: Optional[str] = None,
) -> str:
    """Generate a minimal README."""

    lines = []

    # Title
    lines.append(f"# {name}")
    lines.append("")
    lines.append(f"> {description}")
    lines.append("")

    # Badges
    lines.append(generate_badges(name, org, include_extras=False))
    lines.append("")
    lines.append("---")
    lines.append("")

    # Install
    lines.append("## Install")
    lines.append("")
    lines.append("```bash")
    if install_cmd:
        lines.append(install_cmd)
    else:
        lines.append(f"pip install {name.lower().replace(' ', '-')}")
    lines.append("```")
    lines.append("")

    # Usage
    lines.append("## Usage")
    lines.append("")
    lines.append("```bash")
    lines.append(f"{name.lower().replace(' ', '-')} --help")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Footer
    lines.append(f"*{get_random_signature()}*")

    return "\n".join(lines)


def generate_cli_readme(
    name: str,
    description: str,
    org: str = "haKC-ai",
    commands: Optional[dict] = None,
) -> str:
    """Generate a CLI-focused README."""

    lines = []

    # Banner block
    lines.append("```")
    lines.append(f"╔{'═' * 58}╗")
    lines.append(f"║{name.upper().center(58)}║")
    lines.append(f"║{description[:56].center(58)}║")
    lines.append(f"╚{'═' * 58}╝")
    lines.append("```")
    lines.append("")

    # Badges
    lines.append("<p align=\"center\">")
    lines.append("")
    lines.append(generate_badges(name, org))
    lines.append("")
    lines.append("</p>")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Install
    lines.append("## Installation")
    lines.append("")
    lines.append("```bash")
    lines.append(f"pip install {name.lower().replace(' ', '-')}")
    lines.append("# or")
    lines.append(f"pipx install {name.lower().replace(' ', '-')}")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Commands
    lines.append("## Commands")
    lines.append("")
    if commands:
        lines.append("| Command | Description |")
        lines.append("|---------|-------------|")
        for cmd, desc in commands.items():
            lines.append(f"| `{cmd}` | {desc} |")
    else:
        lines.append("```bash")
        lines.append(f"{name.lower().replace(' ', '-')} --help")
        lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Footer
    lines.append("<p align=\"center\">")
    lines.append("")
    lines.append(f"*{get_random_signature()}*")
    lines.append("")
    lines.append("</p>")

    return "\n".join(lines)


def interactive_mode():
    """Interactive README generation wizard."""
    print("\n" + "=" * 60)
    print("  haKC README Generator - Interactive Mode")
    print("  The Pinnacle of Hakcing Quality")
    print("=" * 60 + "\n")

    name = input("  Project name: ").strip()
    if not name:
        name = "MyProject"

    description = input("  Description: ").strip()
    if not description:
        description = "A haKC.ai project"

    org = input("  Organization [haKC-ai]: ").strip()
    if not org:
        org = "haKC-ai"

    print("\n  Templates:")
    print("    1. full    - Complete README with all sections")
    print("    2. minimal - Basic README")
    print("    3. cli     - CLI tool focused")

    template = input("\n  Template [1]: ").strip()
    templates = {"1": "full", "2": "minimal", "3": "cli"}
    template = templates.get(template, "full")

    print("\n  Features (comma-separated, or empty to skip):")
    features_str = input("  Features: ").strip()
    features = [f.strip() for f in features_str.split(",")] if features_str else None

    # Generate
    if template == "full":
        readme = generate_full_readme(name, description, org, features)
    elif template == "minimal":
        readme = generate_minimal_readme(name, description, org)
    else:
        readme = generate_cli_readme(name, description, org)

    print("\n" + "=" * 60 + "\n")
    print(readme)

    save = input("\n  Save to README.md? [y/N]: ").strip().lower()
    if save == "y":
        filename = input("  Filename [README.md]: ").strip()
        if not filename:
            filename = "README.md"

        Path(filename).write_text(readme)
        print(f"  Saved to: {filename}")

    print("\n  ───── ▓ signed, /dev/haKCØRY.23: ▓ ─────\n")


def main():
    parser = argparse.ArgumentParser(
        description="haKC README Generator - The Pinnacle of Hakcing Quality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Templates:
  full     - Complete README with all sections
  minimal  - Basic README (description, install, usage)
  cli      - CLI tool focused README

Examples:
  hakc_readme.py --name "MyTool" --description "Does cool stuff"
  hakc_readme.py --name "MyCLI" --template cli
  hakc_readme.py --interactive

signed, /dev/haKCØRY.23
        """,
    )

    parser.add_argument("--name", "-n", help="Project name")
    parser.add_argument("--description", "-d", help="Project description")
    parser.add_argument("--org", "-o", default="haKC-ai", help="GitHub organization")
    parser.add_argument(
        "--template", "-t",
        choices=["full", "minimal", "cli"],
        default="full",
        help="README template",
    )
    parser.add_argument("--features", "-f", help="Comma-separated features list")
    parser.add_argument("--output", help="Output file")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--python", default="3.10+", help="Python version requirement")
    parser.add_argument("--license", dest="license_type", default="MIT", help="License type")
    parser.add_argument("--no-banner", action="store_true", help="Skip ASCII banner")

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        return

    if not args.name:
        print("Error: --name is required (or use --interactive)")
        parser.print_help()
        return

    description = args.description or f"A {args.org} project"
    features = [f.strip() for f in args.features.split(",")] if args.features else None

    # Generate README
    if args.template == "full":
        readme = generate_full_readme(
            args.name,
            description,
            args.org,
            features,
            python_version=args.python,
            license_type=args.license_type,
            include_banner=not args.no_banner,
        )
    elif args.template == "minimal":
        readme = generate_minimal_readme(args.name, description, args.org)
    else:
        readme = generate_cli_readme(args.name, description, args.org)

    if args.output:
        Path(args.output).write_text(readme)
        print(f"  Saved: {args.output}")
    else:
        print(readme)

    print("\n  ───── ▓ signed, /dev/haKCØRY.23: ▓ ─────\n")


if __name__ == "__main__":
    main()
