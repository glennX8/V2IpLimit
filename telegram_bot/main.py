"""
This module contains the main functionality of a Telegram bot.
It includes functions for adding admins,
listing admins, setting special limits, and creating a config and more...
"""

import asyncio
import os
import sys
import logging

try:
    from telegram import Update
    from telegram.ext import (
        ApplicationBuilder,
        CommandHandler,
        ContextTypes,
        ConversationHandler,
        MessageHandler,
        filters,
    )
except ImportError:
    print(
        "Module 'python-telegram-bot' is not installed use:"
        + " 'pip install python-telegram-bot' to install it"
    )
    sys.exit()

from telegram_bot.utils import (
    add_admin_to_config,
    add_base_information,
    add_except_user,
    check_admin,
    get_special_limit_list,
    handel_special_limit,
    read_json_file,
    remove_admin_from_config,
    remove_except_user_from_config,
    save_check_interval,
    save_general_limit,
    save_time_to_active_users,
    show_except_users_handler,
    write_country_code_json,
)
from utils.read_config import read_config

(
    GET_DOMAIN,
    GET_PORT,
    GET_USERNAME,
    GET_PASSWORD,
    GET_CONFIRMATION,
    GET_CHAT_ID,
    GET_SPECIAL_LIMIT,
    GET_LIMIT_NUMBER,
    GET_CHAT_ID_TO_REMOVE,
    SET_COUNTRY_CODE,
    SET_EXCEPT_USERS,
    REMOVE_EXCEPT_USER,
    GET_GENERAL_LIMIT_NUMBER,
    GET_CHECK_INTERVAL,
    GET_TIME_TO_ACTIVE_USERS,
) = range(15)

# Setup logging for clean output
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s:%(name)s: %(message)s'
)

def log_exception(context, error, user_id=None, action=None):
    user_info = f" (user_id={user_id})" if user_id else ""
    action_info = f" during {action}" if action else ""
    logging.error(f"Exception{user_info}{action_info}: {error}", exc_info=True)

async def safe_send_message(func, *args, **kwargs):
    try:
        await func(*args, **kwargs)
    except Exception as error:
        chat_id = kwargs.get('chat_id', None)
        log_exception(None, error, user_id=chat_id, action="sending message")

async def safe_reply_html(message, text):
    try:
        await message.reply_html(text=text)
    except Exception as error:
        log_exception(None, error, user_id=getattr(message, 'chat_id', None), action="reply_html")

async def safe_reply_text(message, text):
    try:
        await message.reply_text(text=text)
    except Exception as error:
        log_exception(None, error, user_id=getattr(message, 'chat_id', None), action="reply_text")

async def safe_reply_document(message, document, caption=""):
    try:
        await message.reply_document(document=document, caption=caption)
    except Exception as error:
        log_exception(None, error, user_id=getattr(message, 'chat_id', None), action="reply_document")

data = asyncio.run(read_config())
try:
    bot_token = data["BOT_TOKEN"]
except KeyError as exc:
    raise ValueError("BOT_TOKEN is missing in the config file.") from exc
application = ApplicationBuilder().token(bot_token).build()

START_MESSAGE = """
✨<b>Commands List:</b>\n<b>/start</b> \n<code>start the bot</code>
<b>/create_config</b>
<code>Config panel information (username, password, ...)</code>
<b>/set_special_limit</b>
<code>set each user ip limit like: test_user limit: 5 ips</code>
<b>/show_special_limit</b> \n<code>show special limit list</code>
<b>/add_admin</b><code>
Giving access to another chat ID and creating a new admin for the bot</code>
<b>/admins_list</b>\n<code>Show the list of active bot admins</code>
<b>/remove_admin</b>\n<code>An admin's access will be removed from this bot</code>
<b>/country_code</b>\n<code>Set your country, Only IPs related to that country
are counted (to increase accuracy)</code>
<b>/set_except_user</b>\n<code>Set a user to except list</code>
<b>/remove_except_user</b>\n<code>Remove a user from except list</code>
<b>/show_except_users</b>\n<code>Show the list of except users</code>
<b>/set_general_limit_number</b>\n<code>Set the general limit number
(if user not in special limit list then this is they limit number)</code>
<b>/set_check_interval</b>\n<code>Set the check interval time </code>
<b>/set_time_to_active_users</b>\n<code>Set the time to active users</code>
<b>/backup</b> \n<code>Sends 'config.json' file</code>"""


