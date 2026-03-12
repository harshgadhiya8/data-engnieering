# 🚀 Data Analyst to Data Engineer: Project-Based Roadmap

> **Philosophy**: You already know Python, SQL, and Excel. This roadmap skips the basics and focuses on building the skills and portfolio of a working Data Engineer — through real, progressive projects.

---

## 🏗️ What Data Engineering Actually Is

Think of it this way:
- **Data Analyst**: "Given the data in this database, what insights can I find?"
- **Data Engineer**: "How do I reliably build, automate, and scale the system that gets that data into the database in the first place?"

You will learn all 6 pillars of modern data engineering:

| # | Domain | Key Tools |
|---|---|---|
| 1 | **Programming & Scripting** | Python, Bash/Linux |
| 2 | **Databases & Data Warehouses** | PostgreSQL, Snowflake, BigQuery |
| 3 | **Data Modeling & Transformations** | dbt, Star Schema, Dimensional Modeling |
| 4 | **Containerization & Orchestration** | Docker, Apache Airflow |
| 5 | **Cloud Computing** | AWS (S3, Lambda, IAM), GCP/Azure |
| 6 | **Big Data & Streaming** | Apache Spark, Apache Kafka, Delta Lake |

---

## Phase 1: ETL Fundamentals & File Formats (Weeks 1-4)
*Goal: Stop analyzing data manually. Start building scripts that extract, transform, and load data automatically.*

### 🎯 Core Concepts
- **ETL (Extract, Transform, Load)**: The foundation of every data pipeline.
- **APIs**: Fetching data programmatically using Python's `requests` library.
- **File Formats**: Why data engineers don't just use CSV files.
  - **CSV**: Simple, human-readable, but slow and large.
  - **JSON**: Great for APIs and semi-structured data.
  - **Parquet**: Columnar format — compressed, fast, the standard in production data pipelines.
- **Python for DE**: `pandas` for transformation, `SQLAlchemy`/`psycopg2` for database connections, `logging` for error tracking.
- **Git**: Every pipeline you write must be version controlled from Day 1.

### 🛠️ Project 1: Automated API-to-Database Pipeline
**You will build:** A Python script that automatically fetches data from a public API every day, transforms it, saves it as Parquet, and loads it into a PostgreSQL database.

