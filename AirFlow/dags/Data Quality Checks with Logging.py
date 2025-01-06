import os
from datetime import datetime, timedelta
import pandas as pd
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from sqlalchemy import create_engine

# MS-SQL Server connection string
db_connection_string = (
    "mssql+pyodbc://sqlserver:1010@35.242.141.179/aircraft_maintenance"
    "?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
)

#table configuration
tables_with_primary_keys = {
    "Products": ["product_id"],
    "Airport": ["airport_id"],
    "Technician": ["technician_id"],
    "Engine": ["engine_id"],
    "Maintenance_Actions": ["maintenance_id"],
    "Engine_Orders": ["order_id"],
    "Shipments": ["shipment_id"],
}

#data quality issues table
def create_issues_table():
    engine = create_engine(db_connection_string)
    with engine.connect() as connection:
        create_table_query = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='data_quality_issues' AND xtype='U')
        CREATE TABLE data_quality_issues (
            id INT IDENTITY(1,1) PRIMARY KEY,
            table_name VARCHAR(100),
            column_name VARCHAR(100),
            issue_type VARCHAR(50),
            issue_details VARCHAR(MAX),
            checked_at DATETIME
        );
        """
        connection.execute(create_table_query)

#missing values check
def check_missing_values(table_name, **kwargs):
    try:
        engine = create_engine(db_connection_string)
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, con=engine)

        missing_values = df.isnull().sum()
        missing_rows = missing_values[missing_values > 0]
        
        if not missing_rows.empty:
            print(f"Missing values found in table {table_name}:")
            print(missing_rows)
            
            with engine.connect() as connection:
                issue_log = pd.DataFrame({
                    "table_name": [table_name] * len(missing_rows),
                    "column_name": missing_rows.index,
                    "issue_type": ["missing_values"] * len(missing_rows),
                    "issue_details": missing_rows.astype(str),
                    "checked_at": [datetime.now()] * len(missing_rows)
                })
                issue_log.to_sql("data_quality_issues", con=connection, if_exists="append", index=False)
        else:
            print(f"No missing values found in table {table_name}.")
    except Exception as e:
        print(f"Error checking missing values in table {table_name}: {e}")
        raise

#duplicate rows check
def check_duplicates(table_name, primary_keys, **kwargs):
    try:
        engine = create_engine(db_connection_string)
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, con=engine)

        #duplicates check
        if primary_keys:
            duplicates = df[df.duplicated(subset=primary_keys, keep=False)]
        else:
            duplicates = df[df.duplicated(keep=False)]
        
        if not duplicates.empty:
            print(f"Duplicate rows found in table {table_name}:")
            print(duplicates)
            
            #log issues tp the data_quality_issues table
            with engine.connect() as connection:
                issue_log = pd.DataFrame({
                    "table_name": [table_name] * len(duplicates),
                    "column_name": ["primary_keys"] * len(duplicates),
                    "issue_type": ["duplicate_rows"] * len(duplicates),
                    "issue_details": duplicates.to_json(orient="records"),
                    "checked_at": [datetime.now()] * len(duplicates)
                })
                issue_log.to_sql("data_quality_issues", con=connection, if_exists="append", index=False)
        else:
            print(f"No duplicate rows found in table {table_name}.")
    except Exception as e:
        print(f"Error checking duplicates in table {table_name}: {e}")
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
    "data_quality_checks_dag",
    default_args=default_args,
    description="Perform data quality checks on MS SQL Server tables",
    schedule_interval="0 */12 * * *",  # Every 12 hours
    start_date=datetime(2025, 1, 1),
    catchup=False,
)

#create tasks
tasks = []
for table_name, primary_keys in tables_with_primary_keys.items():
    #missing values task
    missing_task = PythonOperator(
        task_id=f"check_missing_values_{table_name.lower()}",
        python_callable=check_missing_values,
        op_kwargs={"table_name": table_name},
        dag=dag,
    )
    
    #duplicate rows task
    duplicate_task = PythonOperator(
        task_id=f"check_duplicates_{table_name.lower()}",
        python_callable=check_duplicates,
        op_kwargs={"table_name": table_name, "primary_keys": primary_keys},
        dag=dag,
    )
    
    #task dependencies
    missing_task >> duplicate_task
    tasks.extend([missing_task, duplicate_task])

#create data quality issues table task
create_issues_table_task = PythonOperator(
    task_id="create_issues_table",
    python_callable=create_issues_table,
    dag=dag,
)

#making sure the issues table is created before running other tasks
for task in tasks:
    create_issues_table_task >> task