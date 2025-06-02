"""
Send logs to telegram bot.
"""

import logging
from telegram_bot.main import application
from telegram_bot.utils import check_admin

# Set up logging for clean output
logger = logging.getLogger(__name__)

async def send_logs(msg):
    """Send logs to all admins, with retries and clean error logging."""
    admins = await check_admin()
    retries = 2
    if admins:
        for admin in admins:
            for attempt in range(1, retries + 1):
                try:
                    await application.bot.sendMessage(
                        chat_id=admin, text=msg, parse_mode="HTML"
                    )
                    break  # Success, exit retry loop
                except Exception as e:  # pylint: disable=broad-except
                    logger.warning(f"Attempt {attempt}: Failed to send message to admin {admin}: {e}")
                    if attempt == retries:
                        logger.error(f"Giving up after {retries} failed attempts to send message to admin {admin}.")
    else:
        logger.warning("No admins found to send logs.")
