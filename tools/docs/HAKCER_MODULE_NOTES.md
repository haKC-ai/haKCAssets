# How `hakcer` Module Works (Technical Deep Dive)

The `hakcer` module is a wrapper around `terminaltexteffects` that provides themed ASCII banner animations.

## Architecture

```
hakcer/
├── __init__.py      # Exports: show_banner, list_effects, set_theme, etc.
├── banner.py        # Core effect logic, effect configs, show_banner()
└── themes.py        # Color palettes (THEMES dict), theme management
```

## Core Function: `show_banner()`

```python
from hakcer import show_banner

show_banner(
    effect_name="decrypt",      # Specific effect OR None for random
    speed_preference="fast",    # "fast" | "medium" | "slow" | "any" (used when effect_name=None)
    hold_time=1.5,              # Seconds to display after animation
    clear_after=False,          # Clear terminal when done
    theme="synthwave",          # Color theme name
    custom_text=None,           # Inline ASCII art string
    custom_file="banner.txt",   # Path to ASCII art file (overrides custom_text)
)
```

## How Effects Work Internally

1. **Effect Selection** (line 424-439):
   ```python
   if effect_name:
       selected_effect = effect_name
   else:
       # Random selection based on speed_preference
       if speed_preference == "fast":
           selected_effect = random.choice(FAST_EFFECTS)
       elif speed_preference == "medium":
           selected_effect = random.choice(MEDIUM_EFFECTS)
       # ...
   ```

2. **Effect Config Generation** - `_get_effect_config()` maps effect name -> `terminaltexteffects` module + themed args:
   ```python
   configs = {
       "decrypt": {
           "module": effect_decrypt,
           "class_name": "Decrypt",
           "args": [
               "--typing-speed", "2",
               "--ciphertext-colors"] + colors["accent"] + [
               "--final-gradient-stops"] + colors["gradient_stops"],
       },
       # ... 20+ more effects
   }
   ```

3. **Effect Instantiation** (line 447-455):
   ```python
   effect_class, config_class = config["module"].get_effect_and_args()
   kwargs = _parse_args_to_kwargs(config["args"])  # CLI-style args -> kwargs
   effect_config = config_class(**kwargs)
   effect = effect_class(ascii_art)
   effect.effect_config = effect_config
   ```

4. **Render Loop** (line 457-459):
   ```python
   with effect.terminal_output() as terminal:
       for frame in effect:
           terminal.print(frame)
   ```

## Speed Categories

| Speed | Effects |
|-------|---------|
| **FAST** | `expand`, `overflow`, `rain`, `random_sequence`, `scattered`, `slide` |
| **MEDIUM** | `beams`, `bouncyballs`, `burn`, `errorcorrect`, `pour`, `spray`, `wipe` |
| **SLOW** | `binarypath`, `blackhole`, `colorshift`, `crumble`, `decrypt`, `fireworks`, `matrix`, `rings`, `spotlights`, `synthgrid`, `unstable`, `vhstape`, `waves` |

**Broken effects (excluded):** `orbittingvolley`, `swarm`

## Theme Structure

Each theme defines hex color arrays:
```python
"synthwave": {
    "colors": {
        "primary": ["00D9FF", "FF10F0", "7928CA"],  # Main gradient
        "accent": ["FF0080", "00F0FF"],              # Highlights
        "error": ["FF006E"],                         # Error states
        "gradient_stops": ["00D9FF", "FF10F0", "7928CA"],
        "beam_colors": ["00D9FF", "FF0080"],         # For beam effects
    }
}
```

**Available themes:** `cyberpunk`, `dracula`, `gruvbox`, `matrix`, `neon`, `nord`, `synthwave`, `tokyo_night`, `tokyo_night_storm`

---

## TESTING FINDINGS: CRITICAL BUG

### Bug: SLOW_EFFECTS Not Exposed

**Location:** `banner.py` line 357

```python
# CURRENT (BROKEN):
ALL_EFFECTS = FAST_EFFECTS + MEDIUM_EFFECTS

# SHOULD BE:
ALL_EFFECTS = FAST_EFFECTS + MEDIUM_EFFECTS + SLOW_EFFECTS
```

