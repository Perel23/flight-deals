import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from data_manager import DataManager
from flight_search import FlightSearch
from flight_data import find_cheapest_flight
from notification_manager import NotificationManager
from ai_assistant import AIAssistant

load_dotenv()

ORIGIN_CITY_IATA = os.getenv("ORIGIN_CITY_IATA")
DESTINATION_EMAIL = os.getenv("DESTINATION_EMAIL")

data_manager = DataManager()
flight_search = FlightSearch()
notification_manager = NotificationManager()
ai_assistant = AIAssistant()

sheet_data = data_manager.get_destination_data()
# Fill in any missing data using Gemini
for row in sheet_data:
    missing_iata = row.get("iataCode", "") == ""
    missing_price = row.get("lowestPrice", 0) == 0

    if missing_iata or missing_price:
        print(f"Incomplete data for '{row['city']}' — asking Gemini...")
        iata, price = ai_assistant.get_city_data(row["city"], ORIGIN_CITY_IATA)
        if missing_iata:
            row["iataCode"] = iata
        if missing_price:
            row["lowestPrice"] = price

data_manager.update_destination_codes()

tomorrow = datetime.now() + timedelta(days=1)
six_month_from_today = datetime.now() + timedelta(days=(6 * 30))

# Check for cheap flights from origin to each destination
for destination in sheet_data:
    if not destination.get("iataCode", ""):
        print(f"Skipping {destination['city']} — no IATA code.")
        continue

    print(f"Checking flights to {destination['city']}...")
    flights = flight_search.check_flights(
        ORIGIN_CITY_IATA,
        destination["iataCode"],
        from_time=tomorrow,
        to_time=six_month_from_today,
        is_direct=True,
    )
    cheapest_flight = find_cheapest_flight(flights, max_stops=0)

    if cheapest_flight.price == "N/A":
        print(f"No direct flight found. Searching for indirect flights to {destination['city']}...")
        flights = flight_search.check_flights(
            ORIGIN_CITY_IATA,
            destination["iataCode"],
            from_time=tomorrow,
            to_time=six_month_from_today,
            is_direct=False,
        )
        cheapest_flight = find_cheapest_flight(flights, max_stops=2)

    time.sleep(2)

    if cheapest_flight.price == "N/A":
        print(f"  No flights found.")
        continue

    print(f"  £{cheapest_flight.price}")

    if cheapest_flight.price < destination["lowestPrice"]:
        print(f"  Low price alert! £{cheapest_flight.price} (threshold: £{destination['lowestPrice']})")

        stops_str = "Direct" if cheapest_flight.stops == 0 else f"{cheapest_flight.stops} stop(s)"
        google_flights_link = (
            f"https://www.google.com/travel/flights?q=flights+from+"
            f"{ORIGIN_CITY_IATA}+to+{destination['iataCode']}+on+{cheapest_flight.out_date}"
        )

        notification_manager.send_emails(
            email_list=[DESTINATION_EMAIL],
            message=(
                f"Low price alert!\n\n"
                f"From:      {cheapest_flight.origin_airport}\n"
                f"To:        {destination['city']} ({cheapest_flight.destination_airport})\n"
                f"Date:      {cheapest_flight.out_date}\n"
                f"Return:    {cheapest_flight.return_date}\n"
                f"Price:     £{cheapest_flight.price}\n"
                f"Stops:     {stops_str}\n\n"
                f"Search on Google Flights:\n{google_flights_link}"
            )
        )
    else:
        print(f"  £{cheapest_flight.price} — not cheaper than threshold £{destination['lowestPrice']}.")