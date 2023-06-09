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


def top_air(flights) -> list:
    local_flights = []
    airlines = {}
    for flight in flights:
        try:
            if flight.on_ground:
                continue
            airline = flight.airline_iata
            if airline == 'N/A':
                continue
            if airline in airlines:
                airlines[airline] += 1
            else:
                airlines[airline] = 1
        except:
            pass

    airlines = dict(sorted(airlines.items(), key=lambda x: x[1], reverse=True))
    top_airlines = list(airlines.items())[:10]
    return top_airlines


def get_flight_by_id(id):
    flights = fr_api.get_flights()
    for flight in flights:
        if flight.id == id:
            return flight
    return None


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


def format_airlines_ranking(top_airlines):
    i = 1
    text = ""
    for air in top_airlines:
        text += f'{i}. '
        air_line = fr_api.get_airlines()
        text += air_line[i]["Name"]
        text += ": "
        text += f'{air[1]}'
        text += "\n"
        i += 1
    return text


def format_flight(flight) -> str:
    text = ''
    text += f'ID: {flight.id}\n'
    text += f'Flight number: {flight.registration}\n'
    text += f'From: {flight.origin_airport_iata}\n'
    text += f'To: {flight.destination_airport_iata}\n'
    text += f'Latitude: {flight.latitude}\n'
    text += f'Longitude: {flight.longitude}\n'
    text += f'Ground speed: {flight.ground_speed}'
    return text


def format_icao(airline) -> str:
    text = ''
    text += f'Name: {airline["Name"]}\n'
    text += f'Company code: {airline["Code"]}\n'
    text += f'ICAO: {airline["ICAO"]}'
    return text


def air_by_icao(airline_icao):
    airlines = fr_api.get_airlines()
    text = ''
    for airline in airlines:
        if airline["ICAO"] == airline_icao:
            return airline
    return text


def airp_by_icao(airport_icao) -> str:
    text = ""
    airports = fr_api.get_airports()
    for airport in airports:
        if airport["icao"] == airport_icao:
            return airport
    return text


def airp_by_iata(airport_iata) -> str:
    text = ""
    airports = fr_api.get_airports()
    for airport in airports:
        if airport["iata"] == airport_iata:
            return airport
    return text


def is_flight_delayed(flight_id):
    try:
        details = fr_api.get_flight_details(flight_id)
        if details["time"]["scheduled"]["arrival"] is None:
            return None
        elif details["time"]["estimated"]["arrival"] is not None:
            diff = details["time"]["estimated"]["arrival"] - details["time"]["scheduled"]["arrival"]
            return diff
        else:
            # Flight arrives on time
            return 0
    except:
        return None
