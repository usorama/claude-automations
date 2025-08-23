#!/bin/bash
# Development utilities

case "$1" in
    test)
        echo "Running tests..."
        source venv/bin/activate
        pytest tests/ -v --cov=src --cov-report=term-missing
        ;;
    lint)
        echo "Running linters..."
        source venv/bin/activate
        python -m flake8 src/ tests/
        python -m black src/ tests/ --check
        ;;
    format)
        echo "Formatting code..."
        source venv/bin/activate
        python -m black src/ tests/
        ;;
    run)
        echo "Running main program..."
        source venv/bin/activate
        python src/main.py "${@:2}"
        ;;
    *)
        echo "Usage: ./dev.sh {test|lint|format|run}"
        exit 1
        ;;
esac
