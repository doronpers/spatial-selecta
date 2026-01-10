# Agent Reformatting & Linting Guidelines

**Purpose**: A standardized instruction set for AI agents to synchronize repository-wide formatting and linting to the 88-character standard.

## 1. Configuration Check

Before reformatting, ensure the following configuration files exist at the repository root and are synchronized:

### A. `.flake8` (Root)

Ensure `max-line-length` is set to 88 and conflicts with `black` are ignored.

```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,venv,.venv
```

### B. `pyproject.toml` (Root & Sub-projects)

Ensure `black` and `isort` are explicitly configured to 88 characters.

```toml
[tool.black]
line-length = 88
target-version = ["py311"]

[tool.isort]
profile = "black"
line_length = 88
```

## 2. Execution Steps

Follow these steps in order to ensure a clean transition:

1. **Clean Workspace**: Ensure there are no uncommitted changes before starting.
2. **Apply Configurations**: Create or update `.flake8` and `pyproject.toml` as described above.
3. **Run Black**: Execute `black . --line-length 88` from the root.
4. **Run Isort**: Execute `isort .` (if available) to synchronize import ordering.
5. **Verify with Flake8**: Run `flake8 .` and resolve any remaining `E501` errors that automated tools missed (e.g., in complex docstrings or long strings).
6. **Documentation**: Update the repository's governance documentation (e.g., `DOCUMENTATION_ORGANIZATION_STANDARDS.md`) to reflect the 88-character requirement.

## 3. Maintenance Rules

- **Pre-commit Hooks**: Always check `.pre-commit-config.yaml` to ensure automated gates match these standards.
- **Surgical Fixes**: If a line MUST exceed 88 characters (e.g., a URL), use `# noqa: E501` sparingly.
- **Agent Priming**: When starting a new task, agents should read these guidelines to prevent introducing formatting regressions.
