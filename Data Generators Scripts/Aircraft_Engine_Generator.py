import pandas as pd
import random
from datetime import datetime, timedelta

#defining engine types and models
engine_types = ['Turbofan', 'Prop', 'Jet']
models = {
    'Turbofan': ['GE90-115B', 'Trent XWB', 'CFM56-5B', 'PW1000G', 'Trent 700', 'CF34-10E', 'V2500', 'PW206B', 'CFM56-7B', 'AE3007'],
    'Prop': ['PT6A-67R', 'TPE331', 'AE 2100', 'GE Aviation H80', 'Lycoming TIO-540-A2C', 'PT6A-21', 'AE2100D2', 'TPE331-10', 'PT6A-68', 'PT6A-114A'],
    'Jet': ['F110', 'F135', 'RB211', 'J85', 'Spey', 'General Electric F110', 'Pratt & Whitney F135', 'Rolls-Royce RB211', 'General Electric J85', 'Rolls-Royce Spey']
}

#engine componenents
components = {
    'Turbofan': ['Fan Blade', 'Turbine Blade', 'Compressor Disc', 'Gearbox', 'Exhaust Case', 'Fan Disk', 'Combustion Chamber', 'High Pressure Turbine', 'Low Pressure Turbine'],
    'Prop': ['Propeller Blade', 'Gearbox', 'Fuel Nozzle', 'Compressor', 'Turbocharger', 'Reduction Gearbox', 'Fuel Controller', 'Turbine Blade', 'Compressor Blade'],
    'Jet': ['Afterburner', 'Fan Blade', 'Compressor Blade', 'Turbine Disc', 'Thrust Reverser', 'Valve', 'Sensor', 'Starter', 'Exhaust Pipe']
}

#generate random dates
def random_date(start, end):
    #generating a random date between start and end date
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")
    delta = end_date - start_date
    random_days = random.randrange(delta.days)
    random_date = start_date + timedelta(days=random_days)
    return random_date.strftime("%Y-%m-%d")

#automatically generate 100 aircraft engines
data = []
for i in range(100):
    engine_type = random.choice(engine_types)
    model = random.choice(models[engine_type])
    component = random.choice(components[engine_type])
    component_type = f"{component} System"
    manufacture_date = random_date('1990-01-01', '2022-12-31')
    
    data.append({
        'engine_id': i + 1,
        'engine_model': model,
        'engine_type': engine_type,
        'component_name': component,
        'component_type': component_type,
        'manufacture_date': manufacture_date
    })

#dataframe
df_engines = pd.DataFrame(data)

#saving to csv
df_engines.to_csv('/Users/prajishpradeep/Downloads/Aircraft_Engines.csv', index=False)