#Glue Jobs (PySpark) - Streaming ETL

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
import pyspark.sql.functions as F
from pyspark.sql.types import StringType, StructType, StructField, FloatType, IntegerType

# Parse job arguments
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

# Initialize Glue and Spark contexts
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Increase retries and timeout settings for handling S3 read timeouts
spark.conf.set("spark.hadoop.fs.s3a.connection.maximum", "100")
spark.conf.set("spark.hadoop.fs.s3a.connection.timeout", "600000")

# Define S3 paths
input_path = "s3://aircraft-maintenance-data/"
output_path = "s3://pred-realtime-output/"
checkpoint_path = "s3://pred-output/stream_etl/"

# Define schema for CSV data
schema = StructType([
    StructField("Unit_ID", IntegerType(), True),
    StructField("Time_in_Cycles", FloatType(), True),
    StructField("Setting_1", FloatType(), True),
    StructField("Setting_2", FloatType(), True),
    StructField("Setting_3", FloatType(), True),
    StructField("T2", FloatType(), True),
    StructField("T24", FloatType(), True),
    StructField("T30", FloatType(), True),
    StructField("T50", FloatType(), True),
    StructField("P2", FloatType(), True),
    StructField("P15", FloatType(), True),
    StructField("P30", FloatType(), True),
    StructField("Nf", FloatType(), True),
    StructField("Nc", FloatType(), True),
    StructField("epr", FloatType(), True),
    StructField("Ps30", FloatType(), True),
    StructField("phi", FloatType(), True),
    StructField("NRf", FloatType(), True),
    StructField("NRc", FloatType(), True),
    StructField("BPR", FloatType(), True),
    StructField("farB", FloatType(), True),
    StructField("htBleed", FloatType(), True),
    StructField("Nf_dmd", FloatType(), True),
    StructField("PCRfR_dmd", FloatType(), True),
    StructField("W31", FloatType(), True),
    StructField("W32", FloatType(), True)
])

# Load streaming data from S3
stream_df = spark.readStream \
    .format("csv") \
    .schema(schema) \
    .option("header", "true") \
    .load(input_path)

# Drop unnecessary columns if they exist
columns_to_drop = [col for col in ["Setting_3", "T2", "P2", "epr", "farB", "Nf_dmd", "P15", "PCRfR_dmd"] if col in stream_df.columns]
transformed_df = stream_df.drop(*columns_to_drop)

# Define critical sensors and their acceptable thresholds
critical_sensors = {
    "P15": (21.60, 21.61),
    "T24": 641.71,
    "T50": 1588.45,
    "P30": 554.85
}

# Define UDF for real-time monitoring and alert generation
def monitor_sensors(row):
    alerts = []
    for sensor, threshold in critical_sensors.items():
        if sensor in row:  # Check if column exists
            actual_value = row[sensor]
            if isinstance(threshold, tuple):  # Range check
                if not (threshold[0] <= actual_value <= threshold[1]):
                    alerts.append(f"Alert: {sensor} out of range ({actual_value}) for Engine {row['Unit_ID']}")
            else:  # Exact value check
                if actual_value != threshold:
                    alerts.append(f"Alert: {sensor} deviation detected ({actual_value}) for Engine {row['Unit_ID']}")
    return ", ".join(alerts)

# Register UDF
monitor_sensors_udf = F.udf(monitor_sensors, StringType())

# Apply UDF to create alerts column
transformed_df = transformed_df.withColumn("alerts", monitor_sensors_udf(F.struct([transformed_df[x] for x in transformed_df.columns])))

# Write transformed data to S3 in streaming mode with checkpointing
query = transformed_df.writeStream \
    .format("parquet") \
    .outputMode("append") \
    .option("checkpointLocation", checkpoint_path) \
    .start(output_path)

# Wait for termination for testing; remove in production
query.awaitTermination()

# Finalize the job
job.commit()