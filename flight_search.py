import os
from datetime import datetime, timedelta
from amadeus import Client, ResponseError
from dotenv import load_dotenv

load_dotenv()


class FlightSearch:
    def __init__(self):
        self.amadeus = Client(
            client_id=os.getenv("AMADEUS_API_KEY"),
            client_secret=os.getenv("AMADEUS_SECRET"),
        )

    def get_iata_code(self, city_name):
        response = self.amadeus.reference_data.locations.get(
            keyword=city_name,
            subType="CITY"
        )
        if not response.data:
            print(f"No IATA code found for '{city_name}'. Skipping.")
            return ""
        return response.data[0]["iataCode"]

    def check_flights(self, origin_city_code, destination_city_code):
        cheapest = None

        for day_offset in range(1, 181):
            departure_date = (datetime.now() + timedelta(days=day_offset)).strftime("%Y-%m-%d")
            try:
                response = self.amadeus.shopping.flight_offers_search.get(
                    originLocationCode=origin_city_code,
                    destinationLocationCode=destination_city_code,
                    departureDate=departure_date,
                    adults=1,
                    currencyCode="GBP",
                    max=1,
                )
                if response.data:
                    offer = response.data[0]
                    price = float(offer["price"]["grandTotal"])
                    if cheapest is None or price < float(cheapest["price"]["grandTotal"]):
                        cheapest = offer
            except ResponseError as error:
                print(f"{departure_date}: {error}")

        return cheapest
