# Agent Knowledge Base

> **For AI Agents**: This file contains critical guidelines and standards for working on this repository.

---

## Documentation Standards

**CRITICAL**: Follow [Documentation Organization Standards](Documentation/Governance/DOCUMENTATION_ORGANIZATION_STANDARDS.md) for all documentation work.

**Key Rules:**
- Root directory: ≤10 markdown files
- Single source of truth for each topic
- Consolidate duplicate content (don't leave multiple dated versions)
- Archive (don't delete) superseded documentation
- Update all indices when reorganizing

---

## Quick Reference

- **Organize docs**: See workflow in `.agent/workflows/organize-docs.md`
- **Check compliance**: Count root markdown files: `find . -maxdepth 1 -name "*.md" -type f | wc -l`
- **Standards**: [DOCUMENTATION_ORGANIZATION_STANDARDS.md](Documentation/Governance/DOCUMENTATION_ORGANIZATION_STANDARDS.md)
