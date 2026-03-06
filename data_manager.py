import os
import requests
from dotenv import load_dotenv

load_dotenv()

SHEETY_ENDPOINT = os.getenv("SHEETY_ENDPOINT")

class DataManager:
    def __init__(self):
        self.destination_data = {}
        self.headers = {"Authorization": f"Bearer {os.getenv('SHEETY_BEARER_TOKEN')}"}

    def get_destination_data(self):
        response = requests.get(url=SHEETY_ENDPOINT, headers=self.headers)
        data = response.json()
        self.destination_data = data["prices"]
        return self.destination_data

    def update_destination_codes(self):
        for city in self.destination_data:
            new_data = {
                "price": {
                    "iataCode": city["iataCode"]
                }
            }
            response = requests.put(url=f"{SHEETY_ENDPOINT}/{city['id']}", json=new_data, headers=self.headers)
            print(f"Updating {city['city']}: {response.status_code} {response.text}")