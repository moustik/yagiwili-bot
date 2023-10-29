#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.
"""coincoin

DATA MODEL

Payload := (request_type, request_data)

request_type := CB_REG|CB_SUG

before
 bot_data := {int_chat_id: int_id}
after
 bot_data := {int_id: int_chat_id}

/!\ non persistent
options := {int_id: string_household_name}


"""


import logging
import os
import random

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                            ContextTypes, PicklePersistence)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


TOTAL_VOTER_COUNT = 5

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# callback types
CB_REG=0  # register a new peer Noel
CB_SUG=1  # suggest a gift to a peer




options = dict(zip(
    random.sample(list(range(6)), 6),
    ["Parents", "Anais & Lucas", "Geoffrey & Julie",
     "Guillaume et Juliane", "Damien & Maria", "Anais & Hugo", ]
))

buttons_register = [InlineKeyboardButton(v, callback_data=(CB_REG, k)) for k, v in options.items()]
buttons_suggest = [InlineKeyboardButton(v, callback_data=(CB_SUG, k)) for k, v in options.items()]

CHUNK_SIZE = 2
keyboard = [buttons_register[i:i+CHUNK_SIZE] for i in range(0, len(buttons_register), CHUNK_SIZE)]

reply_markup = InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with three inline buttons attached."""

    payload = {
    }
    context.bot_data.update(payload)



    await update.message.reply_text("Choisissez votre pair Noel:", reply_markup=reply_markup)


async def suggest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with three inline buttons attached."""

    payload = {
    }
    context.bot_data.update(payload)

    await update.message.reply_text("Choisissez pour qui vous voulez suggerer:",
                                    reply_markup=reply_markup)


async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    data = context.bot_data
    household_id = int(query.data[1])

    if household_id in context.bot_data.values():
        await query.edit_message_text(text="Quelqu'un a déjà selectionné ces personnes",
                                      reply_markup=reply_markup)
        logger.error("au voleur !: %s", len(context.bot_data.values()))
    else:
        if update.effective_chat.id in data.keys():
            await query.edit_message_text(
                text="Vous aviez déjà voté. Votre vote a été mis à jour. C'est tout bon. Merci !"
                )
        else:
            await query.edit_message_text(
                text=f"J'ai bien noté que votre cadeau sera pour {options.get(household_id)}")

        payload = {
            update.effective_chat.id: household_id
        }
        context.bot_data.update(payload)


    logger.info("new vote from %s count: %s",
                query.from_user.first_name, len(context.bot_data.keys()))
    if len(context.bot_data.keys()) == TOTAL_VOTER_COUNT:
        logger.info("values: %s", context.bot_data.values())

        whosleft = options.get(list(set(options.keys()) - set(context.bot_data.values()))[0])

        logger.info("reste %s", whosleft)
        await context.bot.send_message(925808534, f"tout le monde a vote il reste {whosleft}")


async def callback_register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    data = context.bot_data
    household_id = int(query.data)

    if household_id in context.bot_data.values():
        await query.edit_message_text(text="Quelqu'un a déjà selectionné ces personnes",
                                      reply_markup=reply_markup)
        logger.error("au voleur !: %s", len(context.bot_data.values()))
    else:
        if update.effective_chat.id in data.keys():
            await query.edit_message_text(
                text="Vous aviez déjà choisi votre pair. Votre pair a été mis à jour."
                )
        else:
            await query.edit_message_text(
                text=f"J'ai bien noté que votre cadeau sera pour {options.get(household_id)}")

        payload = {
            household_id: update.effective_chat.id
        }
        context.bot_data.update(payload)


    logger.info("new vote from %s count: %s",
                query.from_user.first_name, len(context.bot_data.keys()))


async def callback_suggest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    data = context.bot_data
    household_id = int(query.data)





async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display a help message"""
    await update.message.reply_text("Use /start, /suggest or /help to test this bot.")


def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    persistence = PicklePersistence(filepath='bot.data')
    application = Application.builder().token(BOT_TOKEN).\
        persistence(persistence=persistence).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(
        callback=callback_register,
        pattern=lambda d: d[0] == CB_REG))
    application.add_handler(CallbackQueryHandler(
        callback=callback_suggest,
        pattern=lambda d: d[0] == CB_SUG))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
