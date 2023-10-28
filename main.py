#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, PicklePersistence

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


TOTAL_VOTER_COUNT = 5

BOT_TOKEN = os.environ("BOT_TOKEN")

"""
async def init_cadeaux(update, context):
    msg = 'Hello *{}*'.format(update.message.from_user.first_name)

    reply_keyboard = [[telegram.InlineKeyboardButton('@avtu_bot {}'.format(n), callback_data="k_light_on")] for n in nearest_sts]
    await update.message.reply_text(text=msg, parse_mode='Markdown',
                                    reply_markup=telegram.InlineKeyboardMarkup(reply_keyboard))

    await update.message.reply_text(str(update.message.from_user.id))
"""
import  random


options = dict(zip(
    random.sample(list(range(6)), 6),
    ["Parents", "Anais & Lucas", "Geoffrey & Julie", "Guillaume et Juliane", "Damien & Maria", "Anais & Hugo", ]
))

buttons = [InlineKeyboardButton(v, callback_data=k) for k, v in options.items()]

chunk_size = 2
keyboard = [buttons[i:i+chunk_size] for i in range(0, len(buttons), chunk_size)]

reply_markup = InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with three inline buttons attached."""

    payload = {
    }
    context.bot_data.update(payload)



    await update.message.reply_text("Choisissez:", reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    data = context.bot_data
    resp = int(query.data)

    if resp in context.bot_data.values():
        await query.edit_message_text(text=f"Quelqu'un a déjà selectionné ces personnes",
                                      reply_markup=reply_markup)
        logger.error(f"au voleur !: {len(context.bot_data.values())}")
    else:
        if update.effective_chat.id in data.keys():
            await query.edit_message_text(text=f"Vous aviez déjà voté mais votre vote a été mis à jour. C'est tout bon. Merci !")
        else:
            await query.edit_message_text(text=f"J'ai bien noté que votre cadeau sera pour {options.get(resp)}")

        payload = {
            update.effective_chat.id: int(query.data)
        }
        context.bot_data.update(payload)


    logger.info(f"new vote from {query.from_user.first_name} count: {len(context.bot_data.keys())}")
    if len(context.bot_data.keys()) == TOTAL_VOTER_COUNT:
        logger.info(f"values: {context.bot_data.values()}")

        whosleft = options.get(list(set(options.keys()) - set(context.bot_data.values()))[0])

        logger.info(f"reste {whosleft}")
        await context.bot.send_message(925808534, f"tout le monde a vote il reste {whosleft}")
        pass




async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display a help message"""
    await update.message.reply_text("Use /quiz, /poll or /preview to test this bot.")


def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    persistence = PicklePersistence(filepath='bot.data')
    application = Application.builder().token(BOT_TOKEN).persistence(persistence=persistence).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
