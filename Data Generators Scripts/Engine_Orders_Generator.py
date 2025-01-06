import pandas as pd
import random
from datetime import datetime, timedelta

#generating a random date within the last year
def random_date():
    start = datetime.now() - timedelta(days=365)
    random_days = random.randint(0, 365)
    return (start + timedelta(days=random_days)).strftime('%Y-%m-%d')

#data generation
data = []
for order_id in range(1000, 1151):
    engine_id = random.randint(1, 100)
    order_amount = round(random.uniform(10000, 30000), 2)
    order_date = random_date()
    airport_id = random.randint(1, 30)
    product_id = random.randint(1, 200)

    data.append({
        'order_id': order_id,
        'engine_id': engine_id,
        'order_amount': order_amount,
        'order_date': order_date,
        'airport_id': airport_id,
        'product_id': product_id
    })

#dataFrame
df_engine_orders = pd.DataFrame(data)

#saving to CSV
df_engine_orders.to_csv('/Users/prajishpradeep/Downloads/Engine_Orders.csv', index=False)