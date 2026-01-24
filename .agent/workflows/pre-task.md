---
description: Pre-task instructions for all agents working on this Sonotheia repository
---

# Before Starting Any Task

Before making ANY changes, read the `AGENT_KNOWLEDGE_BASE.md` file in the repository root.

```bash
cat AGENT_KNOWLEDGE_BASE.md
```

This file contains critical instructions including:

1. **Patent Compliance** - NEVER use LPC, source-filter models, or static formant values
2. **Security** - NEVER log API keys, PII, or raw audio bytes
3. **Coding Standards** - black, flake8, Pydantic
4. **Audio Format** - float32 mono numpy arrays at 16kHz

## Verification

After completing your task, run the pre-commit checklist:

```bash
# Format and lint
black .
flake8 .

# Check YAML
yamllint .

# Run all pre-commit hooks (final check)
pre-commit run --all-files

# Run tests
pytest
```

**CRITICAL**: See `.agent/workflows/pre-commit-checklist.md` for detailed requirements to prevent commit failures.
