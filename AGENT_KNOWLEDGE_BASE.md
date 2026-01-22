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
* **Dependencies**: Lock versions. Do not upgrade without explicit instruction.

---

## 2. Coding Standards (The "Gold Standard")

* **Python**:
  * **Formatter**: `black` (line-length: 100)
  * **Linter**: `ruff` (Select: E, F, I, N, W, B). Imports must be sorted (`I`).
  * **Typing**: `mypy` required for all new code.
* **Structure**:
  * **src-layout**: All code lives in `src/<package_name>/`.
  * **No Root Scripts**: Scripts belong in `scripts/` or `bin/`.

---

## 3. Common Pitfalls & Anti-Patterns

* **Duplicate Logic**: Do not copy-paste LLM handling or Config loading. Use `shared-ai-utils`.
* **Silent Failures**: Never `except Exception: pass`. Log the error or re-raise.
* **Global State**: Minimize module-level globals. Use dependency injection.
* **Magic Numbers**: Extract constants to a config or constants file.

---

## 4. Documentation

* Update `README.md` if installation steps change.
* Update `AGENT_KNOWLEDGE_BASE.md` if you discover a new recurrent issue.
