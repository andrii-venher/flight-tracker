import random

from FlightRadar24.api import FlightRadar24API
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ForceReply
from telegram.ext import ContextTypes

from common import text_from_airport, plot_to_bytes
from services import flight_service, plot_service

import matplotlib.pyplot as plt
import numpy as np

fr_api = FlightRadar24API()

countries = ['Italy', 'Spain', 'Denmark', 'Poland', 'Germany',
             'France', 'Portugal', 'Sweden', 'Finland',
             'China', 'Austria', 'Japan', 'Norway',
             'Switzerland', 'Netherlands', 'Brazil', 'Argentina']
items_per_page = 4
max_number_of_countries_pages = len(countries) // items_per_page

airports = fr_api.get_airports()

AIRPORTS, AIRPORT_INFO, FLIGHTS, FLIGHT_INFO = range(4)


# For navigating between countries list
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


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user

    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


async def random_airport(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    airport = random.choice(airports)
    text = text_from_airport(airport)
    await update.message.reply_text(text)


async def countries_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Echo the user message."""
    reply_markup = countries_list_formatter(1)
    await update.message.reply_text("Please choose a country: ", reply_markup=reply_markup)

    return AIRPORTS


async def airports_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    # Show more countries or show airports
    if query.data.isdigit():
        reply_markup = countries_list_formatter(int(query.data))

        await query.edit_message_text("Please choose a country: ", reply_markup=reply_markup)
        return AIRPORTS
    else:
        context.user_data["country"] = query.data
        reply = f"Airports in {query.data}:\n"

        reply_markup = airports_list_formatter(1, query.data)
        await query.edit_message_text(text=reply, reply_markup=reply_markup)
        return AIRPORT_INFO


async def airport_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    reply = ''
    country = context.user_data["country"]

    if query.data.isdigit():
        reply_markup = airports_list_formatter(int(query.data), country)

        await query.edit_message_text(text=query.message.text, reply_markup=reply_markup)
        return AIRPORT_INFO
    else:
        local_airports = get_local_airports(country)

        for airport in local_airports:
            if airport["name"] == query.data:
                reply = text_from_airport(airport)

        await query.edit_message_text(text=reply)
        return -1


async def random_flight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    flights = fr_api.get_flights()
    flight = random.choice(flights)
    text = ''
    text += f'Flight number: {flight.registration}\n'
    text += f'From: {flight.origin_airport_iata}\n'
    text += f'To: {flight.destination_airport_iata}\n'
    text += f'Latitude: {flight.latitude}\n'
    text += f'Longitude: {flight.longitude}\n'
    text += f'Ground speed: {flight.ground_speed}'
    await update.message.reply_text(text)


async def random_airline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Retrieve the list of airlines
    airlines = fr_api.get_airlines()
    airline = random.choice(airlines)
    text = ''
    text += f'Name: {airline["Name"]}\n'
    text += f'Company code: {airline["Code"]}\n'
    text += f'ICAO: {airline["ICAO"]}'
    await update.message.reply_text(text)


async def top_destinations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    airports_ranking = flight_service.get_top_destinations()[:10]

    text = 'Top 10 destinations at the moment:\n'
    text += flight_service.format_airports_ranking(airports_ranking)

    await update.message.reply_text(text)


async def top_origins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    airports_ranking = flight_service.get_top_origins()[:10]

    text = 'Top 10 origins at the moment:\n'
    text += flight_service.format_airports_ranking(airports_ranking)

    await update.message.reply_text(text)


async def zones_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Echo the user message."""
    reply_markup = zones_list_formatter(1)
    await update.message.reply_text("Please choose a zone: ", reply_markup=reply_markup)
    return FLIGHTS


async def flights_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    # Show more countries or show airports
    if query.data.isdigit():
        reply_markup = zones_list_formatter(int(query.data))
        await query.edit_message_text("Please choose a zone: ", reply_markup=reply_markup)
        return FLIGHTS
    else:
        context.user_data["zone"] = query.data
        reply = f"Flights in {query.data}:\n"

        reply_markup = flights_list_formatter(1, query.data)
        await query.edit_message_text(text=reply, reply_markup=reply_markup)
        return FLIGHT_INFO


async def flight_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()
    reply = 'Your flight:\n'
    zone = context.user_data["zone"]

    if query.data.isdigit():
        reply_markup = flights_list_formatter(int(query.data), zone)
        await query.edit_message_text(text=query.message.text, reply_markup=reply_markup)
        return FLIGHT_INFO
    else:
        try:
            details = fr_api.get_flight_details(query.data)
            reply += f'id: {details["identification"]["id"]}\n'
            reply += f'arrival: {details["status"]["text"]} {details["airport"]["destination"]["timezone"]["abbr"]}\n'
            reply += f'aircraft: {details["aircraft"]["model"]["text"]}\n'
            reply += f'airline: {details["airline"]["name"]}\n'
            reply += f'origin: {details["airport"]["origin"]["name"]}' \
                     f' ({details["airport"]["origin"]["position"]["country"]["name"]})\n'
            reply += f'destination: {details["airport"]["destination"]["name"]} ' \
                     f'({details["airport"]["destination"]["position"]["country"]["name"]})\n'
        except:
            reply += "Data not found"

        await query.edit_message_text(text=reply)
        return -1


async def top_destinations_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    airports_ranking = flight_service.get_top_destinations()[:10]

    fig = plot_service.make_airports_ranking_chart(airports_ranking, 'Incoming flights')

    await update.message.reply_photo(plot_to_bytes(fig), flight_service.format_airports_ranking(airports_ranking))


async def top_origins_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    airports_ranking = flight_service.get_top_origins()[:10]

    fig = plot_service.make_airports_ranking_chart(airports_ranking, 'Outgoing flights')

    await update.message.reply_photo(plot_to_bytes(fig), flight_service.format_airports_ranking(airports_ranking))
