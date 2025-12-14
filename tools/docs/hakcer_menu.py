#!/usr/bin/env python3
"""
haKCer Effects Tester - Control each banner component with its own effect/theme
Mouse-clickable dropdowns for Component, Effect, and Theme.
Uses composite rendering to overlay components on a single canvas.

Usage:
  python hakcer_menu.py                      # Use default banner_full.txt
  python hakcer_menu.py /path/to/banner.txt  # Use specific banner file
  python hakcer_menu.py /path/to/dir/        # Use directory with banner files
"""

import sys
import os
import time
import random
import math
import shutil
import argparse
from pathlib import Path

# Add haKCer to path
sys.path.insert(0, '/Users/0xdeadbeef/haKCer')

from prompt_toolkit import Application
from prompt_toolkit.layout import Layout, Window, FormattedTextControl
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.mouse_events import MouseEventType

from hakcer import show_banner, set_theme
from hakcer.themes import THEMES

# Configuration
DEFAULT_DIR = Path("/Users/0xdeadbeef/Desktop/hakcer_effects_tester")
HOLD_TIME = 2.0

# Effects and themes
EFFECTS = ["none", "decrypt", "matrix", "synthgrid", "waves", "fireworks", "vhstape", "typewriter", "glitch", "rain", "scan"]
THEME_LIST = ["matrix", "synthwave", "cyberpunk", "neon", "tokyo_night", "dracula", "monokai", "gruvbox"]

# Default component definitions for banner_full.txt
# (name, start_row, end_row) - 0-indexed rows
DEFAULT_COMPONENT_DEFS = [
    ("Main Logo", 0, 19),        # Lines 1-20: The PH logo
    ("Title Text", 3, 4),        # Line 4: "THE PINNACLE OF HAKCING QUALITY"
    ("Divider Line", 16, 17),    # Line 17: ===[ haKCer ]===
    ("Arrows", 17, 20),          # Lines 18-21: Arrow decorations
    ("Effects Banner", 20, 21),  # Line 21: EFFECTS decorative line
    ("TESTER ASCII", 22, 31),    # Lines 23-32: The ASCII art "TESTER"
    ("Border Frame", 21, 32),    # Lines 22-33: The | border frame
]


def find_banner_files(path: Path) -> list[Path]:
    """Find all .txt banner files in a path."""
    if path.is_file():
        return [path]
    elif path.is_dir():
        # Look for txt files, prioritize banner_full.txt if exists
        files = list(path.glob("*.txt"))
        return sorted(files, key=lambda f: (f.name != "banner_full.txt", f.name))
    return []


