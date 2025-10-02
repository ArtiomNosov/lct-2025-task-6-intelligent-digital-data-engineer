from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-engineer',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    'simple_spark_test',
    default_args=default_args,
    description='Simple Spark test DAG',
    schedule_interval=None,  # Запуск только вручную
    catchup=False,
    tags=['spark', 'test'],
) as dag:

    # Простая Spark задача
    spark_hello_world = BashOperator(
        task_id='spark_hello_world',
        bash_command="""
        echo "Running simple Spark job..."
        docker exec spark-master /opt/spark/bin/spark-submit \
            --master spark://spark-master:7077 \
            --class org.apache.spark.examples.SparkPi \
            /opt/spark/examples/jars/spark-examples_2.12-3.5.1.jar 10
        """,
    )

    # Тест PySpark
    pyspark_test = BashOperator(
        task_id='pyspark_test',
        bash_command="""
        echo "Running PySpark test..."
        docker exec spark-master /opt/spark/bin/pyspark \
            --master spark://spark-master:7077 \
            --executor-memory 1g \
            --executor-cores 1 \
            -c "
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName('AirflowTest').getOrCreate()
df = spark.createDataFrame([(1, 'Hello'), (2, 'World')], ['id', 'message'])
df.show()
spark.stop()
print('PySpark test completed!')
"
        """,
    )