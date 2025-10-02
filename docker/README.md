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
```

- Подключиться к PostgreSQL:

```bash
docker compose exec postgres psql -U admin
```

- Подключиться к Kafka:
```bash
docker exec -it kafka bash
```

---

## 🧪 Тестирование Kafka

### Создание топика
```bash
docker exec -it kafka bash
kafka-topics --create --topic test-topic --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1
```

### Отправка и получение сообщений
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

### 5. Ошибка "manifest not found" для образов
Используются зафиксированные версии Confluent:
- `confluentinc/cp-zookeeper:7.6.1`
- `confluentinc/cp-kafka:7.6.1`

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

---

## 🗂️ Структура volumes

- `postgres_data` — данные PostgreSQL
- `kafka_data` — данные Kafka (топики, оффсеты)