**Predictive Aircraft Maintenance System**

1. Data Management:

The project contains two main types of data:

(i)	Operational Data: This includes maintenance records, orders, shipments, products, and technicians.
	
•	Generation: The operational data is created using Python generator scripts, which are located in the "Data Generator Scripts" directory.
•	Sample Data: The generated sample data can be found in the "Generated Data Files" directory.
•	ETL Process: These data files are processed (Extracted, Transformed, and Loaded) using Python scripts found in the Airflow/dags directory.
•	Scheduling and Storage: Airflow schedules the tasks to process this data and sends it to tables in an MS SQL Server hosted on Google Cloud Platform.
•	Visualisation: The processed data is visualised in PowerBI.
•	Logs and Backups: All logs, backups, and reports generated during the ETL process are stored in the Airflow directory.
	
(ii)	Sensor Data: This represents real-time streaming data from aircraft sensors.
   
Data Generation: A Python script generates continuous streaming data. These scripts can be found in the Kafka Scripts directory, specifically in Producer.py and Consumer.py.
Data Flow: One set of this data is sent to an S3 bucket using Confluent Kafka. Another set is stored as a backup.
Cataloging: The data in S3 is cataloged using AWS Glue Crawlers.
ETL and ML Transformation: AWS Glue performs both batch ETL and Machine Learning data transformations. The scripts for these processes are located in the AWS Glue Scripts directory.
Storage: Transformed data is saved in Parquet format and loaded into Snowflake.

2.	Snowflake Integration:
   
•	Snowflake handles storage, ETL pipelines, Fourier transforms, ML predictions, and custom UDFs for advanced data processing.
•	The Snowflake Scripts directory contains all related SQL scripts, including:
•	Data ETL and Streaming
•	Steps for Slowly Changing Dimensions (SCD)
•	Fourier analysis for signal reconstruction
•	Loading and utilising ML models
•	Machine Learning predictions are also visualised in PowerBI.

3.	Machine Learning:
   
•	All details regarding model selection, exploratory data analysis, hyperparameter tuning, and Fourier analysis are documented in the Machine_Learning_Code.ipynb file.
•	The AWS Lambda directory includes the handler script for deploying the XGBoost model.

4.	Application Development and Deployment:

•	Files for deploying this project on Google Cloud Platform using Docker are included in the repository.

This setup ensures easy integration of operational and sensor data for insights, prediction, and visualisation, as shown in the architectural diagram.

![Architectural Diagram](https://github.com/user-attachments/assets/888f9dce-84c4-4036-8c08-54d43a98466c)
