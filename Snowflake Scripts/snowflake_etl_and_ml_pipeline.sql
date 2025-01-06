---Snowflake ETL and ML Pipeline


CREATE WAREHOUSE Aircraft_Maintenance; --creating warehouse (perform data loading and transformation tasks)
CREATE DATABASE engine_maintenance_data; --creating database (store related schemas and tables)
CREATE SCHEMA engine_maintenance_data.ETL; --creating schema 

USE DATABASE engine_maintenance_data;  --switching to your database
USE SCHEMA ETL; 

--creating a storage integration object for accessing data in Amazon S3
CREATE STORAGE INTEGRATION S3_engine_data
TYPE = EXTERNAL_STAGE
STORAGE_PROVIDER = 'S3'
ENABLED = TRUE
STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::122610512265:role/pred-air' --ARN of the IAM role with access to S3
STORAGE_ALLOWED_LOCATIONS = ('s3://pred-batch-output/transformed-data/');

DESC INTEGRATION S3_engine_data;


CREATE STAGE aircraft_data_stage
URL = 's3://pred-batch-output/transformed-data/'
STORAGE_INTEGRATION = S3_engine_data
FILE_FORMAT = (TYPE = 'PARQUET');


CREATE TABLE transformed_aircraft_maintenance_data (
    unit_id INT,
    time_in_cycles BIGINT,
    setting_1 DOUBLE,
    setting_2 DOUBLE,
    t24 DOUBLE,
    t30 DOUBLE,
    t50 DOUBLE,
    p30 DOUBLE,
    nf DOUBLE,
    nc DOUBLE,
    ps30 DOUBLE,
    phi DOUBLE,
    nrf DOUBLE,
    nrc DOUBLE,
    bpr DOUBLE,
    htbleed BIGINT,
    w31 DOUBLE,
    w32 DOUBLE
);

--creating Stream on the 'PM_test' table to track changes (inserts/updates/deletes)
CREATE STREAM maintenance_data_stream ON TABLE transformed_aircraft_maintenance_data;


COPY INTO transformed_aircraft_maintenance_data
FROM @aircraft_data_stage
FILE_FORMAT = (TYPE = 'PARQUET')
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
PATTERN = '.*[.]parquet'
ON_ERROR = 'CONTINUE';


DESCRIBE TABLE transformed_aircraft_maintenance_data;

SELECT * FROM transformed_aircraft_maintenance_data;

SELECT COUNT(*) AS total_count
FROM transformed_aircraft_maintenance_data;

-- Create or replace the Snowpipe for continuous data loading from S3 into Snowflake
CREATE PIPE snow_pipe
AUTO_INGEST = TRUE
AS
COPY INTO transformed_aircraft_maintenance_data
FROM @aircraft_data_stage
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
FILE_FORMAT = (TYPE = 'PARQUET')
ON_ERROR = 'CONTINUE';


--checking the status of the ETL pipe to ensure it is running correctly
SELECT system$pipe_status('snow_pipe'); 

----describing the ETL pipe for detailed information and event notifications
DESC PIPE snow_pipe; --arn:aws:sqs:eu-north-1:448049824393:sf-snowpipe-AIDAWQUOZYKEWOAT43I4U-wl66yL9D3fj-QAKBX25XBg


--checking the copy history for the to verify data loads
SELECT * FROM TABLE (INFORMATION_SCHEMA.COPY_HISTORY
    (TABLE_NAME =>'transformed_aircraft_maintenance_data',
    START_TIME => DATEADD(HOUR, -2, CURRENT_TIMESTAMP())
    ) );

-- Target table for merged and deduplicated data
CREATE TABLE ETL.target_aircraft_maintenance_data (
    unit_id INT,
    time_in_cycles BIGINT,
    setting_1 DOUBLE,
    setting_2 DOUBLE,
    t24 DOUBLE,
    t30 DOUBLE,
    t50 DOUBLE,
    p30 DOUBLE,
    nf DOUBLE,
    nc DOUBLE,
    ps30 DOUBLE,
    phi DOUBLE,
    nrf DOUBLE,
    nrc DOUBLE,
    bpr DOUBLE,
    htbleed BIGINT,
    w31 DOUBLE,
    w32 DOUBLE
);


-- Task to load data incrementally from the stream into the target table
CREATE TASK load_data_from_stream
   WAREHOUSE = Aircraft_Maintenance
   SCHEDULE = '1 MINUTE'  -- Runs every minute; you can adjust this schedule as needed
   WHEN SYSTEM$STREAM_HAS_DATA('ETL.maintenance_data_stream')  -- Trigger when new data is available in the stream
