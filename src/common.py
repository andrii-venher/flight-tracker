def text_from_airport(airport):
    text = f'{airport["name"]}\n'
    text += f'Country: {airport["country"]}\n'
    text += f'IATA: {airport["iata"]}\n'
    text += f'ICAO: {airport["icao"]}\n'
    text += f'Latitude: {airport["lat"]}\n'
    text += f'Longitude: {airport["lon"]}\n'
    text += f'Alt: {airport["alt"]}'
    return text
