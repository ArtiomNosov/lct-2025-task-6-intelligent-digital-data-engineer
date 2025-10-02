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