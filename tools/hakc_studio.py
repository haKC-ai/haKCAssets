#!/usr/bin/env python3
"""
haKC Studio - The Ultimate Asset Generation Orchestrator
The Pinnacle of Hakcing Quality

A menu-driven interface for all haKC asset generation tools.
Uses the hakcer module for animated effects.

Usage:
  hakc_studio.py                    # Interactive menu
  hakc_studio.py --quick            # Skip banner animation
  hakc_studio.py --theme synthwave  # Set hakcer theme

Tools available:
  - Banner Generator: Create ASCII banners in various styles
  - Menu Generator: Generate CLI menu templates
  - MOTD Generator: Message of the day system
  - Art Generator: Generate ASCII art from vibes
  - NFO Effects: Animated NFO-style banners

signed, /dev/haKCØRY.23
"""

import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Script paths
SCRIPT_DIR = Path(__file__).parent
GENERATORS_DIR = SCRIPT_DIR / "generators"
OUTPUT_BASE = Path.cwd() / "hakc_output"

# Try to import hakcer for effects
HAKCER_AVAILABLE = False
try:
    sys.path.insert(0, "/Users/0xdeadbeef/haKCer")
    from hakcer import show_banner, set_theme, list_themes
    HAKCER_AVAILABLE = True
except ImportError:
    pass

# ANSI colors
COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "cyan": "\033[36m",
    "magenta": "\033[35m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "red": "\033[31m",
    "white": "\033[37m",
}

# Studio banner
STUDIO_BANNER = r"""
                 ██████████
                █▓       ░██
                █▒        ██ T H E   P I N A C L E  O F  H A K C I N G   Q U A L I T Y
    █████████████░        █████████████████ ████████████ ████████████      ████████████
   ██         ███░        ███▓▒▒▒▒▒▒▒▒▒▒▒██ █▒▒▒▒▒▒▒▒▓████        █████████▓          ▒█
   ██         ███         ███▒▒▒▒▒▒▒▒▒▒▒▒▓██████████████▓        ███▓▒      ▒▓░       ▒█
   ██         ███        ░██▓▒▒▒▒▒▒▒▒▒▒▒▒▒▓██▓▒▒▒▒▒▒▒▒█▓        ███░       ░██░       ▒█
   ██         ███        ▒██▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒██▓▒▒▒▒▒▒▒▓▒        ██  ▓        ██░       ▓█
   ██         ██▓        ███▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒█▓▒▒▒▒▒▒▒▓▒       ██   █        ██░       ▓
   ██         ██▒        ██▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓▒▒▒▒▒▒▒▓▒      ██    █        ▓█████████
   ██                    ██▒▒▒▒▒▒▒▒█▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▒   ▒███████ █░       ░▓        █
   ██         ░░         ██▒▒▒▒▒▒▒▒██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓█ ▓        ░█ ▓       ░▒       ░█
   ██         ██░       ░█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓█ █░        ▒ █                ░█
   ██         ██        ▓█▒▒▒▒▒▒▒▒▒██▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓█ █░        ▒ █░               ▒█
    ██████████  ███████████▓██▓▓█▓█  █▓▒▒▒▒▒▒▒▒▒▓██▓██   █▓▓▓▓▓▓▓█    █▓▓▓▓▓▓▓▓▓▓▓▓▓▓██
  .:/====================█▓██▓██=========████▓█▓████=======[ S T U D I O ]==========\:.
                           ██▓██           █▓▓▓██ ██
                             █▓█             ██▓██
                              ██               ███
"""

