from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import json

default_args = {
    'owner': 'data-engineer',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=3),
}


def create_spark_streaming_job():
    """Создание Spark Streaming job для обработки Kafka данных"""
    spark_code = '''
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import json

# Создание Spark сессии
spark = SparkSession.builder \\
    .appName("KafkaSparkStreaming") \\
    .master("spark://spark-master:7077") \\
    .config("spark.sql.adaptive.enabled", "true") \\
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \\
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Схемы для разных типов данных
user_schema = StructType([
    StructField("user_id", IntegerType(), True),
    StructField("name", StringType(), True),
    StructField("email", StringType(), True),
    StructField("registration_date", StringType(), True)
])

transaction_schema = StructType([
    StructField("transaction_id", StringType(), True),
    StructField("user_id", IntegerType(), True),
    StructField("amount", DoubleType(), True),
    StructField("currency", StringType(), True),
    StructField("timestamp", StringType(), True)
])

event_schema = StructType([
    StructField("event_id", StringType(), True),
    StructField("user_id", IntegerType(), True),
    StructField("event_type", StringType(), True),
    StructField("properties", StringType(), True),
    StructField("timestamp", StringType(), True)
])

# Чтение из Kafka
kafka_df = spark \\
    .readStream \\
    .format("kafka") \\
    .option("kafka.bootstrap.servers", "kafka:9092") \\
    .option("subscribe", "user-events,transactions,system-events") \\
    .option("startingOffsets", "latest") \\
    .load()

# Парсинг сообщений
parsed_df = kafka_df.select(
    col("topic"),
    col("partition"),
    col("offset"),
    col("timestamp").alias("kafka_timestamp"),
    col("value").cast("string").alias("json_data")
)

# Обработка разных топиков
def process_user_events(df):
    return df.filter(col("topic") == "user-events") \\
        .select(
            from_json(col("json_data"), user_schema).alias("data"),
            col("kafka_timestamp")
        ) \\
        .select("data.*", "kafka_timestamp") \\
        .withColumn("processed_at", current_timestamp())

def process_transactions(df):
    return df.filter(col("topic") == "transactions") \\
        .select(
            from_json(col("json_data"), transaction_schema).alias("data"),
            col("kafka_timestamp")
        ) \\
        .select("data.*", "kafka_timestamp") \\
        .withColumn("processed_at", current_timestamp()) \\
        .withColumn("amount_usd", 
            when(col("currency") == "RUB", col("amount") / 100)
            .when(col("currency") == "EUR", col("amount") * 1.1)
            .otherwise(col("amount"))
        )

def process_system_events(df):
    return df.filter(col("topic") == "system-events") \\
        .select(
            from_json(col("json_data"), event_schema).alias("data"),
            col("kafka_timestamp")
        ) \\
        .select("data.*", "kafka_timestamp") \\
        .withColumn("processed_at", current_timestamp())

# Обработка каждого типа данных
user_events_df = process_user_events(parsed_df)
transactions_df = process_transactions(parsed_df)
system_events_df = process_system_events(parsed_df)

# Запись в консоль для мониторинга
user_query = user_events_df \\
    .writeStream \\
    .outputMode("append") \\
    .format("console") \\
    .option("truncate", False) \\
    .queryName("user_events_console") \\
    .start()

transaction_query = transactions_df \\
    .writeStream \\
    .outputMode("append") \\
    .format("console") \\
    .option("truncate", False) \\
    .queryName("transactions_console") \\
    .start()

# Агрегация данных
transaction_aggregates = transactions_df \\
    .groupBy(
        window(col("kafka_timestamp"), "5 minutes"),
        col("currency")
    ) \\
    .agg(
        count("*").alias("transaction_count"),
        sum("amount").alias("total_amount"),
        avg("amount").alias("avg_amount"),
        max("amount").alias("max_amount")
    ) \\
    .withColumn("window_start", col("window.start")) \\
    .withColumn("window_end", col("window.end")) \\
    .drop("window")

# Запись агрегатов
aggregate_query = transaction_aggregates \\
    .writeStream \\
    .outputMode("update") \\
    .format("console") \\
    .option("truncate", False) \\
    .queryName("transaction_aggregates") \\
    .start()

print("Spark Streaming jobs started...")
print("Monitoring queries for 2 minutes...")

# Ожидание обработки
user_query.awaitTermination(120)
transaction_query.awaitTermination(120)
aggregate_query.awaitTermination(120)

print("Spark Streaming completed!")
spark.stop()
'''

    with open('/tmp/spark_streaming_job.py', 'w') as f:
        f.write(spark_code)

    print("Spark streaming job created!")


