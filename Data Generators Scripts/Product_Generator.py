import pandas as pd
import random

#product types
product_types = [
    'Engine', 'Avionics', 'Hydraulic Pump', 'Fuel Meter', 'Landing Gear', 'Turbine Blade', 'Exhaust System', 'Flight Control System', 'Sensor', 'Propeller', 
    'Cabin Pressure System', 'Navigation System', 'Aircraft Battery', 'Aircraft Tire', 'Aircraft Brake', 'Aircraft Lighting', 
    'Aircraft Antenna', 'Aircraft Starter', 'Aircraft Alternator', 'Aircraft Generator','Aircraft Fuel Pump'
]

manufacturers = [
    {'name': 'Boeing', 'location': 'Chicago, IL, USA', 'contact': 'contact@boeing.com'},
    {'name': 'Airbus', 'location': 'Toulouse, France', 'contact': 'contact@airbus.com'},
    {'name': 'Raytheon Technologies', 'location': 'Waltham, MA, USA', 'contact': 'info@raytheon.com'},
    {'name': 'GE Aviation', 'location': 'Evendale, OH, USA', 'contact': 'services@geaviation.com'},
    {'name': 'Rolls-Royce', 'location': 'London, UK', 'contact': 'queries@rolls-royce.com'},
    {'name': 'Honeywell Aerospace', 'location': 'Charlotte, NC, USA', 'contact': 'aero@honeywell.com'},
    {'name': 'Safran', 'location': 'Paris, France', 'contact': 'contact@safran-group.com'},
    {'name': 'Pratt & Whitney', 'location': 'East Hartford, CT, USA', 'contact': 'help@prattwhitney.com'}
]

#data generation
data = []
for i in range(1, 201):
    product_type = random.choice(product_types)
    manufacturer = random.choice(manufacturers)

    data.append({
        'product_id': i,
        'product_type': product_type,
        'manufacturer_name': manufacturer['name'],
        'location': manufacturer['location'],
        'contact_info': manufacturer['contact']
    })

#dataframe
df_products = pd.DataFrame(data)

#saving to CSV
df_products.to_csv('/Users/prajishpradeep/Downloads/Products.csv', index=False)