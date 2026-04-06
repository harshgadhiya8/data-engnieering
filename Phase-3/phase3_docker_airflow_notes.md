# Phase 3 — Docker & Airflow Notes + Runbook

---

## Core Concepts

### What is Docker?
Docker is a tool that packages your code and all its dependencies into a **container** — a self-contained environment that runs identically on any machine. It solves the "it works on my machine" problem.

**Analogy:** Instead of sharing a recipe and hoping someone has the same kitchen, you ship them the entire kitchen.

### Key Docker Terms

| Term | What it is |
|---|---|
| **Image** | A blueprint/snapshot of your environment. Built once, run many times. |
| **Container** | A running instance of an image. Like a running program from an exe file. |
| **Dockerfile** | A recipe file with instructions to build an image. |
| **Docker Compose** | A tool to run multiple containers together using a single YAML file. |
| **Volume** | A way to share files between your machine and a container. |
| **Registry** | A place to store and share images. Docker Hub is the public one. |

### Dockerfile Structure
```dockerfile
FROM python:3.12-slim          # base image to start from
WORKDIR /app                   # working directory inside container
COPY requirements.txt .        # copy requirements into container
RUN pip install -r requirements.txt  # install dependencies
COPY pipeline.py .             # copy your script into container
CMD ["python", "pipeline.py"]  # command to run when container starts
```

### What is Apache Airflow?
Airflow is a pipeline scheduler and orchestrator. Instead of running pipelines manually, Airflow runs them on a schedule, retries failed tasks automatically, and gives you a monitoring UI.

**Key idea:** You define your pipeline as a DAG (Python file), and Airflow takes care of running it.

### Key Airflow Terms

| Term | What it is |
|---|---|
| **DAG** | Directed Acyclic Graph — a Python file defining tasks and their order |
| **Task** | One step in your pipeline (extract, transform, load etc.) |
| **Operator** | The type of task — PythonOperator runs Python functions |
| **Schedule** | When the DAG runs — defined using cron syntax |
| **Run** | One execution of the DAG |
| **XCom** | Way to pass data between tasks (we used files instead) |

### Cron Syntax Quick Reference
```
┌───── minute (0-59)
│ ┌───── hour (0-23)
│ │ ┌───── day of month (1-31)
│ │ │ ┌───── month (1-12)
│ │ │ │ ┌───── day of week (0-6, Sunday=0)
│ │ │ │ │
* * * * *

0 7 * * *    → every day at 7:00 AM
0 0 * * *    → every day at midnight
0 9 * * 1    → every Monday at 9:00 AM
*/15 * * * * → every 15 minutes
```

---

## Your Phase 3 Architecture

```
Phase-3/
├── docker-compose.yaml      # runs Airflow + Postgres together
├── .env                     # contains AIRFLOW_UID
├── dags/
│   ├── etl_pipeline.py      # Airflow DAG file
│   └── pipeline.py          # ETL functions (copied from Phase 1)
├── logs/                    # Airflow task logs
└── plugins/                 # custom Airflow plugins (empty for now)
```

### DAG Task Flow
```
extract → transform → load → dbt_run
```
- **extract** — calls Open-Meteo API, saves raw data as `raw_weather.json`
- **transform** — reads JSON, cleans data, saves as `weather_data.parquet`
- **load** — reads Parquet, loads into PostgreSQL
- **dbt_run** — runs dbt models in Phase 2 project

### Why Functions Communicate Through Files
Each Airflow task runs independently — variables don't persist between tasks. So:
- `extract()` saves output to a file
- `transform()` reads that file, saves its output to another file
- `load()` reads that file
This keeps each task self-contained and independently retriable.

---

## DAG File Structure

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys

sys.path.insert(0, '/opt/airflow/dags')
from pipeline import extract, transform, load, dbt_run

default_args = {
    'owner': 'harsh',
    'retries': 3,                           # retry 3 times on failure
    'retry_delay': timedelta(minutes=5),    # wait 5 mins between retries
    'email_on_failure': False               # set True + add email to enable alerts
}

with DAG(
    dag_id='weather_etl_pipeline',
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval='0 7 * * *',          # runs daily at 7AM
    catchup=False                           # don't run missed past schedules
) as dag:

    task_extract = PythonOperator(task_id='extract', python_callable=extract)
    task_transform = PythonOperator(task_id='transform', python_callable=transform)
    task_load = PythonOperator(task_id='load', python_callable=load)
    task_dbt_run = PythonOperator(task_id='dbt_run', python_callable=dbt_run)

    task_extract >> task_transform >> task_load >> task_dbt_run
```

---

## Runbook — How to Run the Pipeline

### First Time Setup

**Step 1 — Make sure Docker Desktop is running**
Open Docker Desktop from Applications. Wait for the whale icon in menu bar to stop animating.

**Step 2 — Add Docker to PATH (if not permanent)**
```bash
export PATH="$PATH:/Applications/Docker.app/Contents/Resources/bin"
```

**Step 3 — Navigate to Phase 3 folder**
```bash
cd path/to/Phase-3
```

**Step 4 — Create the .env file**
```bash
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

