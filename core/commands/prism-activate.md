---
description: Activate PRISM Unified Intelligence System
---

# PRISM Activation

Activate the PRISM Unified Intelligence System for automatic intelligence collection, observable metrics, and failure prevention.

## Usage

```
/prism-activate
```

## What This Does

1. **Creates SQLite database** for intelligence storage
2. **Installs Python dependencies** (rich for dashboard)
3. **Sets up commands** (/prism dashboard access)
4. **Registers hooks** for automatic collection
5. **Runs health check** to verify system
6. **Tests components** to ensure operation
7. **Activates all features**:
   - Automatic intelligence collection
   - Observable metrics dashboard
   - Health monitoring & alerts
   - Cross-repository learning
   - Failure prevention

## After Activation

Use these commands:
- `/prism` - View current metrics
- `/prism health` - System health check
- `/prism alerts` - View active alerts
- `/prism learn` - Show learning patterns
- `/prism live` - Live dashboard

## Implementation

```bash
#!/bin/bash

# Check if activation script exists
ACTIVATION_SCRIPT="$HOME/claude-automations/prism/activate.sh"

if [ ! -f "$ACTIVATION_SCRIPT" ]; then
    echo "❌ PRISM activation script not found"
    echo "Please ensure claude-automations is properly installed"
    exit 1
fi

# Run activation
bash "$ACTIVATION_SCRIPT"
```

$ARGUMENTS