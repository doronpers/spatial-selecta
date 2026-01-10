#!/bin/bash
#
# Standardization Setup Script
#
# This script applies global standards to a repository, including:
# - Governance documentation deployment
# - Code formatting configuration (Black, isort, flake8)
# - Pre-commit hooks setup
# - .gitignore and .editorconfig creation
#
# Usage:
#   ./scripts/standardize_repo.sh
#   STANDARDS_SOURCE_DIR=/path/to/standards ./scripts/standardize_repo.sh
#   RUN_BLACK=true ./scripts/standardize_repo.sh
#   CLEANUP_BACKUPS=true ./scripts/standardize_repo.sh
#
# Environment Variables:
#   STANDARDS_SOURCE_DIR  - Path to governance standards directory
#                          (default: /Volumes/Treehorn/Gits/sonotheia-enhanced/documentation/Governance)
#   RUN_BLACK             - Auto-run black formatter after setup (default: false)
#   CLEANUP_BACKUPS       - Remove backup files older than 30 days (default: false)
#
# Exit codes:
#   0 - Success
#   1 - Partial failure (some operations failed)
#   2 - Critical failure (could not proceed)

# Strict error handling
set -euo pipefail

# Version constants (updated as of Jan 2026)
readonly BLACK_VERSION="25.1.0"
readonly ISORT_VERSION="6.0.0"
readonly FLAKE8_VERSION="7.1.2"
readonly PRE_COMMIT_HOOKS_VERSION="v4.6.0"

# Configuration
readonly SOURCE_DIR="${STANDARDS_SOURCE_DIR:-/Volumes/Treehorn/Gits/sonotheia-enhanced/documentation/Governance}"
readonly RUN_BLACK="${RUN_BLACK:-false}"
readonly CLEANUP_BACKUPS="${CLEANUP_BACKUPS:-false}"

# Track operations for summary
OPERATIONS_SUCCESS=()
OPERATIONS_FAILED=()

# Helper: Backup file
backup_file() {
    local file="$1"
    if [ -f "$file" ]; then
        local backup="${file}.bak.$(date +%s)"
        if cp "$file" "$backup" 2>/dev/null; then
            echo "📦 Backed up $file to $backup"
        else
            echo "⚠️  Failed to backup $file"
        fi
    fi
}

# Helper: Add pattern to .gitignore if not present
add_to_gitignore() {
    local pattern="$1"
    if [ ! -f ".gitignore" ]; then
        touch .gitignore
        OPERATIONS_SUCCESS+=("Created .gitignore")
    fi
    if ! grep -qF "$pattern" .gitignore 2>/dev/null; then
        echo "$pattern" >> .gitignore
        OPERATIONS_SUCCESS+=("Added $pattern to .gitignore")
    fi
}

# Helper: Check if tool is available
check_tool() {
    local tool="$1"
    if command -v "$tool" &> /dev/null; then
        return 0
    else
        echo "⚠️  $tool not found (optional, but recommended for full workflow)"
        return 1
    fi
}

# Helper: Validate source directory
validate_source_dir() {
    if [[ "$SOURCE_DIR" =~ \.\. ]]; then
        echo "❌ Invalid source directory (contains '..'): $SOURCE_DIR"
        OPERATIONS_FAILED+=("Invalid source directory path")
        return 1
    fi
    
    if [ ! -d "$SOURCE_DIR" ]; then
        echo "⚠️  Source directory not found: $SOURCE_DIR"
        echo "   Set STANDARDS_SOURCE_DIR environment variable or update script default."
        echo "   Continuing without governance file deployment..."
        return 1
    fi
    return 0
}

# Helper: Update pyproject.toml with tool configs
update_pyproject_toml() {
    local toml_file="$1"
    local updated=false
    
    if [ ! -f "$toml_file" ]; then
        return 0
    fi
    
    backup_file "$toml_file"
    
    if ! grep -q "\[tool.black\]" "$toml_file" 2>/dev/null; then
        {
            echo ""
            echo "[tool.black]"
            echo "line-length = 88"
        } >> "$toml_file"
        updated=true
        OPERATIONS_SUCCESS+=("Added [tool.black] to $toml_file")
    fi
    
    if ! grep -q "\[tool.isort\]" "$toml_file" 2>/dev/null; then
        {
            echo ""
            echo "[tool.isort]"
            echo "profile = \"black\""
            echo "line_length = 88"
        } >> "$toml_file"
        updated=true
        OPERATIONS_SUCCESS+=("Added [tool.isort] to $toml_file")
    fi
    
    if [ "$updated" = false ]; then
        OPERATIONS_SUCCESS+=("Skipped $toml_file update (already configured)")
    fi
}

echo "🚀 Starting Repository Standardization..."
echo "📁 Source directory: $SOURCE_DIR"
echo ""

# Validate source directory
if ! validate_source_dir; then
    echo "⚠️  Continuing with limited functionality (governance files will be skipped)"
    echo ""
