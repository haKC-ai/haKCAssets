#!/usr/bin/env python3
"""
haKC Generators - Shared Library
Common utilities for ASCII art generation

signed, /dev/haKCØRY.23
"""

import random
from datetime import datetime

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

# Big text alphabet (5 lines high)
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
    "0": [" ▄██▄ ", " █  █ ", " █  █ ", " █  █ ", " ▀██▀ "],
    "1": ["  █  ", " ██  ", "  █  ", "  █  ", " ███ "],
    "2": [" ▄██▄ ", "    █ ", "  ██  ", " █    ", " ████ "],
    "3": [" ███▄ ", "    █ ", "  ██  ", "    █ ", " ███▀ "],
    "4": [" █  █ ", " █  █ ", " ████ ", "    █ ", "    █ "],
    "5": [" ████ ", " █    ", " ███▄ ", "    █ ", " ███▀ "],
    "6": [" ▄███ ", " █    ", " ███▄ ", " █  █ ", " ▀██▀ "],
    "7": [" ████ ", "    █ ", "   █  ", "  █   ", "  █   "],
    "8": [" ▄██▄ ", " █  █ ", " ▄██▄ ", " █  █ ", " ▀██▀ "],
    "9": [" ▄██▄ ", " █  █ ", " ▀███ ", "    █ ", " ███▀ "],
    " ": ["      ", "      ", "      ", "      ", "      "],
    "-": ["      ", "      ", " ──── ", "      ", "      "],
    ".": ["    ", "    ", "    ", "    ", " ▄  "],
    "_": ["      ", "      ", "      ", "      ", " ──── "],
    ":": ["  ", " ▄", "  ", " ▄", "  "],
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


def random_decoration(category: str = "lines") -> str:
    """Get a random decoration from a category."""
    return random.choice(DECORATIONS.get(category, DECORATIONS["lines"]))


def get_timestamp() -> str:
    """Get current timestamp in standard format."""
    return datetime.now().strftime("%Y-%m-%d")


def get_signature(author: str = "/dev/haKCØRY.23", style: str = "warez") -> str:
    """Generate a signature."""
    if style == "warez":
        return f'───── ▓ signed, {author}: ▓ ─────'
    else:
        return f"─ {author}"
