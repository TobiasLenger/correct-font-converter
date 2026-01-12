#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$DIR/.venv"

# Ensure venv exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Please run ./woff2otf.sh first to setup the environment."
    exit 1
fi

# Run the GUI
"$VENV_DIR/bin/python3" "$DIR/gui_app.py"
