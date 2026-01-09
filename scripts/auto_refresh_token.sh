#!/bin/bash
# Wrapper script for refreshing Apple Music Token via cron

# Define check paths
PROJECT_DIR="/Volumes/Treehorn/Gits/spatial-selecta"
LOGFILE="$PROJECT_DIR/scripts/refresh_token.log"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python"
SCRIPT_PATH="$PROJECT_DIR/scripts/refresh_token.py"

# Logging start
echo "========================================" >> "$LOGFILE"
echo "Starting refresh at $(date)" >> "$LOGFILE"

# check if directory exists
if [ -d "$PROJECT_DIR" ]; then
    cd "$PROJECT_DIR"
    
    if [ -f "$VENV_PYTHON" ]; then
        "$VENV_PYTHON" "$SCRIPT_PATH" >> "$LOGFILE" 2>&1
    else
         echo "Error: Python venv not found at $VENV_PYTHON" >> "$LOGFILE"
    fi
else
    echo "Error: Project directory not found at $PROJECT_DIR" >> "$LOGFILE"
fi

echo "Finished refresh at $(date)" >> "$LOGFILE"
echo "========================================" >> "$LOGFILE"
