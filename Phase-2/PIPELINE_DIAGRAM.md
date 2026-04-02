# Phase-2 Pipeline Architecture Diagram

## Overview

This document provides visual representations of the data pipeline architecture.

---

## End-to-End Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           PHASE 2 DATA PIPELINE                         │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│   EXTRACT & LOAD     │
│   (Python Script)    │
└──────────────────────┘
          │
          │ main.py + pandas + SQLAlchemy
          │
          ▼
┌──────────────────────────────────────────────────────────────┐
│                     RAW DATA SOURCES                         │
│                   (PostgreSQL - public schema)               │
├──────────────────────────────────────────────────────────────┤
│  • orders              (99,441 rows)                         │
│  • order_items         (292,437 rows)                        │
│  • order_payments      (103,886 rows)                        │
│  • order_reviews       (99,224 rows)                         │
│  • customers           (99,441 rows)                         │
│  • products            (32,951 rows)                         │
│  • sellers             (3,095 rows)                          │
│  • geolocation         (1M+ rows)                            │
│  • product_categories  (71 rows)                             │
└──────────────────────────────────────────────────────────────┘
          │
          │ dbt source declarations (sources.yaml)
          │
          ▼
┌──────────────────────────────────────────────────────────────┐
│              STAGING LAYER (dbt - dev schema)                │
│                  Materialized as VIEWS                       │
├──────────────────────────────────────────────────────────────┤
│  stg_order          ──┐                                      │
│  stg_order_item       │                                      │
│  stg_order_payments   ├── Clean, Rename, Standardize        │
│  stg_order_reviews    │                                      │
│  stg_customers        │                                      │
│  stg_products         │                                      │
│  stg_sellers        ──┘                                      │
└──────────────────────────────────────────────────────────────┘
          │
          │ dbt ref() functions + SQL transformations
          │
          ▼
┌──────────────────────────────────────────────────────────────┐
│           MARTS LAYER - STAR SCHEMA (dev schema)             │
│         Dimensions (VIEWS) + Fact (TABLE incremental)        │
└──────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┼───────────┐
                │           │           │
                ▼           ▼           ▼
    ┌──────────────┐  ┌──────────┐  ┌──────────────┐
    │dim_customers │  │dim_date  │  │dim_products  │
    │  99,441 rows │  │99,441 rows│  │ 32,951 rows  │
    └──────────────┘  └──────────┘  └──────────────┘
                │           │           │
                └───────────┼───────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │ fact_orders  │
                    │ 292,437 rows │
                    │ (incremental)│
                    └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │dim_sellers   │
                    │  3,095 rows  │
                    └──────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                     DATA QUALITY TESTS                       │
│                       (dbt test)                             │
├──────────────────────────────────────────────────────────────┤
│  ✓ fact_orders: not_null on IDs                             │
│  ✓ fact_orders: accepted_values on order_status             │
│  ✓ dim_customers: unique customer_id                        │
│  ✓ dim_customers: not_null on customer_id                   │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│               ANALYTICS-READY DATA WAREHOUSE                 │
│              Ready for BI Tools & Analysis                   │
└──────────────────────────────────────────────────────────────┘
```

---

## Star Schema Detailed View

```
                    ┌─────────────────────────┐
                    │      dim_date           │
                    ├─────────────────────────┤
                    │ order_purchase_date (PK)│
                    │ year                    │
                    │ month                   │
                    │ day                     │
                    │ quarter                 │
                    │ day_of_week             │
                    └──────────┬──────────────┘
                               │
                               │
┌─────────────────────────┐   │   ┌─────────────────────────┐
│   dim_customers         │   │   │   dim_products          │
├─────────────────────────┤   │   ├─────────────────────────┤
│ customer_id (PK)        │   │   │ product_id (PK)         │
│ customer_unique_id      │   │   │ product_category        │
│ customer_zip_code       │   │   │ product_name_length     │
│ customer_city           │   │   │ product_description_len │
│ customer_state          │   │   │ product_photos_qty      │
└────────┬────────────────┘   │   └─────────┬───────────────┘
         │                    │             │
         │                    │             │
         │    ┌───────────────┴──────────┐  │
         └────┤     fact_orders          ├──┘
              ├──────────────────────────┤
              │ order_id (PK)            │
              │ order_item_id (PK)       │
              │ customer_id (FK)         │──┐
              │ product_id (FK)          │  │
              │ seller_id (FK)           │  │
              │ order_purchase_timestamp │  │
              │ price (MEASURE)          │  │
              │ freight_value (MEASURE)  │  │
              │ payment_value (MEASURE)  │  │
              │ review_score (MEASURE)   │  │
              │ order_status             │  │
              └──────────────────────────┘  │
                           │                │
                           └────────────────┘
                                   │
                    ┌──────────────┴──────────┐
                    │   dim_sellers           │
                    ├─────────────────────────┤
                    │ seller_id (PK)          │
                    │ seller_zip_code         │
                    │ seller_city             │
                    │ seller_state            │
                    └─────────────────────────┘

