import pandas as pd

#airport in UK(reference: wikipedia)
airports_data = [
    {"airport_id": 1, "airport_name": "Birmingham International Airport", "location": "Birmingham"},
    {"airport_id": 2, "airport_name": "Bournemouth Airport", "location": "Bournemouth"},
    {"airport_id": 3, "airport_name": "Bristol Airport", "location": "Bristol"},
    {"airport_id": 4, "airport_name": "Cardiff Airport", "location": "Cardiff"},
    {"airport_id": 5, "airport_name": "Doncaster Sheffield Airport", "location": "Doncaster"},
    {"airport_id": 6, "airport_name": "Durham Tees Valley Airport", "location": "Durham"},
    {"airport_id": 7, "airport_name": "East Midlands Airport", "location": "Castle Donington"},
    {"airport_id": 8, "airport_name": "Exeter International Airport", "location": "Exeter"},
    {"airport_id": 9, "airport_name": "Leeds Bradford International Airport", "location": "Leeds"},
    {"airport_id": 10, "airport_name": "Liverpool John Lennon Airport", "location": "Liverpool"},
    {"airport_id": 11, "airport_name": "London City Airport", "location": "London"},
    {"airport_id": 12, "airport_name": "Gatwick Airport", "location": "London"},
    {"airport_id": 13, "airport_name": "Heathrow Airport", "location": "London"},
    {"airport_id": 14, "airport_name": "Luton Airport", "location": "London"},
    {"airport_id": 15, "airport_name": "Stansted Airport", "location": "London"},
    {"airport_id": 16, "airport_name": "Manchester Airport", "location": "Manchester"},
    {"airport_id": 17, "airport_name": "Newcastle Airport", "location": "Newcastle"},
    {"airport_id": 18, "airport_name": "Newquay Cornwall Airport", "location": "Newquay"},
    {"airport_id": 19, "airport_name": "Norwich International Airport", "location": "Norwich"},
    {"airport_id": 20, "airport_name": "Southampton Airport", "location": "Southampton"},
    {"airport_id": 21, "airport_name": "Aberdeen Airport", "location": "Aberdeen"},
    {"airport_id": 22, "airport_name": "Edinburgh Airport", "location": "Edinburgh"},
    {"airport_id": 23, "airport_name": "Glasgow International Airport", "location": "Glasgow"},
    {"airport_id": 24, "airport_name": "Glasgow Prestwick Airport", "location": "Prestwick"},
    {"airport_id": 25, "airport_name": "Inverness Airport", "location": "Inverness"},
    {"airport_id": 26, "airport_name": "Belfast International Airport", "location": "Belfast"},
    {"airport_id": 27, "airport_name": "George Best Belfast City Airport", "location": "Belfast"},
    {"airport_id": 28, "airport_name": "City of Derry Airport", "location": "Derry"},
    {"airport_id": 29, "airport_name": "London Southend Airport", "location": "London"},
    {"airport_id": 30, "airport_name": "Dundee Airport", "location": "Dundee"}
]

#create dataframe
df_airports = pd.DataFrame(airports_data)

#saving to csv
df_airports.to_csv('/Users/prajishpradeep/Downloads/UK_Airports.csv', index=False)