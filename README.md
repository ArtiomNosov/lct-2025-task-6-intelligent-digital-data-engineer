# lct-2025-task-6-intelligent-digital-data-engineer

Ссылка на данные: https://huggingface.co/datasets/ArtiomNosov/lct-2025-task-6-intelligent-digital-data-engineer-dataset

# Cursor rules

- [add_commit](https://github.com/ArtiomNosov/hackathon-starter-pack/blob/main/.cursor/rules/commit.mdc)
- [init_task](https://github.com/ArtiomNosov/hackathon-starter-pack/blob/main/.cursor/rules/task.mdc)

# Big Data ETL Environment

Репозиторий-шаблон для запуска инфраструктуры инженера данных на хакатоне.  
Цель — предоставить готовую среду с инструментами **Big Data** и **ETL**, включая:

- [Apache Airflow](https://airflow.apache.org/) — оркестрация ETL процессов
- [PostgreSQL](https://www.postgresql.org/) — база данных для хранения результатов
- (позже) [Apache Kafka](https://kafka.apache.org/) — потоковая обработка
- (позже) [Apache Spark](https://spark.apache.org/) — обработка больших данных
- (позже) [MongoDB](https://www.mongodb.com/) — NoSQL хранилище
- (позже) [Grafana](https://grafana.com/) и [Prometheus](https://prometheus.io/) — мониторинг

---

## 🚀 Быстрый старт

1. Установите **Docker** и **Docker Compose**  
   См. [docs/install.md](docs/install.md)

2. Клонируйте репозиторий:
   ```bash
   git clone <ваш-репозиторий>
   cd <ваш-репозиторий>/docker