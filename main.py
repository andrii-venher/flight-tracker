import os

from dotenv import load_dotenv

load_dotenv()

from FlightRadar24.api import FlightRadar24API

fr_api = FlightRadar24API()

airports = fr_api.get_airports()

#Countires info
countries = ['Italy', 'Spain', 'Denmark', 'Poland', 'Germany', 'France', 'Portugal', 'Sweden', 'Finland', 'China', 'Austria', 'Japan']
countries_page = 1
countries_per_page = 3
max_number_of_pages = len(countries)//countries_per_page

import logging

from telegram import __version__ as TG_VER
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, ConversationHandler

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

#Conversation Handler values
AIRPORTS, AIRPORT_INFO = range(2)

# For navigating between countries pages
def countries_list_formatter():
    keyboard = []
    
    for country in countries[(countries_page-1)*countries_per_page:countries_page*countries_per_page]:
        keyboard.append([InlineKeyboardButton(country, callback_data=country)])
        
    keyboard.append([InlineKeyboardButton("<", callback_data="LEFT"), InlineKeyboardButton(">", callback_data="RIGHT")])
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
    airports = fr_api.get_airports()
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

    #Show more countries or show airports
    if query.data == "RIGHT":
        if countries_page < max_number_of_pages:
            countries_page += 1
            reply_markup = countries_list_formatter()
            await query.edit_message_text("Please choose a country: ", reply_markup=reply_markup)

        return AIRPORTS
    elif query.data == "LEFT":
        if countries_page > 1:
            countries_page -= 1
            reply_markup = countries_list_formatter()
            await query.edit_message_text("Please choose a country: ", reply_markup=reply_markup)

        return AIRPORTS
    else:
        keyboard = []
        airports = fr_api.get_airports()
        reply = f"Airports in {query.data}:\n"
        for airport in airports:
            if airport["country"] == query.data:
                keyboard.append([InlineKeyboardButton(airport["name"], callback_data=airport["name"])])

        reply_markup = InlineKeyboardMarkup(keyboard[:5])
            
        await query.edit_message_text(text=reply, reply_markup=reply_markup)

        return AIRPORT_INFO

async def airport_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    global countries_page

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    airports = fr_api.get_airports()
    reply = f"{query.data}\n"
    for airport in airports:
        if airport["name"] == query.data:
            reply += f'iata: {airport["iata"]}\n'
            reply += f'icao: {airport["icao"]}\n'
            reply += f'lat: {airport["lat"]}\n'
            reply += f'lon: {airport["lon"]}\n'
            reply += f'country: {airport["country"]}\n'
            reply += f'alt: {airport["alt"]}\n'

    countries_page = 1
    await query.edit_message_text(text=reply)
    
    return -1

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.getenv("BOT_TOKEN")).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start),
                      CommandHandler("help", help_command),
                      CommandHandler("airport", airport),
                      CommandHandler("airports", countries_list)],
        states={
            AIRPORTS: [CallbackQueryHandler(airports_list)],
            AIRPORT_INFO: [CallbackQueryHandler(airport_info)]
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # on different commands - answer in Telegram
    application.add_handler(conv_handler)

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()
