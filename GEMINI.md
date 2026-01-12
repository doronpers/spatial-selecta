# Gemini AI Configuration for Spatial Selecta

## System Instructions

Before starting any task on this repository, read `AGENT_KNOWLEDGE_BASE.md` in the repository root. This file contains:

- Prime directives (patent compliance, security, design philosophy)
- Coding standards
- Development workflows
- Testing requirements

## Quick Reference

### Patent Compliance (CRITICAL)

- NEVER use LPC, source-filter models, or static formant values
- ALWAYS use dynamic trajectories, phase analysis, velocity-based methods

### Style

- Formatter: `black`
- Linter: `flake8`
- Style: `snake_case` for functions, `PascalCase` for classes

### Commands

```bash
black .        # Format
flake8 .       # Lint
pytest         # Test
```

### Security

- Never log API keys or PII
- Never commit .env files
- Audio: float32 mono numpy arrays at 16kHz
