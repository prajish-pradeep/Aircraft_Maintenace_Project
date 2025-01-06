import os
from datetime import datetime, timedelta
import pandas as pd
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from sqlalchemy import create_engine

#MS-SQL Server connection string
db_connection_string = (
    "mssql+pyodbc://sqlserver:1010@35.242.141.179/aircraft_maintenance"
    "?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
)

#filepath inside the container
data_dir = "/opt/airflow/data"
files = {
    "Products": "Products.csv",
    "Airport": "UK_Airports.csv",
    "Technician": "Technicians.csv",
    "Engine": "Aircraft_Engines.csv",
    "Maintenance_Actions": "Maintenance_Action.csv",
    "Engine_Orders": "Engine_Orders.csv",
    "Shipments": "Shipments.csv",
}

#insert function
def insert_data(table_name, file_name, **kwargs):
    try:
        engine = create_engine(db_connection_string)
        file_path = os.path.join(data_dir, file_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist.")
        
        df = pd.read_csv(file_path)
        print(f"Loaded data from {file_path} with {len(df)} rows.")
        
        with engine.connect() as connection:
            df.to_sql(table_name, con=connection, if_exists="append", index=False)
        print(f"Data from {file_name} inserted into {table_name}.")
    except Exception as e:
        print(f"Error inserting data from {file_name} into {table_name}: {e}")
        raise

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
    "csv_to_mssql_dag",
    default_args=default_args,
    description="Load CSV data into MS SQL Server",
    schedule_interval="0 */12 * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
)

#creating tasks
tasks = []
for table_name, file_name in files.items():
    task = PythonOperator(
        task_id=f"insert_{table_name.lower()}",
        python_callable=insert_data,
        op_kwargs={"table_name": table_name, "file_name": file_name},
        dag=dag,
    )
    tasks.append(task)

#task dependencies
for i in range(len(tasks) - 1):
    tasks[i] >> tasks[i + 1]