**Steps:**
1. Pick a free API — e.g., [OpenWeatherMap](https://openweathermap.org/api) (weather), [CoinGecko](https://www.coingecko.com/en/api) (crypto prices), or [Open Library](https://openlibrary.org/developers/api) (books).
2. Write a Python script to `GET` the JSON data from the API.
3. Use `pandas` to flatten, clean, and transform the JSON into rows and columns.
4. **Save the transformed data as a `.parquet` file** using `pandas.to_parquet()`. This is how real pipelines store intermediate data.
5. Use `SQLAlchemy` to load the Parquet data into a local PostgreSQL database table.
6. Add `logging` to your script — log every step (extraction, transformation, load) and any errors.

**Skills gained**: ETL fundamentals, API integration, Parquet file format, PostgreSQL, Python logging, Git.

---

## Phase 2: Data Modeling & Warehousing with dbt (Weeks 5-8)
*Goal: Learn how to design databases for analytics, not just use them.*

### 🎯 Core Concepts
- **OLTP vs OLAP**: Transactional databases (fast writes) vs. Analytical databases (fast reads across millions of rows).
- **Dimensional Modeling**: The industry-standard way to structure an analytical database.
  - **Fact Table**: The core events/metrics (e.g., `fact_sales` — each row is a sale).
  - **Dimension Tables**: The context around events (e.g., `dim_customer`, `dim_product`, `dim_date`).
  - **Star Schema**: One fact table connected to multiple dimension tables. Fast, intuitive.
- **dbt (Data Build Tool)**: Write SQL `SELECT` statements. dbt handles the `CREATE TABLE` part. Industry standard for transformations.
- **Incremental Models**: A critical pattern — instead of reloading the entire table every day, only process *new or changed* data. This is faster, cheaper, and how production pipelines work.
- **Data Quality & Testing**: How do you know your data is correct? `dbt test` lets you write rules (e.g., "this column must never be NULL", "these IDs must be unique").

### 🛠️ Project 2: Retail Data Warehouse with dbt + Incremental Loads
**You will build:** A proper analytical data warehouse using a Kaggle dataset, then use dbt to transform raw data into a Star Schema with automated quality tests.

**Steps:**
1. Download the [Brazilian E-Commerce (Olist) dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) from Kaggle — it has real orders, products, customers, and reviews.
2. Load the raw CSV files into a PostgreSQL database. This is your raw "source" layer.
3. On paper, design a Star Schema: `fact_orders` as your fact table, with `dim_customers`, `dim_products`, `dim_sellers`, and `dim_dates` as dimensions.
4. Install `dbt-core` and `dbt-postgres`. Create a dbt project.
5. Write dbt **staging models** to clean the raw tables (fix data types, rename columns, handle NULLs).
6. Write dbt **mart models** to build your final Star Schema fact and dimension tables.
7. **Implement an incremental model** for `fact_orders`: configure it so dbt only processes orders with an `order_date` newer than the last run.
8. Write `dbt tests` for data quality: unique order IDs, no null customer IDs, valid date ranges.
9. Run `dbt run && dbt test` to build and validate your warehouse. Fix any failures.

**Skills gained**: Dimensional modeling, Star Schema, dbt, incremental loads, data quality testing.

---

## Phase 3: Containerization & Orchestration (Weeks 9-12)
*Goal: Your pipelines need to run automatically, reliably, every day — even when you are asleep.*

### 🎯 Core Concepts
- **Docker**: A "container" packages your code + all its dependencies together, so it runs identically on your laptop, a server, or the cloud. Essential because "it works on my machine" is not acceptable in production.
- **Docker Compose**: Runs multiple containers together (e.g., your pipeline container + a Postgres container + an Airflow container).
- **Apache Airflow**: The industry-standard pipeline scheduler. You write a DAG (Directed Acyclic Graph) — a Python file that defines tasks and their dependencies. Airflow runs it on a schedule, retries on failure, and gives you a monitoring UI.
- **Pipeline Monitoring & Alerting**: How do you know if a pipeline silently failed at 3AM? You need alerts — Airflow can send email/Slack notifications on failure.

### 🛠️ Project 3: Fully Orchestrated, Dockerized Data Pipeline
**You will build:** A complete, automated, monitored pipeline — your Project 1 script running on a daily schedule inside Docker, orchestrated by Airflow, with failure alerts.

**Steps:**
1. Write a `Dockerfile` for your Project 1 Python ETL script. It should install Python, your libraries (`requests`, `pandas`, `pyarrow`, `psycopg2`), and run the script.
2. Write a `docker-compose.yml` that starts both Airflow and your PostgreSQL database.
3. Write an **Airflow DAG** in Python with the following tasks in sequence:
   - **Task 1** (`extract`): Call the API, save raw JSON locally.
   - **Task 2** (`transform`): Read raw JSON, clean it, save as Parquet.
   - **Task 3** (`load`): Load Parquet into PostgreSQL.
   - **Task 4** (`dbt_run`): Run dbt to update your Star Schema models.
4. Configure task **retries** (retry 3 times if a task fails, wait 5 minutes between retries).
5. Set up **failure email alerts** in Airflow using its `email_on_failure` feature.
6. Schedule the DAG to run every day at 7:00 AM.
7. Open the Airflow Web UI, trigger a manual run, and verify all tasks succeed (green!).

**Skills gained**: Docker, Docker Compose, Apache Airflow, DAGs, task dependencies, retries, monitoring, alerting.

---

## Phase 4: Cloud — Building a Modern Data Stack on AWS (Weeks 13-18)
*Goal: Almost all real production data engineering happens in the cloud. Learn to build the same pipelines using cloud-managed services.*

### 🎯 Core Concepts
- **IAM (Identity and Access Management)**: Before anything in AWS, you need to understand permissions — which services can talk to which other services, and how to do it securely. This trips up almost every beginner.
- **AWS S3**: Cheap, infinitely scalable object storage. The industry standard for raw data (your "Data Lake").
- **AWS Lambda**: Serverless Python functions — runs your code in response to an event (e.g., when a new file lands in S3) without you managing a server.
- **Snowflake**: A massively popular cloud data warehouse, separate from AWS. Connects to S3 natively.
- **dbt Cloud**: The managed, cloud-hosted version of dbt. Runs transformations on a schedule.

### 🛠️ Project 4: Event-Driven Cloud Pipeline (S3 → Lambda → Snowflake → dbt Cloud)
**You will build:** A fully cloud-native data pipeline where dropping a file into S3 automatically triggers loading into Snowflake, which then triggers dbt transformations.

**Steps:**
1. **Create an AWS Free Tier account**. Set up a new IAM user with least-privilege permissions (don't use the root account!).
2. **Create an S3 Bucket** — this is your raw data landing zone.
3. **Set up a free Snowflake trial account**. Create a database, schema, and warehouse. Configure the [Snowflake storage integration with S3](https://docs.snowflake.com/en/user-guide/data-load-s3-config-storage-integration).
4. **Write an AWS Lambda function** (Python) that:
   - Triggers automatically when a new `.parquet` file is uploaded to your S3 bucket.
   - Connects to Snowflake and runs a `COPY INTO` SQL command to load the file.
   - Logs success/failure to AWS CloudWatch.
5. Upload a Parquet file to your S3 bucket. Watch the Lambda function trigger automatically. Verify data appears in Snowflake.
6. **Create a dbt Cloud account** (free tier). Connect it to your Snowflake warehouse. Migrate your dbt models from Project 2 to dbt Cloud. Schedule them to run after the Lambda completes.
7. Connect Snowflake to **PowerBI, Tableau, or Google Looker Studio** and build a simple sales dashboard.

**Skills gained**: AWS IAM, S3, Lambda, CloudWatch, event-driven architecture, Snowflake, dbt Cloud, end-to-end cloud pipeline.

---

## Phase 5: Big Data & Streaming (Weeks 19+)
*Goal: When datasets are too large for Pandas or need to be processed in real-time, you need distributed systems.*

### 🎯 Core Concepts
- **Why Pandas Falls Short**: Pandas loads everything into RAM. With 100GB+ datasets, it crashes. Spark distributes the work across multiple machines.
- **Apache Spark / PySpark**: Distributed data processing. Syntax is similar to Pandas + SQL. The industry standard for big data batch processing.
- **Delta Lake**: An open-source storage format (built on Parquet) that adds ACID transactions, versioning ("Time Travel"), and schema enforcement to a data lake. The backbone of the "Lakehouse" architecture.
- **Apache Kafka**: A distributed message queue for real-time data streams. Instead of processing data in daily batches, Kafka lets you process it within seconds of it being generated.

### 🛠️ Project 5A: Batch Big Data Processing with PySpark & Delta Lake
**You will build:** A Spark pipeline that processes a massive dataset and stores results in Delta Lake format on Databricks.

**Steps:**
1. Create a free [Databricks Community Edition account](https://community.cloud.databricks.com/) — this gives you a managed Spark environment.
2. Download the [NYC Taxi Trip dataset](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) (multiple gigabytes of real trip data).
3. Upload it to Databricks File System (DBFS).
4. Write PySpark code to:
   - Read all Parquet files.
   - Calculate: average fare by pickup zone, busiest hours, and revenue per driver.
   - Write the aggregated results as **Delta Lake** tables.
5. Enable **Delta Lake Time Travel**: query data "as of" yesterday using `VERSION AS OF` SQL syntax.
6. Add **schema enforcement**: try inserting a row with a wrong column type and observe the error.

---

### 🛠️ Project 5B: Real-Time Streaming Pipeline with Kafka
**You will build:** A real-time pipeline that streams events through Kafka and processes them as they arrive.

**Steps:**
1. Install **Apache Kafka** locally using Docker Compose.
2. Write a Python **Producer** script that simulates a stream of e-commerce orders being placed (one event every second).
3. Write a Python **Consumer** script that reads from Kafka in real-time and:
   - Calculates a rolling 1-minute average order value.
   - Detects and flags orders over ₹10,000 as potential fraud.
   - Writes flagged events to a separate Kafka topic.
4. Write a second consumer that reads from the "flagged" topic and inserts into a PostgreSQL table.
5. View your real-time metrics updating live.

**Skills gained**: PySpark, Delta Lake, Databricks, Time Travel, Apache Kafka, stream processing, real-time fraud detection.

---

## 📚 Essential Resources

| Type | Resource | Why |
|---|---|---|
| 📘 Book | *Fundamentals of Data Engineering* – Joe Reis & Matt Housley | Best overview of architecture without tool-hype |
| 📘 Book | *Designing Data-Intensive Applications* – Martin Kleppmann | Deep dive into why systems work the way they do |
| 🎓 Course | [Data Engineering Zoomcamp](https://github.com/DataTalks-Club/data-engineering-zoomcamp) – DataTalks.Club | Free, hands-on, project-based. Highly recommended |
| 🎓 Course | [dbt Learn](https://courses.getdbt.com/) – dbt Labs | Free official dbt courses |
| 📺 YouTube | Seattle Data Guy | Real-world DE topics for beginners |
| 📺 YouTube | Data with Zach | Great for analyst → engineer transition |
| 💬 Community | r/dataengineering | Ask questions, follow industry discussions |
| 💬 Community | dbt Community Slack | Largest dbt community, very helpful |

---

## 🏆 Portfolio Checklist

By the end of this roadmap, your GitHub should have:

- [ ] **Project 1**: API → Parquet → PostgreSQL pipeline with logging
- [ ] **Project 2**: dbt Star Schema with incremental models and data quality tests
- [ ] **Project 3**: Dockerized, Airflow-orchestrated, multi-step pipeline with monitoring
- [ ] **Project 4**: Full cloud pipeline on AWS + Snowflake + dbt Cloud with a dashboard
- [ ] **Project 5A**: PySpark + Delta Lake big data processing on Databricks
- [ ] **Project 5B**: Real-time Kafka streaming pipeline with fraud detection

Each repo should have a detailed `README.md` with: the business problem, architecture diagram, tech stack, and setup instructions.

---

## 💡 Key Mindset Shifts for the Transitioning Analyst

1. **Think systems, not queries**: You're not just writing SQL anymore — you're designing the system that runs SQL reliably every day.
2. **SQL is still your superpower**: dbt, Snowflake, Spark SQL — SQL is everywhere in DE. You're ahead of most beginners.
3. **Failure is expected; handling it is the job**: Production pipelines break. Logging, retries, and alerts are not optional.
4. **Start small, then automate**: Build it manually first to understand it. Then automate. Never automate something you don't understand.

---

*Follow this in order. Each project builds directly on the previous one. By Project 4, you'll have a cloud-native, end-to-end pipeline that a real company would be proud of.*
