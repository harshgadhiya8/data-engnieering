from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys

# Add your Phase 1 path so Airflow can find your functions
sys.path.insert(0, '/opt/airflow/dags')
from pipeline import extract, transform, load, dbt_run

# Default arguments for all tasks
default_args = {
    'owner': 'harsh',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False
}

# Define the DAG
with DAG(
    dag_id='weather_etl_pipeline',
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval='0 7 * * *',
    catchup=False
) as dag:

    task_extract = PythonOperator(
        task_id='extract',
        python_callable=extract
    )

    task_transform = PythonOperator(
        task_id='transform',
        python_callable=transform
    )

    task_load = PythonOperator(
        task_id='load',
        python_callable=load
    )

    task_dbt_run = PythonOperator(
        task_id='dbt_run',
        python_callable=dbt_run
    )

    # Set task order
    task_extract >> task_transform >> task_load >> task_dbt_run