import os
import requests
from datetime import datetime, timedelta
from amadeus import Client, ResponseError
from dotenv import load_dotenv

load_dotenv()

AMADEUS_TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"


class FlightSearch:
    def __init__(self):
        self.amadeus = Client(
            client_id=os.getenv("AMADEUS_API_KEY"),
            client_secret=os.getenv("AMADEUS_SECRET"),
        )

    def get_bearer_token(self):
        response = requests.post(
            url=AMADEUS_TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": os.getenv("AMADEUS_API_KEY"),
                "client_secret": os.getenv("AMADEUS_SECRET"),
            },
        )
        response.raise_for_status()
        token = response.json()["access_token"]
        print(f"Bearer token: {token}")
        return token

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

        for week_offset in range(1, 27):
            departure_date = (datetime.now() + timedelta(weeks=week_offset)).strftime("%Y-%m-%d")
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
                print(f"  {departure_date}: {error}")

        return cheapest