fi

# Check for recommended tools
echo "🔍 Checking for recommended tools..."
check_tool black || true
check_tool isort || true
check_tool flake8 || true
check_tool pre-commit || true
echo ""

# 1. Create Governance Directory
if mkdir -p documentation/Governance 2>/dev/null; then
    chmod 755 documentation/Governance 2>/dev/null || true
    OPERATIONS_SUCCESS+=("Created documentation/Governance directory")
else
    echo "❌ Failed to create documentation/Governance directory (check permissions)"
    OPERATIONS_FAILED+=("Failed to create documentation/Governance directory")
fi

# 2. Deploy Standards Files (only if source directory exists)
if [ -d "$SOURCE_DIR" ]; then
    if [ -f "$SOURCE_DIR/AGENT_REFORMATTING_GUIDELINES.md" ]; then
        if cat "$SOURCE_DIR/AGENT_REFORMATTING_GUIDELINES.md" > documentation/Governance/AGENT_REFORMATTING_GUIDELINES.md 2>/dev/null; then
            OPERATIONS_SUCCESS+=("Deployed AGENT_REFORMATTING_GUIDELINES.md")
        else
            OPERATIONS_FAILED+=("Failed to deploy AGENT_REFORMATTING_GUIDELINES.md")
        fi
    else
        echo "⚠️  AGENT_REFORMATTING_GUIDELINES.md not found in $SOURCE_DIR"
        OPERATIONS_FAILED+=("AGENT_REFORMATTING_GUIDELINES.md not found")
    fi
    
    if [ -f "$SOURCE_DIR/AGENT_BEHAVIORAL_STANDARDS.md" ]; then
        if cat "$SOURCE_DIR/AGENT_BEHAVIORAL_STANDARDS.md" > documentation/Governance/AGENT_BEHAVIORAL_STANDARDS.md 2>/dev/null; then
            OPERATIONS_SUCCESS+=("Deployed AGENT_BEHAVIORAL_STANDARDS.md")
        else
            OPERATIONS_FAILED+=("Failed to deploy AGENT_BEHAVIORAL_STANDARDS.md")
        fi
    else
        echo "⚠️  AGENT_BEHAVIORAL_STANDARDS.md not found in $SOURCE_DIR"
        OPERATIONS_FAILED+=("AGENT_BEHAVIORAL_STANDARDS.md not found")
    fi
else
    echo "⚠️  Skipping governance file deployment (source directory not available)"
fi

# 3. Create/Update .flake8
backup_file ".flake8"
if cat <<EOF > .flake8
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,venv,.venv,node_modules,dist,build,.mypy_cache,.pytest_cache
EOF
then
    chmod 644 .flake8 2>/dev/null || true
    OPERATIONS_SUCCESS+=("Created/updated .flake8")
else
    OPERATIONS_FAILED+=("Failed to create/update .flake8")
fi

# 4. Update root pyproject.toml if it exists
if [ -f "pyproject.toml" ]; then
    echo "Checking pyproject.toml for tool configurations..."
    update_pyproject_toml "pyproject.toml"
fi

# 5. Update subdirectory pyproject.toml files (optional, non-blocking)
echo "Checking subdirectory pyproject.toml files..."
find . -name "pyproject.toml" -not -path "./.git/*" -not -path "./venv/*" -not -path "./.venv/*" -not -path "./node_modules/*" | while read -r toml_file; do
    if [ "$toml_file" != "./pyproject.toml" ]; then
        update_pyproject_toml "$toml_file"
    fi
done

# 6. Add "Priming" instructions to README.md
if [ -f "README.md" ]; then
    if ! grep -q "AGENT_BEHAVIORAL_STANDARDS" README.md 2>/dev/null; then
        backup_file "README.md"
        if {
            echo ""
            echo "## Agent Instructions"
            echo "This repository follows [Agent Behavioral Standards](documentation/Governance/AGENT_BEHAVIORAL_STANDARDS.md). All AI agents MUST read these before performing any tasks."
        } >> README.md; then
            OPERATIONS_SUCCESS+=("Added Agent Instructions to README.md")
        else
            OPERATIONS_FAILED+=("Failed to add Agent Instructions to README.md")
        fi
    else
        OPERATIONS_SUCCESS+=("Skipped README.md update (already contains Agent Instructions)")
    fi
else
    echo "⚠️  README.md not found - skipping agent instructions"
    OPERATIONS_FAILED+=("README.md not found")
fi

# 7. Update .gitignore
backup_file ".gitignore"

# Basic Python ignores
add_to_gitignore "__pycache__"
add_to_gitignore "*.pyc"
add_to_gitignore ".DS_Store"
add_to_gitignore "venv/"
add_to_gitignore ".venv/"
add_to_gitignore ".env"
add_to_gitignore ".mypy_cache/"
add_to_gitignore ".pytest_cache/"

# Backup files created by this script
add_to_gitignore "*.bak.*"

