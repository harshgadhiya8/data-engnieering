# Phase-2 E-Commerce Data Pipeline - Documentation Index

## Choose Your Learning Path

### I'm a Complete Beginner
Start here if you've never used dbt before:

1. **[QUICK_START.md](QUICK_START.md)** ⚡ *5 minutes*
   - Get the pipeline running immediately
   - Minimal explanations, just commands
   - Perfect for "I just want it to work"

2. **[RUNBOOK.md](RUNBOOK.md)** 📚 *30 minutes*
   - Complete operational guide
   - How to run the pipeline
   - 10+ common errors and how to fix them
   - Best practices and workflows

3. **[README.md](README.md)** 🎓 *1-2 hours*
   - Deep dive into dbt concepts
   - Understand OLAP, Star Schema, Incremental Models
   - Learn the "why" behind everything
   - Great reference material

---

### I Need Quick Answers
Reference materials when you know what you're looking for:

- **[DBT_CHEATSHEET.md](DBT_CHEATSHEET.md)** ⚡
  - One-page quick reference
  - Common commands with examples
  - Quick fixes for errors
  - Keep this open while working

- **[PIPELINE_DIAGRAM.md](PIPELINE_DIAGRAM.md)** 📊
  - Visual architecture diagrams
  - Star schema structure
  - Data flow illustrations
  - Folder structure map

---

### I Want to Understand the Architecture
Deep dives into how the system works:

- **[PIPELINE_DIAGRAM.md](PIPELINE_DIAGRAM.md)** 📊
  - End-to-end data flow
  - Star schema detailed view
  - Incremental loading strategy
  - Technology stack layers

- **[README.md](README.md)** 🎓
  - dbt concepts and theory
  - Naming conventions
  - Best practices
  - Further reading resources

---

## Document Quick Reference

| Document | What It's For | When to Use It |
|----------|---------------|----------------|
| **QUICK_START.md** | Get running fast | First time setup, just want it to work |
| **RUNBOOK.md** | Complete operations guide | Running pipeline, troubleshooting errors |
| **DBT_CHEATSHEET.md** | Command reference | Daily work, quick lookups |
| **PIPELINE_DIAGRAM.md** | Visual architecture | Understanding data flow, debugging |
| **README.md** | Learning dbt concepts | Deep understanding, learning |
| **INDEX.md** | This file | Finding the right document |

---

## Common Use Cases - Where to Look

### "I need to run the pipeline"
→ [QUICK_START.md](QUICK_START.md) or [RUNBOOK.md](RUNBOOK.md) Section 3

### "I got an error, how do I fix it?"
→ [RUNBOOK.md](RUNBOOK.md) Section 6: Troubleshooting

### "What does this dbt command do?"
→ [DBT_CHEATSHEET.md](DBT_CHEATSHEET.md) or [RUNBOOK.md](RUNBOOK.md) Section 5

### "How does this pipeline work?"
→ [PIPELINE_DIAGRAM.md](PIPELINE_DIAGRAM.md)

### "What is a star schema / incremental model?"
→ [README.md](README.md)

### "How do I add a new model?"
→ [RUNBOOK.md](RUNBOOK.md) Section 8: Best Practices

### "The pipeline ran, how do I verify it worked?"
→ [RUNBOOK.md](RUNBOOK.md) Section 9: FAQ

### "I want to understand dbt deeply"
→ [README.md](README.md) + Official dbt docs

---

## Suggested Reading Order

### Path 1: Fast Track (For Practitioners)
1. **QUICK_START.md** - Get it running (5 min)
2. **DBT_CHEATSHEET.md** - Learn essential commands (10 min)
3. **RUNBOOK.md** - Skim troubleshooting section (15 min)
4. Start using the pipeline!

**Total Time:** ~30 minutes

---

### Path 2: Comprehensive (For Learners)
1. **QUICK_START.md** - Get it running (5 min)
2. **README.md** - Learn dbt concepts (1-2 hours)
3. **PIPELINE_DIAGRAM.md** - Understand architecture (30 min)
4. **RUNBOOK.md** - Deep dive operations (30 min)
5. **DBT_CHEATSHEET.md** - Quick reference (bookmark it)

**Total Time:** ~3-4 hours (worth it for solid understanding)

---

### Path 3: Emergency (Something's Broken)
1. **RUNBOOK.md Section 6** - Find your error and fix it
2. If not found, check logs: `cat ecommerce/logs/dbt.log | tail -100`
3. Post in dbt Community Slack with error message

---

## Additional Resources

### Inside This Project
- `ecommerce/README.md` - Original dbt starter documentation
- `ecommerce/logs/dbt.log` - Detailed execution logs
- `ecommerce/target/` - Compiled SQL and metadata

### External Resources
- [Official dbt Documentation](https://docs.getdbt.com/)
- [dbt Community Slack](https://community.getdbt.com/)
- [dbt Free Course](https://courses.getdbt.com/)
- [dbt Best Practices](https://docs.getdbt.com/best-practices)

---

## Visual Guide to Documents

```
┌─────────────────────────────────────────────────────┐
│           START: What do you need?                  │
└─────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Run Pipeline │ │ Learn dbt    │ │ Fix Problem  │
└──────────────┘ └──────────────┘ └──────────────┘
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ QUICK_START  │ │   README.md  │ │  RUNBOOK.md  │
│    .md       │ │              │ │  Section 6   │
└──────────────┘ └──────────────┘ └──────────────┘
        │               │               │
        ▼               │               │
┌──────────────┐        │               │
│   RUNBOOK    │        │               │
│    .md       │◄───────┘               │
└──────────────┘                        │
        │                               │
        ▼                               │
┌──────────────┐                        │
│ DBT_CHEAT    │                        │
│  SHEET.md    │◄───────────────────────┘
└──────────────┘
        │
        ▼
┌──────────────┐
│ Keep it open │
│ while working│
└──────────────┘
```

---

## Document Maintenance

This documentation was created on **April 1, 2026** for:
- dbt version: 1.11.7
- PostgreSQL: localhost:5432
- Database: phase-2
- Python: 3.11

If you upgrade any components, refer to [RUNBOOK.md](RUNBOOK.md) Section 9: FAQ for upgrade instructions.

---

## Questions?

1. Check the document index above
2. Search within documents (they're markdown, searchable)
3. Review [RUNBOOK.md FAQ Section](RUNBOOK.md#faq)
4. Check `ecommerce/logs/dbt.log` for detailed logs
5. Ask in dbt Community Slack

---

## Quick Command Reminder

```bash
# Navigate to project
cd /Users/harsh/data-engineering/Phase-2/ecommerce

# Standard workflow
dbt run         # Build models
dbt test        # Run tests
dbt docs serve  # View documentation

# Help commands
dbt --help
dbt run --help
```

---

**Happy data engineering!** 🚀

Start with [QUICK_START.md](QUICK_START.md) if you're new, or jump to [DBT_CHEATSHEET.md](DBT_CHEATSHEET.md) for quick reference.
