---
description: Organize repository documentation structure
---

# Documentation Organization Workflow

Follow [Documentation Organization Standards](../../Documentation/Governance/DOCUMENTATION_ORGANIZATION_STANDARDS.md)

## Step 1: Survey Current State

Check root-level markdown files:
// turbo
```bash
find . -maxdepth 1 -name "*.md" -type f | wc -l
```

**Target**: ≤10 files

## Step 2: Analyze Documentation

Run analysis:
```bash
# List all root markdown files
ls -1 *.md 2>/dev/null

# Check Documentation/ structure
find Documentation -name "*.md" -type f | head -20
```

## Step 3: Reference Standards

Read the complete standards:
- [DOCUMENTATION_ORGANIZATION_STANDARDS.md](../../Documentation/Governance/DOCUMENTATION_ORGANIZATION_STANDARDS.md)

## Step 4: Create Implementation Plan

Follow the 5-phase checklist from standards:
1. **Survey** - Identify all docs, find duplicates
2. **Plan** - Map consolidation strategy, get approval
3. **Execute** - Merge and archive files
4. **Update** - Fix all cross-references and indices
5. **Verify** - Test navigation paths

Create `implementation_plan.md` artifact following the template in standards.

## Step 5: Execute Consolidation

**Get user approval first**, then:
- Consolidate dated reports (CODE_REVIEW_*.md → CODE_REVIEW_LATEST.md)
- Merge similar docs (design audits, setup guides)
- Archive superseded files to `Documentation/Archive/`
- Update `CONTRIBUTING.md` with merged setup content

## Step 6: Update Indices

Update all navigation files:
- Root README.md
- Documentation/README.md
- Documentation/DOCUMENTATION_INDEX.md
- Any pointer files (like CODE_REVIEW.md)

## Step 7: Verify

Check results:
// turbo
```bash
# Verify root file count
find . -maxdepth 1 -name "*.md" -type f | wc -l

# Should be ≤10
```

Test navigation paths for different user types.

## Success Criteria

- [ ] Root has ≤10 markdown files
- [ ] No duplicate content
- [ ] Single source of truth for each topic
- [ ] All links functional
- [ ] Clear user navigation paths
