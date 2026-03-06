import os
from dotenv import load_dotenv
from data_manager import DataManager
from flight_search import FlightSearch
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
    missing_iata = row["iataCode"] == ""
    missing_price = row["lowestPrice"] == 0

    if missing_iata or missing_price:
        print(f"Incomplete data for '{row['city']}' — asking Gemini...")
        iata, price = ai_assistant.get_city_data(row["city"], ORIGIN_CITY_IATA)
        if missing_iata:
            row["iataCode"] = iata
        if missing_price:
            row["lowestPrice"] = price

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

        segments = cheapest_flight["itineraries"][0]["segments"]
        departure_dt = segments[0]["departure"]["at"]
        departure_date = departure_dt.split("T")[0]
        arrival_date = segments[-1]["arrival"]["at"].split("T")[0]
        stops = len(segments) - 1
        stops_str = "Direct" if stops == 0 else f"{stops} stop(s)"
        airlines = ", ".join(set(s["carrierCode"] for s in segments))

        google_flights_link = (
            f"https://www.google.com/travel/flights?q=flights+from+"
            f"{ORIGIN_CITY_IATA}+to+{destination['iataCode']}+on+{departure_date}"
        )

        notification_manager.send_emails(
            email_list=[DESTINATION_EMAIL],
            message=(
                f"Low price alert!\n\n"
                f"From:      {ORIGIN_CITY_IATA}\n"
                f"To:        {destination['city']} ({destination['iataCode']})\n"
                f"Date:      {departure_date}\n"
                f"Arrives:   {arrival_date}\n"
                f"Price:     £{price}\n"
                f"Stops:     {stops_str}\n"
                f"Airline(s): {airlines}\n\n"
                f"Search on Google Flights:\n{google_flights_link}"
            )
        )
    else:
        print(f"  £{price} — not cheaper than threshold £{lowest}.")