AS
MERGE INTO ETL.target_aircraft_maintenance_data t  -- Target table for the merge operation
USING ETL.maintenance_data_stream s  -- Source stream with incremental changes
ON t.unit_id = s.unit_id AND t.time_in_cycles = s.time_in_cycles  -- Primary key or unique identifier now includes time_in_cycles
WHEN MATCHED AND s.metadata$action = 'DELETE' THEN 
    DELETE  -- Deletes records if the action is DELETE
WHEN MATCHED AND s.metadata$action = 'UPDATE' THEN 
    UPDATE SET 
        t.setting_1 = s.setting_1,
        t.setting_2 = s.setting_2,
        t.t24 = s.t24,
        t.t30 = s.t30,
        t.t50 = s.t50,
        t.p30 = s.p30,
        t.nf = s.nf,
        t.nc = s.nc,
        t.ps30 = s.ps30,
        t.phi = s.phi,
        t.nrf = s.nrf,
        t.nrc = s.nrc,
        t.bpr = s.bpr,
        t.htbleed = s.htbleed,
        t.w31 = s.w31,
        t.w32 = s.w32  -- Specify each column to update
WHEN NOT MATCHED AND s.metadata$action = 'INSERT' THEN 
    INSERT (unit_id, time_in_cycles, setting_1, setting_2, t24, t30, t50, p30, nf, nc, ps30, phi, nrf, nrc, bpr, htbleed, w31, w32) 
    VALUES (s.unit_id, s.time_in_cycles, s.setting_1, s.setting_2, s.t24, s.t30, s.t50, s.p30, s.nf, s.nc, s.ps30, s.phi, s.nrf, s.nrc, s.bpr, s.htbleed, s.w31, s.w32);


--showing all tasks to verify the creation of the new task
SHOW TASKS;

--enable the task to start running
ALTER TASK load_data_from_stream RESUME; 

--suspend the task to stop running
ALTER TASK load_data_from_stream SUSPEND; 

SELECT * FROM maintenance_data_stream;

SHOW WAREHOUSES;

SELECT TOP 100 *
FROM target_aircraft_maintenance_data
ORDER BY unit_id, time_in_cycles;


SELECT COUNT(*) AS total_count
FROM target_aircraft_maintenance_data;


SELECT *
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
    TABLE_NAME => 'target_aircraft_maintenance_data',
    START_TIME => DATEADD(HOUR, -24, CURRENT_TIMESTAMP())
));


CREATE OR REPLACE FUNCTION principal_signal_reconstruction(sensor_data ARRAY)
RETURNS ARRAY
LANGUAGE PYTHON
RUNTIME_VERSION = '3.8'
HANDLER = 'signal_reconstruct'
PACKAGES = ('numpy', 'pandas', 'scipy')
AS $$
import numpy as np
import pandas as pd
from scipy.fft import fft, ifft

def signal_reconstruct(sensor_data):
    # Convert to numpy array for Fourier transform
    dataset = np.array(sensor_data)

    # Apply Fourier transform
    fourier = fft(dataset)
    magnitude_spectrum = np.abs(fourier)

    # Define principal percentage and calculate number of frequencies to retain
    principal_percentage = 30
    top_frequency_count = int(len(dataset) * principal_percentage / 100)

    # Find indices of principal frequencies
    principal_indices = magnitude_spectrum.argsort()[-top_frequency_count:][::-1]

    # Set up Fourier DataFrame to retain only significant frequencies
    fourier_df = pd.DataFrame({"fourier_values": fourier})
    fourier_df["significant_fourier_values"] = 0
    fourier_df.loc[principal_indices, "significant_fourier_values"] = fourier_df.loc[principal_indices, "fourier_values"]

    # Perform inverse Fourier transform on significant frequencies
    reconstructed_signal = ifft(fourier_df["significant_fourier_values"].values).real
    return reconstructed_signal.tolist()  # Convert back to list for Snowflake ARRAY return
$$;



