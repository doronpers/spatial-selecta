# Documentation Organization Standards

**Purpose**: Guidelines for AI agents and developers to maintain clean, organized documentation structure across repositories.

**Last Updated**: 2026-01-10
**Status**: Active Standard

---

## Core Principles

Following Dieter Rams' "Less but Better" philosophy:

1. **Single Source of Truth**: Each topic has ONE authoritative document
2. **Clear Navigation**: Multiple entry points for different user types
3. **Active vs Archive**: Clear distinction between current and historical content
4. **Consolidate, Don't Delete**: Archive superseded content for historical reference
5. **Update Indices**: All navigation files stay current with structure changes

---

## Root-Level Documentation Structure

### Maximum Files: 10 markdown files

**Essential Root Files**:

- `README.md` - Project overview, quick start, features (REQUIRED)
- `CONTRIBUTING.md` - Development setup, contribution guidelines (REQUIRED)
- `CHANGELOG.md` - Version history (RECOMMENDED)
- `QUICKSTART.md` or equivalent - 5-minute setup guide (OPTIONAL)

**AI Agent Files** (if applicable):

- `AGENT_KNOWLEDGE_BASE.md` - Prime directives for AI agents
- `CLAUDE.md` or similar - Detailed AI assistant guide

**Other Allowed**:

- `DIRECTORY_STRUCTURE.md` - Repository organization reference
- Domain-specific docs (e.g., `PATENT_COMPLIANCE.md`, `SECURITY.md`)

### What NOT to Keep at Root

❌ **Multiple dated reports** (CODE_REVIEW_2026-01-04.md, CODE_REVIEW_2026-01-08.md...)
→ Consolidate into single latest + archive old versions

❌ **Redundant setup guides** (VENV_SETUP.md, DOCKER_SETUP.md...)
→ Merge into CONTRIBUTING.md

❌ **Multiple similar files** (INTEGRATION_SUMMARY.md when detailed guide exists)
→ Consolidate or archive

❌ **Legacy documentation** (outdated guides, obsolete references)
→ Move to Archive/

---

## Documentation/ Directory Structure

### Recommended Organization

```
Documentation/
├── README.md                    # Documentation hub (navigation)
├── DOCUMENTATION_INDEX.md       # Complete index
├── Core/ or root files          # Essential references (5-7 files)
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── [domain-specific].md
├── Guides/                      # How-to guides (5-10 files)
│   ├── QUICKSTART.md
│   ├── INTEGRATION_GUIDE.md
│   └── [specific guides].md
├── Reports/                     # Status reports and reviews
│   ├── CODE_REVIEW_LATEST.md   # Consolidated latest
│   ├── [TOPIC]_CONSOLIDATED.md # Consolidated by topic
│   └── YYYY-MM/                # Dated subfolder for time-specific reports
├── Governance/ or Strategy/     # Long-term planning (2-3 files)
│   ├── ROADMAP.md
│   └── AGENTS.md
├── Security/                    # Security docs (3-5 files)
└── Archive/                     # Historical preservation
    ├── Reports-Historical/
    ├── Guides-Legacy-YYYY/
    └── [dated-category]-YYYY/
```

### File Limits by Category

| Category | Target Count | Notes |
|----------|--------------|-------|
| Core docs | 5-7 files | Essential references only |
| Guides | 5-10 files | Consolidate similar topics |
| Reports | 2-3 core files | Use dated subfolders for historical |
| Governance | 2-3 files | Long-term planning |

**Total Active Documentation Target**: 20-30 files (excluding Archive/)

---

## Consolidation Rules

### When to Consolidate

**Trigger consolidation when:**

- ✅ Multiple files cover the same topic with different dates
- ✅ Similar guides exist for the same purpose
- ✅ Setup instructions scattered across multiple files
- ✅ Root directory has >10 markdown files
- ✅ Finding information requires checking multiple files

### How to Consolidate

1. **Code Reviews / Audits**:
   - Create `CODE_REVIEW_LATEST.md` or `[TOPIC]_CONSOLIDATED.md`
   - Include recent fixes + historical context
   - Archive old versions to `Archive/Reports-Historical/`
   - Update `CODE_REVIEW.md` navigation file pointing to latest

2. **Setup Guides**:
   - Merge into `CONTRIBUTING.md` under "Development Setup"
   - Keep one comprehensive guide vs multiple fragmented ones
   - Archive originals if they have unique historical value

3. **Integration Summaries**:
   - Consolidate into detailed guide in `Guides/`
   - Archive summary if guide is comprehensive

### Archival Strategy

**Archive, don't delete:**

