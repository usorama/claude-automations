---
description: Display the current statusline configuration
argument-hint: [show|test|toggle]
allowed-tools: Bash
---

Check and display the current statusline configuration.

Based on the arguments:
- **show**: Display current statusline configuration
- **test**: Test the statusline output  
- **toggle**: Toggle statusline on/off

If no arguments provided, show the current statusline status.

! echo "Statusline Configuration:"
! cat ~/.claude/settings.json | jq '.statusLine' 2>/dev/null || echo "No statusLine configuration found"
! echo ""
! echo "Testing statusline output:"
! ~/.claude/statusline.sh