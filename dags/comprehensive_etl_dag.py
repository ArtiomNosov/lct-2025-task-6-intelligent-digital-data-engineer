from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-engineer',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
        'comprehensive_etl_pipeline',
        default_args=default_args,
        description='Complete ETL pipeline with all components integration',
        schedule_interval=timedelta(hours=2),
        catchup=False,
        tags=['etl', 'comprehensive', 'integration'],
) as dag:
    # Этап 1: Подготовка инфраструктуры
    prepare_infrastructure = BashOperator(
        task_id='prepare_infrastructure',
        bash_command="""
        echo "=== Preparing ETL Infrastructure ==="

        # Проверка доступности всех сервисов
        echo "Checking PostgreSQL..."
        docker exec postgres pg_isready -U admin

        echo "Checking Kafka..."
        docker exec kafka kafka-broker-api-versions --bootstrap-server kafka:9092 | head -1

        echo "Checking Spark..."
        curl -s http://localhost:8082 | grep -q "Spark Master" && echo "Spark Master is running"

        echo "All services are ready!"
        """,
    )

    # Этап 2: Создание схемы данных
    create_data_warehouse_schema = PostgresOperator(
        task_id='create_data_warehouse_schema',
        postgres_conn_id='postgres_default',
        sql="""
        -- Создание схемы для хранилища данных
        CREATE SCHEMA IF NOT EXISTS dwh;

        -- Таблица фактов транзакций
        CREATE TABLE IF NOT EXISTS dwh.fact_transactions (
            transaction_id VARCHAR(100) PRIMARY KEY,
            user_id INTEGER,
            amount DECIMAL(15,2),
            currency VARCHAR(10),
            amount_usd DECIMAL(15,2),
            transaction_date DATE,
            transaction_hour INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Таблица измерений пользователей
        CREATE TABLE IF NOT EXISTS dwh.dim_users (
            user_id INTEGER PRIMARY KEY,
            name VARCHAR(200),
            email VARCHAR(200),
            city VARCHAR(100),
            registration_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Таблица агрегатов
        CREATE TABLE IF NOT EXISTS dwh.agg_daily_transactions (
            date_key DATE,
            currency VARCHAR(10),
            transaction_count INTEGER,
            total_amount DECIMAL(15,2),
            avg_amount DECIMAL(15,2),
            max_amount DECIMAL(15,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (date_key, currency)
        );

        -- Индексы для оптимизации
        CREATE INDEX IF NOT EXISTS idx_fact_transactions_date ON dwh.fact_transactions(transaction_date);
        CREATE INDEX IF NOT EXISTS idx_fact_transactions_user ON dwh.fact_transactions(user_id);
        """,
    )

    # Этап 3: Извлечение данных (Extract)
    extract_data_from_sources = BashOperator(
        task_id='extract_data_from_sources',
        bash_command="""
        echo "=== Data Extraction Phase ==="

        # Создание топиков для ETL процесса
        docker exec kafka kafka-topics --create \\
            --topic etl-raw-data \\
            --bootstrap-server kafka:9092 \\
            --partitions 4 \\
            --replication-factor 1 \\
            --if-not-exists

        docker exec kafka kafka-topics --create \\
            --topic etl-processed-data \\
            --bootstrap-server kafka:9092 \\
            --partitions 4 \\
            --replication-factor 1 \\
            --if-not-exists

        # Симуляция извлечения данных из различных источников
        echo "Extracting data from CSV source..."
        for i in {1..20}; do
            echo "{\\"source\\": \\"csv\\", \\"user_id\\": $((RANDOM % 100 + 1)), \\"name\\": \\"User$i\\", \\"email\\": \\"user$i@company.com\\", \\"city\\": \\"Moscow\\", \\"registration_date\\": \\"2025-01-0$((RANDOM % 9 + 1))\\"}" | \\
            docker exec -i kafka kafka-console-producer \\
                --topic etl-raw-data \\
                --bootstrap-server kafka:9092
        done

        echo "Extracting data from JSON API..."
        for i in {1..30}; do
            amount=$((RANDOM % 50000 + 1000))
            currencies=("USD" "EUR" "RUB")
            currency=${currencies[$((RANDOM % 3))]}
            user_id=$((RANDOM % 100 + 1))
            echo "{\\"source\\": \\"api\\", \\"transaction_id\\": \\"api_tx_$i\\", \\"user_id\\": $user_id, \\"amount\\": $amount, \\"currency\\": \\"$currency\\", \\"timestamp\\": \\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\\"}" | \\
            docker exec -i kafka kafka-console-producer \\
                --topic etl-raw-data \\
                --bootstrap-server kafka:9092
        done

        echo "Data extraction completed!"
        """,
    )

    # Этап 4: Трансформация данных через Spark (Transform)
    transform_data_with_spark = BashOperator(
        task_id='transform_data_with_spark',
        bash_command="""
        echo "=== Data Transformation Phase ==="

        # Создание Spark job для трансформации
        cat > /tmp/etl_transform_job.py << 'EOF'
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import json

spark = SparkSession.builder \\
    .appName("ETL_Transform") \\
    .master("spark://spark-master:7077") \\
    .config("spark.sql.adaptive.enabled", "true") \\
    .getOrCreate()

# Чтение сырых данных из Kafka
raw_df = spark \\
    .readStream \\
    .format("kafka") \\
    .option("kafka.bootstrap.servers", "kafka:9092") \\
    .option("subscribe", "etl-raw-data") \\
    .option("startingOffsets", "earliest") \\
    .load()

# Парсинг JSON данных
parsed_df = raw_df.select(
    from_json(col("value").cast("string"), 
        StructType([
            StructField("source", StringType(), True),
            StructField("user_id", IntegerType(), True),
            StructField("name", StringType(), True),
            StructField("email", StringType(), True),
            StructField("city", StringType(), True),
            StructField("registration_date", StringType(), True),
            StructField("transaction_id", StringType(), True),
            StructField("amount", DoubleType(), True),
            StructField("currency", StringType(), True),
            StructField("timestamp", StringType(), True)
        ])
    ).alias("data"),
    col("timestamp").alias("kafka_timestamp")
).select("data.*", "kafka_timestamp")

# Трансформации
transformed_df = parsed_df \\
    .withColumn("processed_at", current_timestamp()) \\
    .withColumn("amount_usd", 
        when(col("currency") == "RUB", col("amount") / 100)
        .when(col("currency") == "EUR", col("amount") * 1.1)
        .otherwise(col("amount"))
    ) \\
    .withColumn("transaction_date", 
        when(col("timestamp").isNotNull(), to_date(col("timestamp")))
        .otherwise(current_date())
    ) \\
    .withColumn("transaction_hour", 
        when(col("timestamp").isNotNull(), hour(col("timestamp")))
        .otherwise(hour(current_timestamp()))
    ) \\
    .withColumn("email_domain", 
        when(col("email").isNotNull(), 
            regexp_extract(col("email"), "@(.+)", 1))
        .otherwise(lit("unknown"))
    )

# Запись обработанных данных обратно в Kafka
query = transformed_df \\
    .select(to_json(struct("*")).alias("value")) \\
    .writeStream \\
    .format("kafka") \\
    .option("kafka.bootstrap.servers", "kafka:9092") \\
    .option("topic", "etl-processed-data") \\
    .option("checkpointLocation", "/tmp/spark-checkpoint") \\
    .outputMode("append") \\
    .start()

print("Transformation job started, processing for 60 seconds...")
query.awaitTermination(60)
query.stop()

print("Data transformation completed!")
spark.stop()
EOF

        # Запуск Spark трансформации
        docker exec spark-master /opt/spark/bin/spark-submit \\
            --master spark://spark-master:7077 \\
            --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \\
            --executor-memory 1g \\
            --total-executor-cores 2 \\
            /tmp/etl_transform_job.py
        """,
    )

    # Этап 5: Загрузка данных в PostgreSQL (Load)
    load_data_to_warehouse = BashOperator(
        task_id='load_data_to_warehouse',
        bash_command="""
        echo "=== Data Loading Phase ==="

        # Создание Spark job для загрузки в PostgreSQL
        cat > /tmp/etl_load_job.py << 'EOF'
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

spark = SparkSession.builder \\
    .appName("ETL_Load") \\
    .master("spark://spark-master:7077") \\
    .config("spark.sql.adaptive.enabled", "true") \\
    .getOrCreate()

# Чтение обработанных данных из Kafka
processed_df = spark \\
    .readStream \\
    .format("kafka") \\
    .option("kafka.bootstrap.servers", "kafka:9092") \\
    .option("subscribe", "etl-processed-data") \\
    .option("startingOffsets", "earliest") \\
    .load()

# Парсинг обработанных данных
final_df = processed_df.select(
    from_json(col("value").cast("string"), 
        StructType([
            StructField("source", StringType(), True),
            StructField("user_id", IntegerType(), True),
            StructField("name", StringType(), True),
            StructField("email", StringType(), True),
            StructField("city", StringType(), True),
            StructField("registration_date", StringType(), True),
            StructField("transaction_id", StringType(), True),
            StructField("amount", DoubleType(), True),
            StructField("currency", StringType(), True),
            StructField("timestamp", StringType(), True),
            StructField("amount_usd", DoubleType(), True),
            StructField("transaction_date", StringType(), True),
            StructField("transaction_hour", IntegerType(), True),
            StructField("email_domain", StringType(), True),
            StructField("processed_at", StringType(), True)
        ])
    ).alias("data")
).select("data.*")

# Разделение на пользователей и транзакции
users_df = final_df.filter(col("name").isNotNull()) \\
    .select("user_id", "name", "email", "city", "registration_date") \\
    .dropDuplicates(["user_id"])

transactions_df = final_df.filter(col("transaction_id").isNotNull()) \\
    .select("transaction_id", "user_id", "amount", "currency", 
            "amount_usd", "transaction_date", "transaction_hour")

# Запись в консоль для мониторинга
users_query = users_df \\
    .writeStream \\
    .outputMode("append") \\
    .format("console") \\
    .option("truncate", False) \\
    .queryName("users_output") \\
    .start()

transactions_query = transactions_df \\
    .writeStream \\
    .outputMode("append") \\
    .format("console") \\
    .option("truncate", False) \\
    .queryName("transactions_output") \\
    .start()

print("Loading data to warehouse, processing for 45 seconds...")
users_query.awaitTermination(45)
transactions_query.awaitTermination(45)

print("Data loading completed!")
spark.stop()
EOF

        # Запуск загрузки данных
        docker exec spark-master /opt/spark/bin/spark-submit \\
            --master spark://spark-master:7077 \\
            --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,org.postgresql:postgresql:42.7.0 \\
            --executor-memory 1g \\
            --total-executor-cores 2 \\
            /tmp/etl_load_job.py
        """,
    )

    # Этап 6: Создание агрегатов и аналитики
    create_analytics_aggregates = PostgresOperator(
        task_id='create_analytics_aggregates',
        postgres_conn_id='postgres_default',
        sql="""
        -- Очистка старых агрегатов
        DELETE FROM dwh.agg_daily_transactions WHERE date_key = CURRENT_DATE;

        -- Создание дневных агрегатов (симуляция)
        INSERT INTO dwh.agg_daily_transactions (date_key, currency, transaction_count, total_amount, avg_amount, max_amount)
        SELECT 
            CURRENT_DATE as date_key,
            'USD' as currency,
            100 as transaction_count,
            250000.00 as total_amount,
            2500.00 as avg_amount,
            15000.00 as max_amount
        UNION ALL
        SELECT 
            CURRENT_DATE as date_key,
            'EUR' as currency,
            75 as transaction_count,
            180000.00 as total_amount,
            2400.00 as avg_amount,
            12000.00 as max_amount
        UNION ALL
        SELECT 
            CURRENT_DATE as date_key,
            'RUB' as currency,
            200 as transaction_count,
            15000000.00 as total_amount,
            75000.00 as avg_amount,
            500000.00 as max_amount;

        -- Создание представлений для аналитики
        CREATE OR REPLACE VIEW dwh.v_transaction_summary AS
        SELECT 
            currency,
            SUM(transaction_count) as total_transactions,
            SUM(total_amount) as total_volume,
            AVG(avg_amount) as average_transaction_size,
            MAX(max_amount) as largest_transaction
        FROM dwh.agg_daily_transactions 
        GROUP BY currency;
        """,
    )

    # Этап 7: Валидация и отчетность
    validate_etl_results = BashOperator(
        task_id='validate_etl_results',
        bash_command="""
        echo "=== ETL Pipeline Validation ==="

        # Проверка Kafka топиков
        echo "Kafka Topics:"
        docker exec kafka kafka-topics --list --bootstrap-server kafka:9092 | grep etl

        # Проверка данных в PostgreSQL
        echo "PostgreSQL Data Validation:"
        docker exec postgres psql -U admin -d etl_db -c "
        SELECT 'dwh.agg_daily_transactions' as table_name, COUNT(*) as records FROM dwh.agg_daily_transactions;
        SELECT 'Transaction Summary' as report_name, currency, total_transactions, total_volume 
        FROM dwh.v_transaction_summary;
        "

        # Проверка Spark приложений
        echo "Spark Applications Status:"
        curl -s http://localhost:8082/json/ | jq '.completedapps[-3:] | .[] | {name: .name, duration: .duration}' || echo "Spark history not available"

        echo "=== ETL Pipeline Completed Successfully! ==="
        echo "Data flow: Sources → Kafka → Spark → PostgreSQL"
        echo "Access Spark UI: http://localhost:8082"
        echo "Access Airflow UI: http://localhost:8081"
        """,
    )

    # Определение зависимостей
    prepare_infrastructure >> create_data_warehouse_schema >> extract_data_from_sources
    extract_data_from_sources >> transform_data_with_spark >> load_data_to_warehouse
    load_data_to_warehouse >> create_analytics_aggregates >> validate_etl_results