### Impact

| API Call | Result |
|----------|--------|
| `list_effects()` | Returns only 13 effects (missing 13 SLOW effects) |
| `show_banner(effect_name="decrypt")` | **FAILS** - ValueError: Unknown effect |
| `show_banner(effect_name="matrix")` | **FAILS** - ValueError: Unknown effect |
| `show_banner(speed_preference="slow")` | **WORKS** - bypasses validation, random selection |

### Effects That CANNOT Be Called By Name

These 13 effects exist in config but fail validation:
- `binarypath`, `blackhole`, `colorshift`, `crumble`, `decrypt`
- `fireworks`, `matrix`, `rings`, `spotlights`, `synthgrid`
- `unstable`, `vhstape`, `waves`

### Workaround

Use `speed_preference="slow"` for random slow effect selection:
```python
# This works (random slow effect):
show_banner(speed_preference="slow", theme="matrix")

# This FAILS:
show_banner(effect_name="decrypt", theme="matrix")  # ValueError!
```

### gitcloakd Impact

The current gitcloakd usage in `main.py`:
```python
show_banner(custom_file=banner_path, effect_name='decrypt', theme='synthwave', hold_time=2.0)
```

**This will FAIL** if hakcer is updated or reinstalled with this bug. The fallback banner (`_print_fallback_banner()`) catches this exception, so the CLI still works but loses the animation.

---

## Examples: Combining Effects & Randomization

### 1. Random effect from speed category:
```python
from hakcer import show_banner

# Random fast effect with cyberpunk colors
show_banner(speed_preference="fast", theme="cyberpunk")

# Random from ALL effects (currently only FAST+MEDIUM due to bug)
show_banner(speed_preference="any", theme="matrix")

# Random SLOW effect (WORKS despite bug - bypasses validation)
show_banner(speed_preference="slow", theme="synthwave")
```

### 2. Specific effect + theme combo (FAST/MEDIUM only due to bug):
```python
# These work:
show_banner(effect_name="rain", theme="matrix", hold_time=3.0)
show_banner(effect_name="burn", theme="synthwave")

# These FAIL (slow effects):
# show_banner(effect_name="decrypt", theme="matrix")  # ValueError!
# show_banner(effect_name="fireworks", theme="neon")  # ValueError!
```

### 3. Randomize both effect AND theme:
```python
import random
from hakcer import show_banner, list_effects, list_themes

# Note: list_effects() only returns FAST+MEDIUM effects
show_banner(
    effect_name=random.choice(list_effects()),
    theme=random.choice(list_themes()),
    hold_time=2.0
)
```

### 4. Weighted random (favor fast effects):
```python
import random
from hakcer import show_banner, get_effects_by_speed

weights = {"fast": 0.6, "medium": 0.3, "slow": 0.1}
speed = random.choices(list(weights.keys()), weights=list(weights.values()))[0]

# Use speed_preference instead of effect_name to work around bug
show_banner(speed_preference=speed, theme="neon")
```

### 5. Custom banner with random effect:
```python
show_banner(
    custom_file="/path/to/my_banner.txt",
    speed_preference="medium",  # Use this instead of effect_name for reliability
    theme="dracula",
    hold_time=1.0,
    clear_after=True
)
```

### 6. Inline ASCII art:
```python
my_art = """
    +===============+
    |  MY CLI TOOL  |
    +===============+
"""
show_banner(custom_text=my_art, effect_name="rain", theme="tokyo_night")
```

### 7. Global theme + random effects:
```python
from hakcer import set_theme, show_banner

set_theme("cyberpunk")  # Set globally

# All subsequent calls use cyberpunk
show_banner(speed_preference="fast")  # Random fast effect
show_banner(speed_preference="medium")  # Random medium effect
```

### 8. Effect rotation (only works for FAST+MEDIUM):
```python
from hakcer import show_banner, list_effects

effects = list_effects()  # Only 13 effects due to bug
for i, effect in enumerate(effects):
    print(f"Showing {effect} ({i+1}/{len(effects)})")
    show_banner(effect_name=effect, theme="synthwave", hold_time=0.5)
```
