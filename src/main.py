import asyncio
import logging
import os
from dotenv import load_dotenv
from bot import build_bot, start_webhook, start_pooling

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def main() -> None:
    application = build_bot()

    if os.getenv("BOT_USE_WEBHOOK") == "true":
        asyncio.run(start_webhook(application))
    else:
        start_pooling(application)


if __name__ == "__main__":
    main()
