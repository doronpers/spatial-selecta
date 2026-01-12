# Global Agent Knowledge Base & Instructional Set

This document is the **Single Source of Truth** for all AI agents (Claude, Cursor, etc.) working on Sonotheia and related repositories. You MUST refer to this before and during your tasks.

---

## 0. Prime Directives (NON-NEGOTIABLE)

1. **Patent Compliance**:
    * **NEVER** use Linear Predictive Coding (LPC), source-filter models, glottal closure/opening detection, or static formant values. These are patent-protected.
    * **ALWAYS** use dynamic trajectories, phase analysis, and velocity-based methods (e.g., GlottalInertia, PhaseCoherence).
    * See `documentation/PATENT_COMPLIANCE.md` if available.

2. **Security & Privacy**:
    * **NEVER** log raw audio bytes, PII (Personal Identifiable Information), or secrets (API keys).
    * **ALWAYS** use `get_error_response` for errors to avoid leaking internal stack traces to clients (log them instead).

3. **Design Philosophy (The Advisory Council)**:
    * **Dieter Rams**: "Less but Better". Remove clutter. Unify styles.
    * **Martin Dempsey**: "Make it matter". Focus on mission command and decentralized execution.
    * **Daniel Kahneman**: Reduce cognitive load. "System 1 vs System 2".
    * **Julian Treasure**: Conscious listening. Authentic sound.
    * **CONSTRAINT**: Use these "lenses" to audit and improve, but **DO NOT** brand features with these names (e.g., no "Rams Protocol"). Use descriptive functional names.

4. **Accuracy & Consistency**:
    * Prioritize increasing detection accuracy. Verify changes do not degrade performance.

---

## 1. Operational Guardrails

* **Configuration**: `backend/config/settings.yaml` (or equivalent) is the **SINGLE** source of truth for sensor weights, thresholds, and fusion config. **DO NOT** hardcode weights.
* **Audio Format**: All sensors expect **float32 mono numpy arrays at 16kHz**. Use `backend/sensors/utils.py` for loading/preprocessing.
* **Demo Mode**: **DO NOT** disable `DEMO_MODE` or convert demo features to production without explicit tests, configuration updates, and approval.
* **Dependencies**: **DO NOT** upgrade critical frontend deps (`react`, `react-dom`, `@mui/*`) beyond specified versions (React 18, MUI 5) to maintain build compatibility.

---

## 2. Coding Standards

* **Python**:
  * Formatter: `black`
  * Linter: `flake8`
  * Style: `snake_case` for functions/vars, `PascalCase` for classes.
  * Validation: Use **Pydantic** models for all data structures.
* **Frontend**:
  * Framework: React 18 + Material-UI (MUI).
  * Style: Functional components with hooks. `camelCase` for vars, `PascalCase` for components.
* **Testing**:
  * Backend: `pytest`. Run `pytest` before committing.
  * Frontend: `npm test` (Vitest/Jest).
* **Error Handling**:
  * Sensors must **NEVER** raise exceptions during `analyze()`. Return `SensorResult(passed=None, detail="...")`.

---

## 3. Sensor Development Workflow

When adding or modifying a sensor:

1. **Extend BaseSensor**: Inherit from `BaseSensor`.
2. **Define Category**:
    * `"prosecution"`: Detects FAKE (high score = suspicious).
    * `"defense"`: Detects REAL (high score = authentic).
    * **MUST** include `metadata={"category": self.category}` in `SensorResult`.
3. **Register**: Add to `backend/sensors/registry.py`.
4. **Configure**: Add weights/thresholds to `settings.yaml`.
5. **Test**: Add unit tests in `tests/`.

---

## 4. Common Patterns

**FastAPI Endpoint:**

```python
@router.post("/process")
@limiter.limit("20/minute")
async def process(request: Request, body: MyModel, api_key: str = Depends(verify_api_key)):
    # Validate and process
```

**Logging:**

* `logger.info`: High-level flow.
* `logger.error`: Exceptions (use `exc_info=True`).
* `logger.debug`: Detailed steps (NOT in production).

---

## 5. Quick Reference (Core Platform Map)

*(Note: File paths below refer to the primary `sono-platform` repository. Other repositories may follow `src/` and `tests/` structures.)*

* `backend/api/main.py`: Entry point.
* `backend/config/settings.yaml`: Configuration.
* `backend/sensors/`: Sensor implementations.
* `frontend/src/App.js`: Frontend entry.

---

## Documentation Standards

Follow [Documentation Organization Standards](documentation/governance/DOCUMENTATION_ORGANIZATION_STANDARDS.md)
