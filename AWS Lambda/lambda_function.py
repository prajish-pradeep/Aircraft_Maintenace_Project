import os
import sys
import json
import joblib
import xgboost as xgb
import snowflake.connector
import numpy as np
import pandas as pd

sys.path.append('/mnt/efs/xgboost-libs')
MODEL_PATH = '/xgb_model.pkl'
model = joblib.load(MODEL_PATH)

def lambda_handler(event, context):
    # Connect to Snowflake
    conn = snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema=os.getenv('SNOWFLAKE_SCHEMA'),
        role=os.getenv('SNOWFLAKE_ROLE')
    )
    
    try:
        # Query the latest_sensor_data_with_id view for prediction input
        query = "SELECT * FROM engine_maintenance_data.ETL.sensor_data;"
        data_df = pd.read_sql(query, conn)

        # Separate identifiers and sensor values
        identifiers = data_df[['unit_id', 'time_in_cycles']]
        sensor_data_df = data_df.drop(columns=['unit_id', 'time_in_cycles'])

        # Prepare data for prediction
        features = xgb.DMatrix(sensor_data_df)

        # Make predictions
        predictions = model.predict(features)

        # Format results with Unit_ID, Time_in_Cycles, and RUL
        results = []
        for idx, (unit_id, time_in_cycles) in identifiers.iterrows():
            rul = int(round(predictions[idx]))
            results.append({
                "Unit_ID": int(unit_id),
                "Time_in_Cycles": int(time_in_cycles),
                "RUL": rul
            })

        # Return formatted results
        response = {
            'statusCode': 200,
            'body': json.dumps(results)
        }
        return response

    finally:
        # Close Snowflake connection
        conn.close()
