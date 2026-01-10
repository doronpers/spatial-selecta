te#!/bin/bash

# Standardization Setup Script
# Use this to quickly apply global standards to any new repository.

echo "🚀 Starting Repository Standardization..."

# 1. Create Governance Directory
mkdir -p Documentation/Governance

# 2. Deploy Standards Files (Replace URLs with your actual hosted raw URLs)
# Note: For now, we mimic the file creation. In a real scenario, use curl.
cat <<EOF > Documentation/Governance/AGENT_REFORMATTING_GUIDELINES.md
$(cat /Volumes/Treehorn/Gits/sonotheia-enhanced/Documentation/Governance/AGENT_REFORMATTING_GUIDELINES.md)
EOF

cat <<EOF > Documentation/Governance/AGENT_BEHAVIORAL_STANDARDS.md
$(cat /Volumes/Treehorn/Gits/sonotheia-enhanced/Documentation/Governance/AGENT_BEHAVIORAL_STANDARDS.md)
EOF

# 3. Create/Update .flake8
cat <<EOF > .flake8
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,venv,.venv
EOF

# 4. Update root pyproject.toml if it exists
if [ -f "pyproject.toml" ]; then
    echo "Updating pyproject.toml..."
    # Ensure tool.black and tool.isort are present (Simplified append)
    echo "" >> pyproject.toml
    echo "[tool.black]" >> pyproject.toml
    echo "line-length = 88" >> pyproject.toml
    echo "" >> pyproject.toml
    echo "[tool.isort]" >> pyproject.toml
    echo "profile = \"black\"" >> pyproject.toml
    echo "line_length = 88" >> pyproject.toml
fi

# 5. Add "Priming" instructions to README.md
if ! grep -q "AGENT_BEHAVIORAL_STANDARDS" README.md; then
    echo -e "\n## Agent Instructions\nThis repository follows [Agent Behavioral Standards](Documentation/Governance/AGENT_BEHAVIORAL_STANDARDS.md). All AI agents MUST read these before performing any tasks." >> README.md
fi

echo "✅ Standardization Complete! Run 'black .' to finalize."
