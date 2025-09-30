## Интеллектуальный цифровой инженер данных (ИЦИД) — конкурентный анализ

Версия: v0.2 (Cursor = UI, без внешних БД в демо, без Kafka, cron‑расписание, отчёты .md, секреты через .env)

### Краткое описание решения (ёмко)
Цель: развернуть «рабочий стол» дата‑инженера, где единственный UI — IDE Cursor. Пользователь ведёт диалог в панели Cursor, видит ASCII‑диаграмму пайплайна; преобразования выполняются скриптами/утилитами в контейнере. Правила (`.cursor/rules/`) заставляют ассистента анализировать данные, предлагать форматы/план, обновлять диаграмму и формировать отчёт `.md`. Запуски — через `make`/`python` внутри Docker; расписание — `cron` в контейнере.

Что в демо: локальные файлы (CSV/JSON/XML, ZIP) → трансформации → артефакты (CSV/Parquet/SQLite) в контейнере/томе. Подключения к внешним БД в демо отсутствуют.

### Список сопоставляемых решений
- Apache Airflow (OSS)
- Prefect (OSS + Cloud)
- Dagster (OSS + Cloud)
- Kedro (OSS)
- Flyte (OSS + Cloud)
- dbt Core / dbt Cloud
- Meltano (OSS)
- Airbyte (OSS + Cloud)
- AWS Glue (Commercial)
- Azure Data Factory (Commercial)
- Google Cloud Data Fusion (Commercial)

### Сравнение по ключевым критериям (14)
| Критерий | ИЦИД (ваш MVP) | Apache Airflow | Prefect | Dagster | Kedro | Flyte | dbt | Meltano | Airbyte | AWS Glue | Azure Data Factory | GCP Data Fusion |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1) Лицензия/модель | OSS‑подход, локально | OSS | OSS+Cloud | OSS+Cloud | OSS | OSS+Cloud | OSS+Cloud | OSS | OSS+Cloud | Commercial | Commercial | Commercial |
| 2) Основной UI | IDE Cursor (чат/терминал) | Web | Web+CLI | Web | CLI | Web/CLI | Web (Cloud)/CLI | CLI | Web | Web | Web | Web |
| 3) Оркестрация DAG | Cron в контейнере | Сильная | Сильная | Сильная | Через внешние | Сильная | Нет | Через внешние | Базовая для sync | Managed | Managed | Managed |
| 4) EL/ELT коннекторы | Нет (локальные файлы) | Плагины/операторы | Blocks/flows | IO‑менеджеры | Нет | Плагины | Через адаптеры DWH | Singer (taps/targets) | Большая библиотека | Glue connectors | Linked services | Prebuilt connectors |
| 5) Трансформации | Python/pandas/pyarrow | Операторы (внешние движки) | Tasks | Ops/SDAs | Python nodes | Tasks | SQL‑трансформации | ELT‑оркестрация | Ограниченные | Spark/ETL | Data Flows | Wrangler/Plugins |
| 6) Потоки/стриминг | Нет | Ограниченно | Есть | Есть частично | Нет | Есть | Нет | Нет | Ограниченно | Да | Да | Да |
| 7) Расписание | Cron (.env) | Scheduler | Scheduler | Scheduler | Внешний | Scheduler | Внешний | Внешний | Scheduler | Managed | Managed | Managed |
| 8) Наблюдаемость/логи | Markdown‑отчёты, логи контейнера | UI/метрики/алерты | UI/Cloud | UI/asset obs. | Внешние | UI/метрики | Tests/docs | Внешние | UI/мониторинг | CloudWatch/Glue | Azure Monitor | Cloud Monitoring |
| 9) Масштабируемость | Контейнер локально | Высокая (k8s/celery) | Высокая | Высокая | От среды | Высокая | От DWH | От оркестратора | Высокая (Cloud) | Высокая | Высокая | Высокая |
| 10) Безопасность/секреты | .env локально | Secrets backends | Secrets/Blocks | Secrets | От среды | Secrets/SA | Secrets в CI/Cloud | От среды | Secrets (Cloud) | IAM/KMS | Managed identities | IAM/KMS |
| 11) Развёртывание | Docker Compose 1 svc | Docker/k8s | OSS/Cloud | OSS/Cloud | Any env | k8s/Cloud | Local/Cloud | Local | Local/Cloud | Managed AWS | Managed Azure | Managed GCP |
| 12) Стоимость | Бесплатно | Бесплатно | OSS/подписка | OSS/подписка | Бесплатно | OSS/подписка | OSS/подписка | Бесплатно | OSS/подписка | Платно | Платно | Платно |
| 13) Сообщество | Молодое | Крупное | Крупное | Растущее | Зрелое | Растущее | Крупное | Активное | Крупное | Enterprise | Enterprise | Enterprise |
| 14) Фокус/позиционирование | IDE‑first, правила, ASCII/отчёты | Оркестрация | Оркестрация+DevX | Оркестрация+SDAs | Каркас проекта | k8s‑native оркестрация | SQL‑трансформации | ELT‑каркас | Интеграции ELT | Managed ETL | Managed ETL | Managed iPaaS ETL |

