# dbt Notes — Phase 2 Reference

## Quick Navigation

**New to dbt?** Start here:
1. **[RUNBOOK.md](RUNBOOK.md)** - Complete guide to running the pipeline and troubleshooting errors
2. **[DBT_CHEATSHEET.md](DBT_CHEATSHEET.md)** - Quick reference for common commands
3. **This README** - Deep dive into dbt concepts and best practices

---

## What is dbt?

dbt (Data Build Tool) is a transformation tool that sits on top of your database. You write SQL SELECT statements, and dbt handles creating the tables and views for you. It brings software engineering practices — version control, testing, modularity — into data transformation.

**Key idea**: You never write `CREATE TABLE` yourself. You just write a SELECT statement in a `.sql` file, and dbt turns it into a table or view in your database.

---

## OLTP vs OLAP

| OLTP | OLAP |
|---|---|
| Optimized for fast reads/writes | Optimized for analytical queries |
| Transactional databases | Data warehouses |
| Example: recording an order | Example: total revenue by category last month |
| PostgreSQL in production apps | Star Schema, Snowflake, BigQuery |

---

## Star Schema

The industry standard way to structure an analytical database.

**Fact Table** — the core measurable events
- Each row represents one event (e.g. one order item)
- Contains measurements you'd SUM or AVERAGE (price, freight, payment value)
- Contains foreign keys linking to dimension tables

**Dimension Tables** — the context around events
- Describe WHO, WHAT, WHERE, WHEN
- Contains descriptive attributes you'd GROUP BY (city, category, status)

**The golden rule:**
- Ask yourself — *"would I ever SUM or AVERAGE this?"*
- Yes → fact table
- No, it's descriptive → dimension table

**Your Star Schema:**
```
                dim_dates
                    |
dim_customers — fact_orders — dim_sellers
                    |
              dim_products
```

---

## dbt Project Structure

```
your_project/
├── dbt_project.yml          # main config file
├── profiles.yml             # database connection (lives in ~/.dbt/)
└── models/
    ├── sources.yml          # declares raw source tables
    ├── staging/             # staging models (stg_)
    │   ├── stg_orders.sql
    │   ├── stg_customers.sql
    │   └── ...
    └── marts/               # final fact and dimension models
        ├── schema.yml       # data quality tests
        ├── fact_orders.sql
        ├── dim_customers.sql
        └── ...
```

---

## The Three Layers

### Layer 1 — Raw
- Your source CSV data loaded directly into Postgres
- Never touch or transform this
- Declared in `sources.yml`

### Layer 2 — Staging (`stg_`)
- One model per raw table
- Clean but don't restructure
- Rename columns, fix data types, handle nulls
- Reference raw tables using `{{ source() }}`

### Layer 3 — Marts (`dim_` and `fct_`)
- Final fact and dimension tables
- This is your Star Schema
- Reference staging models using `{{ ref() }}`
- Joins happen here

---

## Key dbt Functions

### `{{ source('source_name', 'table_name') }}`
Used in staging models to reference raw tables declared in `sources.yml`
```sql
from {{ source('raw', 'orders') }}
```

### `{{ ref('model_name') }}`
Used in mart models to reference other dbt models. This is how dbt understands dependencies and builds models in the correct order.
```sql
from {{ ref('stg_orders') }}
```

### `{{ this }}`
Refers to the current model's table. Used in incremental models to reference the existing table.
```sql
select max(order_purchase_timestamp) from {{ this }}
```

### `{{ is_incremental() }}`
Returns true if the model already exists and is being run incrementally. Always wrap in `{% if %}` block.
```sql
{% if is_incremental() %}
where order_purchase_timestamp > (select max(order_purchase_timestamp) from {{ this }})
{% endif %}
```

---

## sources.yml Structure

Declares your raw tables so dbt knows where they live.

```yaml
version: 2

sources:
  - name: raw
    schema: public
    tables:
      - name: orders
      - name: customers
      - name: products
```

---

## Materializations

How dbt physically creates your model in the database.

| Type | What it does | When to use |
|---|---|---|
| `view` | Creates a SQL view, no data stored | Staging models |
| `table` | Creates a full table, data stored | Dimension tables |
| `incremental` | Appends only new rows | Large fact tables |

Set in the config block at the top of your SQL file:
```sql
{{ config(materialized='incremental') }}
```

---

## Incremental Models

### Why?
Rebuilding millions of rows every day is slow and expensive. Incremental models only process new rows since the last run.

### How it works
- First run: builds the full table
- Subsequent runs: only processes rows newer than the latest timestamp

### Full structure
```sql
{{ config(
    materialized='incremental',
    unique_key=['order_id', 'order_item_id']
) }}

select ...
from {{ ref('stg_orders') }} o
join ...

{% if is_incremental() %}
where o.order_purchase_timestamp > (select max(order_purchase_timestamp) from {{ this }})
{% endif %}
```

### Force full rebuild
```bash
dbt run --full-refresh
```
Use this when you change the structure of an incremental model (add/remove columns).

---

## dbt Tests

Data quality checks that verify your data follows rules.

### Four built-in generic tests
| Test | What it checks |
|---|---|
| `unique` | No duplicate values in a column |
| `not_null` | No null values in a column |
| `accepted_values` | Column only contains specific values |
| `relationships` | Foreign key exists in another table |

### schema.yml structure
```yaml
version: 2

models:
  - name: fact_orders
    columns:
      - name: order_id
        tests:
          - not_null
      - name: order_status
        tests:
          - accepted_values:
              arguments:
                values: ['delivered', 'shipped', 'canceled']

  - name: dim_customers
    columns:
      - name: customer_id
        tests:
          - unique
          - not_null
```

### Running tests
```bash
dbt test          # run all tests
dbt run           # build all models
dbt run && dbt test   # build then test (do this together)
```

---

## Key dbt Commands

```bash
dbt init          # create a new project
dbt debug         # test database connection
dbt run           # build all models
dbt test          # run all tests
dbt run --full-refresh   # force full rebuild of incremental models
dbt docs generate # generate documentation
dbt docs serve    # view documentation in browser
```

---

## Naming Conventions

| Prefix | Layer | Example |
|---|---|---|
| `stg_` | Staging | `stg_orders.sql` |
| `dim_` | Dimension | `dim_customers.sql` |
| `fct_` | Fact | `fct_orders.sql` |

---

## Important Things to Remember

1. **`ref()` builds the dependency graph** — dbt knows to build staging before marts because marts use `ref('stg_...')`. Never hardcode schema.table names.

2. **Staging is one-to-one** — one staging model per raw table. No joins in staging.

3. **Fact tables carry foreign keys, not dimension data** — don't join dimensions into your fact table. Just carry the IDs.

4. **`order_item_id` is not globally unique** — it's a sequence number within an order (1, 2, 3...). The unique combination is `order_id + order_item_id`.

5. **Always `dbt run` before `dbt test`** — tests run against the built tables. If you change a model, rebuild first.

6. **`profiles.yml` lives outside your project** — in `~/.dbt/profiles.yml`. This keeps credentials out of Git.

7. **Incremental models need `--full-refresh` when structure changes** — adding or removing columns requires a full rebuild.

---

## Further Reading

- dbt Best Practice Workflows: `docs.getdbt.com/best-practices/best-practice-workflows`
- How to structure dbt projects: `docs.getdbt.com/best-practices/how-we-structure/1-guide-overview`
- How to style dbt models: `docs.getdbt.com/best-practices/how-we-style/1-how-we-style-our-dbt-models`
- Free official dbt course: `courses.getdbt.com`