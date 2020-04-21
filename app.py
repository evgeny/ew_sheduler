#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

import telegram
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from data import get_flights_by_day
from reply import create_replay
from values import TELEGRAM_BOT_TOKEN

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

ORIGIN, DESTINATION, WEEK, FLIGHTS = range(4)


def start(update, context):
    reply_keyboard = [['CGN', 'HAM', 'STR']]
    update.message.reply_text("""
    Hey!
    Looking for a fly with Evrowings.       
    Then let us start with the origin station you want to fly from
    """, parse_mode=telegram.ParseMode.MARKDOWN,
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return ORIGIN


def echo(update, context):
    message = update.edited_message if update.edited_message else update.message
    # logger.info(message.text)

    # context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

    # markup = telegram.ReplyKeyboardMarkup([[telegram.KeyboardButton(text="Heyyy-%d" % getFakeId())]])
    # message.reply_text("""hey""", parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=markup)
    flights = get_flights_by_day("CGN", "BER", "2020-11-16", "2020-11-22")
    for flight in flights:
        message.reply_text(create_replay(flight))


def origin(update, context):
    origin_station = update.message.text
    context.user_data['origin'] = origin_station
    reply_keyboard = [['STR', 'HAM', 'TXL']]
    update.message.reply_text(f'Alright, you want a fly from {origin_station} to:',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return DESTINATION


def destination(update, context):
    destination = update.message.text
    context.user_data['destination'] = destination
    reply_keyboard = [['2020-11-16 2020-11-22', '2020-11-16 2020-11-22', '2020-11-16 2020-11-22']]
    update.message.reply_text("You,ve choose flight %s-%s"
                              "Next select the week you want flight at." % (context.user_data['origin'], destination),
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return WEEK


def week(update, context):
    week = update.message.text
    context.user_data['week'] = week

    update.message.reply_text(f"You select the week on {week}")
    flights(update, context)
    #return FLIGHTS


def flights(update, context):
    origin = context.user_data['origin']
    destination = context.user_data['destination']

    logger.info("user select origin=%s and destination=%s", origin, destination)

    flights = get_flights_by_day(origin, destination, "2020-11-16", "2020-11-22")
    for flight in flights:
        update.message.reply_text(create_replay(flight))


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! Thank you for yousing our service.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def init():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            ORIGIN: [MessageHandler(Filters.text, origin)],

            DESTINATION: [MessageHandler(Filters.text, destination)],

            WEEK: [MessageHandler(Filters.text, week)],
            #           CommandHandler('skip', skip_location)],

            FLIGHTS: [MessageHandler(Filters.text, flights)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # on different commands - answer in Telegram
    # dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    init()