# Additional common ignores
add_to_gitignore "*.log"
add_to_gitignore ".env.local"
add_to_gitignore ".env.*.local"
add_to_gitignore "coverage/"

# 8. Create .editorconfig
if [ ! -f ".editorconfig" ]; then
    if cat <<EOF > .editorconfig
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.py]
indent_style = space
indent_size = 4
max_line_length = 88

[*.{js,jsx,ts,tsx,json}]
indent_style = space
indent_size = 2

[*.md]
trim_trailing_whitespace = false

[*.{yml,yaml}]
indent_style = space
indent_size = 2

[Makefile]
indent_style = tab
EOF
    then
        chmod 644 .editorconfig 2>/dev/null || true
        OPERATIONS_SUCCESS+=("Created .editorconfig")
    else
        OPERATIONS_FAILED+=("Failed to create .editorconfig")
    fi
else
    OPERATIONS_SUCCESS+=("Skipped .editorconfig (already exists)")
fi

# 9. Create/Update .pre-commit-config.yaml
if [ ! -f ".pre-commit-config.yaml" ]; then
    if cat <<EOF > .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: ${BLACK_VERSION}
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: ${ISORT_VERSION}
    hooks:
      - id: isort
        args: ["--profile", "black"]
  - repo: https://github.com/pycqa/flake8
    rev: ${FLAKE8_VERSION}
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: ${PRE_COMMIT_HOOKS_VERSION}
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-toml
EOF
    then
        chmod 644 .pre-commit-config.yaml 2>/dev/null || true
        OPERATIONS_SUCCESS+=("Created .pre-commit-config.yaml")
    else
        OPERATIONS_FAILED+=("Failed to create .pre-commit-config.yaml")
    fi
else
    OPERATIONS_SUCCESS+=("Skipped .pre-commit-config.yaml (already exists)")
fi

# 10. Create .env.example if .env exists but .env.example doesn't
if [ -f ".env" ] && [ ! -f ".env.example" ]; then
    if cat <<EOF > .env.example
# Environment variables template
# Copy this file to .env and fill in the actual values
# Never commit .env to version control

# Example variables (customize for your project):
# API_KEY=your_api_key_here
# DATABASE_URL=postgresql://user:password@localhost/dbname
# DEBUG=false
EOF
    then
        chmod 644 .env.example 2>/dev/null || true
        OPERATIONS_SUCCESS+=("Created .env.example template")
    else
        OPERATIONS_FAILED+=("Failed to create .env.example")
    fi
fi

# 11. Cleanup old backup files (if requested)
if [ "$CLEANUP_BACKUPS" = "true" ]; then
    if find . -name "*.bak.*" -type f -mtime +30 -delete 2>/dev/null; then
        OPERATIONS_SUCCESS+=("Cleaned up backup files older than 30 days")
    else
        # No old backups found is not a failure
        OPERATIONS_SUCCESS+=("No old backup files to clean up")
    fi
fi

# Print summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Standardization Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ${#OPERATIONS_SUCCESS[@]} -gt 0 ]; then
    echo "✅ Successful operations (${#OPERATIONS_SUCCESS[@]}):"
    for op in "${OPERATIONS_SUCCESS[@]}"; do
        echo "   • $op"
    done
fi

if [ ${#OPERATIONS_FAILED[@]} -gt 0 ]; then
    echo ""
    echo "❌ Failed operations (${#OPERATIONS_FAILED[@]}):"
    for op in "${OPERATIONS_FAILED[@]}"; do
        echo "   • $op"
    done
fi

echo ""

# 12. Optional: Run black formatter
if [ "$RUN_BLACK" = "true" ]; then
    if command -v black &> /dev/null; then
        echo "🎨 Running black formatter..."
        if black . 2>/dev/null; then
            OPERATIONS_SUCCESS+=("Ran black formatter")
            echo "✅ Black formatting complete"
        else
            OPERATIONS_FAILED+=("Black formatting failed")
            echo "⚠️  Black formatting encountered errors"
        fi
    else
        echo "⚠️  Black not found - skipping auto-format"
        OPERATIONS_FAILED+=("Black not available for auto-format")
    fi
    echo ""
fi

# Final status
if [ ${#OPERATIONS_FAILED[@]} -eq 0 ]; then
    if [ "$RUN_BLACK" != "true" ]; then
        echo "✅ Standardization Complete!"
        echo "💡 Tip: Run 'black .' to format Python files, or set RUN_BLACK=true"
    else
        echo "✅ Standardization Complete!"
    fi
    echo ""
    echo "📝 Next steps:"
    echo "   1. Review the changes made"
    echo "   2. Install pre-commit hooks: pre-commit install"
    echo "   3. Run black formatter: black ."
    echo "   4. Commit the standardization changes"
    exit 0
else
    echo "⚠️  Standardization completed with errors. Please review above."
    echo "   Some operations failed, but the repository may still be partially standardized."
    exit 1
fi
