import pandas as pd
import random
from datetime import datetime, timedelta

#generating a random date within the last year
def random_date():
    start = datetime.now() - timedelta(days=365)
    random_days = random.randint(0, 365)
    return (start + timedelta(days=random_days)).strftime('%Y-%m-%d')

#maintenance actions
actions = [
    "Routine avionics system diagnostics",
    "Complete engine overhaul",
    "Hydraulic system fluid replacement",
    "Electrical systems integrity check",
    "Fuel pump inspection and calibration",
    "Structural integrity review for fuselage",
    "Fire suppression system functional test",
    "Propulsion system efficiency analysis",
    "Aerodynamic performance assessment",
    "Environmental control system maintenance",
    "Powerplant module replacement",
    "Flight control system recalibration",
    "Exhaust nozzle cleaning",
    "Cooling system pressure test",
    "Lubrication system flush and refill",
    "Ignition system troubleshooting",
    "Turbine blade stress testing",
    "Corrosion inspection and mitigation",
    "Instrumentation and inspection systems check",
    "Navigation software update"
]

#data generation
data = []
for maintenance_id in range(1, 301):
    engine_id = random.randint(1, 100)
    technician_id = random.randint(1, 200)
    action_taken = random.choice(actions)  # Randomly select a maintenance action
    date = random_date()  # Random date from the last year

    data.append({
        'maintenance_id': maintenance_id,
        'engine_id': engine_id,
        'technician_id': technician_id,
        'action_taken': action_taken,
        'date': date
    })

#dataframe
df_maintenance_actions = pd.DataFrame(data)

#saving to CSV
df_maintenance_actions.to_csv('/Users/prajishpradeep/Downloads/Maintenance_Action.csv', index=False)