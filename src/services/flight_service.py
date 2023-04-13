from FlightRadar24.api import FlightRadar24API

fr_api = FlightRadar24API()


def get_top_flights_by_iata(iata_selector, descending_by_flights=True):
    flights = fr_api.get_flights()
    dictionary = {}

    for flight in flights:
        try:
            iata = iata_selector(flight)

            if iata == 'N/A':
                continue

            if iata in dictionary:
                dictionary[iata] += 1
            else:
                dictionary[iata] = 0
        except:
            pass

    return sorted(dictionary.items(), key=lambda item: item[1], reverse=descending_by_flights)


def get_top_destinations():
    return get_top_flights_by_iata(lambda flight: flight.destination_airport_iata)


def get_top_origins():
    return get_top_flights_by_iata(lambda flight: flight.origin_airport_iata)


def format_airports_ranking(airports_ranking):
    text = ""
    i = 1
    for airport_tuple in airports_ranking:
        text += f'{i}. '
        airport = fr_api.get_airport(airport_tuple[0])
        text += airport["name"]
        text += f' ({airport["position"]["country"]["name"]})'
        text += ": "
        text += f'{airport_tuple[1]}'
        text += "\n"
        i += 1
    return text
