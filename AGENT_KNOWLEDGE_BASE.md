# Global Agent Knowledge Base & Instructional Set

This document is the **Single Source of Truth** for all AI agents (Claude, Cursor, Gemini, etc.) working on Sonotheia and related repositories. You MUST refer to this before and during your tasks.

> **License**: This document and the associated codebase are licensed under the [MIT License](LICENSE). When using or adapting code from this repository, include the original copyright notice. Third-party dependencies retain their original licenses.

---

## 0. Prime Directives (NON-NEGOTIABLE)

1. **Patent Compliance**:
    * **NEVER** use Linear Predictive Coding (LPC), source-filter models, glottal closure/opening detection, or static formant values.
    * **ALWAYS** use dynamic trajectories, phase analysis, and velocity-based methods.

2. **Security & Privacy**:
    * **NEVER** log raw audio bytes, PII, or API keys.
    * **ALWAYS** use environment variables for secrets.

3. **Design Philosophy (The Advisory Council)**:
    * **Dieter Rams ("Less but Better")**: Radical simplification. If a feature adds complexity without proportional value, kill it.
    * **Daniel Kahneman ("System 2 Thinking")**: Code should handle failure gracefully. validation before execution.
    * **Constraint**: No "branding" of these names in code. Use descriptive names.

4. **Agent Behavior: "Defense Against Complexity"**:
    * **Stop and Think**: Before writing code, ask: "Is this the simplest way to solve the user's *actual* problem?"
    * **No Speculative Features**: Do not add "nice to have" flexibility. Build exactly what is needed now.
    * **Refactor First**: If the code is hard to change, refactor it first. Do not pile hacks on top of technical debt.
    * **Error Prevention**:
        * **Type Safety**: Use Pydantic strict mode where possible.
        * **Fail Fast**: Validate inputs at the boundary (API/CLI), not deep in the stack.
        * **Atomic Operations**: Side effects (DB writes, File IO) should be isolated.

---

## 1. Operational Guardrails

* **Config**: `pyproject.toml` is the source of truth for tooling. `settings.yaml` (or equivalent) for app config.
* **Audio**: Float32 mono 16kHz numpy arrays only.
* **Dependencies**: Lock versions. Do not upgrade without explicit instruction. Use pragmatic dependency management - avoid unnecessary dependencies, but framework dependencies (e.g., FastAPI for API modules) are acceptable when appropriate.

---

## 2. Coding Standards (The "Gold Standard")

* **Python**:
  * **Formatter**: `black` (line-length: 100)
  * **Linter**: `ruff` (Select: E, F, I, N, W, B). Imports must be sorted (`I`).
  * **Typing**: `mypy` required for all new code.
  * **Style**: Use `snake_case` for functions and variables, `PascalCase` for classes.
* **Frontend**:
  * **Framework**: React 18 + MUI 5
  * **Style**: Use `camelCase` for JavaScript variables and functions, `PascalCase` for components.
* **Structure**:
  * **src-layout**: All code lives in `src/<package_name>/`.
  * **No Root Scripts**: Scripts belong in `scripts/` or `bin/`.
* **Configuration**: `backend/config/settings.yaml` is the SINGLE source of truth for application configuration.

---

## 3. Common Pitfalls & Anti-Patterns

### Code Duplication

* **Duplicate Logic**: Do not copy-paste LLM handling or Config loading. Use `shared-ai-utils`.
* **Custom Providers**: Never implement custom LLM provider logic. Use `shared-ai-utils.LLMManager`.

### Error Handling

* **Silent Failures**: Never `except Exception: pass`. Log the error or re-raise.
* **Bare Except**: Use specific exception types: `except (TypeError, ValueError) as e:`

### Architecture

* **Global State**: Minimize module-level globals. Use dependency injection.
* **Magic Numbers**: Extract constants to a config or constants file.

### Environment & Tooling

* **Virtual Environments**: Always use `.venv` (not `venv`). Check for duplicates before creating new ones.
* **Pre-commit Hooks**: When updating Python versions, ensure pre-commit tool versions support it (e.g., `black 26.1.0+` for Python 3.13).
* **Version Conflicts**: If pre-commit fails with "invalid target-version", update the tool in `.pre-commit-config.yaml`, not `pyproject.toml`.
* **Bypassing Hooks**: Use `--no-verify` only for structural migrations, not to hide code quality issues.
* **IDE Setup**: Enable "Format on Save" and configure linter to use `.pre-commit-config.yaml` (see AGENT_KNOWLEDGE_BASE.md).
* **Bulk Operations**: Use `git diff --stat` to audit changes, then run `python3 -m compileall .` before committing (see AGENT_KNOWLEDGE_BASE.md).

### Import Management

* **Circular Imports**: Use Protocol pattern (typing.Protocol) for dependency-free interfaces.
* **Import Order**: Run `ruff check --fix` or `isort` to auto-fix import sorting issues.

---

## 4. Key Commands

### Python

```bash
black .              # Format Python
flake8 .             # Lint Python (if using flake8 instead of ruff)
pytest               # Test backend
```

### Frontend

```bash
npm test             # Test frontend
```

---

## 5. Key Paths

* `backend/api/main.py` - Entry point
* `backend/config/settings.yaml` - Configuration
* `backend/sensors/` - Sensor implementations
* `frontend/src/App.js` - Frontend entry

---

## 6. AI-Assisted Development

* **Feedback Loop**: When generating code, checking for errors, or reviewing PRs, ALWAYS consider patterns from the **Feedback Loop** library if available (run `feedback-loop memory query` or check `.feedback_loop/patterns.json`).
* **Learn from Failures**: If a test fails, run `feedback-loop analyze` to update the pattern library before attempting a fix.

---

## 7. Documentation

* Update `README.md` if installation steps change.
* Update `AGENT_KNOWLEDGE_BASE.md` if you discover a new recurrent issue.

### Documentation Standards

* **Markdown Linting**: When creating or editing markdown files, ensure all headings are unique to avoid markdownlint MD024 errors. If multiple sections use the same heading text (e.g., "Problem Statement", "Solution Overview"), make them unique by adding context (e.g., "Problem Statement - Error Handling", "Problem Statement - Onboarding"). Always run markdownlint before committing documentation changes.

* **Heading Spacing (MD022)**: Headings must be surrounded by blank lines both above and below. This applies to all heading levels (##, ###, ####, etc.). For example:

  ```markdown
  ## Section Title
  
  Content here...
  
  ### Subsection
  
  More content...
  ```

  Always ensure there's a blank line after headings, especially before code blocks, lists, or other content.

* **Code Block Spacing (MD031)**: Fenced code blocks (```) must be surrounded by blank lines both above and below. Always add a blank line before opening a code block and after closing it.

* **Markdown Tables**: When creating markdown tables, use the "compact" style format required by markdownlint MD060. This means separator rows must have spaces around pipes: `| ------ | ------ |` instead of `|------|------|`. The header row and separator row must have consistent spacing. Always verify table formatting with markdownlint before committing.

---

## 8. Reasoning Logs

After significant tasks (complex, architectural, refactoring, non-obvious bug fixes), create a reasoning log entry at `feedback-loop/agent_reasoning_logs/logs/YYYY-MM-DD_sono-platform_task.md` (see template: `feedback-loop/agent_reasoning_logs/templates/reasoning_entry.md`).
