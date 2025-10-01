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

### 3. Остановить сервисы
```bash
docker compose down
```

---

## 🔍 Проверка состояния

- Посмотреть список сервисов:

```bash
docker compose ps 
```

- Логи сервиса (например, Airflow):

```bash
docker compose logs airflow-webserver --tail=100 
```

- Подключиться к PostgreSQL:

```bash
docker compose exec postgres psql -U admin
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

---

## 📌 Сервисы по умолчанию

- **Airflow UI** → http://localhost:8081
Логин: admin, Пароль: admin

- **PostgreSQL**

    - Host: localhost

    - Port: 5432

    - User: admin

    - Password: admin

    - DB: etl_db