---
description: Pre-commit checklist to prevent hook failures
---

# Pre-Commit Checklist for Agents

**CRITICAL**: Run this checklist before committing any code to prevent pre-commit hook failures.

## Quick Checklist

Before finishing any task, verify:

- [ ] All required imports are present (check similar existing files)
- [ ] All functions have type hints
- [ ] All modules have docstrings (even `__init__.py`)
- [ ] No unused imports (especially in test files)
- [ ] YAML files use 2-space indentation
- [ ] Long lines are wrapped (max 100 chars)
- [ ] FastAPI `Depends()` uses `# noqa: B008`
- [ ] All pre-commit hooks pass

## Commands to Run

```bash
# 1. Format code
black .

# 2. Check linting
flake8 .

# 3. Check YAML
yamllint .

# 4. Run all pre-commit hooks (final verification)
pre-commit run --all-files
```

## Common Issues & Fixes

### Missing Imports
**Error**: `NameError: name 'X' is not defined` or mypy: `error: Name "X" is not defined`

**Fix**: Add missing imports at top of file. Check similar existing files for import patterns:
- FastAPI: `from fastapi import APIRouter, Depends, HTTPException, status`
- Pydantic: `from pydantic import BaseModel, Field`
- Typing: `from typing import Any, Dict, List, Optional`

### Unused Imports (flake8 F401)
**Error**: `F401 'json' imported but unused`

**Fix**: Remove the unused import or use `# noqa: F401` if needed for dynamic reasons.

### YAML Indentation (yamllint)
**Error**: `error wrong indentation: expected 2 but found 0`

**Fix**: Use 2 spaces for indentation (not tabs, not 4 spaces).

### Missing Docstrings (flake8 D104, D200)
**Error**: `D104 Missing docstring in public package` or `D200 One-line docstring should fit on one line`

**Fix**:
- Add `"""Module description."""` to empty `__init__.py` files
- Use `"""Single line."""` format for one-line docstrings (no blank line)

### FastAPI Depends() (flake8 B008)
**Error**: `B008 Do not perform function calls in argument defaults`

**Fix**: This is acceptable for FastAPI. Add `# noqa: B008`:
```python
async def endpoint(user: User = Depends(get_current_user)):  # noqa: B008
```

## When Creating New Files

1. **Check similar existing files** for import patterns
2. **Copy import structure** from similar files
3. **Add type hints** to all functions
4. **Add docstrings** to all public functions and modules
5. **Run the checklist** before committing

## Do NOT

- ❌ Bypass hooks with `--no-verify` (except for structural migrations)
- ❌ Leave unused imports "for later"
- ❌ Skip type hints "to save time"
- ❌ Ignore pre-commit failures

## Reference Files

- `.pre-commit-config.yaml` - Hook configuration
- `.cursorrules` - Agent rules and pre-commit requirements
- `AGENT_KNOWLEDGE_BASE.md` - Complete coding standards
