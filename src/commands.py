from FlightRadar24.api import FlightRadar24API
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ForceReply
from telegram.ext import ContextTypes

fr_api = FlightRadar24API()

countries = ['Italy', 'Spain', 'Denmark', 'Poland', 'Germany',
             'France', 'Portugal', 'Sweden', 'Finland',
             'China', 'Austria', 'Japan', 'Norway',
             'Switzerland', 'Netherlands', 'Brazil', 'Argentina']
countries_page = 1
countries_per_page = 4
max_number_of_pages = len(countries) // countries_per_page

airports_page = 1
airports_per_page = 4
airports = fr_api.get_airports()
local_airports = []

right_button = InlineKeyboardButton(">", callback_data="RIGHT")
left_button = InlineKeyboardButton("<", callback_data="LEFT")

AIRPORTS, AIRPORT_INFO = range(2)


# For navigating between countries list
def countries_list_formatter():
    keyboard = []

    for country in countries[(countries_page - 1) * countries_per_page:countries_page * countries_per_page]:
        keyboard.append([InlineKeyboardButton(country, callback_data=country)])

    reply_markup = add_arrows(keyboard, countries_page, max_number_of_pages)
    return reply_markup


# For navigating between airports list
def airports_list_formatter():
    keyboard = []

    for airport in local_airports[(airports_page - 1) * airports_per_page:airports_page * airports_per_page]:
        keyboard.append([InlineKeyboardButton(airport["name"], callback_data=airport["name"])])

    reply_markup = add_arrows(keyboard, airports_page, len(local_airports) // airports_per_page)
    return reply_markup


def add_arrows(keyboard, cur_page, max_page):
    if 1 < cur_page < max_page:
        keyboard.append([left_button, right_button])
    elif cur_page > 1:
        keyboard.append([left_button])
    else:
        keyboard.append([right_button])

    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


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


async def airport(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(airports[0])


async def countries_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    reply_markup = countries_list_formatter()
    await update.message.reply_text("Please choose a country: ", reply_markup=reply_markup)

    return AIRPORTS


async def airports_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()
    global countries_page

    # Show more countries or show airports
    if query.data == "RIGHT":
        countries_page += 1
        reply_markup = countries_list_formatter()

        await query.edit_message_text("Please choose a country: ", reply_markup=reply_markup)
        return AIRPORTS
    elif query.data == "LEFT":
        countries_page -= 1
        reply_markup = countries_list_formatter()

        await query.edit_message_text("Please choose a country: ", reply_markup=reply_markup)
        return AIRPORTS
    else:
        reply = f"Airports in {query.data}:\n"
        for airport in airports:
            if airport["country"] == query.data:
                local_airports.append(airport)

        reply_markup = airports_list_formatter()
        await query.edit_message_text(text=reply, reply_markup=reply_markup)
        return AIRPORT_INFO


async def airport_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    global countries_page
    global airports_page

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    if query.data == "RIGHT":
        airports_page += 1
        reply_markup = airports_list_formatter()

        await query.edit_message_text(text=query.message.text, reply_markup=reply_markup)
        return AIRPORT_INFO
    elif query.data == "LEFT":
        airports_page -= 1
        reply_markup = airports_list_formatter()

        await query.edit_message_text(text=query.message.text, reply_markup=reply_markup)
        return AIRPORT_INFO
    else:
        airports = fr_api.get_airports()
        reply = f"{query.data}\n"
        for airport in local_airports:
            if airport["name"] == query.data:
                reply += f'iata: {airport["iata"]}\n'
                reply += f'icao: {airport["icao"]}\n'
                reply += f'lat: {airport["lat"]}\n'
                reply += f'lon: {airport["lon"]}\n'
                reply += f'country: {airport["country"]}\n'
                reply += f'alt: {airport["alt"]}\n'

        countries_page = 1
        airports_page = 1
        local_airports.clear()

        await query.edit_message_text(text=reply)
        return -1
