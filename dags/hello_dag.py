from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="hello_world",
    start_date=datetime(2025, 10, 1),
    schedule="@once",
    catchup=False,
) as dag:

    task = BashOperator(
        task_id="print_hello",
        bash_command="echo 'Hello from Airflow!'"
    )