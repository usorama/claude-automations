#!/bin/bash
# Run project-specific tests after changes

FILE_PATH="$1"
PROJECT_TYPE="$2"

case "$PROJECT_TYPE" in
    node)
        if [[ "$FILE_PATH" == *.test.js || "$FILE_PATH" == *.spec.js ]]; then
            npm test -- "$FILE_PATH" 2>&1 | tee -a .claude/logs/test-results.log
        fi
        ;;
    python)
        if [[ "$FILE_PATH" == *_test.py || "$FILE_PATH" == test_*.py ]]; then
            python -m pytest "$FILE_PATH" 2>&1 | tee -a .claude/logs/test-results.log
        fi
        ;;
esac
