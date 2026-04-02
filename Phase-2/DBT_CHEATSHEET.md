# dbt Quick Reference Cheat Sheet

## Essential Commands

```bash
# Always run from project directory
cd /Users/harsh/data-engineering/Phase-2/ecommerce

# Standard workflow
dbt run         # Build all models
dbt test        # Run all tests

# Development workflow
dbt compile                      # Check SQL syntax
dbt run --select my_model        # Run one model
dbt test --select my_model       # Test one model
dbt run --select +my_model+      # Run model with dependencies
```

## Common Flags

```bash
--select MODEL_NAME              # Run specific model
--select +MODEL_NAME             # Include upstream dependencies
--select MODEL_NAME+             # Include downstream dependencies
--select TAG_NAME                # Run models with specific tag
--full-refresh                   # Rebuild incremental models
--debug                          # Verbose logging
```

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| "relation does not exist" | Run `python main.py` to load raw data |
| "could not connect" | Check PostgreSQL: `psql -U harsh -d phase-2` |
| "command not found: dbt" | Activate env: `source dbt-env/bin/activate` |
| "schema dev does not exist" | `psql -U harsh -d phase-2 -c "CREATE SCHEMA dev;"` |
| Tests failing | Query failing records, check source data |
| Models not updating | Try `--full-refresh` flag |

## Emergency Reset

```bash
# Nuclear option - start completely fresh
psql -U harsh -d phase-2 -c "DROP SCHEMA dev CASCADE; CREATE SCHEMA dev;"
dbt run --full-refresh
dbt test
```

## Check Pipeline Health

```bash
# Verify connection
dbt debug

# Check if tables exist
psql -U harsh -d phase-2 -c "\dt dev.*"

# Count records
psql -U harsh -d phase-2 -c "SELECT COUNT(*) FROM dev.fact_orders;"

# View recent logs
tail -50 logs/dbt.log

# Check for errors
cat logs/dbt.log | grep -i error
```

## Selection Syntax Examples

```bash
# Run all staging models
dbt run --select staging.

# Run all mart models
dbt run --select marts.

# Run one model and test it
dbt run --select fact_orders && dbt test --select fact_orders

# Run models that failed last time
dbt run --select result:error
```

## Documentation

```bash
# Generate and view docs
dbt docs generate
dbt docs serve
# Opens browser at http://localhost:8080
```

## Project Structure Reference

```
models/
├── sources.yaml           # Raw data sources (public schema)
├── staging/              # Cleaned data (stg_*)
│   ├── stg_order.sql
│   ├── stg_customers.sql
│   └── ...
└── marts/                # Star schema (dim_*, fact_*)
    ├── schema.yml        # Tests defined here
    ├── fact_orders.sql
    ├── dim_customers.sql
    └── ...
```

## Quick Verification Queries

```bash
# Check data warehouse contents
psql -U harsh -d phase-2 -c "
SELECT 'fact_orders' as table, COUNT(*) FROM dev.fact_orders
UNION ALL SELECT 'dim_customers', COUNT(*) FROM dev.dim_customers
UNION ALL SELECT 'dim_products', COUNT(*) FROM dev.dim_products
UNION ALL SELECT 'dim_sellers', COUNT(*) FROM dev.dim_sellers
UNION ALL SELECT 'dim_date', COUNT(*) FROM dev.dim_date;
"

# Check for nulls in important fields
psql -U harsh -d phase-2 -c "
SELECT COUNT(*) as null_customer_ids
FROM dev.fact_orders
WHERE customer_id IS NULL;
"

# View recent orders
psql -U harsh -d phase-2 -c "
SELECT * FROM dev.fact_orders
ORDER BY order_purchase_timestamp DESC
LIMIT 5;
"
```

## Success Indicators

### Successful dbt run
```
Completed successfully
Done. PASS=12 WARN=0 ERROR=0 SKIP=0 TOTAL=12
```

### Successful dbt test
```
Completed successfully
Done. PASS=6 WARN=0 ERROR=0 SKIP=0 TOTAL=6
```

### Expected row counts
- fact_orders: ~292K rows
- dim_customers: ~99K rows
- dim_products: ~33K rows
- dim_sellers: ~3K rows
- dim_date: ~99K rows

## Getting Help

1. Check `RUNBOOK.md` for detailed troubleshooting
2. Review logs: `cat logs/dbt.log | tail -100`
3. Official docs: https://docs.getdbt.com/
4. dbt Community: https://community.getdbt.com/

---

**Pro Tip:** Keep this file open in a separate terminal window for quick reference!