Legend:
  PK = Primary Key
  FK = Foreign Key
  MEASURE = Numeric values to aggregate (SUM, AVG, etc.)
```

---

## dbt Model Dependencies (Lineage)

```
┌─────────────────────────────────────────────────────────────┐
│                       SOURCE TABLES                         │
│                      (public schema)                        │
└─────────────────────────────────────────────────────────────┘
        │           │           │           │           │
        │           │           │           │           │
        ▼           ▼           ▼           ▼           ▼
  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
  │  stg_   │ │  stg_   │ │  stg_   │ │  stg_   │ │  stg_   │
  │ order   │ │ order_  │ │ order_  │ │customers│ │products │
  │         │ │  item   │ │payments │ │         │ │         │
  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘
       │           │           │           │           │
       └───────────┴───────┬───┴───────────┼───────────┘
                           │               │
                           ▼               │
                   ┌──────────────┐        │
                   │ fact_orders  │        │
                   │ (INCREMENTAL)│        │
                   └──────┬───────┘        │
                          │                │
            ┌─────────────┼────────────────┘
            │             │
            ▼             ▼             ▼
     ┌───────────┐  ┌──────────┐  ┌──────────┐
     │dim_       │  │dim_date  │  │dim_      │
     │customers  │  │          │  │products  │
     └───────────┘  └──────────┘  └──────────┘


     ┌─────────┐ ┌─────────┐
     │  stg_   │ │  stg_   │
     │ sellers │ │ order_  │
     │         │ │ reviews │
     └────┬────┘ └────┬────┘
          │           │
          ▼           │
    ┌──────────┐      │
    │dim_      │      │
    │sellers   │      │
    └──────────┘      │
                      │
            (Used in fact_orders join)
```

---

## Data Transformation Logic Flow

### Staging Layer Transformations

```
RAW TABLE                 STAGING MODEL              TRANSFORMATIONS
─────────────────────────────────────────────────────────────────────

orders                →  stg_order                  • Rename columns
├─ order_id              ├─ order_id                • Cast timestamps
├─ customer_id           ├─ customer_id             • Handle nulls
├─ order_status          ├─ order_status            • Standardize formats
├─ order_purchase...     ├─ order_purchase...
└─ ...                   └─ ...

order_items           →  stg_order_item             • Clean IDs
├─ order_id              ├─ order_id                • Cast numerics
├─ order_item_id         ├─ order_item_id           • Remove duplicates
├─ product_id            ├─ product_id
├─ seller_id             ├─ seller_id
├─ price                 ├─ price
└─ ...                   └─ ...

[Similar for other staging models...]
```

### Marts Layer Transformations

```
STAGING MODELS           MART MODEL                 TRANSFORMATIONS
─────────────────────────────────────────────────────────────────────

stg_order            ┐
stg_order_item       ├─→  fact_orders              • Join order + items
stg_order_payments   │      ├─ order_id            • Aggregate payments
stg_order_reviews    ┘      ├─ customer_id         • Include review scores
                            ├─ product_id          • Incremental logic
                            ├─ seller_id           • Composite key
                            ├─ price               • Calculate totals
                            ├─ freight_value
                            ├─ payment_value
                            ├─ review_score
                            └─ order_status


stg_customers        ───→  dim_customers           • Select attributes
                            ├─ customer_id         • Add zip/city/state
                            ├─ customer_unique_id  • One row per customer
                            ├─ customer_zip_code
                            └─ ...


stg_products         ───→  dim_products            • Clean product info
                            ├─ product_id          • Category translations
                            ├─ product_category    • Calculate lengths
                            └─ ...


stg_sellers          ───→  dim_sellers             • Seller location
                            ├─ seller_id           • Contact info
                            └─ ...


stg_order            ───→  dim_date                • Extract date parts
                            ├─ order_purchase_date • Calculate quarter
                            ├─ year                • Day of week
                            ├─ month               • Week of year
                            ├─ day
                            └─ ...
```

---

## Incremental Loading Strategy

### fact_orders Incremental Logic

```
┌──────────────────────────────────────────────────────────────┐
│                    FIRST RUN (Full Load)                     │
└──────────────────────────────────────────────────────────────┘

  Source Data              Process           Result
  ───────────              ───────           ──────
  All orders        ──→    Full SELECT  ──→  fact_orders
  (2016-2018)              No filter         (292,437 rows)

  ┌────────────────────────────────────────────────────────────┐
  │ fact_orders table created with all historical data         │
  └────────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────┐