CREATE OR REPLACE TABLE reconstructed_aircraft_data AS
SELECT 
    unit_id,
    time_in_cycles,
    setting_1,
    setting_2,
    
    -- Apply Fourier reconstruction to each row’s sensor value
    principal_signal_reconstruction(ARRAY_CONSTRUCT(t24)) AS principal_recon_t24,
    principal_signal_reconstruction(ARRAY_CONSTRUCT(t30)) AS principal_recon_t30,
    principal_signal_reconstruction(ARRAY_CONSTRUCT(t50)) AS principal_recon_t50,
    principal_signal_reconstruction(ARRAY_CONSTRUCT(p30)) AS principal_recon_p30,
    principal_signal_reconstruction(ARRAY_CONSTRUCT(nf)) AS principal_recon_nf,
    principal_signal_reconstruction(ARRAY_CONSTRUCT(nc)) AS principal_recon_nc,
    principal_signal_reconstruction(ARRAY_CONSTRUCT(ps30)) AS principal_recon_ps30,
    principal_signal_reconstruction(ARRAY_CONSTRUCT(phi)) AS principal_recon_phi,
    principal_signal_reconstruction(ARRAY_CONSTRUCT(nrf)) AS principal_recon_nrf,
    principal_signal_reconstruction(ARRAY_CONSTRUCT(nrc)) AS principal_recon_nrc,
    principal_signal_reconstruction(ARRAY_CONSTRUCT(bpr)) AS principal_recon_bpr,
    principal_signal_reconstruction(ARRAY_CONSTRUCT(htbleed)) AS principal_recon_htbleed,
    principal_signal_reconstruction(ARRAY_CONSTRUCT(w31)) AS principal_recon_w31,
    principal_signal_reconstruction(ARRAY_CONSTRUCT(w32)) AS principal_recon_w32

FROM ETL.target_aircraft_maintenance_data;


select * from reconstructed_aircraft_data;


CREATE OR REPLACE VIEW sensor_data AS
SELECT 
    unit_id,
    time_in_cycles,
    principal_recon_t24,
    principal_recon_t30,
    principal_recon_t50,
    principal_recon_p30,
    principal_recon_nf,
    principal_recon_nc,
    principal_recon_ps30,
    principal_recon_phi,
    principal_recon_nrf,
    principal_recon_nrc,
    principal_recon_bpr,
    principal_recon_htbleed,
    principal_recon_w31,
    principal_recon_w32
FROM reconstructed_aircraft_data
QUALIFY ROW_NUMBER() OVER (PARTITION BY unit_id ORDER BY time_in_cycles DESC) = 1
ORDER BY unit_id;


SELECT * FROM sensor_data;


CREATE USER lambda_user PASSWORD = '10203040';
CREATE ROLE pred_user;
GRANT ROLE pred_user TO USER lambda_user;
GRANT USAGE ON DATABASE engine_maintenance_data TO ROLE pred_user;
GRANT USAGE ON SCHEMA engine_maintenance_data.ETL TO ROLE pred_user;

CREATE STAGE model_stage
STORAGE_INTEGRATION = S3_engine_data
URL = 'S3://pred-batch-output/transformed-data/Models/xgb_model.pkl';

LIST @model_stage;


CREATE OR REPLACE TABLE training_data (
    unit_id INT,
    time_in_cycles BIGINT,
    principal_recon_t24 DOUBLE,
    principal_recon_t30 DOUBLE,
    principal_recon_t50 DOUBLE,
    principal_recon_p30 DOUBLE,
    principal_recon_nf DOUBLE,
    principal_recon_nc DOUBLE,
    principal_recon_ps30 DOUBLE,
    principal_recon_phi DOUBLE,
    principal_recon_nrf DOUBLE,
    principal_recon_nrc DOUBLE,
    principal_recon_bpr DOUBLE,
    principal_recon_htbleed BIGINT,
    principal_recon_w31 DOUBLE,
    principal_recon_w32 DOUBLE,
    RUL INT 
); 

select * from training_data;

CREATE OR REPLACE MODEL xgb_model
USING
(
    SELECT 
      principal_recon_t24, 
      principal_recon_t30, 
      principal_recon_t50, 
      principal_recon_p30, 
      principal_recon_nf, 
      principal_recon_nc, 
      principal_recon_ps30, 
      principal_recon_phi, 
      principal_recon_nrf, 
      principal_recon_nrc, 
      principal_recon_bpr, 
      principal_recon_htbleed, 
      principal_recon_w31, 
      principal_recon_w32,
      RUL
    FROM training_data
)
WITH
(
    OBJECTIVE = 'reg:squarederror',
    INPUT_COLS = ['principal_recon_t24', 'principal_recon_t30', 'principal_recon_t50', 'principal_recon_p30', 'principal_recon_nf', 'principal_recon_nc', 'principal_recon_ps30', 'principal_recon_phi', 'principal_recon_nrf', 'principal_recon_nrc', 'principal_recon_bpr', 'principal_recon_htbleed', 'principal_recon_w31', 'principal_recon_w32'],
    LABEL_COLS = ['RUL'],
    MAX_DEPTH = 3,
    LEARNING_RATE = 0.05,
    N_ESTIMATORS = 100
);
