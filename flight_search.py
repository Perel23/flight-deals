import requests
from datetime import datetime, timedelta
import os
import time
from dotenv import load_dotenv

load_dotenv()

IATA_ENDPOINT = "https://test.api.amadeus.com/v1/reference-data/locations/cities"
FLIGHT_ENDPOINT = "https://test.api.amadeus.com/v2/shopping/flight-offers"
TOKEN_ENDPOINT = "https://test.api.amadeus.com/v1/security/oauth2/token"


class FlightSearch:

    def __init__(self):
        self._api_key = os.environ["AMADEUS_API_KEY"]
        self._api_secret = os.environ["AMADEUS_SECRET"]
        self._token = self._get_new_token()

    def _get_new_token(self):
        header = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        body = {
            'grant_type': 'client_credentials',
            'client_id': self._api_key,
            'client_secret': self._api_secret
        }
        response = requests.post(url=TOKEN_ENDPOINT, headers=header, data=body)
        print(f"Your token is {response.json()['access_token']}")
        print(f"Your token expires in {response.json()['expires_in']} seconds")
        return response.json()['access_token']

    def get_iata_code(self, city_name):
        headers = {"Authorization": f"Bearer {self._token}"}
        query = {
            "keyword": city_name,
            "max": "2",
            "include": "AIRPORTS",
        }
        response = requests.get(url=IATA_ENDPOINT, headers=headers, params=query)
        try:
            code = response.json()["data"][0]['iataCode']
        except IndexError:
            print(f"IndexError: No airport code found for {city_name}.")
            return "N/A"
        except KeyError:
            print(f"KeyError: No airport code found for {city_name}.")
            return "Not Found"
        return code

    def check_flights(self, origin_city_code, destination_city_code):
        headers = {"Authorization": f"Bearer {self._token}"}
        all_flights = []

        for week_offset in range(1, 27):
            departure_date = (datetime.now() + timedelta(weeks=week_offset)).strftime("%Y-%m-%d")
            query = {
                "originLocationCode": origin_city_code,
                "destinationLocationCode": destination_city_code,
                "departureDate": departure_date,
                "adults": 1,
                "currencyCode": "GBP",
                "max": "5",
            }
            response = requests.get(url=FLIGHT_ENDPOINT, headers=headers, params=query)

            if response.status_code != 200:
                print(f"  {departure_date}: response code {response.status_code}")
                time.sleep(2)
                continue

            data = response.json().get("data", [])
            if data:
                all_flights.extend(data)
                print(f"  {departure_date}: found {len(data)} flight(s)")

            time.sleep(2)

        if not all_flights:
            return None

        return {"data": all_flights}