│              SUBSEQUENT RUNS (Incremental)                   │
└──────────────────────────────────────────────────────────────┘

  ┌─────────────────┐
  │ fact_orders     │
  │ MAX(timestamp)  │ = 2018-08-31 23:59:00
  └────────┬────────┘
           │
           ▼
  Check: Is this incremental? YES
           │
           ▼
  ┌──────────────────────────────────────────┐
  │ Filter:                                  │
  │ WHERE order_purchase_timestamp >         │
  │   (SELECT MAX(order_purchase_timestamp)  │
  │    FROM fact_orders)                     │
  └──────────────────────────────────────────┘
           │
           ▼
  Only new orders    ──→    INSERT INTO    ──→   fact_orders
  (after 2018-08-31)         fact_orders          (+ new rows)


┌──────────────────────────────────────────────────────────────┐
│              FULL REFRESH (--full-refresh)                   │
└──────────────────────────────────────────────────────────────┘

  dbt run --select fact_orders --full-refresh
           │
           ▼
  ┌─────────────────────────────────────────┐
  │ DROP TABLE fact_orders                  │
  │ CREATE TABLE fact_orders AS             │
  │   SELECT * FROM all_source_data         │
  └─────────────────────────────────────────┘
           │
           ▼
  Complete rebuild from scratch
```

---

## Data Quality Testing Flow

```
┌──────────────────────────────────────────────────────────────┐
│                       dbt test                               │
└──────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │  Test Suite  │ │  Test Suite  │ │  Test Suite  │
    │ fact_orders  │ │dim_customers │ │dim_products  │
    └──────────────┘ └──────────────┘ └──────────────┘
            │               │               │
            │               │               │
    ┌───────┴─────┐  ┌──────┴──────┐       │
    │             │  │             │       │
    ▼             ▼  ▼             ▼       ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│not_null │ │accepted │ │ unique  │ │not_null │ │  [etc]  │
│order_id │ │ values  │ │customer │ │customer │ │         │
│         │ │  status │ │   _id   │ │   _id   │ │         │
└────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘
     │           │           │           │           │
     ▼           ▼           ▼           ▼           ▼
   PASS        PASS        PASS        PASS        PASS

┌──────────────────────────────────────────────────────────────┐
│              Result: All tests passed                        │
│              Done. PASS=6 ERROR=0                            │
└──────────────────────────────────────────────────────────────┘
```

### What Each Test Does

```sql
-- Test 1: not_null on fact_orders.order_id
SELECT COUNT(*)
FROM fact_orders
WHERE order_id IS NULL
-- Expected: 0 rows

-- Test 2: accepted_values on fact_orders.order_status
SELECT COUNT(*)
FROM fact_orders
WHERE order_status NOT IN (
  'delivered', 'shipped', 'canceled',
  'processing', 'unavailable', 'invoiced',
  'created', 'approved'
)
-- Expected: 0 rows

-- Test 3: unique on dim_customers.customer_id
SELECT customer_id, COUNT(*)
FROM dim_customers
GROUP BY customer_id
HAVING COUNT(*) > 1
-- Expected: 0 rows