MAIN_MENU = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                          h a K C   S T U D I O                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║   [1] Banner Generator       Create ASCII banners (warez, minimal, etc.)     ║
║   [2] Menu Generator         Generate CLI menu templates                     ║
║   [3] Art Generator          Generate ASCII art with NFO vibes               ║
║   [4] MOTD System            Message of the day manager                      ║
║   [5] NFO Effects            Show animated NFO banner                        ║
║                                                                              ║
╟──────────────────────────────────────────────────────────────────────────────╢
║                                                                              ║
║   [S] Settings               Configure themes and output                     ║
║   [Q] Quit                   Exit haKC Studio                                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

  Select option: """


class HakcStudio:
    def __init__(self, theme: str = "synthwave", skip_banner: bool = False):
        self.theme = theme
        self.skip_banner = skip_banner
        self.output_dir = OUTPUT_BASE
        self.project_name = "untitled"

        if HAKCER_AVAILABLE:
            set_theme(theme)

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def show_animated_banner(self):
        """Show the studio banner with hakcer effects."""
        if self.skip_banner:
            print(STUDIO_BANNER)
            return

        if HAKCER_AVAILABLE:
            try:
                show_banner(
                    custom_text=STUDIO_BANNER,
                    speed_preference="fast",
                    theme=self.theme,
                    hold_time=1.0,
                    clear_after=False,
                )
            except Exception:
                print(STUDIO_BANNER)
        else:
            print(STUDIO_BANNER)

    def color(self, text: str, color: str) -> str:
        return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"

    def prompt(self, message: str, default: str = "") -> str:
        """Get user input with optional default."""
        if default:
            display = f"  {message} [{default}]: "
        else:
            display = f"  {message}: "

        result = input(display).strip()
        return result if result else default

    def get_output_path(self, name: str, ext: str = "txt") -> Path:
        """Get organized output path."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_dir = self.output_dir / self.project_name / timestamp
        project_dir.mkdir(parents=True, exist_ok=True)
        return project_dir / f"{name}.{ext}"

    def save_output(self, content: str, name: str, also_static: bool = True) -> Path:
        """Save output to organized directory."""
        path = self.get_output_path(name)
        path.write_text(content)
        print(f"\n  {self.color('Saved:', 'green')} {path}")
        return path

    # =========================================================================
    # BANNER GENERATOR
    # =========================================================================
    def run_banner_generator(self):
        self.clear_screen()
        print(f"\n{self.color('=== BANNER GENERATOR ===', 'cyan')}\n")

        name = self.prompt("Project name", "MyProject")
        self.project_name = name.lower().replace(" ", "_")

        org = self.prompt("Organization", "haKC.ai")

        print("\n  Styles:")
        print("    1. warez    - Classic NFO/warez scene")
        print("    2. minimal  - Clean and simple")
        print("    3. cyberpunk - Futuristic vibes")
        print("    4. retro    - BBS era nostalgia")
        print("    5. modern   - Contemporary look")

        style_choice = self.prompt("Style", "1")
        styles = {"1": "warez", "2": "minimal", "3": "cyberpunk", "4": "retro", "5": "modern"}
        style = styles.get(style_choice, "warez")

        # Import and run generator
        sys.path.insert(0, str(GENERATORS_DIR / "banner"))
        try:
            from hakc_banner import generate_banner
            banner = generate_banner(name, org, style)
        except ImportError:
            # Fallback inline generation
            banner = self._generate_banner_inline(name, org, style)

        print(f"\n{self.color('=== PREVIEW ===', 'yellow')}\n")
        print(banner)

        # Show animated version if hakcer available
        if HAKCER_AVAILABLE and self.prompt("Show animated version?", "y").lower() == "y":
            self.clear_screen()
            try:
                show_banner(
                    custom_text=banner,
                    speed_preference="medium",
                    theme=self.theme,
                    hold_time=2.0,
                )
            except Exception as e:
                print(f"Animation failed: {e}")

        # Save options
        if self.prompt("Save banner?", "y").lower() == "y":
            self.save_output(banner, "banner")

            # Also save metadata
            metadata = f"""# {name} Banner
Generated: {datetime.now().isoformat()}
Style: {style}
Organization: {org}
Generator: haKC Studio
"""
            self.save_output(metadata, "banner_meta", also_static=False)

        input("\n  Press Enter to continue...")

    def _generate_banner_inline(self, name: str, org: str, style: str) -> str:
        """Fallback banner generation."""
        width = 60
        lines = []
        lines.append("╔" + "═" * (width - 2) + "╗")
        lines.append("║" + name.center(width - 2) + "║")
        lines.append("║" + org.center(width - 2) + "║")
        lines.append("╚" + "═" * (width - 2) + "╝")
        return "\n".join(lines)

    # =========================================================================
    # MENU GENERATOR
    # =========================================================================
    def run_menu_generator(self):
        self.clear_screen()
        print(f"\n{self.color('=== MENU GENERATOR ===', 'cyan')}\n")

        name = self.prompt("Menu name", "Main Menu")
        self.project_name = name.lower().replace(" ", "_")

        options_str = self.prompt("Menu options (comma-separated)", "Start,Settings,Help,About")
        options = [o.strip() for o in options_str.split(",")]

        print("\n  Styles:")
        print("    1. warez  - Classic scene style")
        print("    2. minimal - Clean and simple")
        print("    3. bbs    - BBS era style")
        print("    4. modern - Contemporary look")

        style_choice = self.prompt("Style", "1")
        styles = {"1": "warez", "2": "minimal", "3": "bbs", "4": "modern"}
        style = styles.get(style_choice, "warez")

        # Import and run generator
        sys.path.insert(0, str(GENERATORS_DIR / "menu"))
        try:
            from hakc_menu import GENERATORS
            generator = GENERATORS.get(style)
            menu = generator(name, options)
        except ImportError:
            menu = self._generate_menu_inline(name, options)

        print(f"\n{self.color('=== PREVIEW ===', 'yellow')}\n")
        print(menu)

        if self.prompt("Save menu?", "y").lower() == "y":
            self.save_output(menu, "menu")

        input("\n  Press Enter to continue...")

    def _generate_menu_inline(self, name: str, options: list) -> str:
        """Fallback menu generation."""
        width = 50
        lines = []
        lines.append("╔" + "═" * (width - 2) + "╗")
        lines.append("║" + name.center(width - 2) + "║")
        lines.append("╠" + "═" * (width - 2) + "╣")
        for i, opt in enumerate(options, 1):
            lines.append("║" + f"  [{i}] {opt}".ljust(width - 2) + "║")
        lines.append("║" + "  [Q] Quit".ljust(width - 2) + "║")
        lines.append("╚" + "═" * (width - 2) + "╝")
        return "\n".join(lines)

    # =========================================================================
    # ART GENERATOR
    # =========================================================================
    def run_art_generator(self):
        self.clear_screen()
        print(f"\n{self.color('=== ART GENERATOR ===', 'cyan')}\n")

        name = self.prompt("What to generate art for", "haKC")
        self.project_name = name.lower().replace(" ", "_")

        print("\n  Styles:")
        print("    1. warez    - Classic NFO style")
        print("    2. minimal  - Clean ASCII art")
        print("    3. cyberpunk - Futuristic")
        print("    4. bbs      - BBS era")

        style_choice = self.prompt("Style", "1")
        styles = {"1": "warez", "2": "minimal", "3": "cyberpunk", "4": "bbs"}
        style = styles.get(style_choice, "warez")

        # Import and run generator
        sys.path.insert(0, str(GENERATORS_DIR / "hackerart"))
        try:
            if style == "warez":
                from hakc_art import generate_warez_art
                art = generate_warez_art(name)
            elif style == "minimal":
                from hakc_art import generate_minimal_art
                art = generate_minimal_art(name)
            elif style == "cyberpunk":
                from hakc_art import generate_cyberpunk_art
                art = generate_cyberpunk_art(name)
            else:
                from hakc_art import generate_bbs_art
                art = generate_bbs_art(name)
        except ImportError:
            art = f"=== {name} ===\n(Art generator not available)"

        print(f"\n{self.color('=== PREVIEW ===', 'yellow')}\n")
        print(art)

        # Show animated version
        if HAKCER_AVAILABLE and self.prompt("Show animated version?", "y").lower() == "y":
            self.clear_screen()
            try:
                show_banner(
                    custom_text=art,
                    speed_preference="slow",
                    theme=self.theme,
                    hold_time=2.0,
                )
            except Exception as e:
                print(f"Animation failed: {e}")

        if self.prompt("Save art?", "y").lower() == "y":
            self.save_output(art, "art")

        input("\n  Press Enter to continue...")

    # =========================================================================
    # MOTD SYSTEM
    # =========================================================================
    def run_motd_system(self):
        self.clear_screen()
        print(f"\n{self.color('=== MOTD SYSTEM ===', 'cyan')}\n")

        print("  Options:")
        print("    1. Show random MOTD")
        print("    2. Show full MOTD (greet + message + sig)")
        print("    3. Add new MOTD")
        print("    4. List all MOTDs")
        print("    5. Back")

        choice = self.prompt("Select", "1")

        sys.path.insert(0, str(GENERATORS_DIR / "motd"))
        try:
            from hakc_motd import load_motd_data, get_random_motd, get_full_motd, add_motd, list_motds

            data = load_motd_data()

            if choice == "1":
                motd = get_random_motd(data)
                print(f"\n  {self.color(motd, 'cyan')}\n")
            elif choice == "2":
                motd = get_full_motd(data, use_ansi=True)
                print(f"\n{motd}\n")
            elif choice == "3":
                new_msg = self.prompt("New MOTD message")
                if new_msg:
                    if add_motd(data, new_msg):
                        print(f"\n  {self.color('Added!', 'green')}")
                    else:
                        print(f"\n  {self.color('Already exists!', 'red')}")
            elif choice == "4":
                print(f"\n{list_motds(data, use_ansi=True)}\n")

        except ImportError:
            print("  MOTD system not available")

        input("\n  Press Enter to continue...")

    # =========================================================================
    # NFO EFFECTS
    # =========================================================================
    def run_nfo_effects(self):
        self.clear_screen()
        print(f"\n{self.color('=== NFO EFFECTS ===', 'cyan')}\n")

        print("  Options:")
        print("    1. Static NFO banner")
        print("    2. Animated sparkle effect")
        print("    3. Typing effect")
        print("    4. Back")

        choice = self.prompt("Select", "1")

        sys.path.insert(0, str(GENERATORS_DIR / "hackerart"))
        try:
            from nfo_effects import print_static, animate_sparkles, print_with_typing, clear_screen

            if choice == "1":
                clear_screen()
                print_static()
            elif choice == "2":
                frames = int(self.prompt("Animation frames", "50"))
                clear_screen()
                try:
                    animate_sparkles(iterations=frames)
                except KeyboardInterrupt:
                    pass
                clear_screen()
                print_static()
            elif choice == "3":
                clear_screen()
                print_with_typing()

        except ImportError:
            print("  NFO effects not available")

        input("\n  Press Enter to continue...")

    # =========================================================================
    # SETTINGS
    # =========================================================================
    def run_settings(self):
        self.clear_screen()
        print(f"\n{self.color('=== SETTINGS ===', 'cyan')}\n")

        print(f"  Current theme: {self.color(self.theme, 'magenta')}")
        print(f"  Output directory: {self.output_dir}")
        print(f"  hakcer available: {self.color('Yes' if HAKCER_AVAILABLE else 'No', 'green' if HAKCER_AVAILABLE else 'red')}")

        if HAKCER_AVAILABLE:
            print(f"\n  Available themes: {', '.join(list_themes())}")

        print("\n  Options:")
        print("    1. Change theme")
        print("    2. Change output directory")
        print("    3. Back")

        choice = self.prompt("Select", "3")

        if choice == "1" and HAKCER_AVAILABLE:
            new_theme = self.prompt("Theme", self.theme)
            if new_theme in list_themes():
                self.theme = new_theme
                set_theme(new_theme)
                print(f"  {self.color('Theme updated!', 'green')}")
            else:
                print(f"  {self.color('Invalid theme', 'red')}")
        elif choice == "2":
            new_dir = self.prompt("Output directory", str(self.output_dir))
            self.output_dir = Path(new_dir)
            print(f"  {self.color('Output directory updated!', 'green')}")

        input("\n  Press Enter to continue...")

    # =========================================================================
    # MAIN LOOP
    # =========================================================================
    def run(self):
        """Main menu loop."""
        self.clear_screen()
        self.show_animated_banner()

        while True:
            self.clear_screen()
            print(MAIN_MENU, end="")

            choice = input().strip().upper()

            if choice == "1":
                self.run_banner_generator()
            elif choice == "2":
                self.run_menu_generator()
            elif choice == "3":
                self.run_art_generator()
            elif choice == "4":
                self.run_motd_system()
            elif choice == "5":
                self.run_nfo_effects()
            elif choice == "S":
                self.run_settings()
            elif choice == "Q":
                self.clear_screen()
                print(f"\n  {self.color('───── ▓ signed, /dev/haKCØRY.23: ▓ ─────', 'dim')}")
                print(f'  {self.color(\'"nano > vim. come fight us."\', "dim")}\n')
                break
            else:
                print(f"\n  {self.color('Invalid option', 'red')}")
                time.sleep(0.5)


def main():
    parser = argparse.ArgumentParser(
        description="haKC Studio - The Ultimate Asset Generation Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Tools available:
  - Banner Generator: Create ASCII banners (warez, minimal, cyberpunk, etc.)
  - Menu Generator: Generate CLI menu templates
  - Art Generator: Generate ASCII art with NFO vibes
  - MOTD System: Message of the day manager
  - NFO Effects: Animated NFO-style banners

signed, /dev/haKCØRY.23
        """,
    )

    parser.add_argument("--quick", "-q", action="store_true", help="Skip banner animation")
    parser.add_argument("--theme", "-t", default="synthwave", help="hakcer theme")
    parser.add_argument("--output", "-o", help="Output directory")

    args = parser.parse_args()

    studio = HakcStudio(theme=args.theme, skip_banner=args.quick)

    if args.output:
        studio.output_dir = Path(args.output)

    try:
        studio.run()
    except KeyboardInterrupt:
        print("\n\n  Interrupted. Bye!\n")


if __name__ == "__main__":
    main()
