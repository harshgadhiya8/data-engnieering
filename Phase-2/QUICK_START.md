# Quick Start Guide - 5 Minutes to Running Pipeline

## For Absolute Beginners

If you're new to dbt and just want to run the pipeline, follow these steps exactly:

---

## Step 1: Open Terminal

```bash
# Navigate to the project
cd /Users/harsh/data-engineering/Phase-2/ecommerce
```

---

## Step 2: Run the Pipeline

```bash
# Build all models (this creates your data warehouse)
dbt run

# Test data quality
dbt test
```

---

## Step 3: Verify Success

You should see:
```
Completed successfully
Done. PASS=12 WARN=0 ERROR=0 SKIP=0 TOTAL=12
```

That's it! Your data warehouse is built.

---

## Step 4: Check Your Data (Optional)

```bash
# See what tables were created
psql -U harsh -d phase-2 -c "\dt dev.*"

# Count records in fact table
psql -U harsh -d phase-2 -c "SELECT COUNT(*) FROM dev.fact_orders;"

# View sample data
psql -U harsh -d phase-2 -c "SELECT * FROM dev.fact_orders LIMIT 5;"
```

---

## What Just Happened?

1. **dbt run** read data from raw tables in PostgreSQL
2. Created 7 staging models (cleaned data)
3. Built 4 dimension tables + 1 fact table (star schema)
4. Saved everything to the `dev` schema

---

## Common Issues and Quick Fixes

### "dbt: command not found"
```bash
# Activate virtual environment first
cd /Users/harsh/data-engineering/Phase-2
source dbt-env/bin/activate
cd ecommerce
dbt run
```

### "could not connect to database"
```bash
# Check if PostgreSQL is running
psql -U harsh -d phase-2 -c "SELECT 1;"

# If that fails, start PostgreSQL
brew services start postgresql
```

### "relation does not exist"
```bash
# Load raw data first
cd /Users/harsh/data-engineering/Phase-2
python main.py
cd ecommerce
dbt run
```

### Still stuck?
See [RUNBOOK.md](RUNBOOK.md) for detailed troubleshooting.

---

## Next Steps

Now that your pipeline is running, explore:

1. **[DBT_CHEATSHEET.md](DBT_CHEATSHEET.md)** - Common commands
2. **[RUNBOOK.md](RUNBOOK.md)** - Complete guide with troubleshooting
3. **[README.md](README.md)** - Learn dbt concepts in depth
4. **[PIPELINE_DIAGRAM.md](PIPELINE_DIAGRAM.md)** - Visual architecture

---

## Daily Usage

Every time you want to refresh your data warehouse:

```bash
cd /Users/harsh/data-engineering/Phase-2/ecommerce
dbt run && dbt test
```

That's it!

---

## Understanding the Output

### Good Output
```
✓ Completed successfully
✓ Done. PASS=12 WARN=0 ERROR=0
```

### Bad Output
```
✗ Completed with 1 error
✗ Done. PASS=11 ERROR=1
```

If you see errors, check [RUNBOOK.md](RUNBOOK.md) Section 6: "Troubleshooting Common Errors"

---

## Pro Tips

1. Always run `dbt test` after `dbt run` to validate data quality
2. Use `dbt run --select model_name` to run just one model
3. Check logs if something fails: `cat logs/dbt.log | tail -50`
4. Need to rebuild everything? Use `dbt run --full-refresh`

---

**Congratulations!** You've successfully run your first dbt pipeline.
