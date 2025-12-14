CapturedPortal/
├── installer.sh              # Main installer script
├── banner                    # ASCII art banner
├── platformio.ini            # Build configuration
├── DISCLAIMER.md             # Legal disclaimer
├── USAGE_GUIDELINES.md       # Acceptable use policy
├── RESPONSIBLE_DISCLOSURE.md # Vulnerability disclosure policy
├── CODE_OF_CONDUCT.md        # Community standards
├── src/
│   ├── main.cpp              # Entry point
│   ├── core/
│   │   ├── scanner.cpp       # WiFi scanning & portal detection
│   │   ├── enumerator.cpp    # Credential enumeration
│   │   └── power.cpp         # Power management
│   ├── display/
│   │   ├── ui.cpp            # Display UI
│   │   └── effects.cpp       # Hacker animations
│   ├── web/
│   │   └── server.cpp        # Web server & API
│   └── llm/
│       └── engine.cpp        # LLM inference
├── include/
│   └── config.h              # Configuration
├── data/
│   ├── web/                  # Web UI files
│   └── wordlists/            # Enumeration wordlists
└── tools/
    ├── requirements.txt      # Python dependencies (hakcer, platformio, pyserial)
    ├── build.py              # Build & test menu tool
    └── test_portal.py        # Test captive portal server