[etc...]
```

---

## Technology Stack Layers

```
┌──────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                      │
├──────────────────────────────────────────────────────────────┤
│  • Terminal / Command Line                                   │
│  • dbt Documentation (http://localhost:8080)                 │
│  • psql CLI                                                  │
└──────────────────────────────────────────────────────────────┘
                            │
┌──────────────────────────────────────────────────────────────┐
│                 ORCHESTRATION / TOOLING LAYER                │
├──────────────────────────────────────────────────────────────┤
│  • dbt-core (transformation framework)                       │
│  • Python 3.11 (scripting)                                   │
│  • pandas (data manipulation)                                │
│  • SQLAlchemy (database connectivity)                        │
└──────────────────────────────────────────────────────────────┘
                            │
┌──────────────────────────────────────────────────────────────┐
│                     DATABASE LAYER                           │
├──────────────────────────────────────────────────────────────┤
│  • PostgreSQL 14+ (localhost:5432)                           │
│    ├─ Database: phase-2                                      │
│    ├─ Schema: public (raw data)                              │
│    └─ Schema: dev (transformed data)                         │
└──────────────────────────────────────────────────────────────┘
                            │
┌──────────────────────────────────────────────────────────────┐
│                      STORAGE LAYER                           │
├──────────────────────────────────────────────────────────────┤
│  • Local filesystem                                          │
│    ├─ CSV files (archive/)                                   │
│    ├─ dbt models (.sql files)                                │
│    ├─ Configuration (.yml files)                             │
│    └─ PostgreSQL data directory                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Folder Structure Map

```
Phase-2/
│
├─ 📁 archive/                    # Raw CSV data files
│  ├─ olist_orders_dataset.csv
│  ├─ olist_order_items_dataset.csv
│  └─ ... (7 more files)
│
├─ 📁 ecommerce/                  # dbt project root
│  │
│  ├─ 📄 dbt_project.yml          # dbt configuration
│  ├─ 📄 README.md                # dbt starter docs
│  │
│  ├─ 📁 models/                  # All SQL models
│  │  │
│  │  ├─ 📄 sources.yaml          # Source declarations
│  │  │
│  │  ├─ 📁 staging/              # Layer 2: Staging models
│  │  │  ├─ 📄 stg_order.sql
│  │  │  ├─ 📄 stg_order_item.sql
│  │  │  ├─ 📄 stg_order_payments.sql
│  │  │  ├─ 📄 stg_order_reviews.sql
│  │  │  ├─ 📄 stg_customers.sql
│  │  │  ├─ 📄 stg_products.sql
│  │  │  └─ 📄 stg_sellers.sql
│  │  │
│  │  └─ 📁 marts/                # Layer 3: Star schema
│  │     ├─ 📄 schema.yml         # Tests
│  │     ├─ 📄 fact_orders.sql
│  │     ├─ 📄 dim_customers.sql
│  │     ├─ 📄 dim_products.sql
│  │     ├─ 📄 dim_sellers.sql
│  │     └─ 📄 dim_date.sql
│  │
│  ├─ 📁 logs/                    # Execution logs
│  │  └─ 📄 dbt.log
│  │
│  └─ 📁 target/                  # Generated files
│     ├─ 📁 compiled/             # Compiled SQL
│     ├─ 📁 run/                  # Executed SQL
│     └─ 📄 manifest.json         # Metadata
│
├─ 📁 dbt-env/                    # Python virtual environment
│
├─ 📄 main.py                     # Data loader script
├─ 📄 README.md                   # dbt concept guide
├─ 📄 RUNBOOK.md                  # Operation guide (YOU ARE HERE)
├─ 📄 DBT_CHEATSHEET.md           # Quick reference
└─ 📄 PIPELINE_DIAGRAM.md         # This file
```

---

## Execution Timeline

```
Time: 0s                  Run: dbt run
├─────────────────────────────────────────────────────────────┤
│  Parsing project...                                          │
│  Found 12 models, 6 tests, 9 sources                        │
└─────────────────────────────────────────────────────────────┘

Time: 0.1s               Build Staging Models (parallel)
├─────────────────────────────────────────────────────────────┤
│  [Thread 1] stg_customers          ✓ CREATE VIEW (0.11s)    │
│  [Thread 2] stg_order              ✓ CREATE VIEW (0.11s)    │
│  [Thread 3] stg_order_item         ✓ CREATE VIEW (0.11s)    │
│  [Thread 4] stg_order_payments     ✓ CREATE VIEW (0.11s)    │
└─────────────────────────────────────────────────────────────┘

Time: 0.2s               Build More Staging (parallel)
├─────────────────────────────────────────────────────────────┤
│  [Thread 1] stg_order_reviews      ✓ CREATE VIEW (0.04s)    │
│  [Thread 2] stg_products           ✓ CREATE VIEW (0.04s)    │
│  [Thread 3] stg_sellers            ✓ CREATE VIEW (0.04s)    │
└─────────────────────────────────────────────────────────────┘

Time: 0.3s               Build Dimensions (parallel)
├─────────────────────────────────────────────────────────────┤
│  [Thread 1] dim_customers          ✓ CREATE VIEW (0.04s)    │
│  [Thread 2] dim_date               ✓ CREATE VIEW (0.04s)    │
│  [Thread 3] dim_sellers            ✓ CREATE VIEW (0.04s)    │
│  [Thread 4] dim_products           ✓ CREATE VIEW (0.04s)    │
└─────────────────────────────────────────────────────────────┘

Time: 0.4s               Build Fact Table
├─────────────────────────────────────────────────────────────┤
│  fact_orders                       ✓ INSERT 0 0 (0.24s)     │
│  (incremental - no new data)                                │
└─────────────────────────────────────────────────────────────┘

Time: 0.53s              Complete
├─────────────────────────────────────────────────────────────┤
│  Completed successfully                                      │
│  Done. PASS=12 WARN=0 ERROR=0 SKIP=0 TOTAL=12              │
└─────────────────────────────────────────────────────────────┘
```

---

## Summary

This pipeline demonstrates modern data engineering best practices:

- **Separation of concerns**: Extract/Load → Transform → Test
- **Layered architecture**: Raw → Staging → Marts
- **Incremental processing**: Efficient updates for large datasets
- **Data quality**: Automated testing for reliability
- **Documentation**: Self-documenting via dbt
- **Version control**: All code in Git
- **Reproducibility**: Single command to rebuild everything

For operational instructions, see [RUNBOOK.md](RUNBOOK.md).
For quick command reference, see [DBT_CHEATSHEET.md](DBT_CHEATSHEET.md).
For dbt concepts, see [README.md](README.md).
