import pandas as pd
import random
from datetime import datetime, timedelta

#generating a random date within the last year
def random_date():
    start = datetime.now() - timedelta(days=365)
    random_days = random.randint(0, 365)
    return (start + timedelta(days=random_days)).strftime('%Y-%m-%d')

# Generate data
data = []
for shipment_id in range(1500, 1651):
    airport_id = random.randint(1, 30)
    engine_id = random.randint(1, 100)
    order_id = random.randint(1000, 1151)
    shipment_date = random_date()

    data.append({
        'shipment_id': shipment_id,
        'airport_id': airport_id,
        'engine_id': engine_id,
        'order_id': order_id,
        'shipment_date': shipment_date
    })

# Create DataFrame and save to CSV
df_shipments = pd.DataFrame(data)

df_shipments.to_csv('/Users/prajishpradeep/Downloads/Shipments.csv', index=False)