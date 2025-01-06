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

#backup function
def backup_old_maintenance_actions(**kwargs):
    engine = create_engine(db_connection_string)
    query = "SELECT * FROM Maintenance_Actions WHERE date < DATEADD(YEAR, -1, GETDATE())"
    df = pd.read_sql(query, con=engine)

    backup_dir = "/opt/airflow/backups"
    os.makedirs(backup_dir, exist_ok=True)
    backup_path = os.path.join(backup_dir, "maintenance_actions_backup.csv")
    df.to_csv(backup_path, index=False)
    print(f"Old maintenance actions backed up to {backup_path}.")

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
    "data_backup_dag",
    default_args=default_args,
    description="Backup old data to CSV",
    schedule_interval="@daily",
    start_date=datetime(2025, 1, 1),
    catchup=False,
)

#task definition
backup_task = PythonOperator(
    task_id="backup_old_maintenance_actions",
    python_callable=backup_old_maintenance_actions,
    dag=dag,
)