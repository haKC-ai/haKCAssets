prompthakcer/
├── manifest.json           # Chrome extension manifest (MV3)
├── rules.json              # Remote-synced optimization rules
├── background/
│   └── service-worker.js   # Background service worker
├── content/
│   ├── content.js          # Content script for AI sites
│   └── modal.css           # On-page modal styles
├── lib/
│   ├── rules-engine.js     # Core optimization engine
│   ├── site-detector.js    # Site detection and config
│   └── history-manager.js  # History management
├── popup/
│   ├── popup.html/css/js   # Extension popup
├── options/
│   ├── options.html/css/js # Settings page
└── icons/
    └── icon*.png           # Extension icons