with DAG(
        'kafka_spark_streaming_pipeline',
        default_args=default_args,
        description='Real-time data processing: Kafka → Spark → PostgreSQL',
        schedule_interval=timedelta(minutes=30),
        catchup=False,
        tags=['kafka', 'spark', 'streaming', 'realtime'],
) as dag:
    # Создание топиков Kafka
    create_kafka_topics = BashOperator(
        task_id='create_kafka_topics',
        bash_command="""
        echo "Creating Kafka topics..."

        # Топик для пользовательских событий
        docker exec kafka kafka-topics --create \\
            --topic user-events \\
            --bootstrap-server kafka:9092 \\
            --partitions 3 \\
            --replication-factor 1 \\
            --if-not-exists

        # Топик для транзакций
        docker exec kafka kafka-topics --create \\
            --topic transactions \\
            --bootstrap-server kafka:9092 \\
            --partitions 3 \\
            --replication-factor 1 \\
            --if-not-exists

        # Топик для системных событий
        docker exec kafka kafka-topics --create \\
            --topic system-events \\
            --bootstrap-server kafka:9092 \\
            --partitions 2 \\
            --replication-factor 1 \\
            --if-not-exists

        echo "Kafka topics created successfully!"
        docker exec kafka kafka-topics --list --bootstrap-server kafka:9092
        """,
    )

    # Генерация тестовых данных в Kafka
    generate_test_data = BashOperator(
        task_id='generate_test_data',
        bash_command="""
        echo "Generating test data for Kafka topics..."

        # Пользовательские события
        for i in {1..10}; do
            echo "{\\"user_id\\": $i, \\"name\\": \\"User$i\\", \\"email\\": \\"user$i@example.com\\", \\"registration_date\\": \\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\\"}" | \\
            docker exec -i kafka kafka-console-producer \\
                --topic user-events \\
                --bootstrap-server kafka:9092
            sleep 1
        done

        # Транзакции
        currencies=("USD" "EUR" "RUB")
        for i in {1..15}; do
            currency=${currencies[$((RANDOM % 3))]}
            amount=$((RANDOM % 10000 + 100))
            user_id=$((RANDOM % 10 + 1))
            echo "{\\"transaction_id\\": \\"tx_$(date +%s)_$i\\", \\"user_id\\": $user_id, \\"amount\\": $amount, \\"currency\\": \\"$currency\\", \\"timestamp\\": \\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\\"}" | \\
            docker exec -i kafka kafka-console-producer \\
                --topic transactions \\
                --bootstrap-server kafka:9092
            sleep 2
        done

        # Системные события
        events=("login" "logout" "page_view" "click" "purchase")
        for i in {1..8}; do
            event_type=${events[$((RANDOM % 5))]}
            user_id=$((RANDOM % 10 + 1))
            echo "{\\"event_id\\": \\"evt_$(date +%s)_$i\\", \\"user_id\\": $user_id, \\"event_type\\": \\"$event_type\\", \\"properties\\": \\"{\\\\\\"page\\\\\\": \\\\\\"home\\\\\\"}\\", \\"timestamp\\": \\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\\"}" | \\
            docker exec -i kafka kafka-console-producer \\
                --topic system-events \\
                --bootstrap-server kafka:9092
            sleep 1
        done

        echo "Test data generation completed!"
        """,
    )

    # Создание Spark streaming job
    create_streaming_job = PythonOperator(
        task_id='create_streaming_job',
        python_callable=create_spark_streaming_job,
    )

    # Запуск Spark Streaming
    run_spark_streaming = BashOperator(
        task_id='run_spark_streaming',
        bash_command="""
        echo "Starting Spark Streaming job..."
        docker exec spark-master /opt/spark/bin/spark-submit \\
            --master spark://spark-master:7077 \\
            --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,org.postgresql:postgresql:42.7.0 \\
            --executor-memory 1g \\
            --executor-cores 1 \\
            --total-executor-cores 2 \\
            /tmp/spark_streaming_job.py
        """,
    )

    # Проверка результатов
    check_processing_results = BashOperator(
        task_id='check_processing_results',
        bash_command="""
        echo "=== Kafka Topics Status ==="
        docker exec kafka kafka-topics --list --bootstrap-server kafka:9092

        echo "=== Topic Descriptions ==="
        for topic in user-events transactions system-events; do
            echo "--- Topic: $topic ---"
            docker exec kafka kafka-topics --describe --topic $topic --bootstrap-server kafka:9092
        done

        echo "=== Spark Applications ==="
        curl -s http://localhost:8082/json/ | jq '.activeapps[] | {id: .id, name: .name, starttime: .starttime}' || echo "Spark Master API not available"

        echo "=== Processing completed successfully! ==="
        """,
    )

    # Определение зависимостей
    create_kafka_topics >> generate_test_data >> create_streaming_job >> run_spark_streaming >> check_processing_results