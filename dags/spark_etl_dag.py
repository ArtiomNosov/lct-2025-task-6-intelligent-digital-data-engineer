from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import json

# Параметры DAG по умолчанию
default_args = {
    'owner': 'data-engineer',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Создание DAG
with DAG(
        'spark_etl_pipeline',
        default_args=default_args,
        description='ETL pipeline using Spark, Kafka and PostgreSQL',
        schedule_interval=timedelta(hours=1),  # Запуск каждый час
        catchup=False,
        tags=['spark', 'etl', 'kafka'],
) as dag:
    # Задача 1: Проверка доступности Spark кластера
    check_spark_cluster = BashOperator(
        task_id='check_spark_cluster',
        bash_command="""
        echo "Checking Spark cluster status..."
        docker exec spark-master /opt/spark/bin/spark-submit \
            --master spark://spark-master:7077 \
            --class org.apache.spark.deploy.master.Master \
            --version
        """,
    )

    # Задача 2: Создание топика в Kafka
    create_kafka_topic = BashOperator(
        task_id='create_kafka_topic',
        bash_command="""
        echo "Creating Kafka topic for ETL data..."
        docker exec kafka kafka-topics --create \
            --topic etl-data \
            --bootstrap-server kafka:9092 \
            --partitions 3 \
            --replication-factor 1 \
            --if-not-exists
        """,
    )

    # Задача 3: Генерация тестовых данных и отправка в Kafka
    generate_and_send_data = BashOperator(
        task_id='generate_and_send_data',
        bash_command="""
        echo "Generating test data and sending to Kafka..."
        # Генерируем JSON данные и отправляем в Kafka
        for i in {1..10}; do
            echo "{\"id\": $i, \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"value\": $((RANDOM % 100))}" | \
            docker exec -i kafka kafka-console-producer \
                --topic etl-data \
                --bootstrap-server kafka:9092
        done
        echo "Sent 10 messages to Kafka topic 'etl-data'"
        """,
    )

    # Задача 4: Spark задача для обработки данных из Kafka
    spark_kafka_processing = BashOperator(
        task_id='spark_kafka_processing',
        bash_command="""
        echo "Running Spark job to process Kafka data..."

        # Создаём временный Python скрипт для Spark
        cat > /tmp/spark_kafka_job.py << 'EOF'
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType

# Создание Spark сессию
spark = SparkSession.builder \
    .appName("KafkaETLJob") \
    .master("spark://spark-master:7077") \
    .config("spark.sql.adaptive.enabled", "true") \
    .getOrCreate()

# Схема для JSON данных
schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("timestamp", StringType(), True),
    StructField("value", IntegerType(), True)
])

try:
    # Чтение данных из Kafka
    kafka_df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "etl-data") \
        .option("startingOffsets", "earliest") \
        .load()

    # Парсинг JSON и добавление колонок
    parsed_df = kafka_df \
        .select(
            from_json(col("value").cast("string"), schema).alias("data"),
            current_timestamp().alias("processing_time")
        ) \
        .select(
            col("data.id"),
            col("data.timestamp"),
            col("data.value"),
            col("processing_time")
        )

    # Вывод результата
    query = parsed_df \
        .writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", False) \
        .start()

    # Ожидание в течение 30 секунд для обработки
    query.awaitTermination(30)
    query.stop()

    print("Spark Kafka processing completed successfully!")

except Exception as e:
    print(f"Error in Spark job: {e}")
    raise

finally:
    spark.stop()
EOF

        # Запуск Spark job
        docker exec -i spark-master /opt/spark/bin/spark-submit \
            --master spark://spark-master:7077 \
            --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \
            /tmp/spark_kafka_job.py
        """,
    )

    # Задача 5: Простая Spark задача для подсчёта статистики
    spark_statistics = BashOperator(
        task_id='spark_statistics',
        bash_command="""
        echo "Running Spark statistics job..."

        # Создание Python скрипта для статистики
        cat > /tmp/spark_stats.py << 'EOF'
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg, max, min

# Создание Spark сессии
spark = SparkSession.builder \
    .appName("StatisticsJob") \
    .master("spark://spark-master:7077") \
    .getOrCreate()

try:
    # Создание тестовых данных
    data = [(i, f"user_{i}", i * 10) for i in range(1, 101)]
    df = spark.createDataFrame(data, ["id", "name", "score"])

    # Вычисление статистики
    stats = df.agg(
        count("*").alias("total_records"),
        avg("score").alias("avg_score"),
        max("score").alias("max_score"),
        min("score").alias("min_score")
    )

    print("=== Statistics Results ===")
    stats.show()

    # Сохранение результата
    stats.coalesce(1).write.mode("overwrite").json("/tmp/spark_stats_output")
    print("Statistics saved to /tmp/spark_stats_output")

except Exception as e:
    print(f"Error in statistics job: {e}")
    raise

finally:
    spark.stop()
EOF

        # Запуск статистики
        docker exec -i spark-master /opt/spark/bin/spark-submit \
            --master spark://spark-master:7077 \
            /tmp/spark_stats.py
        """,
    )

    # Задача 6: Проверка результатов
    check_results = BashOperator(
        task_id='check_results',
        bash_command="""
        echo "Checking job results..."
        echo "=== Spark Master UI ==="
        echo "Access Spark Master UI at: http://localhost:8082"
        echo "=== Spark Worker UI ==="
        echo "Access Spark Worker UI at: http://localhost:8083"
        echo "=== Kafka Topics ==="
        docker exec kafka kafka-topics --list --bootstrap-server kafka:9092
        echo "=== ETL Pipeline completed successfully! ==="
        """,
    )

    # Определение порядка выполнения задач
    check_spark_cluster >> create_kafka_topic >> generate_and_send_data >> spark_kafka_processing >> spark_statistics >> check_results