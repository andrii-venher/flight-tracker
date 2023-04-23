import random
from FlightRadar24.api import FlightRadar24API
from telegram import Update
from telegram.ext import ContextTypes

from common import text_from_airport, plot_to_bytes, map_plot_to_bytes, text_from_seconds
from services import flight_service, plot_service, markup_service
from services.markup_service import AIRPORTS, AIRPORT_INFO, FLIGHTS, FLIGHT_INFO

fr_api = FlightRadar24API()

airports = fr_api.get_airports()


async def unknown_command_echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Unknown command: " + update.message.text)


async def random_airport(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    airport = random.choice(airports)
    text = text_from_airport(airport)
    await update.message.reply_text(text)


async def search_airport(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_markup = markup_service.countries_list_formatter(1)
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
        reply_markup = markup_service.countries_list_formatter(int(query.data))

        await query.edit_message_text("Please choose a country: ", reply_markup=reply_markup)
        return AIRPORTS
    else:
        context.user_data["country"] = query.data
        reply = f"Airports in {query.data}:\n"

        reply_markup = markup_service.airports_list_formatter(1, query.data)
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
        reply_markup = markup_service.airports_list_formatter(int(query.data), country)

        await query.edit_message_text(text=query.message.text, reply_markup=reply_markup)
        return AIRPORT_INFO
    else:
        local_airports = markup_service.get_local_airports(country)

        for airport in local_airports:
            if airport["name"] == query.data:
                reply = text_from_airport(airport)

        await query.edit_message_text(text=reply)
        return -1


async def random_flight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    flights = fr_api.get_flights()
    flights = list(filter(lambda f: f.origin_airport_iata != 'N/A' and f.destination_airport_iata != 'N/A', flights))
    selected_flights = []
    chunks = update.message.text.split(' ')
    if len(chunks) == 1:
        selected_flights.append(random.choice(flights))
    elif len(chunks) == 2 and chunks[1].isdigit() and int(chunks[1]) > 0:
        selected_flights.extend(random.sample(flights, int(chunks[1])))
    for selected_flight in selected_flights:
        await update.message.reply_text(flight_service.format_flight(selected_flight))
    if len(selected_flights) > 1:
        ids = list(map(lambda f: f.id, selected_flights))
        await update.message.reply_text(f"IDs: {' '.join(ids)}")


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


async def top_airlines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    flights = fr_api.get_flights()
    top_airlines = flight_service.top_air(flights)
    text = 'Top 10 airlines by the number of flights at the moment:\n'
    text += flight_service.format_airlines_ranking(top_airlines)

    await update.message.reply_text(text)


async def search_flight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Echo the user message."""
    reply_markup = markup_service.zones_list_formatter(1)
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
        reply_markup = markup_service.zones_list_formatter(int(query.data))
        await query.edit_message_text("Please choose a zone: ", reply_markup=reply_markup)
        return FLIGHTS
    else:
        context.user_data["zone"] = query.data
        reply = f"Flights in {query.data}:\n"

        reply_markup = markup_service.flights_list_formatter(1, query.data)
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
        reply_markup = markup_service.flights_list_formatter(int(query.data), zone)
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


async def top_airlines_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    flights = fr_api.get_flights()
    airlines_ranking = flight_service.top_air(flights)
    fig = plot_service.make_airline_ranking_chart(airlines_ranking, "Total flights")
    await update.message.reply_photo(plot_to_bytes(fig), flight_service.format_airlines_ranking(airlines_ranking))


async def get_aircraft_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chunks = update.message.text.split(' ')
        if len(chunks) < 2:
            await update.message.reply_text("Please provide flight ID.")
            return
        flight_id = chunks[1]
        details = fr_api.get_flight_details(flight_id)

        await update.message.reply_photo(details['aircraft']['images']['large'][0]['src'],
                                         details['aircraft']['model']['text'])
    except:
        await update.message.reply_text("Data not found")


async def flight_by_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chunks = update.message.text.split(' ')
        if len(chunks) < 2:
            await update.message.reply_text("Please provide flight ID.")
            return
        flight_id = chunks[1]
        flight = flight_service.get_flight_by_id(flight_id)
        text = flight_service.format_flight(flight)
        await update.message.reply_text(text)
    except:
        await update.message.reply_text("Data not found")


async def get_flight_map(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chunks = update.message.text.split(' ')
        if len(chunks) < 2:
            await update.message.reply_text("Please provide flight ID.")
            return
        flight_id = chunks[1]
        details = fr_api.get_flight_details(flight_id)
        plot = plot_service.make_flight_map(details)
        await update.message.reply_photo(map_plot_to_bytes(plot),
                                         f"From {details['airport']['origin']['name']} to {details['airport']['destination']['name']}")
    except:
        await update.message.reply_text("Data not found")


async def airline_by_icao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chunks = update.message.text.split(' ')
        if len(chunks) < 2:
            await update.message.reply_text("Please provide airline ICAO.")
            return
        airline_icao = chunks[1]
        airline = flight_service.air_by_icao(airline_icao)
        text = flight_service.format_icao(airline)
        await update.message.reply_text(text)
    except:
        await update.message.reply_text("Data not found")


async def airport_by_icao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chunks = update.message.text.split(' ')
        if len(chunks) < 2:
            await update.message.reply_text("Please provide airport ICAO.")
            return
        airport_icao = chunks[1]
        airport = flight_service.airp_by_icao(airport_icao)
        text = text_from_airport(airport)
        await update.message.reply_text(text)
    except:
        await update.message.reply_text("Data not found")


async def airport_by_iata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chunks = update.message.text.split(' ')
        if len(chunks) < 2:
            await update.message.reply_text("Please provide airport IATA.")
            return
        airport_iata = chunks[1]
        airport = flight_service.airp_by_iata(airport_iata)
        text = text_from_airport(airport)
        await update.message.reply_text(text)
    except:
        await update.message.reply_text("Data not found")


async def is_delayed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chunks = update.message.text.split(' ')
        if len(chunks) < 2:
            await update.message.reply_text("Please provide flight ID.")
            return
        flight_id = chunks[1]
        diff = flight_service.is_flight_delayed(flight_id)
        if diff is None:
            await update.message.reply_text("Data not found")
        elif diff == 0:
            await update.message.reply_text("The flight arrives on time")
        else:
            if diff > 0:
                await update.message.reply_text(f"The flight is delayed by {text_from_seconds(diff)}")
            elif diff < 0:
                await update.message.reply_text(f"The flight will arrive earlier by {text_from_seconds(-diff)}")
    except:
        await update.message.reply_text("Data not found")


async def is_delayed_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chunks = update.message.text.split(' ')
        if len(chunks) < 3 or len(chunks) > 21:
            await update.message.reply_text("Please provide at least 2 and at most 20 flight IDs.")
            return
        # Ignore command chunk
        flight_ids = list(dict.fromkeys(chunks[1:]))
        # Filter out invalid IDs
        flight_ids = list(filter(lambda c: len(c) == 8, flight_ids))
        diffs = []
        for flight_id in flight_ids:
            diff = flight_service.is_flight_delayed(flight_id)
            if diff is None:
                await update.message.reply_text(f"Invalid flight ID: {flight_id}")
                return
            diffs.append(diff // 60)
        fig = plot_service.make_delayed_chart(flight_ids, diffs)
        await update.message.reply_photo(plot_to_bytes(fig))
    except:
        await update.message.reply_text("Data not found")
