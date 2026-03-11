
class FlightData:

    def __init__(self, price, origin_airport, destination_airport, out_date, return_date, stops=0, via_city=None):
        self.price = price
        self.origin_airport = origin_airport
        self.destination_airport = destination_airport
        self.out_date = out_date
        self.return_date = return_date
        self.stops = stops
        self.via_city = via_city if via_city else []


def find_cheapest_flight(data, max_stops=0):
    if data is None or not data['data']:
        print("No flight data")
        return FlightData("N/A", "N/A", "N/A", "N/A", "N/A")

    lowest_price = float("inf")
    cheapest_flight = FlightData("N/A", "N/A", "N/A", "N/A", "N/A")

    for flight in data["data"]:
        segments = flight["itineraries"][0]["segments"]
        num_stops = len(segments) - 1

        if num_stops > max_stops:
            continue

        price = float(flight["price"]["grandTotal"])
        if price < lowest_price:
            lowest_price = price
            origin = segments[0]["departure"]["iataCode"]
            destination = segments[-1]["arrival"]["iataCode"]
            out_date = segments[0]["departure"]["at"].split("T")[0]
            return_date = flight["itineraries"][1]["segments"][0]["departure"]["at"].split("T")[0]
            via_city = [seg["arrival"]["iataCode"] for seg in segments[:-1]]
            cheapest_flight = FlightData(lowest_price, origin, destination, out_date, return_date, num_stops, via_city)
            print(f"Lowest price to {destination} is £{lowest_price}")

    return cheapest_flight