```
Archive/
├── Reports-Historical/          # Old code reviews, audits
├── Guides-Legacy-YYYY/          # Superseded guides
├── Dated-Docs-YYYY-MM/          # Time-specific docs
└── README.md                    # Explains what's archived and why
```

**Always include Archive/README.md** explaining:

- What's archived
- Why it was archived
- Where to find current versions

---

## Navigation Maintenance

### Required Index Files

1. **README.md** (Root):
   - Quick start section
   - Links to Documentation/
   - Links to essential files

2. **Documentation/README.md**:
   - Documentation hub
   - Role-based navigation
   - Recent updates section

3. **Documentation/DOCUMENTATION_INDEX.md**:
   - Complete catalog
   - Categorized by purpose
   - Kept current with structure

### Cross-Reference Updates

**When moving/consolidating files, update:**

- [ ] All index files (README, DOCUMENTATION_INDEX)
- [ ] Files that link to moved content
- [ ] Navigation/pointer files
- [ ] Recent updates sections

---

## Implementation Checklist

When reorganizing documentation in any repo:

### Phase 1: Survey

- [ ] Count all markdown files at root
- [ ] List all files in Documentation/
- [ ] Identify duplicate/overlapping content
- [ ] Find superseded versions

### Phase 2: Plan

- [ ] Identify consolidation opportunities
- [ ] Plan archive structure
- [ ] Map where content will move
- [ ] Get user approval if major changes

### Phase 3: Execute

- [ ] Create consolidated documents
- [ ] Move files to Archive/
- [ ] Update CONTRIBUTING.md with merged content
- [ ] Create navigation/pointer files

### Phase 4: Update Indices

- [ ] Update root README.md
- [ ] Update Documentation/README.md
- [ ] Update DOCUMENTATION_INDEX.md
- [ ] Update cross-references
- [ ] Test all navigation paths

### Phase 5: Verify

- [ ] Root has ≤10 markdown files
- [ ] All content preserved
- [ ] All links functional
- [ ] Clear user paths work

---

## Examples from sonotheia-enhanced

### Successful Consolidation Pattern

**Code Reviews**:

```
Before:
- CODE_REVIEW_2026-01-04.md
- CODE_REVIEW_2026-01-08.md
- CODE_REVIEW_2026-01-10.md

After:
- Documentation/Reports/CODE_REVIEW_LATEST.md (consolidated)
- Documentation/Reports/CODE_REVIEW.md (navigation file)
- Documentation/Archive/Reports-Historical/*.md (archived)
```

**Design Audits**:

```
Before:
- DESIGN_AUDIT_REPORT.md
- DESIGN_AUDIT_FINDINGS.md

After:
- Documentation/Reports/DESIGN_AUDIT_CONSOLIDATED.md
- Archived originals
```

**Setup Docs**:

```
Before:
- VENV_SETUP.md
- LAUNCHER_USAGE.md
- Multiple setup fragments

After:
- CONTRIBUTING.md (includes all setup)
- Referenced from QUICKSTART.md
- Archived originals
```

---

## AI Agent Instructions

### For Ongoing Maintenance

**Monitor these signals:**

- Root directory exceeding 10 markdown files
- Multiple dated versions of same report type
- User confusion about which file to read
- Duplicate information across files

**Standard response:**

1. Survey current state
2. Propose consolidation plan
3. Get user approval
4. Execute with preservation (archive, don't delete)
5. Update all indices
6. Verify navigation paths

### For New Repositories

**Initial setup:**

1. Start with essential root files only (README, CONTRIBUTING)
2. Create Documentation/ structure early
3. Use dated subfolders from the start for reports
4. Establish Archive/ at creation time

### Cross-Repo Consistency

**Reference this standard:**

```markdown
> This repository follows the [Documentation Organization Standards](link-to-this-file)
> maintained across [organization] projects.
```

**Add to CONTRIBUTING.md:**

```markdown
## Documentation Standards
We follow consolidated documentation practices. See [Documentation Organization Standards]
for guidelines on maintaining clean documentation structure.
```

---

## Success Metrics

**Healthy documentation structure:**

- ✅ Root has ≤10 markdown files
- ✅ No duplicate content
- ✅ Single source of truth for each topic
- ✅ Clear navigation for all user types
- ✅ Active vs archived content clearly separated
- ✅ All indices current and accurate

**User experience indicators:**

- ✅ New users find setup instructions quickly
- ✅ Developers find API docs in 1-2 clicks
- ✅ Latest status always clear (not buried in dates)
- ✅ No "which file should I read?" confusion

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-10 | Initial standard based on sonotheia-enhanced consolidation |

---

**For AI Agents**: Reference this standard when organizing documentation in any repository. Follow the principles, apply the patterns, and maintain the structure over time.
