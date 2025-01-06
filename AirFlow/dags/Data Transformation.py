import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
import pandas as pd
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

#MS-SQL Server connection string
db_connection_string = (
    "mssql+pyodbc://sqlserver:1010@35.242.141.179/aircraft_maintenance"
    "?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
)

#transform function
def transform_engine_orders(**kwargs):
    engine = create_engine(db_connection_string)
    query = "SELECT airport_id, product_id, SUM(order_amount) AS total_order_amount FROM Engine_Orders GROUP BY airport_id, product_id"
    df = pd.read_sql(query, con=engine)

    with engine.connect() as connection:
        df.to_sql("Aggregated_Engine_Orders", con=connection, if_exists="replace", index=False)
    print("Aggregated Engine Orders saved to database.")

#DAG definition
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "data_transformation_dag",
    default_args=default_args,
    description="Transform raw data into aggregated formats",
    schedule_interval="0 */6 * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
)

#task definition
transform_task = PythonOperator(
    task_id="transform_engine_orders",
    python_callable=transform_engine_orders,
    dag=dag,
)