#!/bin/bash

# Standardization Setup Script
# Use this to quickly apply global standards to any new repository.

echo "🚀 Starting Repository Standardization..."

# 1. Create Governance Directory
mkdir -p Documentation/Governance

# 2. Deploy Standards Files
# Note: For now, we mimic the file creation. In a real scenario, use curl or cp.
SOURCE_DIR="/Volumes/Treehorn/Gits/sonotheia-enhanced/Documentation/Governance"

if [ -f "$SOURCE_DIR/AGENT_REFORMATTING_GUIDELINES.md" ]; then
    cat "$SOURCE_DIR/AGENT_REFORMATTING_GUIDELINES.md" > Documentation/Governance/AGENT_REFORMATTING_GUIDELINES.md
else
    echo "⚠️ AGENT_REFORMATTING_GUIDELINES.md not found in $SOURCE_DIR"
fi

if [ -f "$SOURCE_DIR/AGENT_BEHAVIORAL_STANDARDS.md" ]; then
    cat "$SOURCE_DIR/AGENT_BEHAVIORAL_STANDARDS.md" > Documentation/Governance/AGENT_BEHAVIORAL_STANDARDS.md
else
    echo "⚠️ AGENT_BEHAVIORAL_STANDARDS.md not found in $SOURCE_DIR"
fi

# 3. Create/Update .flake8
cat <<EOF > .flake8
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,venv,.venv
EOF

# 4. Update root pyproject.toml if it exists
if [ -f "pyproject.toml" ]; then
    echo "Checking pyproject.toml for tool configurations..."
    if ! grep -q "\[tool.black\]" pyproject.toml; then
        echo "Adding [tool.black] to pyproject.toml..."
        echo -e "\n[tool.black]\nline-length = 88" >> pyproject.toml
    fi
    if ! grep -q "\[tool.isort\]" pyproject.toml; then
        echo "Adding [tool.isort] to pyproject.toml..."
        echo -e "\n[tool.isort]\nprofile = \"black\"\nline_length = 88" >> pyproject.toml
    fi
fi

# 5. Add "Priming" instructions to README.md
if ! grep -q "AGENT_BEHAVIORAL_STANDARDS" README.md; then
    echo -e "\n## Agent Instructions\nThis repository follows [Agent Behavioral Standards](Documentation/Governance/AGENT_BEHAVIORAL_STANDARDS.md). All AI agents MUST read these before performing any tasks." >> README.md
fi

echo "✅ Standardization Complete! Run 'black .' to finalize."
