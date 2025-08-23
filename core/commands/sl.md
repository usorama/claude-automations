---
description: Statusline shortcut (backup for /statusline)
argument-hint: [show|test|toggle]
allowed-tools: Bash
---

Backup statusline command in case /statusline isn't recognized.

! echo "Statusline Configuration:"
! cat ~/.claude/settings.json | jq '.statusLine' 2>/dev/null || echo "No statusLine configuration found"
! echo ""
! echo "Testing statusline output:"
! ~/.claude/statusline.sh
