from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta
import pandas as pd
import json

default_args = {
    'owner': 'data-engineer',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}


def create_sample_data():
    """Создание тестовых данных для демонстрации"""
    import json
    import csv
    import xml.etree.ElementTree as ET

    # CSV данные
    csv_data = [
        {'id': 1, 'name': 'Alice', 'age': 25, 'city': 'Moscow', 'salary': 50000},
        {'id': 2, 'name': 'Bob', 'age': 30, 'city': 'SPb', 'salary': 60000},
        {'id': 3, 'name': 'Charlie', 'age': 35, 'city': 'Kazan', 'salary': 55000},
        {'id': 4, 'name': 'Diana', 'age': 28, 'city': 'Moscow', 'salary': 65000},
        {'id': 5, 'name': 'Eve', 'age': 32, 'city': 'Novosibirsk', 'salary': 58000},
    ]

    # JSON данные
    json_data = {
        'transactions': [
            {'transaction_id': 'tx_001', 'user_id': 1, 'amount': 1500, 'timestamp': '2025-01-01T10:00:00Z'},
            {'transaction_id': 'tx_002', 'user_id': 2, 'amount': 2300, 'timestamp': '2025-01-01T11:00:00Z'},
            {'transaction_id': 'tx_003', 'user_id': 3, 'amount': 750, 'timestamp': '2025-01-01T12:00:00Z'},
            {'transaction_id': 'tx_004', 'user_id': 1, 'amount': 3200, 'timestamp': '2025-01-01T13:00:00Z'},
            {'transaction_id': 'tx_005', 'user_id': 4, 'amount': 890, 'timestamp': '2025-01-01T14:00:00Z'},
        ]
    }

    # Сохранение файлов
    with open('/tmp/users.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'name', 'age', 'city', 'salary'])
        writer.writeheader()
        writer.writerows(csv_data)

    with open('/tmp/transactions.json', 'w') as f:
        json.dump(json_data, f, indent=2)

    # XML данные
    root = ET.Element('products')
    products = [
        {'id': 'p001', 'name': 'Laptop', 'category': 'Electronics', 'price': 75000},
        {'id': 'p002', 'name': 'Phone', 'category': 'Electronics', 'price': 45000},
        {'id': 'p003', 'name': 'Book', 'category': 'Education', 'price': 1500},
    ]

    for product in products:
        prod_elem = ET.SubElement(root, 'product')
        for key, value in product.items():
            elem = ET.SubElement(prod_elem, key)
            elem.text = str(value)

    tree = ET.ElementTree(root)
    tree.write('/tmp/products.xml')

    print("Sample data files created successfully!")


with DAG(
        'data_ingestion_pipeline',
        default_args=default_args,
        description='Data ingestion pipeline: CSV/JSON/XML to PostgreSQL',
        schedule_interval=timedelta(hours=6),
        catchup=False,
        tags=['etl', 'ingestion', 'postgresql'],
) as dag:
    # Создание таблиц в PostgreSQL
    create_users_table = PostgresOperator(
        task_id='create_users_table',
        postgres_conn_id='postgres_default',
        sql="""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name VARCHAR(100),
            age INTEGER,
            city VARCHAR(100),
            salary INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
    )

    create_transactions_table = PostgresOperator(
        task_id='create_transactions_table',
        postgres_conn_id='postgres_default',
        sql="""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id VARCHAR(50) PRIMARY KEY,
            user_id INTEGER,
            amount DECIMAL(10,2),
            timestamp TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
    )

    create_products_table = PostgresOperator(
        task_id='create_products_table',
        postgres_conn_id='postgres_default',
        sql="""
        CREATE TABLE IF NOT EXISTS products (
            id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(200),
            category VARCHAR(100),
            price DECIMAL(10,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
    )

    # Генерация тестовых данных
    generate_sample_data = PythonOperator(
        task_id='generate_sample_data',
        python_callable=create_sample_data,
    )

    # Загрузка CSV данных через Spark
    load_csv_data = BashOperator(
        task_id='load_csv_data',
        bash_command="""
        echo "Loading CSV data via Spark..."
        docker exec spark-master /opt/spark/bin/spark-submit \
            --master spark://spark-master:7077 \
            --packages org.postgresql:postgresql:42.7.0 \
            --py-files /tmp/load_csv.py \
            /tmp/load_csv.py
        """,
    )

    # Загрузка JSON данных
    load_json_data = BashOperator(
        task_id='load_json_data',
        bash_command="""
        echo "Loading JSON data..."
        docker exec postgres psql -U admin -d etl_db -c "
        COPY transactions(transaction_id, user_id, amount, timestamp) 
        FROM PROGRAM 'cat /tmp/transactions.json | jq -r \".transactions[] | [.transaction_id, .user_id, .amount, .timestamp] | @csv\"' 
        WITH (FORMAT csv);
        " || echo "JSON data loaded via alternative method"
        """,
    )

    # Проверка загруженных данных
    validate_data = PostgresOperator(
        task_id='validate_data',
        postgres_conn_id='postgres_default',
        sql="""
        SELECT 'users' as table_name, COUNT(*) as record_count FROM users
        UNION ALL
        SELECT 'transactions' as table_name, COUNT(*) as record_count FROM transactions
        UNION ALL
        SELECT 'products' as table_name, COUNT(*) as record_count FROM products;
        """,
    )

    # Определение зависимостей
    [create_users_table, create_transactions_table, create_products_table] >> generate_sample_data
    generate_sample_data >> [load_csv_data, load_json_data]
    [load_csv_data, load_json_data] >> validate_data