def auto_split_components(lines: list[str], num_components: int = 4) -> list[tuple]:
    """Auto-split a banner into roughly equal components."""
    total_lines = len(lines)
    chunk_size = max(1, total_lines // num_components)

    components = []
    for i in range(num_components):
        start = i * chunk_size
        end = min((i + 1) * chunk_size, total_lines) if i < num_components - 1 else total_lines
        components.append((f"Section {i+1}", start, end))

    return components


class BannerComponent:
    """A single banner component with its own effect/theme."""
    def __init__(self, index: int, name: str, start_row: int, end_row: int):
        self.index = index
        self.name = name
        self.start_row = start_row
        self.end_row = end_row
        self.effect_idx = 0  # 0 = none
        self.theme_idx = 0
        self.animating = True
        self.frame = 0

    @property
    def effect(self) -> str:
        return EFFECTS[self.effect_idx]

    @property
    def theme(self) -> str:
        return THEME_LIST[self.theme_idx]


class HakcerTester:
    def __init__(self, banner_path: Path = None):
        self.banner_path = banner_path or DEFAULT_DIR
        self.banner_files: list[Path] = []
        self.current_banner_idx = 0
        self.components: list[BannerComponent] = []
        self.canvas_lines: list[str] = []

        # Find available banners
        self.banner_files = find_banner_files(self.banner_path)
        if not self.banner_files:
            # Fallback to default
            self.banner_files = find_banner_files(DEFAULT_DIR)

        self.load_banner(0)

        self.frame = 0
        self.selected_component = 0
        self.dropdown_open = None  # None, 'component', 'effect', 'theme', 'banner'
        self.dropdown_idx = 0
        self.global_animating = True
        self.app = None
        self.h_padding = 0

    def load_banner(self, idx: int):
        """Load a specific banner file by index."""
        if not self.banner_files:
            self.canvas_lines = ["No banner files found!"]
            self.components = [BannerComponent(0, "Empty", 0, 1)]
            return

        self.current_banner_idx = idx % len(self.banner_files)
        banner_file = self.banner_files[self.current_banner_idx]

        # Load banner content
        content = banner_file.read_text()
        self.canvas_lines = content.split('\n')
        # Remove trailing empty lines
        while self.canvas_lines and not self.canvas_lines[-1].strip():
            self.canvas_lines.pop()

        self.banner_width = max(len(line) for line in self.canvas_lines) if self.canvas_lines else 100

        # Determine component definitions
        self.components = []
        if banner_file.name == "banner_full.txt" and banner_file.parent == DEFAULT_DIR:
            # Use predefined components for the default banner
            for i, (name, start, end) in enumerate(DEFAULT_COMPONENT_DEFS):
                comp = BannerComponent(i, name, start, end)
                comp.theme_idx = i % len(THEME_LIST)
                self.components.append(comp)
        else:
            # Auto-split for other banners
            num_sections = min(6, max(2, len(self.canvas_lines) // 5))
            defs = auto_split_components(self.canvas_lines, num_sections)
            for i, (name, start, end) in enumerate(defs):
                comp = BannerComponent(i, name, start, end)
                comp.theme_idx = i % len(THEME_LIST)
                self.components.append(comp)

        self.selected_component = 0

    @property
    def current_banner_name(self) -> str:
        if self.banner_files:
            return self.banner_files[self.current_banner_idx].name
        return "none"

    def update_centering(self):
        """Update horizontal padding based on current terminal width."""
        try:
            term_width = shutil.get_terminal_size().columns
        except:
            term_width = 120
        self.h_padding = max(0, (term_width - self.banner_width) // 2)

    @property
    def current_component(self) -> BannerComponent:
        return self.components[self.selected_component]

    def get_theme_colors(self, theme_name: str = None) -> list:
        if theme_name is None:
            theme_name = self.current_component.theme
        theme = THEMES.get(theme_name, THEMES["synthwave"])
        colors = theme["colors"]
        primary = colors.get("primary", ["ff00ff"])
        accent = colors.get("accent", ["00ffff"])
        result = primary[:2] + accent[:2]
        while len(result) < 4:
            result.append(result[0])
        return result

    def get_component_for_position(self, row: int) -> BannerComponent:
        """Find which component owns a given row. Later definitions override earlier ones."""
        owner = self.components[0]  # Default to Main Logo
        for comp in self.components:
            if comp.start_row <= row < comp.end_row:
                owner = comp
        return owner

    def apply_effect_char(self, char: str, x: int, y: int, effect: str, frame: int, colors: list) -> tuple:
        """Apply effect to a character. Returns (char, color_index, bold, dim)."""
        if effect == "none" or not char.strip():
            return (char, 0, False, False)

        if effect == "decrypt":
            scramble = "!@#$%^&*()_+-=[]{}|;:',.<>?/~`0123456789"
            if random.random() < max(0, 0.25 - frame * 0.008):
                return (random.choice(scramble), (x + y) % len(colors), True, False)
            return (char, (x + y + frame) % len(colors), True, False)

        elif effect == "matrix":
            drop = (frame + x * 2) % 40
            if y > drop:
                return (random.choice("01"), 1, False, True)
            elif y == drop:
                return (char, 0, True, False)
            return (char, 0, True, False)

        elif effect == "typewriter":
            reveal = frame * 3
            pos = y * 100 + x
            if pos > reveal:
                return (' ', 0, False, False)
            elif pos > reveal - 5:
                return (char, 0, True, False)
            return (char, 1, False, False)

        elif effect == "glitch":
            glitch = "▓▒░█▄▀▐▌"
            if random.random() < 0.05:
                return (random.choice(glitch), random.randint(0, len(colors)-1), True, False)
            return (char, (x + frame) % len(colors), False, False)

        elif effect == "waves":
            wave = math.sin((x + frame) * 0.15) + math.sin((y + frame) * 0.2)
            idx = int((wave + 2) / 4 * len(colors)) % len(colors)
            return (char, idx, wave > 0.5, False)

        elif effect == "synthgrid":
            idx = (x + y + frame) % len(colors)
            return (char, idx, True, False)

        elif effect == "fireworks":
            sparkle = "✦✧★☆·"
            if random.random() < 0.04:
                return (random.choice(sparkle), random.randint(0, len(colors)-1), True, False)
            return (char, (x * y + frame) % len(colors), False, False)

        elif effect == "vhstape":
            band = (y + frame // 2) % 12
            if band < 2 and random.random() < 0.4:
                return ('▒', 1, False, True)
            return (char, (frame + x) % len(colors), False, False)

        elif effect == "rain":
            drop = (frame * 2 + x * 7) % 30
            if y == drop % 25:
                return (char, 0, True, False)
            return (char, 1, False, y > drop % 25)

        elif effect == "scan":
            scan_y = frame % 35
            dist = abs(y - scan_y)
            if dist < 2:
                return (char, 0, True, False)
            elif dist < 4:
                return (char, 1, False, False)
            return (char, 2, False, True)

        return (char, 0, False, False)

    def render_banner(self) -> list:
        """Render the full banner with per-component effects."""
        result = []
        pad = " " * self.h_padding

        for y, line in enumerate(self.canvas_lines):
            # Add centering padding
            result.append(("", pad))

            # Find which component owns this row
            comp = self.get_component_for_position(y)
            colors = self.get_theme_colors(comp.theme)
            frame = comp.frame if comp.animating and self.global_animating else 0

            for x, char in enumerate(line):
                if comp.effect == "none" or not comp.animating or not self.global_animating:
                    result.append((f"#{colors[0]}", char))
                else:
                    new_char, color_idx, bold, dim = self.apply_effect_char(
                        char, x, y, comp.effect, frame, colors
                    )
                    style = f"#{colors[color_idx % len(colors)]}"
                    if bold:
                        style += " bold"
                    if dim:
                        style += " dim"
                    result.append((style, new_char))

            result.append(("", "\n"))

        return result

    def render_controls(self) -> FormattedText:
        """Render the control panel."""
        colors = self.get_theme_colors()
        c1, c2, c3 = colors[0], colors[1], colors[2] if len(colors) > 2 else colors[0]

        comp = self.current_component
        result = []
        pad = " " * self.h_padding

        # Banner selector row (if multiple banners available)
        if len(self.banner_files) > 1:
            result.append(("", "\n"))
            result.append(("", pad))
            result.append((f"#{c2}", "              "))
            banner_style = f"#{c1} bold underline" if self.dropdown_open == 'banner' else f"#{c2} bold"
            result.append((banner_style, f" ▼ Banner: {self.current_banner_name:<25} "))
            result.append(("", "\n"))

            # Banner dropdown list
            if self.dropdown_open == 'banner':
                for i, bf in enumerate(self.banner_files):
                    marker = "► " if i == self.dropdown_idx else "  "
                    style = f"#{c1} bold reverse" if i == self.dropdown_idx else f"#{c2}"
                    result.append(("", pad))
                    result.append((f"#{c2}", "              "))
                    result.append((style, f" {marker}{bf.name:<30} "))
                    result.append(("", "\n"))
                result.append(("", "\n"))

        # Component selector row
        result.append(("", "\n"))
        result.append(("", pad))
        result.append((f"#{c2}", "                                    "))
        comp_style = f"#{c1} bold underline" if self.dropdown_open == 'component' else f"#{c2} bold"
        result.append((comp_style, f" ▼ Component: {comp.name:<15} "))

        result.append(("", "\n\n"))

        # Component dropdown
        if self.dropdown_open == 'component':
            for i, c in enumerate(self.components):
                marker = "► " if i == self.dropdown_idx else "  "
                eff_info = f"[{c.effect}]" if c.effect != "none" else ""
                style = f"#{c1} bold reverse" if i == self.dropdown_idx else f"#{c2}"
                result.append(("", pad))
                result.append((f"#{c2}", "                                    "))
                result.append((style, f" {marker}{c.name:<15} {eff_info:<12} "))
                result.append(("", "\n"))
            result.append(("", "\n"))

        # Effect and Theme row
        result.append(("", pad))
        result.append((f"#{c2}", "                "))

        # Effect dropdown
        eff_style = f"#{c1} bold underline" if self.dropdown_open == 'effect' else f"#{c2} bold"
        result.append((eff_style, f" ▼ Effect: {comp.effect:<12} "))

        result.append((f"#{c2}", "                           "))

        # Theme dropdown
        thm_style = f"#{c1} bold underline" if self.dropdown_open == 'theme' else f"#{c2} bold"
        result.append((thm_style, f" ▼ Theme: {comp.theme:<12} "))

        result.append(("", "\n\n"))

        # Effect dropdown list
        if self.dropdown_open == 'effect':
            for i, eff in enumerate(EFFECTS):
                marker = "► " if i == self.dropdown_idx else "  "
                style = f"#{c1} bold reverse" if i == self.dropdown_idx else f"#{c2}"
                result.append(("", pad))
                result.append((f"#{c2}", "                "))
                result.append((style, f" {marker}{eff:<14} "))
                result.append(("", "\n"))
            result.append(("", "\n"))

        # Theme dropdown list
        if self.dropdown_open == 'theme':
            for i, thm in enumerate(THEME_LIST):
                marker = "► " if i == self.dropdown_idx else "  "
                style = f"#{c1} bold reverse" if i == self.dropdown_idx else f"#{c2}"
                t_colors = self.get_theme_colors(thm)
                result.append(("", pad))
                result.append((f"#{c2}", "                                                       "))
                result.append((style, f" {marker}{thm:<12} "))
                result.append((f"#{t_colors[0]}", "█"))
                result.append((f"#{t_colors[1]}", "█"))
                result.append(("", "\n"))
            result.append(("", "\n"))

        # GO and STOP buttons
        result.append(("", pad))
        result.append((f"#{c2}", "                                  "))
        result.append((f"#{c3} bold", "   ▶ GO   "))
        result.append((f"#{c2}", "         "))
        anim_label = "■ STOP ALL" if self.global_animating else "▶ START ALL"
        result.append((f"#{c2}", f"   {anim_label}   "))

        result.append(("", "\n\n"))
        result.append(("", pad))
        help_text = "Tab ↑↓ Enter | Space: toggle | s: stop | b: banners | q: quit"
        result.append((f"#{c2} dim", f"              {help_text}"))
        result.append(("", "\n"))

        return FormattedText(result)

    def get_full_display(self) -> FormattedText:
        """Combine banner and controls."""
        banner = self.render_banner()
        controls = self.render_controls()
        return FormattedText(banner + list(controls))

    def generate_code(self) -> str:
        """Generate code for components with effects."""
        lines = ["# haKCer multi-component banner configuration\n"]
        lines.append("from hakcer import show_banner, set_theme\n\n")

        for comp in self.components:
            if comp.effect != "none":
                lines.append(f"# {comp.name} (rows {comp.start_row+1}-{comp.end_row})\n")
                lines.append(f"set_theme(\"{comp.theme}\")\n")
                lines.append(f"# Effect: {comp.effect}\n\n")

        return "".join(lines)


def main():
    parser = argparse.ArgumentParser(description="haKCer Effects Tester - Test effects on ASCII banners")
    parser.add_argument("path", nargs="?", default=None,
                        help="Path to banner file or directory containing .txt files")
    args = parser.parse_args()

    banner_path = Path(args.path) if args.path else None
    tester = HakcerTester(banner_path)
    result_action = [None]

    kb = KeyBindings()

    @kb.add('q')
    def quit_(event):
        event.app.exit()

    @kb.add('tab')
    def next_dropdown(event):
        if tester.dropdown_open is None:
            if len(tester.banner_files) > 1:
                tester.dropdown_open = 'banner'
                tester.dropdown_idx = tester.current_banner_idx
            else:
                tester.dropdown_open = 'component'
                tester.dropdown_idx = tester.selected_component
        elif tester.dropdown_open == 'banner':
            tester.dropdown_open = 'component'
            tester.dropdown_idx = tester.selected_component
        elif tester.dropdown_open == 'component':
            tester.dropdown_open = 'effect'
            tester.dropdown_idx = tester.current_component.effect_idx
        elif tester.dropdown_open == 'effect':
            tester.dropdown_open = 'theme'
            tester.dropdown_idx = tester.current_component.theme_idx
        else:
            tester.dropdown_open = None

    @kb.add('escape')
    def close_dropdown(event):
        tester.dropdown_open = None

    @kb.add('up')
    def up(event):
        if tester.dropdown_open == 'banner':
            tester.dropdown_idx = (tester.dropdown_idx - 1) % len(tester.banner_files)
        elif tester.dropdown_open == 'component':
            tester.dropdown_idx = (tester.dropdown_idx - 1) % len(tester.components)
        elif tester.dropdown_open == 'effect':
            tester.dropdown_idx = (tester.dropdown_idx - 1) % len(EFFECTS)
        elif tester.dropdown_open == 'theme':
            tester.dropdown_idx = (tester.dropdown_idx - 1) % len(THEME_LIST)

    @kb.add('down')
    def down(event):
        if tester.dropdown_open == 'banner':
            tester.dropdown_idx = (tester.dropdown_idx + 1) % len(tester.banner_files)
        elif tester.dropdown_open == 'component':
            tester.dropdown_idx = (tester.dropdown_idx + 1) % len(tester.components)
        elif tester.dropdown_open == 'effect':
            tester.dropdown_idx = (tester.dropdown_idx + 1) % len(EFFECTS)
        elif tester.dropdown_open == 'theme':
            tester.dropdown_idx = (tester.dropdown_idx + 1) % len(THEME_LIST)

    @kb.add('enter')
    def select(event):
        if tester.dropdown_open == 'banner':
            tester.load_banner(tester.dropdown_idx)
            tester.dropdown_open = None
        elif tester.dropdown_open == 'component':
            tester.selected_component = tester.dropdown_idx
            tester.dropdown_open = None
        elif tester.dropdown_open == 'effect':
            tester.current_component.effect_idx = tester.dropdown_idx
            tester.current_component.frame = 0
            tester.dropdown_open = None
        elif tester.dropdown_open == 'theme':
            tester.current_component.theme_idx = tester.dropdown_idx
            tester.dropdown_open = None
        else:
            result_action[0] = 'go'
            event.app.exit(result='go')

    @kb.add('space')
    def toggle_all(event):
        tester.global_animating = not tester.global_animating

    @kb.add('s')
    def stop_current(event):
        """Toggle current component's animation."""
        tester.current_component.animating = not tester.current_component.animating

    @kb.add('a')
    def start_all(event):
        """Start all component animations."""
        for comp in tester.components:
            comp.animating = True
        tester.global_animating = True

    @kb.add('b')
    def banner_select(event):
        """Open banner selector."""
        if len(tester.banner_files) > 1:
            tester.dropdown_open = 'banner'
            tester.dropdown_idx = tester.current_banner_idx

    @kb.add('g')
    def go(event):
        result_action[0] = 'go'
        event.app.exit(result='go')

    def mouse_handler(mouse_event):
        """Handle mouse clicks."""
        if mouse_event.event_type == MouseEventType.MOUSE_UP:
            row = mouse_event.position.y
            col = mouse_event.position.x - tester.h_padding

            # Banner ends at canvas line count
            banner_lines = len(tester.canvas_lines)

            # Component dropdown row
            comp_row = banner_lines + 1
            if row == comp_row and 36 <= col <= 70:
                if tester.dropdown_open == 'component':
                    tester.dropdown_open = None
                else:
                    tester.dropdown_open = 'component'
                    tester.dropdown_idx = tester.selected_component
                return

            # Component dropdown items
            if tester.dropdown_open == 'component':
                item_start = banner_lines + 3
                item_idx = row - item_start
                if 0 <= item_idx < len(tester.components) and 36 <= col <= 75:
                    tester.selected_component = item_idx
                    tester.dropdown_open = None
                    return

            # Effect/Theme row
            eff_row = banner_lines + 3
            if tester.dropdown_open == 'component':
                eff_row += len(tester.components) + 1

            # Effect dropdown button
            if row == eff_row and 16 <= col <= 45:
                if tester.dropdown_open == 'effect':
                    tester.dropdown_open = None
                else:
                    tester.dropdown_open = 'effect'
                    tester.dropdown_idx = tester.current_component.effect_idx
                return

            # Theme dropdown button
            if row == eff_row and 55 <= col <= 85:
                if tester.dropdown_open == 'theme':
                    tester.dropdown_open = None
                else:
                    tester.dropdown_open = 'theme'
                    tester.dropdown_idx = tester.current_component.theme_idx
                return

            # Effect dropdown items
            if tester.dropdown_open == 'effect':
                item_start = eff_row + 2
                item_idx = row - item_start
                if 0 <= item_idx < len(EFFECTS) and 16 <= col <= 45:
                    tester.current_component.effect_idx = item_idx
                    tester.current_component.frame = 0
                    tester.dropdown_open = None
                    return

            # Theme dropdown items
            if tester.dropdown_open == 'theme':
                item_start = eff_row + 2
                item_idx = row - item_start
                if 0 <= item_idx < len(THEME_LIST) and 55 <= col <= 85:
                    tester.current_component.theme_idx = item_idx
                    tester.dropdown_open = None
                    return

            # GO button
            btn_row = eff_row + 2
            if tester.dropdown_open == 'effect':
                btn_row += len(EFFECTS) + 1
            elif tester.dropdown_open == 'theme':
                btn_row += len(THEME_LIST) + 1

            if row == btn_row and 34 <= col <= 44:
                result_action[0] = 'go'
                tester.app.exit(result='go')
                return

            # STOP ALL button
            if row == btn_row and 54 <= col <= 72:
                tester.global_animating = not tester.global_animating
                return

    def get_content():
        tester.frame += 1
        tester.update_centering()
        for comp in tester.components:
            if comp.animating and tester.global_animating and comp.effect != "none":
                comp.frame += 1
        return tester.get_full_display()

    content = FormattedTextControl(get_content)
    main_window = Window(content=content)
    main_window.content.mouse_handler = mouse_handler

    layout = Layout(main_window)

    app = Application(
        layout=layout,
        key_bindings=kb,
        full_screen=True,
        refresh_interval=0.08,
        mouse_support=True,
    )
    tester.app = app

    while True:
        result = app.run()

        if result == 'go' or result_action[0] == 'go':
            result_action[0] = None
            print("\033[2J\033[H")
            print("\n  Current configuration:\n")

            for comp in tester.components:
                status = "animating" if comp.animating else "stopped"
                print(f"  {comp.name}: {comp.effect} + {comp.theme} ({status})")

            print("\n═══ GENERATED CODE ═══\n")
            print(tester.generate_code())

            input("\nPress Enter to continue...")
            for comp in tester.components:
                comp.frame = 0
        else:
            break

    print("\nBye!\n")


if __name__ == "__main__":
    main()
