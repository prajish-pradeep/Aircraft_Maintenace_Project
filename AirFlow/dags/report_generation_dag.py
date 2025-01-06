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

#monthly report function
def generate_monthly_report(**kwargs):
    try:
        # Connect to the database
        engine = create_engine(db_connection_string)
        query = """
            SELECT 
                technician_id, 
                engine_id, 
                COUNT(*) AS total_actions, 
                MAX(date) AS last_maintenance_date
            FROM Maintenance_Actions
            GROUP BY technician_id, engine_id
        """
        #load data
        report = pd.read_sql(query, con=engine)
        
        #debug:data loading confirmation
        print(report.head())
        print(f"Report rows: {len(report)}")
        
        #report path
        report_dir = "/opt/airflow/reports"
        os.makedirs(report_dir, exist_ok=True)  # Ensure the directory exists
        report_path = os.path.join(report_dir, "monthly_maintenance_report.csv")
        
        #save report
        print(f"Saving report to: {report_path}")
        report.to_csv(report_path, index=False)
        print(f"Monthly maintenance report saved to {report_path}.")
    except Exception as e:
        print(f"Error generating the monthly maintenance report: {e}")
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
    "report_generation_dag",
    default_args=default_args,
    description="Generate monthly maintenance reports",
    schedule_interval="0 0 1 * *",  # Runs on the first day of every month at midnight
    start_date=datetime(2025, 1, 1),
    catchup=False,
)

#task definition
report_task = PythonOperator(
    task_id="generate_monthly_report",
    python_callable=generate_monthly_report,
    dag=dag,
)