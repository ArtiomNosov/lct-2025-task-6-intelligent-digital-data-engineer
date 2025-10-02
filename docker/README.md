# ⚙️ Docker Setup for ETL Platform

Этот раздел отвечает за запуск инфраструктуры проекта через Docker.

---

## 🚀 Запуск

### 1. Перейти в папку
```bash
cd docker
```

### 2. Поднять сервисы
```bash
docker compose up -d
```

### 3. Инициализация Airflow (первый запуск)
```bash
docker compose run --rm airflow-webserver bash -c "airflow db init && airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com"
```

### 4. Перезапуск после инициализации
```bash
docker compose up -d
```

### 5. Остановить сервисы
```bash
docker compose down
```

---

## 🔍 Проверка состояния

- Посмотреть список сервисов:

```bash
docker compose ps 
```

- Логи сервисов:

```bash
# Airflow webserver
docker compose logs airflow-webserver --tail=100

# Airflow scheduler
docker compose logs airflow-scheduler --tail=100

# Kafka
docker compose logs kafka --tail=100

# Zookeeper
docker compose logs zookeeper --tail=100

# Spark Master
docker compose logs spark-master --tail=100

# Spark Worker
docker compose logs spark-worker --tail=100
```

- Подключиться к PostgreSQL:

```bash
docker compose exec postgres psql -U admin
```

- Подключиться к Kafka:
```bash
docker exec -it kafka bash
```

- Подключиться к Spark Master:
```bash
docker exec -it spark-master bash
```
---

## 🧪 Тестирование компонентов

### Apache spark
```bash
# Зайти в контейнер Spark Master
docker exec -it spark-master bash

# Запустить PySpark
/opt/spark/bin/pyspark --master spark://spark-master:7077

# Простой тест
sc.parallelize([1, 2, 3, 4, 5]).collect()

# Выход
exit()
```

### Spark задачи через submit
```bash
# Запуск примера SparkPi
docker exec spark-master /opt/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    --class org.apache.spark.examples.SparkPi \
    /opt/spark/examples/jars/spark-examples_2.12-3.5.1.jar 10
```

### Apache Kafka
```bash
docker exec -it kafka bash

#Создание топика
kafka-topics --create --topic test-topic --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1
```

```bash
# Терминал 1: Консюмер
kafka-console-consumer --topic test-topic --bootstrap-server kafka:9092 --from-beginning

# Терминал 2: Продюсер  
kafka-console-producer --topic test-topic --bootstrap-server kafka:9092
```

### Проверка топиков
```bash
kafka-topics --list --bootstrap-server kafka:9092
kafka-topics --describe --topic test-topic --bootstrap-server kafka:9092
```

---

## 🛠 Частые проблемы

### 1. Airflow не запускается, пишет db init required

Запустить:
```bash
docker compose run --rm airflow-webserver airflow db init 
```

### 2. Нет пользователя admin для входа в UI
Создать:
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

### 3. Postgres работает, но DAG’и не видны

Проверить, что папка dags/ подключена в docker-compose.yml:
```yaml
volumes: - ../dags:/opt/airflow/dags
```

### 4. Kafka не может подключиться к Zookeeper
Проверить порядок запуска сервисов:
```bash
docker compose ps
```
Zookeeper должен запуститься раньше Kafka.

### 5. Spark Master не видит Worker'ы
Проверить логи:
```bash
docker logs spark-master --tail 50
docker logs spark-worker --tail 50
```

### 6. Ошибка "manifest not found" для образов
Используются зафиксированные версии Confluent:
- `confluentinc/cp-zookeeper:7.6.1`
- `confluentinc/cp-kafka:7.6.1`
- `apache/spark:3.5.1-scala2.12-java11-python3-ubuntu`

### 7. Spark задачи не выполняются
Проверить доступность Master:
```bash
curl http://localhost:8082
```

---

## 📌 Сервисы по умолчанию

- **Airflow UI** → http://localhost:8081
  - Логин: admin, Пароль: admin

- **PostgreSQL**
    - Host: localhost
    - Port: 5432
    - User: admin
    - Password: admin
    - DB: etl_db

- **Apache Kafka**
  - Host: localhost
  - Port: 9092
  - Bootstrap servers: localhost:9092

- **Apache Zookeeper**
  - Host: localhost
  - Port: 2181

- **Apache Spark**
  - **Spark Master UI**: http://localhost:8082
  - **Spark Worker UI**: http://localhost:8083
  - **Master URL**: spark://localhost:7077
  - **Application UI**: http://localhost:4040 (во время выполнения задач)

---

## 🗂️ Структура volumes

- `postgres_data` — данные PostgreSQL
- `kafka_data` — данные Kafka (топики, оффсеты)
- `spark_data` — рабочие файлы Spark

---

## ⚡ Быстрые команды

```bash
# Полный перезапуск стека
docker compose down && docker compose up -d

# Проверка всех сервисов
docker compose ps && docker compose logs --tail=10

# Очистка данных и перезапуск
docker compose down -v && docker compose up -d

# Мониторинг ресурсов
docker stats

# Подключение ко всем основным сервисам
docker exec -it postgres psql -U admin
docker exec -it kafka bash
docker exec -it spark-master bash
```