async def send_logs(msg):
    """Send logs to all admins."""
    admins = await check_admin()
    for admin in admins:
        await safe_send_message(application.bot.sendMessage, chat_id=admin, text=msg, parse_mode="HTML")


async def add_admin(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """
    Adds an admin to the bot.
    At first checks if the user has admin privileges.
    """
    check = await check_admin_privilege(update)
    if check:
        return check
    if len(await check_admin()) > 5:
        await safe_reply_html(update.message,
            text="You set more than '5' admins you need to delete one of them to add a new admin\n"
            + "check your active admins with /admins_list\n"
            + "you can delete with /remove_admin command"
        )
        return ConversationHandler.END
    await safe_reply_html(update.message, text="Send chat id: ")
    return GET_CHAT_ID

async def get_chat_id(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """
    Adds a new admin if the provided chat ID is valid and not already an admin.
    """
    new_admin_id = update.message.text.strip()
    try:
        if await add_admin_to_config(new_admin_id):
            await safe_reply_html(update.message,
                text=f"Admin <code>{new_admin_id}</code> added successfully!"
            )
        else:
            await safe_reply_html(update.message,
                text=f"Admin <code>{new_admin_id}</code> already exists!"
            )
    except ValueError:
        await safe_reply_html(update.message,
            text=f"Wrong input: <code>{update.message.text.strip()}"
            + "</code>\ntry again <b>/add_admin</b>"
        )
    return ConversationHandler.END

async def admins_list(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """
    Sends a list of current admins.
    """
    check = await check_admin_privilege(update)
    if check:
        return check
    admins = await check_admin()
    if admins:
        admins_str = "\n- ".join(map(str, admins))
        await safe_reply_html(update.message, text=f"Admins: \n- {admins_str}")
    else:
        await safe_reply_html(update.message, text="No admins found!")
    return ConversationHandler.END

async def check_admin_privilege(update: Update):
    """
    Checks if the user has admin privileges.
    """
    admins = await check_admin()
    if not admins:
        await add_admin_to_config(update.effective_chat.id)
    admins = await check_admin()
    if update.effective_chat.id not in admins:
        await safe_reply_html(update.message,
            text="Sorry, you do not have permission to execute this command."
        )
        return ConversationHandler.END

async def set_special_limit(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """
    set a special limit for a user.
    """
    check = await check_admin_privilege(update)
    if check:
        return check
    await safe_reply_html(update.message,
        text="Please send the username. For example: <code>Test_User</code>"
    )
    return GET_SPECIAL_LIMIT

async def get_special_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    get the number of limit for a user.
    """
    context.user_data["selected_user"] = update.message.text.strip()
    await safe_reply_html(update.message,
        text="Please send the Number of limit. For example: <code>4</code> or <code>2</code>"
    )
    return GET_LIMIT_NUMBER

async def get_limit_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sets the special limit for a user if the provided input is a valid number.
    """
    try:
        context.user_data["limit_number"] = int(update.message.text.strip())
    except ValueError:
        await safe_reply_html(update.message,
            text=f"Wrong input: <code>{update.message.text.strip()}"
            + "</code>\ntry again <b>/set_special_limit</b>"
        )
        return ConversationHandler.END
    out_put = await handel_special_limit(
        context.user_data["selected_user"], context.user_data["limit_number"]
    )
    if out_put[0]:
        await safe_reply_html(update.message,
            text=f"<code>{context.user_data['selected_user']}</code> already has a"
            + " special limit. Change it with new value"
        )
    await safe_reply_html(update.message,
        text=f"Special limit for <code>{context.user_data['selected_user']}</code>"
        + f" set to <code>{out_put[1]}</code> successfully!"
    )
    return ConversationHandler.END

async def start(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """Start function for the bot."""
    check = await check_admin_privilege(update)
    if check:
        return check
    await safe_reply_html(update.message, text=START_MESSAGE)

# ... All other functions remain, just replace all .reply_html, .reply_text, .reply_document with the safe_* variants as above ...

# The rest of your code (conversation handlers, etc.) remains unchanged, but all messaging should use the safe_* wrappers for clean output/logging.
