from FlightRadar24.api import FlightRadar24API
fr_api = FlightRadar24API()

airports = fr_api.get_airports()

print(airports)