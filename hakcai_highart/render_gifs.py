#!/usr/bin/env python3.11
"""
Animated transparent-background GIFs using terminaltexteffects via hakcer.
One GIF per effect, random theme each time.
"""

import os
import re
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ── hakcer internals ─────────────────────────────────────────────────────────
import importlib
import hakcer
import dataclasses
from terminaltexteffects.engine.terminal import TerminalConfig

# ── config ───────────────────────────────────────────────────────────────────
FONT_PATH = "/Users/coriankennedy/Library/Fonts/HackNerdFontMono-Italic.ttf"
FONT_SIZE  = 36
PADDING    = 48
ASCII_FILE = "/Users/coriankennedy/hailogo/hakcai"
OUTPUT_DIR = "/Users/coriankennedy/hailogo/hakcai_highart"

MAX_FRAMES   = 40   # subsample each animation to at most this many frames
FRAME_MS     = 60   # ms per GIF frame

# All effects supported by hakcer (with theme-aware configs)
ALL_EFFECTS = [
    "beams", "binarypath", "blackhole", "bouncyballs", "burn",
    "colorshift", "crumble", "decrypt", "errorcorrect", "expand",
    "fireworks", "matrix", "orbittingvolley", "overflow", "pour",
    "print", "rain", "random_sequence", "rings", "scattered",
    "slide", "spotlights", "spray", "swarm", "synthgrid",
    "unstable", "vhstape", "waves", "wipe",
]
ALL_THEMES = list(hakcer.THEMES.keys())

def make_terminal_config(**overrides):
    """Build a TerminalConfig by unwrapping ArgSpec defaults, then applying overrides."""
    kwargs = {}
    for f in dataclasses.fields(TerminalConfig):
        val = f.default
        if hasattr(val, 'default'):
            val = val.default
        kwargs[f.name] = overrides.get(f.name, val)
    return TerminalConfig(**kwargs)

# ── font setup ────────────────────────────────────────────────────────────────
font    = ImageFont.truetype(FONT_PATH, FONT_SIZE)
char_w  = round(font.getlength("X"))
ascent, descent = font.getmetrics()
line_h  = ascent + descent

# ── ANSI frame parser ─────────────────────────────────────────────────────────
ANSI_RGB  = re.compile(r'\x1b\[38;2;(\d+);(\d+);(\d+)m(.)\x1b\[0m')
ANSI_STRIP = re.compile(r'\x1b\[[^m]*m')

def parse_frame(ansi_str, num_cols, num_rows):
    """
    Parse a terminaltexteffects ANSI frame string into a 2D list of
    (char, r, g, b) tuples. Spaces and unparsed characters are (None,...).
    Returns list of rows, each a list of (char|None, r, g, b).
    """
    rows = ansi_str.split('\n')
    result = []
    for row_idx in range(num_rows):
        row_str = rows[row_idx] if row_idx < len(rows) else ""
        cells = []
        # Build a map: col_index → (char, r, g, b)
        col_map = {}
        # Walk through matches in order
        plain_col = 0
        i = 0
        while i < len(row_str):
            m = ANSI_RGB.match(row_str, i)
            if m:
                r, g, b, ch = int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)
                col_map[plain_col] = (ch, r, g, b)
                plain_col += 1
                i = m.end()
            elif row_str[i] == '\x1b':
                # skip other escape sequences
                end = row_str.find('m', i)
                i = end + 1 if end != -1 else i + 1
            else:
                # plain character (space or other)
                col_map[plain_col] = (row_str[i], 0, 0, 0)
                plain_col += 1
                i += 1
        for col in range(num_cols):
            cells.append(col_map.get(col, (None, 0, 0, 0)))
        result.append(cells)
    return result

def render_parsed_frame(parsed, num_cols, num_rows):
    """Render a parsed frame to an RGBA PIL Image."""
    img_w = num_cols * char_w + PADDING * 2
    img_h = num_rows * line_h  + PADDING * 2
    img   = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    draw  = ImageDraw.Draw(img)
    for row_idx, cells in enumerate(parsed):
        for col_idx, (ch, r, g, b) in enumerate(cells):
            if ch is None or ch == ' ':
                continue
            x = PADDING + col_idx * char_w
            y = PADDING + row_idx * line_h
            draw.text((x, y), ch, font=font, fill=(r, g, b, 255))
    return img

def rgba_to_gif_frame(frame_rgba):
    """Convert RGBA PIL image → palette-mode image suitable for transparent GIF."""
    arr   = np.array(frame_rgba)
    alpha = arr[:, :, 3]
    rgb   = Image.fromarray(arr[:, :, :3], "RGB")
    p_img = rgb.quantize(colors=255, method=Image.Quantize.FASTOCTREE, dither=0)
    pal   = p_img.getpalette()
    pal[255 * 3: 255 * 3 + 3] = [0, 0, 0]
    p_img.putpalette(pal)
    p_arr = np.array(p_img)
    p_arr[alpha < 128] = 255
    result = Image.fromarray(p_arr, "P")
    result.putpalette(pal)
    return result

def save_gif(rgba_frames, path, frame_ms=FRAME_MS):
    gif_frames = [rgba_to_gif_frame(f) for f in rgba_frames]
    gif_frames[0].save(
        path,
        save_all=True,
        append_images=gif_frames[1:],
        loop=0,
        duration=frame_ms,
        disposal=2,
        transparency=255,
        optimize=False,
    )
    kb = os.path.getsize(path) // 1024
    print(f"  → {os.path.basename(path)}  ({len(rgba_frames)} frames, {kb}KB)")

# ── main ──────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(ASCII_FILE) as f:
        ascii_text = f.read()

    ascii_lines = ascii_text.splitlines()
    num_rows = len(ascii_lines)
    num_cols = max(len(l) for l in ascii_lines)

    print(f"Canvas: {num_cols}×{num_rows} chars  →  "
          f"{num_cols*char_w + PADDING*2}×{num_rows*line_h + PADDING*2}px\n")
    print(f"Generating {len(ALL_EFFECTS)} GIFs (one per effect, random theme)...\n")

    for effect_name in ALL_EFFECTS:
        print(f"[{effect_name}]")

        # Load TTE module and run with default config
        mod = importlib.import_module(
            f"terminaltexteffects.effects.effect_{effect_name}"
        )
        _, effect_class, _ = mod.get_effect_resources()
        terminal_cfg = make_terminal_config(ignore_terminal_dimensions=True, canvas_width=-1, canvas_height=-1)
        effect = effect_class(ascii_text, terminal_config=terminal_cfg)

        # Collect all raw ANSI frames
        all_frames = list(effect)

        # Subsample evenly to MAX_FRAMES
        if len(all_frames) <= MAX_FRAMES:
            sampled = all_frames
        else:
            indices = [int(i * (len(all_frames) - 1) / (MAX_FRAMES - 1))
                       for i in range(MAX_FRAMES)]
            sampled = [all_frames[i] for i in indices]

        # Parse + render each sampled frame
        rgba_frames = []
        for ansi in sampled:
            parsed = parse_frame(ansi, num_cols, num_rows)
            rgba_frames.append(render_parsed_frame(parsed, num_cols, num_rows))

        out_path = os.path.join(OUTPUT_DIR, f"haKCai_{effect_name}.gif")
        save_gif(rgba_frames, out_path)

    print(f"\nDone. {len(ALL_EFFECTS)} GIFs in {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
