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
- Создать и протестировать DAG’и (рабочие процессы).

---

## 🛠 Используемые технологии
- 🐘 **PostgreSQL** — хранилище данных  
- 🌬 **Apache Airflow** — оркестрация ETL процессов  
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

### 4. Доступ к сервисам

- 🌐 **Airflow UI**: http://localhost:8081

   Логин: admin

   Пароль: admin

- 🐘 **PostgreSQL**:

   Хост: localhost 

   Порт: 5432 

   Пользователь: admin 

   Пароль: admin 

   База: etl_db 

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
После запуска DAG появится в Airflow UI и выведет сообщение.

---

### 👥 Команда
- ФИО / Telegram / GitHub участников команды

---
## 📌 Дополнительно

- DAG’и добавляются в папку dags/ (автоматически подхватываются Airflow).

- Для создания администратора вручную:

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