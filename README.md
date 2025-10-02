# lct-2025-task-6-intelligent-digital-data-engineer

Ссылка на данные: https://huggingface.co/datasets/ArtiomNosov/lct-2025-task-6-intelligent-digital-data-engineer-dataset

# Cursor rules

- [add_commit](https://github.com/ArtiomNosov/hackathon-starter-pack/blob/main/.cursor/rules/commit.mdc)
- [init_task](https://github.com/ArtiomNosov/hackathon-starter-pack/blob/main/.cursor/rules/task.mdc)

# 🚀 Intelligent Digital Data Engineer – ETL Platform

## 📖 Описание проекта
Этот проект реализует прототип ETL-платформы на базе **Big Data** инструментов.  
Решение создано в рамках хакатона для демонстрации работы с потоками данных, их оркестрации и хранения.  

Основные цели:
- Развернуть инфраструктуру на Docker.
- Поднять **Airflow** для оркестрации ETL-процессов.
- Настроить **PostgreSQL** для хранения данных.
- Интегрировать **Apache Kafka** для потоковой обработки данных.
- Настроить **Apache Spark** для распределённых вычислений.
- Создать и протестировать DAG’и (рабочие процессы).

---

## 🛠 Используемые технологии
- 🐘 **PostgreSQL** — хранилище данных  
- 🌬 **Apache Airflow** — оркестрация ETL процессов
- ⚡ **Apache Kafka** — потоковая обработка данных
- 🗂️ **Apache Zookeeper** — координация Kafka кластера
- 🔥 **Apache Spark** — распределённые вычисления и аналитика
- 🐳 **Docker / Rancher Desktop** — контейнеризация  
- (опционально) 📊 **Grafana + Prometheus** — мониторинг  

---

## ⚡ Быстрый старт

### 1. Установите Docker (Rancher Desktop)  
[Скачать Rancher Desktop](https://rancherdesktop.io/)

---

### 2. Клонируйте репозиторий
```bash
git clone https://github.com/<your_team_repo>.git
cd lct-2025-task-6-intelligent-digital-data-engineer/docker
```

---

### 3. Запустите сервисы
```bash
docker compose up -d
```

---

### 4. Инициализация Airflow (первый запуск)
```bash
docker compose run --rm airflow-webserver bash -c "airflow db init && airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com"
```

Затем перезапустите сервисы:
```bash
docker compose up -d
```

---

### 5. Доступ к сервисам

- 🌐 **Airflow UI**: http://localhost:8081
  - Логин: admin
  - Пароль: admin

- 🐘 **PostgreSQL**:
  - Хост: localhost
  - Порт: 5432
  - Пользователь: admin
  - Пароль: admin
  - База: etl_db 

- ⚡ **Apache Kafka**:
  - Хост: localhost
  - Порт: 9092
  - Брокер: PLAINTEXT://localhost:9092

- 🗂️ **Apache Zookeeper**:
  - Хост: localhost
  - Порт: 2181

- 🔥 **Apache Spark**:
  - **Spark Master UI**: http://localhost:8082
  - **Spark Worker UI**: http://localhost:8083
  - **Master URL**: spark://localhost:7077
---
## 🧪 Тестирование компонентов

### Apache Spark
```bash
# Зайти в контейнер Spark Master
docker exec -it spark-master bash

# Запустить PySpark
/opt/spark/bin/pyspark --master spark://spark-master:7077

# Простой тест в PySpark
sc.parallelize([1, 2, 3, 4, 5]).collect()
df = spark.createDataFrame([(1, "Alice"), (2, "Bob")], ["id", "name"])
df.show()
```

## 🧪 Apache Kafka
```bash
# Зайти в контейнер Kafka
docker exec -it kafka bash

# Создать топик
kafka-topics --create --topic test-topic --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1

# Запустить консюмера (терминал 1)
kafka-console-consumer --topic test-topic --bootstrap-server kafka:9092 --from-beginning

# Запустить продюсера (терминал 2)
kafka-console-producer --topic test-topic --bootstrap-server kafka:9092
```

### Проверка состояния
```bash
# Список топиков
kafka-topics --list --bootstrap-server kafka:9092

# Описание топика
kafka-topics --describe --topic test-topic --bootstrap-server kafka:9092

# Spark задачи
/opt/spark/bin/spark-submit --master spark://spark-master:7077 --class org.apache.spark.examples.SparkPi /opt/spark/examples/jars/spark-examples_2.12-3.5.1.jar 10
```

---

## ✅ Примеры использования

### 1. DAG "Hello World"

В папке dags/ есть пример DAG:
```python
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
```

### 2. DAG с Spark задачами
```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    'simple_spark_test',
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=['spark', 'test'],
) as dag:

    spark_hello_world = BashOperator(
        task_id='spark_hello_world',
        bash_command="""
        docker exec spark-master /opt/spark/bin/spark-submit \
            --master spark://spark-master:7077 \
            --class org.apache.spark.examples.SparkPi \
            /opt/spark/examples/jars/spark-examples_2.12-3.5.1.jar 10
        """,
    )
```

---

## 🔧 Управление сервисами

### Проверка состояния
```bash
docker compose ps
```

### Просмотр логов
```bash
# Airflow webserver
docker logs airflow-webserver --tail 100

# Airflow scheduler  
docker logs airflow-scheduler --tail 100

# Kafka
docker logs kafka --tail 100

# Zookeeper
docker logs zookeeper --tail 100

# Spark Master
docker logs spark-master --tail 100

# Spark Worker
docker logs spark-worker --tail 100
```

### Остановка сервисов
```bash
docker compose down
```

### Полная очистка (включая данные)
```bash
docker compose down -v
```

---
## 🎯 Архитектура ETL пайплайна

**Поток данных:**
  - Data Sources → Apache Kafka → Apache Spark → PostgreSQL Database
  - ↑ ↑
  - Apache Zookeeper Spark Master
  - ↓
  - Spark Worker

Всё управляется через Apache Airflow

**Компоненты**
- **Data Sources** → **Kafka** → **Spark** → **PostgreSQL**
- **Airflow** управляет всем процессом
- **Zookeeper** координирует Kafka
- **Spark Master** управляет Worker'ами

---

### 👥 Команда
- ФИО / Telegram / GitHub участников команды

---
## 📌 Дополнительно

- DAG’и добавляются в папку dags/ (автоматически подхватываются Airflow).
- Kafka топики создаются автоматически при первом использовании.
- Spark задачи можно запускать как через Airflow DAG'и, так и напрямую.
- Все данные сохраняются в Docker volumes для персистентности.

### Для создания администратора вручную:
```bash
docker compose run --rm airflow-webserver 
    airflow users create 
    --username admin 
    --password admin 
    --firstname Admin 
    --lastname User 
    --role Admin 
    --email admin@example.com
```

### Полезные команды:
```bash
# Перезапуск всех сервисов
docker compose restart

# Просмотр использования ресурсов
docker stats

# Очистка неиспользуемых образов
dock
```

# 📊 Пример: Анализ данных в разных форматах в нашей системе

## Описание примера
Этот пример демонстрирует обработку реальных данных в трех форматах:
- **CSV**: Музейные билеты (~4GB, 12 файлов)
- **JSON**: Реестр индивидуальных предпринимателей (~8.3GB, 31 файл)  
- **XML**: Кадастровые данные недвижимости (~11.8GB, 15 файлов)

## Шаг 1: Подготовка данных
```bash
# Поместите ваши файлы данных в папку data analysis/
mkdir -p "data analysis"
# Скопируйте туда ваши CSV, JSON, XML файлы
```

## Шаг 2: Создание DAG для анализа
Создайте файл `dags/multi_format_analysis.py`:

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta
import json

default_args = {
    'owner': 'data-engineer',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def create_analysis_script():
    """Создание Spark скрипта для анализа данных"""
    spark_code = '''
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import json

spark = SparkSession.builder \\
    .appName("DataAnalysis") \\
    .master("spark://spark-master:7077") \\
    .getOrCreate()

print("🔥 Запуск анализа данных...")

# 1. Анализ CSV данных (Музейные билеты)
csv_df = spark.read \\
    .option("header", "true") \\
    .option("inferSchema", "true") \\
    .csv("/opt/airflow/dags/data_analysis/*.csv")

# Валидация и очистка
csv_cleaned = csv_df \\
    .withColumn("price_valid", when(col("ticket_price") > 0, col("ticket_price")).otherwise(0)) \\
    .withColumn("phone_valid", when(col("client_phone").rlike("^[78]\\d{10}$"), "ВЕРНЫЙ").otherwise("НЕВЕРНЫЙ")) \\
    .withColumn("data_source", lit("museum_csv"))

# Аналитика по музеям
museum_stats = csv_cleaned.groupBy("museum_name") \\
    .agg(
        count("*").alias("total_tickets"),
        sum("price_valid").alias("total_revenue"),
        avg("price_valid").alias("avg_price")
    )

print(f"✅ CSV: {csv_cleaned.count()} записей обработано")

# 2. Анализ JSON данных (Предприниматели)
json_files = spark.sparkContext.wholeTextFiles("/opt/airflow/dags/data_analysis/*.json")
json_rdd = json_files.flatMap(lambda x: json.loads(x[1]) if isinstance(json.loads(x[1]), list) else [json.loads(x[1])])
json_df = spark.createDataFrame(json_rdd)

# Аналитика по предпринимателям
entrepreneur_stats = json_df.groupBy("inf_authority_reg_ind_entrep_name") \\
    .agg(count("*").alias("total_registrations"))

print(f"✅ JSON: {json_df.count()} записей обработано")

# 3. Анализ XML данных (Кадастровые данные)
xml_df = spark.read \\
    .format("xml") \\
    .option("rowTag", "item") \\
    .load("/opt/airflow/dags/data_analysis/*.xml")

# Аналитика по кадастровым данным
cadastral_stats = xml_df.groupBy("type") \\
    .agg(count("*").alias("total_objects"))

print(f"✅ XML: {xml_df.count()} записей обработано")

# Сохранение результатов в PostgreSQL
museum_stats.write \\
    .format("jdbc") \\
    .option("url", "jdbc:postgresql://postgres:5432/etl_db") \\
    .option("dbtable", "museum_analytics") \\
    .option("user", "admin") \\
    .option("password", "admin") \\
    .option("driver", "org.postgresql.Driver") \\
    .mode("overwrite") \\
    .save()

print("✅ Результаты сохранены в PostgreSQL!")
spark.stop()
'''
    
    with open('/tmp/data_analysis.py', 'w') as f:
        f.write(spark_code)

with DAG(
    'multi_format_analysis',
    default_args=default_args,
    description='Анализ данных CSV, JSON, XML',
    schedule_interval=None,
    catchup=False,
    tags=['analysis', 'csv', 'json', 'xml'],
) as dag:

    # Создание таблиц
    create_tables = PostgresOperator(
        task_id='create_tables',
        postgres_conn_id='postgres_default',
        sql="""
        CREATE TABLE IF NOT EXISTS museum_analytics (
            id SERIAL PRIMARY KEY,
            museum_name VARCHAR(500),
            total_tickets INTEGER,
            total_revenue DECIMAL(15,2),
            avg_price DECIMAL(10,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
    )

    # Копирование данных
    copy_data = BashOperator(
        task_id='copy_data',
        bash_command="""
        docker exec spark-master mkdir -p /opt/airflow/dags/data_analysis
        docker cp "data analysis/" spark-master:/opt/airflow/dags/
        echo "✅ Данные скопированы"
        """,
    )

    # Создание скрипта
    create_script = PythonOperator(
        task_id='create_script',
        python_callable=create_analysis_script,
    )

    # Запуск анализа
    run_analysis = BashOperator(
        task_id='run_analysis',
        bash_command="""
        docker exec spark-master /opt/spark/bin/spark-submit \\
            --master spark://spark-master:7077 \\
            --packages org.postgresql:postgresql:42.7.0,com.databricks:spark-xml_2.12:0.15.0 \\
            --executor-memory 1g \\
            /tmp/data_analysis.py
        """,
    )

    # Просмотр результатов
    view_results = BashOperator(
        task_id='view_results',
        bash_command="""
        echo "📊 Результаты анализа:"
        docker exec postgres psql -U admin -d etl_db -c "
        SELECT * FROM museum_analytics LIMIT 10;
        "
        """,
    )

    create_tables >> copy_data >> create_script >> run_analysis >> view_results
```

## Шаг 3: Запуск анализа

1. **Сохраните файл** `multi_format_analysis.py` в папку `dags/`
2. **Поместите ваши данные** в папку `data analysis/`
3. **В Airflow UI** (http://localhost:8081):
   - Найдите DAG `multi_format_analysis`
   - Включите его переключателем
   - Нажмите **"Trigger DAG"** ▶️

## Шаг 4: Просмотр результатов

### В Airflow UI:
- Следите за выполнением задач в Graph View
- Кликните на задачу `view_results` для просмотра результатов

### В PostgreSQL:
```bash
# Подключитесь к базе данных
docker exec -it postgres psql -U admin -d etl_db

# Посмотрите результаты анализа
SELECT * FROM museum_analytics ORDER BY total_revenue DESC LIMIT 10;
```

## Что получите:

✅ **Статистику по музеям** (количество билетов, выручка, средняя цена)  
✅ **Анализ данных предпринимателей** (количество регистраций по органам)  
✅ **Статистику кадастровых объектов** (количество по типам)  
✅ **Валидацию качества данных** (проверка форматов, корректности)  
✅ **Результаты в PostgreSQL** для дальнейшего анализа  

## Настройка под ваши данные:

1. **Замените пути к файлам** в коде на ваши
2. **Адаптируйте поля** под структуру ваших данных
3. **Настройте валидацию** под ваши требования
4. **Добавьте дополнительные метрики** по необходимости

## Архитектура обработки:

- [CSV Files] ──┐
- [JSON Files] ─┼─► [Spark Ingestion] ──► [Data Validator] ──► [Analytics]
- [XML Files] ──┘ │
▼
- [PostgreSQL] ◄── [Results Aggregator] ◄── [Quality Checker]

**Этот пример показывает полный цикл обработки данных: от загрузки до аналитики!** 🚀
