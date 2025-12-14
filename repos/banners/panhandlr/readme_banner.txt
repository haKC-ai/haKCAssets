.
├── analyzers/                # Contains JSON dork files
│   └── sharepoint.json
├── analysis/                 # Directory for all output reports
├── modules/                  # Core logic scripts
│   ├── google_dorks_standalone.py  # Handles the dorking phase
│   └── url2ioc.py                  # Handles the analysis and reporting phase
├── panhandlr.py              # Main entry point with the user interface
├── requirements.txt          # Python dependencies
├── banner.txt                # ASCII art banner
└── start_main.sh             # Helper script to run the application