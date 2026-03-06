import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()


class AIAssistant:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def get_city_data(self, city_name, origin_iata="TLV"):
        prompt = (
            f"For the city '{city_name}', provide:\n"
            f"1. The IATA city code (3 letters).\n"
            f"2. A recommended lowest price threshold in GBP for a one-way flight from {origin_iata} "
            f"that would represent a genuinely good deal (below typical market price).\n\n"
            f"Return ONLY a JSON object with this exact format, no explanation:\n"
            f'{{ "iataCode": "XXX", "lowestPrice": 000 }}'
        )

        response = self.client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )

        data = json.loads(response.text)
        print(f"  Gemini suggests: IATA={data['iataCode']}, lowestPrice=£{data['lowestPrice']}")
        return data["iataCode"], int(data["lowestPrice"])