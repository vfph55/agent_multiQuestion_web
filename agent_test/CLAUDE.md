# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a documentation-only knowledge base repository for ZURU Melon, an AI solutions company. It contains company policies, procedures, and coding standards. There is no executable code, build system, or tests.

## Repository Structure

```
knowledge_base/
├── Company Policies.md              # Code of conduct, ethics, workplace policies
├── Company Procedures & Guidelines.md  # Hiring, onboarding, project procedures
└── Coding Style.md                  # Python and TypeScript coding standards
```

## Key Documentation Contents

### Coding Style Guidelines (`knowledge_base/Coding Style.md`)

When suggesting code changes for other ZURU Melon projects, adhere to:

**Python:**
- Follow PEP 8, 4 spaces, 100 char line limit
- Type hints required for all functions (checked with `mypy`)
- Google-style docstrings
- Specific exception handling (no bare `except:`)
- Naming: `snake_case` (functions/variables), `PascalCase` (classes), `ALL_CAPS` (constants)

**TypeScript:**
- Prettier formatting, 2 spaces, 100 char line limit
- ES6 modules, explicit imports only
- Interfaces preferred over types for objects
- Functional React components only
- Explicit typing for all props and states (no `any`)

**Testing & Tooling:**
- Python: `pytest` for testing, `flake8`/`black`/`mypy` for linting
- TypeScript: `jest`/`react-testing-library` for testing, `eslint`/`prettier` for linting
- Target: 90% code coverage
- All merges must pass CI/CD and code review

### Company Policies

- AI Ethics: All AI solutions must be designed ethically; no bias or discrimination
- Data Security: GDPR compliance, encrypted channels for sensitive data
- Confidentiality: NDAs required, client data access limited to authorized personnel
- IP: All company-developed code/algorithms are company property