Примечания к трактовке: «Оркестрация» — граф зависимостей, ретраи, расписание; «EL/ELT» — перенос данных готовыми коннекторами; «Трансформации» — встроенные механики или через SQL/код; «Потоки» — event/stream, не только batch.

### Краткие описания архитектуры и принципов
- ИЦИД: IDE‑first. Правила в `.cursor/rules/` управляют ассистентом: анализ данных, генерация пайплайна, поддержка ASCII‑диаграммы, отчёт `.md`. Исполнитель — Python‑утилиты в Docker, планирование — cron в контейнере. Демо: локальные файлы/SQLite.
- Apache Airflow: централизованный оркестратор DAG (scheduler/executor), богатые операторы/провайдеры, UI‑мониторинг, развёртывание on‑prem/k8s/Cloud.
- Prefect: оркестрация flows/декораторы Python, OSS/Cloud, удобная наблюдаемость, секреты/blocks.
- Dagster: software‑defined assets, строгая типизация I/O, lineage и наблюдаемость активов, OSS/Cloud.
- Kedro: фреймворк для воспроизводимых пайплайнов (data catalog, pipelines, конфиги); оркестрация — внешняя.
- Flyte: k8s‑native оркестратор, сильные типы/кэширование/ресурсные профили, ML/DE‑кейсы.
- dbt: SQL‑трансформации в DWH, тесты/документация/линейка lineage; не решает EL/оркестрацию.
- Meltano: OSS‑ELT на базе Singer (taps/targets), локальная разработка, интеграции с оркестраторами.
- Airbyte: крупная библиотека коннекторов, OSS/Cloud, фокус на перенос данных, базовые трансформации.
- AWS Glue: managed Spark‑ETL, Data Catalog, коннекторы AWS, serverless масштабирование, мониторинг.
- Azure Data Factory: визуальные pipeline/data flows, широкие интеграции в Azure, триггеры, мониторинг.
- Google Cloud Data Fusion: managed интеграции (CDAP), визуальные потоки, коннекторы, Wrangler, интеграции с GCP.

### Позиционирование ИЦИД
- Уникальность: IDE‑первый опыт (только Cursor как UI), «правила как продукт», авто‑ASCII‑диаграммы и отчёты `.md`.
- Сильные стороны MVP: быстрый офлайн‑поток для файловых источников, прозрачный след артефактов (`/data/output`, `/reports`), воспроизводимость.
- Ограничения MVP: нет внешних БД/коннекторов, нет стриминга, базовая оркестрация (cron), минимум enterprise‑контролей.
- Стратегия Next: коннекторы (Singer/Meltano или Airbyte), внешние DWH + dbt, оркестрация (Airflow/Prefect/Dagster/Flyte), стриминг (Kafka), k8s, мониторинг, безопасное хранение секретов (Vault/KMS).

### Рекомендации для демо и стратегического планирования
- Акцент на скорость итераций: «файл → пайплайн → отчёт» за минуты без веб‑UI.
- Показать traceability: ASCII‑диаграмма и отчёт с причинами решений и метриками.
- Стандартизовать правила: формат диаграмм/отчётов, версионирование `.cursor/rules/`.
- Показать расширяемость: план подключения коннекторов и DWH/dbt; опциональная интеграция оркестраторов.

### Ссылки (официальные ресурсы)
- Airflow — [apache.airflow](https://airflow.apache.org)
- Prefect — [prefect.io](https://www.prefect.io)
- Dagster — [dagster.io](https://dagster.io)
- Kedro — [kedro.org](https://kedro.org)
- Flyte — [flyte.org](https://flyte.org)
- dbt — [getdbt.com](https://www.getdbt.com)
- Meltano — [meltano.com](https://meltano.com)
- Airbyte — [airbyte.com](https://airbyte.com)
- AWS Glue — [aws.amazon.com/glue](https://aws.amazon.com/glue)
- Azure Data Factory — [azure.microsoft.com/services/data-factory](https://azure.microsoft.com/services/data-factory)
- Google Cloud Data Fusion — [cloud.google.com/data-fusion](https://cloud.google.com/data-fusion)
