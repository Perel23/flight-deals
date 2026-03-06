import os
import time
from dotenv import load_dotenv
from data_manager import DataManager
from flight_search import FlightSearch
from notification_manager import NotificationManager

load_dotenv()

ORIGIN_CITY_IATA = os.getenv("ORIGIN_CITY_IATA")
DESTINATION_EMAIL = os.getenv("DESTINATION_EMAIL")

data_manager = DataManager()
flight_search = FlightSearch()
notification_manager = NotificationManager()

sheet_data = data_manager.get_destination_data()

# Fill in any missing IATA codes
for row in sheet_data:
    if row["iataCode"] == "":
        row["iataCode"] = flight_search.get_iata_code(row["city"])
        time.sleep(1)

data_manager.update_destination_codes()

# Check for cheap flights from origin to each destination
for destination in sheet_data:
    if not destination["iataCode"]:
        print(f"Skipping {destination['city']} — no IATA code.")
        continue

    print(f"Checking flights to {destination['city']}...")
    cheapest_flight = flight_search.check_flights(ORIGIN_CITY_IATA, destination["iataCode"])

    if cheapest_flight is None:
        print(f"  No flights found.")
        continue

    price = float(cheapest_flight["price"]["grandTotal"])
    lowest = destination["lowestPrice"]

    if price < lowest:
        print(f"  Low price alert! £{price} (threshold: £{lowest})")
        notification_manager.send_emails(
            email_list=[DESTINATION_EMAIL],
            message=(
                f"Low price alert!\n\n"
                f"Only £{price} to fly from {ORIGIN_CITY_IATA} to {destination['city']} ({destination['iataCode']}).\n"
                f"Your threshold was £{lowest}."
            )
        )
    else:
        print(f"  £{price} — not cheaper than threshold £{lowest}.")