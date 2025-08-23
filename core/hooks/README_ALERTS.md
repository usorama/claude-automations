# Claude Code Audible Alert System

This document describes the restored audible alert system for Claude Code completion events.

## Overview

The alert system provides voice notifications for important Claude Code events, including:
- Task completion
- Waiting for user input
- Command blocking (security)
- Errors and critical events

## Components

### 1. Notification Alert Script
**File**: `~/.claude/hooks/notification_alert.py`
- Main alert handler that processes notification events
- Uses macOS `say` command for text-to-speech
- Fallback to Linux TTS options (pico2wave, espeak)
- Smart filtering to prevent alert fatigue

### 2. Claude Settings Configuration
**File**: `~/.claude/settings.json`
- Notification hook configuration
- Stop hook configuration for task completion
- Terminal bell preference setting

### 3. Test Script
**File**: `~/.claude/hooks/test_alert.py`
- Test script to verify alert functionality
- Run with: `python3 ~/.claude/hooks/test_alert.py`

## Alert Triggers

The system will play voice alerts for these events:

### High Priority (Victoria voice, faster rate)
- Command blocked for security
- Errors and critical failures

### Normal Priority (Alex voice, normal rate)
- Task completion
- Waiting for user input
- Session finished
- Ready for next command

## Configuration

### Enable/Disable Alerts
Edit `~/.claude/settings.json` and modify the hooks section:

```json
"hooks": {
  "Notification": [{
    "hooks": [{
      "type": "command",
      "command": "python3 ~/.claude/hooks/notification_alert.py"
    }]
  }],
  "Stop": [{
    "hooks": [{
      "type": "command", 
      "command": "python3 ~/.claude/hooks/notification_alert.py"
    }]
  }]
}
```

### Notification Channel
Set preferred notification channel:

```json
"preferredNotifChannel": "terminal_bell"
```

Options:
- `terminal_bell` - System bell + voice alerts
- `iterm2` - iTerm2 notifications only
- `notifications_disabled` - No notifications

## Troubleshooting

### No Sound
1. Check system volume
2. Verify `say` command works: `say "test"`
3. Check terminal audio permissions in System Preferences

### Script Errors
1. Run test script: `python3 ~/.claude/hooks/test_alert.py`
2. Check Python path and permissions
3. Enable debug mode: set `CLAUDE_DEBUG=true`

### Hook Not Triggering
1. Verify hook is registered: check `~/.claude/settings.json`
2. Restart Claude Code to reload settings
3. Check hook file permissions: `ls -la ~/.claude/hooks/`

## Customization

### Voice Settings
Edit `notification_alert.py` and modify the `play_alert_sound()` function:
- Change voice: `voice = "Samantha"` (macOS voices)
- Change rate: `rate = "200"` (words per minute)
- Add different voices for different events

### Alert Messages
Edit `get_voice_message()` function to customize spoken messages:

```python
if "task complete" in message.lower():
    return "Your custom completion message"
```

### Alert Filtering
Edit `should_notify()` function to add/remove trigger conditions:

```python
# Add new trigger patterns
if "custom pattern" in message.lower():
    return True
```

## Installation Verification

To verify the system is installed correctly:

1. **Test the alert system**:
   ```bash
   python3 ~/.claude/hooks/test_alert.py
   ```

2. **Check settings**:
   ```bash
   cat ~/.claude/settings.json | grep -A 10 "hooks"
   ```

3. **Test voice command directly**:
   ```bash
   say "Claude Code alerts are working"
   ```

## Backup and Restore

### Backup Current Configuration
```bash
cp ~/.claude/settings.json ~/.claude/settings.json.backup
cp -r ~/.claude/hooks ~/.claude/hooks.backup
```

### Restore from Backup
```bash
cp ~/.claude/settings.json.backup ~/.claude/settings.json
cp -r ~/.claude/hooks.backup ~/.claude/hooks
```

---

**Note**: This alert system was restored from the IronClaude project configuration and adapted for your current Claude Code setup. The system is designed to be lightweight and non-intrusive while providing clear audio feedback for important events.