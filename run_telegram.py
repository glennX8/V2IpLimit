"""Run the telegram bot."""

import asyncio
import logging

from telegram_bot.main import application

# Configure logging for clean, informative output
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s:%(name)s: %(message)s'
)

async def run_telegram_bot():
    """Run the telegram bot."""
    while True:
        try:
            async with application:
                await application.start()
                await application.updater.start_polling()
                while True:
                    await asyncio.sleep(40)
        except Exception as e:  # pylint: disable=broad-except
            logging.error(f"Unhandled exception in telegram bot: {e}", exc_info=True)
            await asyncio.sleep(5)  # Prevents tight restart loop if persistent error

if __name__ == "__main__":
    asyncio.run(run_telegram_bot())
