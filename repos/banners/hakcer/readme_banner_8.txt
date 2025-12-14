════════════════════════════════════════════════════════════════════════════════
  INTEGRATION NOTES:
  
  [*] Always check sys.stdout.isatty() - don't spam logs with ANSI codes
  [*] Provide a --no-banner flag (someone will need it)
  [*] Default to fast effects (production users will thank you)
  [*] Use environment variables for Docker/CI/CD friendliness
  [*] If your tool gets piped to other commands, banners will auto-disable
════════════════════════════════════════════════════════════════════════════════