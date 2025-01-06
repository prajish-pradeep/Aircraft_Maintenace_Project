import pandas as pd
import requests
import random

#extract data from the Randomuser API
def fetch_random_user():
    response = requests.get('https://randomuser.me/api/')
    user_data = response.json()
    user = user_data['results'][0]
    title = user['name']['title']
    first_name = user['name']['first']
    last_name = user['name']['last']
    return f"{title} {first_name} {last_name}"

# maintenance specialties
specialties = ['Avionics', 'Engine Repair', 'Hydraulics', 'Electrical Systems', 'Fuel Systems', 
               'Structural Repair', 'Safety Systems', 'Propulsion', 'Aerodynamics', 'Environmental Systems', 'Powerplant Systems', 'Control Systems', 'Exhaust Systems', 'Cooling Systems', 'Lubrication Systems', 'Ignition Systems', 'Turbine Systems', 'Corrosion Control', 'Inspection Systems', 'Navigation Systems']

#data generation
data = []
for i in range(1, 201):
    full_name = fetch_random_user()
    specialty = random.choice(specialties)
    airport_id = random.randint(1, 30)

    data.append({
        'technician_id': i,
        'technician_name': full_name,
        'specialty': specialty,
        'airport_id': airport_id
    })

#dataframe and saving csv
df_technicians = pd.DataFrame(data)
df_technicians.to_csv('/Users/prajishpradeep/Downloads/Technicians.csv', index=False)