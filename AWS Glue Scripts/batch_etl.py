#Glue Jobs (PySpark) - Batch processing ETL

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

# Initialize Glue context and job parameters
args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Database and table names
database_name = "maintenace_data"
table_name = "aircraft_maintenance_data"
print(f"Loading data from Glue Data Catalog - Database: {database_name}, Table: {table_name}")

# Load the data from the Glue catalog
input_data = glueContext.create_dynamic_frame.from_catalog(
    database=database_name, 
    table_name=table_name
)

# Convert to a Spark DataFrame for easier transformation operations
df = input_data.toDF()

# Drop the unnecessary columns
columns_to_drop = ["Setting_3", "T2", "P2", "epr", "farB", "Nf_dmd", "P15", "PCRfR_dmd"]
df_transformed = df.drop(*columns_to_drop)
print("Columns dropped successfully.")

# Verify the output path is correctly set
output_path = "s3://pred-batch-output/transformed-data/"
print(f"Output path: {output_path}")

# Write the transformed data back to an S3 bucket in Parquet format
df_transformed.write.mode("overwrite").parquet(output_path)

# Commit the job
job.commit()