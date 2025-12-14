#!/usr/bin/env python3
"""
90s NFO Style Hacker Banner with ASCII Sparkle Effects
Authentic warez scene aesthetic
"""

import random
import time
import sys
import os

# ANSI color codes for that classic scene look
CYAN = '\033[96m'
MAGENTA = '\033[95m'
WHITE = '\033[97m'
YELLOW = '\033[93m'
RED = '\033[91m'
GREEN = '\033[92m'
BLUE = '\033[94m'
DIM = '\033[2m'
BRIGHT = '\033[1m'
RESET = '\033[0m'
BLINK = '\033[5m'

# Sparkle characters for animation
SPARKLES = ['✦', '✧', '◆', '◇', '★', '☆', '·', '•', '∙', '°', '¤', '×', '+', '`', "'"]

NFO_ART = r"""
{CYAN}·bg.                                                                              .gb·
{MAGENTA}  :bg:                                                                          :gb:
{CYAN}    ²bg,.                    {YELLOW}*{CYAN}                              {YELLOW}*{CYAN}                .,gb²
{WHITE}       `bg,.    {YELLOW}✦{WHITE}    ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄    {YELLOW}✦{WHITE}   .,gb`
{DIM}═════════════════════════════════════════════════════════════════════════════════════════{RESET}
{CYAN}
                 ██████████                                      {YELLOW}·�·{CYAN}
                █▓       ░██                                           {YELLOW}✧{CYAN}
                █▒        ██ {WHITE}{BRIGHT}T H E   P I N A C L E  O F  H A K C I N G   Q U A L I T Y{RESET}{CYAN}
    █████████████░        █████████████████ ████████████ ████████████      ████████████
   ██         ███░        ███▓▒▒▒▒▒▒▒▒▒▒▒██ █▒▒▒▒▒▒▒▒▓████        █████████▓          ▒█
   ██  {YELLOW}✧{CYAN}      ███         ███▒▒▒▒▒▒▒▒▒▒▒▒▓██████████████▓        ███▓▒      ▒▓░       ▒█
   ██         ███        ░██▓▒▒▒▒▒▒▒▒▒▒▒▒▒▓██▓▒▒▒▒▒▒▒▒█▓        ███░       ░██░       ▒█
   ██         ███        ▒██▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒██▓▒▒▒▒▒▒▒▓▒        ██  ▓        ██░  {YELLOW}◆{CYAN}   ▓█
   ██         ██▓        ███▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒█▓▒▒▒▒▒▒▒▓▒       ██   █        ██░       ▓
   ██         ██▒        ██▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓▒▒▒▒▒▒▒▓▒      ██    █        ▓█████████
   ██     {YELLOW}★{CYAN}              ██▒▒▒▒▒▒▒▒█▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▒   ▒███████ █░       ░▓        █
   ██         ░░         ██▒▒▒▒▒▒▒▒██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓█ ▓        ░█ ▓       ░▒       ░█
   ██         ██░       ░█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓█ █░        ▒ █                ░█
   ██   {YELLOW}·{CYAN}     ██        ▓█▒▒▒▒▒▒▒▒▒██▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓█ █░        ▒ █░               ▒█
    ██████████  ███████████▓██▓▓█▓█  █▓▒▒▒▒▒▒▒▒▒▓██▓██   █▓▓▓▓▓▓▓█    █▓▓▓▓▓▓/\▓▓▓▓▓▓██
{MAGENTA}  .:/_______________________█▓██▓██__________████▓█▓█_███___________________.  /  \._______\:.
{MAGENTA}     _ __ _________________  ██▓██ ____________ █▓▓▓██ ██ ____________________. \/ /\._____ ___
{DIM}                               █▓█               ██▓██                         \  /
                                ██                 ███                          \/
{RESET}
{DIM}═════════════════════════════════════════════════════════════════════════════════════════{RESET}

{CYAN}     .,gPPRg,                                                              ,gRPPg,.
{MAGENTA}    dP'     `Yb   {WHITE}[{YELLOW}★{WHITE}]{CYAN} E L I T E   W A R E Z   D I V I S I O N {WHITE}[{YELLOW}★{WHITE}]{MAGENTA}   dP'     `Yb
{CYAN}    8)       (8                                                          8)       (8
{MAGENTA}    Yb       dP  {DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{MAGENTA}  Yb       dP
{CYAN}     `8ggg8P'                                                              `P8ggg8'
{RESET}

{DIM}┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  {CYAN}✦{DIM} rELEASE......: {WHITE}H4KR T00LZ v3.1337{DIM}                  {CYAN}✦{DIM} dATE.........: {WHITE}XX/XX/XXXX{DIM}       │
│  {CYAN}✦{DIM} cRACKED BY...: {WHITE}iNNER CiRCLE{DIM}                        {CYAN}✦{DIM} sUPPLiER.....: {WHITE}[ANONYMOUS]{DIM}     │
│  {CYAN}✦{DIM} pROTECTiON...: {WHITE}QUANTUM ENCRYPTED{DIM}                   {CYAN}✦{DIM} tYPE.........: {WHITE}UTIL{DIM}           │
│  {CYAN}✦{DIM} OS...........: {WHITE}*NIX / WIN / MAC{DIM}                    {CYAN}✦{DIM} DiSK(s)......: {WHITE}01/01{DIM}          │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│   {WHITE}[{CYAN}!{WHITE}]{DIM} iNSTALL NOTES:                                                              │
│                                                                                         │
│       {CYAN}1.{DIM} Unpack archive to desired location                                         │
│       {CYAN}2.{DIM} Run setup.exe / ./install.sh                                               │
│       {CYAN}3.{DIM} Copy crack to installation directory                                       │
│       {CYAN}4.{DIM} ???                                                                        │
│       {CYAN}5.{DIM} PROFIT                                                                     │
│                                                                                         │
│   {WHITE}[{YELLOW}!{WHITE}]{DIM} Remember: Sharing is caring. Support the scene.                            │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘{RESET}

{MAGENTA}      ▄▄▄   ▄▄▄ ▄▄▄▄▄▄▄   ▄▄▄▄▄▄▄   ▄▄▄▄▄▄▄   ▄▄▄▄▄▄▄   ▄▄▄   ▄▄▄▄▄▄▄   ▄▄▄▄▄▄▄
{MAGENTA}     █   █ █   █       █ █       █ █       █ █   ▄   █ █   █ █       █ █       █
{MAGENTA}     █   █▄█   █    ▄▄▄█ █▄     ▄█ █   ▄   █ █  █ █  █ █   █ █    ▄  █ █    ▄▄▄█
{MAGENTA}     █        ██   █▄▄▄   █   █   █  █ █  █ █   █▄█  █▄█   █ █   █▄█ █ █   █▄▄▄
{MAGENTA}     █        ██    ▄▄▄█  █   █   █  █▄█  █ █    ▄▄▄▄█    ▄█ █    ▄▄▄█ █    ▄▄▄█
{MAGENTA}     █   █▄█   █   █▄▄▄   █   █   █       █ █   █    █   █▄  █   █     █   █▄▄▄
{MAGENTA}     █▄▄▄█ █▄▄▄█▄▄▄▄▄▄▄█  █▄▄▄█   █▄▄▄▄▄▄▄█ █▄▄▄█    █▄▄▄▄▄█ █▄▄▄█     █▄▄▄▄▄▄▄█
{RESET}
{DIM}─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─{RESET}
{WHITE}                  {CYAN}[{WHITE}01{CYAN}]{WHITE} iNFiLTRATE SYSTEM            {CYAN}[{WHITE}05{CYAN}]{WHITE} dECRYPT FILES
                  {CYAN}[{WHITE}02{CYAN}]{WHITE} sCAN NETWORK                {CYAN}[{WHITE}06{CYAN}]{WHITE} lAUNCH PAYLOAD
                  {CYAN}[{WHITE}03{CYAN}]{WHITE} bYPASS FiREWALL              {CYAN}[{WHITE}07{CYAN}]{WHITE} cOVER TRACKS
                  {CYAN}[{WHITE}04{CYAN}]{WHITE} eXTRACT DATA                 {CYAN}[{WHITE}00{CYAN}]{WHITE} eXiT TO SHELL{RESET}
{DIM}─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─·─{RESET}

{CYAN}  .,gb²      {YELLOW}✧ {WHITE}gREETZ: #h4x0rz · #crax0rz · #elite · pHEAR cREW · RAZOR · MYTH{YELLOW} ✧{CYAN}      ²bg,.
{MAGENTA}      :bg:  {DIM}« iF U CAN READ THiS, U R 2 CLOSE 2 UR MONiTOR »{MAGENTA}  :gb:
{CYAN}        `bg,.__________________________________________________________________.,gb`{RESET}

{DIM}                           ·bg.  {CYAN}NFO by [Anonymous] 2024{DIM}  .gb·{RESET}
""".format(
    CYAN=CYAN, MAGENTA=MAGENTA, WHITE=WHITE, YELLOW=YELLOW,
    RED=RED, GREEN=GREEN, BLUE=BLUE, DIM=DIM, BRIGHT=BRIGHT, RESET=RESET
)


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def animate_sparkles(iterations=100, delay=0.12):
    """Animate sparkles across the display."""
    lines = NFO_ART.split('\n')

    # Pre-calculate sparkle candidate positions (empty spaces)
    sparkle_candidates = []
    for i, line in enumerate(lines):
        # Strip ANSI codes to find actual character positions
        clean_line = line
        for code in [CYAN, MAGENTA, WHITE, YELLOW, RED, GREEN, BLUE, DIM, BRIGHT, RESET]:
            clean_line = clean_line.replace(code, '')

        for j in range(len(clean_line)):
            if clean_line[j] == ' ' and random.random() < 0.008:
                sparkle_candidates.append((i, j))

    for frame in range(iterations):
        clear_screen()

        # Active sparkles for this frame
        active_sparkles = {}
        for pos in sparkle_candidates:
            if random.random() < 0.15:  # 15% chance each frame
                sparkle = random.choice(SPARKLES)
                color = random.choice([CYAN, MAGENTA, YELLOW, WHITE])
                active_sparkles[pos] = (sparkle, color)

        # Render with sparkles
        for i, line in enumerate(lines):
            output_line = ""
            char_idx = 0
            j = 0

            while j < len(line):
                # Check for ANSI escape sequences
                if line[j] == '\033':
                    # Find end of escape sequence
                    end = j
                    while end < len(line) and line[end] != 'm':
                        end += 1
                    output_line += line[j:end+1]
                    j = end + 1
                    continue

                # Regular character
                if (i, char_idx) in active_sparkles:
                    sparkle, color = active_sparkles[(i, char_idx)]
                    if line[j] == ' ':
                        output_line += f"{color}{sparkle}{RESET}"
                    else:
                        output_line += line[j]
                else:
                    output_line += line[j]

                char_idx += 1
                j += 1

            print(output_line)

        # Animated border sparkle effect at bottom
        border_sparkle = ''.join(random.choice(['·', '•', '°', '∙', ' ', ' ', ' '])
                                  for _ in range(80))
        print(f"{DIM}{CYAN}{border_sparkle}{RESET}")

        time.sleep(delay)


def print_static():
    """Print the banner without animation."""
    print(NFO_ART)


def print_with_typing(delay=0.001):
    """Print with retro typing effect."""
    in_escape = False
    for char in NFO_ART:
        sys.stdout.write(char)
        sys.stdout.flush()

        if char == '\033':
            in_escape = True
        elif in_escape and char == 'm':
            in_escape = False
        elif not in_escape and char not in [' ', '\n']:
            time.sleep(delay)


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description='90s NFO Style Banner')
    parser.add_argument('--animate', '-a', action='store_true',
                        help='Enable sparkle animation')
    parser.add_argument('--typing', '-t', action='store_true',
                        help='Enable typing effect')
    parser.add_argument('--frames', '-f', type=int, default=100,
                        help='Animation frames (default: 100)')
    args = parser.parse_args()

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


if __name__ == "__main__":
    main()
