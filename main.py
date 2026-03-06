#This file will need to use the DataManager,FlightSearch, FlightData, NotificationManager classes to achieve the program requirements.
import time
from data_manager import DataManager
from flight_search import FlightSearch

data_manager = DataManager()
flight_search = FlightSearch()

sheet_data = data_manager.get_destination_data()

for row in sheet_data:
    if row["iataCode"] == "":
        row["iataCode"] = flight_search.get_iata_code(row["city"])
        time.sleep(3)

data_manager.update_destination_codes()
print("Sheet updated with IATA codes.")
