#!/bin/bash
# Track file changes for project intelligence

CHANGE_LOG=".claude/logs/changes.log"
CHANGE_TYPE="$1"
FILE_PATH="$2"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Log the change
echo "[$TIMESTAMP] $CHANGE_TYPE: $FILE_PATH" >> "$CHANGE_LOG"

# Update file frequency map
FREQ_MAP=".claude/analytics/file-frequency.json"
if [ ! -f "$FREQ_MAP" ]; then
    echo "{}" > "$FREQ_MAP"
fi

# Track patterns for commonly edited files
if [[ "$FILE_PATH" == *.js || "$FILE_PATH" == *.ts || "$FILE_PATH" == *.py ]]; then
    echo "[$TIMESTAMP] Code pattern: $FILE_PATH" >> ".claude/knowledge-base/code-patterns.log"
fi
