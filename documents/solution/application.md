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

Обозначения (легенда):
- UI: W = Web, C = Cursor, L = CLI, A = API
- Оркестрация: +++ = сильная, + = базовая, − = нет/внешняя
- Коннекторы EL/ELT: +++ = широкие, + = есть, − = нет
- Трансформации: SQL = в DWH/SQL, Py = в Python/движки, Ext = внешние движки
- Потоки: ✓ = да, ~ = ограниченно, − = нет
- Расписание: Sch = встроенный, Cron = cron, Ext = внешний, Mg = managed
- Масштабируемость: ↑↑↑ = высокая, ↑ = средняя, env = зависит от среды
- Безопасность: Sec = секреты/хранилища секретов (уровень платформы)
- Развёртывание: Loc = локально, K8s = k8s, Mg = managed cloud
- Стоимость: $ = платно, 0 = бесплатно, 0/$ = есть OSS и платная

| Критерий | ИЦИД | Airflow | Prefect | Dagster | Kedro | Flyte | dbt | Meltano | Airbyte | AWS Glue | ADF | Data Fusion |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Модель | OSS | OSS | 0/$ | 0/$ | OSS | 0/$ | 0/$ | OSS | 0/$ | $ | $ | $ |
| UI | C | W | W/L | W | L | W/L | W/L | L | W | W | W | W |
| Оркестрация | + (Cron) | +++ | +++ | +++ | − (Ext) | +++ | − | − (Ext) | + | Mg | Mg | Mg |
| Коннекторы | − (files) | + | + | + | − | + | Ext | +++ (Singer) | +++ | +++ | +++ | +++ |
| Трансформации | Py | Ext | Py | Py | Py | Py | SQL | Ext | ~ | Spark | Flows | Plugins |
| Потоки | − | ~ | ✓ | ~ | − | ✓ | − | − | ~ | ✓ | ✓ | ✓ |
| Расписание | Cron | Sch | Sch | Sch | Ext | Sch | Ext | Ext | Sch | Mg | Mg | Mg |
| Наблюдаемость | отчёты.md | UI | UI | UI/assets | Ext | UI | tests/docs | Ext | UI | Cloud | Cloud | Cloud |
| Масштабируемость | Loc | ↑↑↑ | ↑↑↑ | ↑↑↑ | env | ↑↑↑ | env (DWH) | env | ↑↑↑ | ↑↑↑ | ↑↑↑ | ↑↑↑ |
| Безопасность | .env | Sec | Sec | Sec | env | Sec | Sec | env | Sec | IAM/KMS | Managed IDs | IAM/KMS |
| Развёртывание | Loc | Loc/K8s | Loc/Cloud | Loc/Cloud | Any | K8s/Cloud | Loc/Cloud | Loc | Loc/Cloud | Mg AWS | Mg Azure | Mg GCP |
| Стоимость | 0 | 0 | 0/$ | 0/$ | 0 | 0/$ | 0/$ | 0 | 0/$ | $ | $ | $ |
| Фокус | IDE‑first | Orchestration | Orchestration/DevX | Orchestr./SDAs | Project FW | k8s‑native | SQL xform | ELT FW | Connectors | Managed ETL | Managed ETL | Managed iPaaS |

Примечание: «Orchestr./SDAs» — software‑defined assets; «FW» — фреймворк; «Ext» — за рамками инструмента; «Cloud» — управляемые сервисы облака.

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
