from FlightRadar24.api import FlightRadar24API
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

fr_api = FlightRadar24API()
airports = fr_api.get_airports()

countries = ['United States', 'United Kingdom', 'Spain', 'Poland',
             'France', 'Portugal', 'Sweden', 'Finland',
             'China', 'Germany', 'Japan', 'Norway',
             'Austria', 'Switzerland', 'Netherlands', 'Brazil',
             'Denmark', 'Turkey', 'Italy', 'Singapore',
             'South Korea', 'United Arab Emirates', 'Australia', 'Canada']
items_per_page = 4
max_number_of_countries_pages = len(countries) // items_per_page

AIRPORTS, AIRPORT_INFO, FLIGHTS, FLIGHT_INFO = range(4)


def countries_list_formatter(page_number):
    keyboard = []
    for country in countries[(page_number - 1) * items_per_page:page_number * items_per_page]:
        keyboard.append([InlineKeyboardButton(country, callback_data=country)])

    reply_markup = add_arrows(keyboard, page_number, max_number_of_countries_pages)
    return reply_markup


# For navigating between airports list
def airports_list_formatter(page_number, country):
    keyboard = []
    local_airports = get_local_airports(country)

    for airport in local_airports[(page_number - 1) * items_per_page:page_number * items_per_page]:
        keyboard.append([InlineKeyboardButton(airport["name"], callback_data=airport["name"])])

    reply_markup = add_arrows(keyboard, page_number, len(local_airports) // items_per_page)
    return reply_markup


def zones_list_formatter(page_number):
    keyboard = []
    zones = fr_api.get_zones()
    zones_names = []

    for zone in list(zones)[(page_number - 1) * items_per_page:page_number * items_per_page]:
        keyboard.append([InlineKeyboardButton(zone.capitalize(), callback_data=zone)])

    reply_markup = add_arrows(keyboard, page_number, len(zones_names) // items_per_page)
    return reply_markup


def flights_list_formatter(page_number, zone):
    keyboard = []
    local_flights = []

    zones = fr_api.get_zones()
    bounds = fr_api.get_bounds(zones[zone])
    flights = fr_api.get_flights(bounds=bounds)

    for flight in flights[(page_number - 1) * items_per_page:page_number * items_per_page]:
        try:
            details = fr_api.get_flight_details(flight.id)
            if details['status']['live']:
                local_flights.append(flight.id)
        except:
            ##bad data
            pass

    for local_flight in local_flights:
        keyboard.append([InlineKeyboardButton(local_flight, callback_data=local_flight)])

    reply_markup = add_arrows(keyboard, page_number, len(flights) // items_per_page)
    return reply_markup


def add_arrows(keyboard, page_number, max_page):
    right_button = InlineKeyboardButton(">", callback_data=page_number + 1)
    left_button = InlineKeyboardButton("<", callback_data=page_number - 1)

    if 1 < page_number < max_page:
        keyboard.append([left_button, right_button])
    elif page_number > 1:
        keyboard.append([left_button])
    else:
        keyboard.append([right_button])

    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def get_local_airports(country) -> list:
    local_airports = []

    for airport in airports:
        if airport["country"] == country:
            local_airports.append(airport)

    return local_airports