**Step 5 — Initialize Airflow database (first time only)**
```bash
docker compose up airflow-init
```
Wait until you see `exited with code 0`.

**Step 6 — Start all services**
```bash
docker compose up
```
Wait until logs settle down.

**Step 7 — Open Airflow UI**
Go to `http://localhost:8080` in your browser.
- Username: `airflow`
- Password: `airflow`

**Step 8 — Enable and trigger the DAG**
- Find `weather_etl_pipeline` in the DAG list
- Toggle the switch to enable it
- Click ▶ to trigger a manual run
- Click the DAG name → Graph view to monitor tasks

---

### Daily Usage (After First Setup)

```bash
# 1. Open Docker Desktop
# 2. Navigate to Phase 3
cd path/to/Phase-3

# 3. Add Docker to PATH if needed
export PATH="$PATH:/Applications/Docker.app/Contents/Resources/bin"

# 4. Start Airflow
docker compose up

# 5. Open http://localhost:8080
```

### Stopping Airflow
```bash
# Stop containers but keep data
docker compose down

# Stop containers and remove all data (fresh start)
docker compose down --volumes --rmi all
```

---

## Runbook — Troubleshooting

### Docker Issues

**`zsh: command not found: docker`**
```bash
export PATH="$PATH:/Applications/Docker.app/Contents/Resources/bin"
```
Make it permanent:
```bash
echo 'export PATH="$PATH:/Applications/Docker.app/Contents/Resources/bin"' >> ~/.zshrc
source ~/.zshrc
```

**`Cannot connect to Docker daemon`**
Docker Desktop is not running. Open it from Applications and wait for it to fully start.

**`docker build` fails**
- Make sure you're in the folder containing the Dockerfile
- Make sure the `.` is at the end of the command: `docker build -t name .`

**Port already in use**
```bash
# Check what's using port 8080
lsof -i :8080

# Kill the process
kill -9 <PID>
```

---

### Airflow Issues

**DAG not appearing in UI**
- Airflow scans the dags folder every 30 seconds — wait and refresh
- Check for Python syntax errors in your DAG file
- Check Airflow logs: `docker compose logs airflow-scheduler`

**Task failing — how to debug**
1. Click on the failed task (red box) in Graph view
2. Click **Logs** to see the full error message
3. Fix the issue in your code
4. Clear the failed task and re-run: click task → **Clear** → **Confirm**

**Import errors in DAG**
- Make sure `pipeline.py` is in the `dags` folder
- Make sure `sys.path.insert(0, '/opt/airflow/dags')` is in your DAG file
- Check the exact function names match between `pipeline.py` and DAG file

**Airflow UI not opening at localhost:8080**
- Make sure `docker compose up` is still running in your terminal
- Check containers are running: `docker ps`
- Wait a minute — webserver takes time to start

**`docker compose up` hangs or crashes**
```bash
# Stop everything
docker compose down

# Remove volumes and start fresh
docker compose down --volumes

# Re-initialize
docker compose up airflow-init
docker compose up
```

---

### Pipeline Issues

**`raw_weather.json` not found error in transform task**
The extract task failed or didn't save the file. Check extract task logs first.

**PostgreSQL connection error in load task**
- Check your connection string in `pipeline.py`
- Make sure PostgreSQL is running
- Check credentials are correct

**dbt run failing in dbt_run task**
- Check the `cwd` path in `dbt_run()` points to your correct Phase 2 ecommerce folder
- Make sure your dbt virtual environment is accessible
- Check dbt logs in the task output

---

## Key Commands Reference

```bash
# Docker
docker images                    # list all images
docker ps                        # list running containers
docker compose up                # start all services
docker compose up -d             # start in background
docker compose down              # stop all services
docker compose logs              # view all logs
docker compose logs airflow-scheduler  # view scheduler logs
docker build -t name .           # build an image

# Airflow (inside container)
docker compose exec airflow-scheduler airflow dags list    # list all DAGs
docker compose exec airflow-scheduler airflow tasks list weather_etl_pipeline  # list tasks
```

---

## Important Things to Remember

1. **Docker Desktop must be running** before any docker commands work
2. **DAG files are picked up automatically** — just save the file in the dags folder
3. **Always check task logs** when something fails — don't guess
4. **`catchup=False`** prevents Airflow from running all missed schedules since `start_date`
5. **`>>` sets task order** — `task_a >> task_b` means b runs after a
6. **Functions communicate through files** — variables don't persist between tasks
7. **`--full-refresh`** needed for incremental dbt models when structure changes
8. **`docker compose down --volumes`** wipes all Airflow metadata — use only for fresh start
