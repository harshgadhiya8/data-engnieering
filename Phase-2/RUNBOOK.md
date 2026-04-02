# Phase-2 E-Commerce Data Pipeline - RUNBOOK

## Table of Contents
1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Understanding the Pipeline](#understanding-the-pipeline)
5. [Essential dbt Commands](#essential-dbt-commands)
6. [Troubleshooting Common Errors](#troubleshooting-common-errors)
7. [Project Structure](#project-structure)
8. [Best Practices](#best-practices)
9. [FAQ](#faq)

---

## Project Overview

This project transforms Brazilian e-commerce data (Olist dataset) into a star schema data warehouse using dbt (Data Build Tool). The pipeline consists of:

1. **Extract & Load**: Python script loads CSV files into PostgreSQL
2. **Transform**: dbt creates staging models and builds star schema
3. **Test**: Automated data quality validation

**Final Output**: An analytics-ready star schema with 1 fact table and 4 dimension tables.

---

## Prerequisites

### Required Software
- Python 3.11
- PostgreSQL (running on localhost:5432)
- dbt-core with PostgreSQL adapter
- psql command-line tool

### Required Setup
- Database: `phase-2` created in PostgreSQL
- PostgreSQL user: `harsh` with access to the database
- dbt profile configured in `~/.dbt/profiles.yml`

### Verify Setup
```bash
# Check PostgreSQL is running
psql -U harsh -d phase-2 -c "SELECT version();"

# Check dbt installation
cd /Users/harsh/data-engineering/Phase-2/ecommerce
dbt --version

# Check dbt can connect to database
dbt debug
```

---

## Quick Start

### First Time Setup

1. **Activate Python environment** (if using virtual environment)
   ```bash
   cd /Users/harsh/data-engineering/Phase-2
   source dbt-env/bin/activate  # If using virtual environment
   ```

2. **Load raw data into PostgreSQL** (if not already loaded)
   ```bash
   python main.py
   ```

3. **Navigate to dbt project**
   ```bash
   cd ecommerce
   ```

4. **Verify dbt connection**
   ```bash
   dbt debug
   ```
   Expected output: `All checks passed!`

### Running the Pipeline

**Standard workflow - Run these commands in order:**

```bash
# 1. Build all models (staging + marts)
dbt run

# 2. Run data quality tests
dbt test

# 3. (Optional) Generate documentation
dbt docs generate
dbt docs serve
```

**Expected output for successful run:**
```
Completed successfully
Done. PASS=12 WARN=0 ERROR=0 SKIP=0 TOTAL=12
```

---

## Understanding the Pipeline

### Data Flow

```
CSV Files (archive/)
    ↓
Python Loader (main.py)
    ↓
PostgreSQL Raw Tables (public schema)
    ↓
dbt Staging Models (dev.stg_*)
    ↓
dbt Marts - Star Schema (dev.dim_*, dev.fact_orders)
    ↓
Analytics-Ready Data Warehouse
```

### What Each Step Does

**Step 1: dbt run**
- Reads from `public` schema (raw data)
- Creates 7 staging views that clean and standardize data
- Builds 4 dimension tables (customers, products, sellers, date)
- Builds 1 fact table (orders) with incremental loading
- All output goes to `dev` schema

**Step 2: dbt test**
- Validates data quality rules
- Checks for null values in required fields
- Verifies referential integrity
- Ensures valid order status values
- Confirms unique customer IDs

**Step 3: dbt docs generate & serve**
- Creates interactive documentation
- Shows data lineage (how tables are built)
- Opens in web browser at http://localhost:8080

---

## Essential dbt Commands

### Core Commands

```bash
# Run all models
dbt run

# Run specific model
dbt run --select fact_orders

# Run a model and all its dependencies
dbt run --select +fact_orders

# Run a model and all downstream models
dbt run --select fact_orders+

# Run all tests
dbt test

# Run tests for specific model
dbt test --select fact_orders

# Compile models without running (good for debugging SQL)
dbt compile

# Show what dbt will run without executing
dbt run --dry-run
```

### Development Commands

```bash
# Check connection and configuration
dbt debug

# List all models in project
dbt list

# List all tests
dbt list --resource-type test

# Show model dependencies
dbt list --select +fact_orders

# Generate and view documentation
dbt docs generate
dbt docs serve

# Clean compiled files and logs
dbt clean
```

### Incremental Model Commands

```bash
# Run incremental model normally (only new data)
dbt run --select fact_orders

# Force full refresh (rebuild from scratch)
dbt run --select fact_orders --full-refresh
```

### Useful Flags

```bash
# Run with verbose logging (helpful for debugging)
dbt run --debug

# Run specific models by tag
dbt run --select tag:staging

# Run models by directory
dbt run --select staging.
dbt run --select marts.

# Run models that failed in last run
dbt run --select result:error
```

---

## Troubleshooting Common Errors

### Error 1: "Database Error - relation does not exist"

**Error Message:**
```
Database Error in model stg_order (models/staging/stg_order.sql)
  relation "public.orders" does not exist
```

**Cause:** Raw data tables are missing from PostgreSQL.

**Solution:**
```bash
# Step 1: Verify raw tables exist
psql -U harsh -d phase-2 -c "\dt public.*"

# Step 2: If tables are missing, reload data
cd /Users/harsh/data-engineering/Phase-2
python main.py

# Step 3: Try dbt run again
cd ecommerce
dbt run
```

---

### Error 2: "Could not connect to database"

**Error Message:**
```
Database Error
  could not connect to server: Connection refused
```

**Cause:** PostgreSQL is not running or connection settings are wrong.

**Solution:**
```bash
# Step 1: Check if PostgreSQL is running
psql -U harsh -d phase-2 -c "SELECT 1;"

# Step 2: If connection fails, start PostgreSQL
# On macOS with Homebrew:
brew services start postgresql

# Step 3: Verify database exists
psql -U harsh -l | grep phase-2

# Step 4: Check dbt profile configuration
cat ~/.dbt/profiles.yml

# Step 5: Test dbt connection
dbt debug
```

---

### Error 3: "Runtime Error - Compilation Error"

**Error Message:**
```
Compilation Error in model fact_orders
  Model 'fact_orders' depends on a node named 'stg_order' which was not found
```

**Cause:** dbt can't find a referenced model (typo in `{{ ref() }}` or missing model).

**Solution:**
```bash
# Step 1: Check if the model exists
ls models/staging/stg_order.sql

# Step 2: Verify the model name matches
grep "{{ ref(" models/marts/fact_orders.sql

# Step 3: List all available models
dbt list

# Step 4: If model name is wrong, edit the .sql file
# Change {{ ref('stg_order') }} to correct name
```

---

### Error 4: "Test Failures"

**Error Message:**
```
Completed with 1 error and 0 warnings:
Failure in test not_null_fact_orders_customer_id
  Got 150 results, configured to fail if != 0
```

**Cause:** Data quality test found issues (null values, invalid data, etc.).

**Solution:**
```bash
# Step 1: Identify which test failed
dbt test --select fact_orders

# Step 2: Investigate the failing data
psql -U harsh -d phase-2 -c "
  SELECT * FROM dev.fact_orders
  WHERE customer_id IS NULL
  LIMIT 10;
"

# Step 3: Check source data for issues
psql -U harsh -d phase-2 -c "
  SELECT * FROM public.orders
  WHERE customer_id IS NULL
  LIMIT 10;
"

# Step 4: Fix data quality issues
# Option A: Clean source data and reload
# Option B: Add data cleaning logic in staging model
# Option C: Adjust test threshold if nulls are expected
```

---

### Error 5: "Incremental Model Not Updating"

**Error Message:**
```
OK created sql incremental model dev.fact_orders ........... [INSERT 0 0 in 0.15s]
```

**Cause:** Incremental logic filtered out all records (no new data detected).

**Solution:**
```bash
# Step 1: Check current max timestamp in fact table
psql -U harsh -d phase-2 -c "
  SELECT MAX(order_purchase_timestamp)
  FROM dev.fact_orders;
"

# Step 2: Check if source has newer data
psql -U harsh -d phase-2 -c "
  SELECT MAX(order_purchase_timestamp)
  FROM public.orders;
"

# Step 3: If you need to reload all data
dbt run --select fact_orders --full-refresh

# Step 4: Verify data was inserted
psql -U harsh -d phase-2 -c "
  SELECT COUNT(*) FROM dev.fact_orders;
"
```

---

### Error 6: "Target schema does not exist"

**Error Message:**
```
Database Error
  schema "dev" does not exist
```

**Cause:** Target schema hasn't been created in PostgreSQL.

**Solution:**
```bash
# Step 1: Create the schema
psql -U harsh -d phase-2 -c "CREATE SCHEMA IF NOT EXISTS dev;"

# Step 2: Grant permissions (if needed)
psql -U harsh -d phase-2 -c "GRANT ALL ON SCHEMA dev TO harsh;"

# Step 3: Run dbt again
dbt run
```

---

### Error 7: "Python/Virtual Environment Issues"

**Error Message:**
```
dbt: command not found
```

**Cause:** Virtual environment not activated or dbt not installed.

**Solution:**
```bash
# Step 1: Check if virtual environment exists
ls /Users/harsh/data-engineering/Phase-2/dbt-env

# Step 2: Activate virtual environment
cd /Users/harsh/data-engineering/Phase-2
source dbt-env/bin/activate

# Step 3: Verify dbt is available
which dbt
dbt --version

# Step 4: If dbt not installed, install it
pip install dbt-core dbt-postgres
```

---

### Error 8: "Out of Memory / Performance Issues"

**Error Message:**
```
Database Error
  out of memory
```

**Cause:** Large dataset or too many parallel threads.

**Solution:**
```bash
# Step 1: Reduce thread count in profiles.yml
# Edit ~/.dbt/profiles.yml and change:
#   threads: 4  →  threads: 1

# Step 2: Run models one at a time
dbt run --select staging.
dbt run --select marts.

# Step 3: For large fact tables, ensure incremental is working
dbt run --select fact_orders  # Should not do full refresh

# Step 4: Check database resources
psql -U harsh -d phase-2 -c "
  SELECT schemaname, tablename,
         pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
  FROM pg_tables
  WHERE schemaname IN ('public', 'dev')
  ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

---

### Error 9: "Git Conflicts in dbt Files"

**Error Message:**
```
<<<<<<< HEAD
=======
>>>>>>> branch-name
```

**Cause:** Merge conflict in dbt model files.

**Solution:**
```bash
# Step 1: Identify conflicted files
git status

# Step 2: Open and manually resolve conflicts
# Remove conflict markers and keep correct code

# Step 3: Test the model compiles
dbt compile --select model_name

# Step 4: Run the model to verify
dbt run --select model_name

# Step 5: Commit resolved changes
git add .
git commit -m "Resolved merge conflict in model_name"
```

---

### Error 10: "Logs showing warnings or deprecations"

**Error Message:**
```
[WARNING]: Deprecated functionality
```

**Cause:** Using outdated dbt syntax or features.

**Solution:**
```bash
# Step 1: Check dbt version
dbt --version

# Step 2: Review deprecation warnings in logs
cat logs/dbt.log | grep WARNING

# Step 3: Update syntax based on dbt migration guides
# Visit: https://docs.getdbt.com/guides/migration/tools

# Step 4: Test changes
dbt compile
dbt run
```

---

## Project Structure

```
Phase-2/
├── archive/                          # Raw CSV data files
│   ├── olist_orders_dataset.csv
│   ├── olist_order_items_dataset.csv
│   └── ... (7 more CSV files)
│
├── main.py                           # Python script to load CSVs to PostgreSQL
│
├── ecommerce/                        # dbt project folder
│   ├── dbt_project.yml              # dbt project configuration
│   │
│   ├── models/                       # SQL transformation models
│   │   ├── sources.yaml             # Declares raw data sources
│   │   │
│   │   ├── staging/                 # Layer 2: Cleaned data
│   │   │   ├── stg_order.sql
│   │   │   ├── stg_order_item.sql
│   │   │   ├── stg_order_payments.sql
│   │   │   ├── stg_order_reviews.sql
│   │   │   ├── stg_customers.sql
│   │   │   ├── stg_products.sql
│   │   │   └── stg_sellers.sql
│   │   │
│   │   └── marts/                   # Layer 3: Star schema
│   │       ├── schema.yml           # Data tests definitions
│   │       ├── fact_orders.sql      # Fact table (incremental)
│   │       ├── dim_customers.sql    # Customer dimension
│   │       ├── dim_products.sql     # Product dimension
│   │       ├── dim_sellers.sql      # Seller dimension
│   │       └── dim_date.sql         # Date dimension
│   │
│   ├── logs/                         # dbt execution logs
│   │   └── dbt.log
│   │
│   └── target/                       # Compiled SQL and artifacts
│       ├── compiled/
│       ├── run/
│       └── manifest.json
│
└── dbt-env/                          # Python virtual environment
```

### Key Files Explained

| File | Purpose |
|------|---------|
| `dbt_project.yml` | Main dbt configuration (project name, model paths) |
| `~/.dbt/profiles.yml` | Database connection settings (host, port, credentials) |
| `models/sources.yaml` | Declares source tables in `public` schema |
| `models/staging/*.sql` | Clean and standardize raw data (views) |
| `models/marts/*.sql` | Business logic, joins, aggregations (star schema) |
| `models/marts/schema.yml` | Data quality tests for final tables |
| `logs/dbt.log` | Detailed execution logs for debugging |
| `target/manifest.json` | Metadata about models, dependencies, timing |

---

## Best Practices

### Daily Development Workflow

1. **Start fresh**
   ```bash
   cd /Users/harsh/data-engineering/Phase-2/ecommerce
   git pull  # Get latest changes
   dbt debug  # Verify connection
   ```

2. **Make changes to models**
   ```bash
   # Edit SQL files in models/
   ```

3. **Test your changes**
   ```bash
   dbt compile --select modified_model  # Check SQL compiles
   dbt run --select modified_model      # Run just your changes
   dbt test --select modified_model     # Run tests
   ```

4. **Run full pipeline**
   ```bash
   dbt run    # Build all models
   dbt test   # Validate data quality
   ```

5. **Review results**
   ```bash
   # Check logs for any issues
   cat logs/dbt.log | grep -i error

   # Query the data
   psql -U harsh -d phase-2
   ```

### Performance Tips

1. **Use incremental models for large fact tables**
   - Already implemented in `fact_orders.sql`
   - Only processes new records based on timestamp
   - Use `--full-refresh` only when necessary

2. **Run models selectively during development**
   ```bash
   dbt run --select +my_model+  # Model, its parents, and children
   ```

3. **Limit thread count if database is slow**
   - Edit `~/.dbt/profiles.yml`
   - Reduce `threads: 4` to `threads: 1` or `2`

4. **Use `dbt compile` before `dbt run` to catch errors early**

### Data Quality Best Practices

1. **Always run tests after making changes**
   ```bash
   dbt test --select modified_model
   ```

2. **Add tests for new models**
   - Edit `models/marts/schema.yml`
   - Add `not_null`, `unique`, `relationships`, `accepted_values` tests

3. **Monitor test results**
   ```bash
   # View test results in detail
   dbt test --store-failures
   ```

4. **Investigate test failures immediately**
   ```bash
   # Query the failing records
   psql -U harsh -d phase-2 -c "SELECT * FROM dev.my_model WHERE problem_field IS NULL;"
   ```

### Version Control Tips

1. **Don't commit generated files**
   - `target/` folder (already in .gitignore)
   - `logs/` folder (already in .gitignore)
   - `dbt_packages/` folder

2. **Do commit**
   - Model SQL files (`.sql`)
   - Configuration files (`.yml`)
   - Documentation files (`.md`)
   - Tests

3. **Write good commit messages**
   ```bash
   git commit -m "Add customer lifetime value calculation to fact_orders"
   ```

---

## FAQ

### Q1: How do I know if the pipeline ran successfully?

**A:** Look for this output at the end:
```
Completed successfully
Done. PASS=12 WARN=0 ERROR=0 SKIP=0 TOTAL=12
```

Also verify data exists:
```bash
psql -U harsh -d phase-2 -c "SELECT COUNT(*) FROM dev.fact_orders;"
```

---

### Q2: How often should I run the pipeline?

**A:** Depends on your needs:
- **Development:** Run whenever you make changes
- **Production:** Typically daily or hourly via scheduled job (cron, Airflow)
- **This project:** Run manually when you want to refresh the data warehouse

---

### Q3: What's the difference between `dbt run` and `dbt build`?

**A:**
- `dbt run`: Executes models only
- `dbt build`: Executes models AND tests in dependency order
- Use `dbt build` for a complete run with validation

---

### Q4: How do I add new columns to existing models?

**A:**
1. Edit the `.sql` file in `models/`
2. Add your new column to the SELECT statement
3. Run `dbt run --select your_model`
4. Add tests in `schema.yml` if needed
5. Run `dbt test --select your_model`

---

### Q5: What if I need to completely rebuild everything?

**A:**
```bash
# Drop all tables in dev schema
psql -U harsh -d phase-2 -c "DROP SCHEMA dev CASCADE; CREATE SCHEMA dev;"

# Rebuild from scratch
dbt run --full-refresh

# Run tests
dbt test
```

---

### Q6: How do I see the actual SQL that dbt generates?

**A:**
```bash
# Compile models without running
dbt compile

# View compiled SQL
cat target/compiled/ecommerce/models/marts/fact_orders.sql

# Or view in dbt docs
dbt docs generate
dbt docs serve
```

---

### Q7: Can I run dbt from outside the ecommerce folder?

**A:** No, you must be inside the dbt project folder:
```bash
cd /Users/harsh/data-engineering/Phase-2/ecommerce
dbt run
```

---

### Q8: How do I update to a newer version of dbt?

**A:**
```bash
# Activate virtual environment
source /Users/harsh/data-engineering/Phase-2/dbt-env/bin/activate

# Upgrade dbt
pip install --upgrade dbt-core dbt-postgres

# Verify new version
dbt --version

# Test compatibility
dbt debug
dbt compile
```

---

### Q9: What do I do if the incremental model has stale data?

**A:**
```bash
# Force a full rebuild of the incremental model
dbt run --select fact_orders --full-refresh

# Or drop and recreate
psql -U harsh -d phase-2 -c "DROP TABLE dev.fact_orders;"
dbt run --select fact_orders
```

---

### Q10: How do I see model dependencies (lineage)?

**A:**
```bash
# Generate and view docs with visual lineage graph
dbt docs generate
dbt docs serve

# Or use CLI
dbt list --select +fact_orders  # Show upstream dependencies
dbt list --select fact_orders+  # Show downstream dependencies
```

---

## Quick Reference Card

### Most Used Commands

| Command | What It Does |
|---------|-------------|
| `dbt run` | Build all models |
| `dbt test` | Run all data quality tests |
| `dbt debug` | Check connection and setup |
| `dbt compile` | Generate SQL without running |
| `dbt docs generate && dbt docs serve` | View documentation |
| `dbt run --select my_model` | Run specific model |
| `dbt run --full-refresh` | Rebuild everything from scratch |

### Emergency Commands

| Issue | Command |
|-------|---------|
| Everything is broken | `dbt clean && dbt deps && dbt run` |
| Need to start over | `DROP SCHEMA dev CASCADE; CREATE SCHEMA dev;` then `dbt run` |
| Check what went wrong | `cat logs/dbt.log \| tail -100` |
| Verify database connection | `dbt debug` |
| See if data exists | `psql -U harsh -d phase-2 -c "\dt dev.*"` |

---

## Getting Help

1. **Check the logs**
   ```bash
   cat logs/dbt.log | grep -i error
   ```

2. **Use dbt debug**
   ```bash
   dbt debug --config-dir
   ```

3. **Official dbt documentation**
   - https://docs.getdbt.com/

4. **dbt Community Slack**
   - https://community.getdbt.com/

5. **Check this runbook's troubleshooting section above**

---

**Last Updated:** April 2026
**dbt Version:** 1.11.7
**Database:** PostgreSQL
**Project:** Phase-2 E-Commerce Data Warehouse
