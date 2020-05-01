#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

import telegram
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from data import get_flights_by_day, fetch_weeks, fetch_stations, fetch_destination_stations
from reply import create_replay
from values import TELEGRAM_BOT_TOKEN

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

ORIGIN, DESTINATION, WEEK, FLIGHTS = range(4)
ORIGIN_QUERY, DESTINATION_QUERY = range(2)

DEPARTURE_CONV_BTN_DEST, DEPARTURE_CONV_BTN_CHANGE = range(2)


def help(update, context):
    help_msg = """
Commands:
*/weekplanner* 
    """
    update.message.reply_text(help_msg, parse_mode=telegram.ParseMode.MARKDOWN)


def start(update, context):
    update.message.reply_text(
        """Welcome to Eurowings Telegram Info Bot\. You can lookup for the following information
*\/weekplanner* 
To display all possible services use
*\/help* commnand
        """, parse_mode=telegram.ParseMode.MARKDOWN_V2)


def select_origin(update, context):
    update.message.reply_text("Enter the TLC or a airport name(at least three letters)")
    return ORIGIN_QUERY


def find_origin(update, context):
    stations = fetch_stations(update.message.text)
    reply_keyboard = []
    for station in stations:
        reply_keyboard.append(
            [InlineKeyboardButton(text=f"{station['label']}", callback_data=f"{station['label']},{station['value']}")])

    update.message.reply_text(f"Stations found:", reply_markup=InlineKeyboardMarkup(reply_keyboard))
    return ORIGIN_QUERY


def station_btn_callback(update, context):
    query = update.callback_query
    # persist user chose
    context.user_data['departure'] = query.data
    query.answer()

    # show user next steps
    reply_keyboard = [[InlineKeyboardButton('Change departure', callback_data=str(DEPARTURE_CONV_BTN_CHANGE))],
                      [InlineKeyboardButton('Select destination', callback_data=str(DEPARTURE_CONV_BTN_DEST))]]

    query.message.reply_text(f"Your departure station is {query.data}. What you would like to do next?",
                             reply_markup=InlineKeyboardMarkup(reply_keyboard))
    return DESTINATION_QUERY


def departure_buttons(update, context):
    query = update.callback_query
    query.answer()

    if query.data == str(DEPARTURE_CONV_BTN_DEST):
        query.edit_message_text("Enter the destination station TLC or a airport name(at least three letters)")
    else:
        query.edit_message_text("not implemented now")


def find_destination(update, context):
    query = update.message.text
    departure = context.user_data['departure']

    update.message.reply_text(f"departure={departure}, destination query={query}")
    # stations = fetch_destination_stations(origin)
    # reply_keyboard = []
    # for station in stations:
    #     # reply_keyboard.append([f"{station['label']}"])
    #     reply_keyboard.append([InlineKeyboardButton(text=f"{station['label']}", callback_data=station['value'])])
    # update.message.reply_text(f"Select origin",
    #                           reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
    #                                                            one_time_keyboard=True))


def week_planner(update, context):
    reply_keyboard = [['CGN', 'HAM', 'STR']]
    update.message.reply_text("""
Hey!
Looking for a fly with Eurowings.       
Then let us start with the origin station you want to fly from
        """, parse_mode=telegram.ParseMode.MARKDOWN,
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return ORIGIN


def origin(update, context):
    origin_station = update.message.text
    context.user_data['origin'] = origin_station
    reply_keyboard = [['STR', 'HAM', 'TXL']]
    update.message.reply_text(f'Alright, you want a fly from {origin_station} to:',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))

    return DESTINATION


def select_week(update, context):
    destination = update.message.text
    context.user_data['destination'] = destination
    origin = context.user_data['origin']
    weeks = fetch_weeks(origin, destination)
    reply_keyboard = []
    for week in weeks:
        reply_keyboard.append([f"{week['fromDateString']} {week['toDateString']}"])
    update.message.reply_text("You,ve choose flight %s-%s. "
                              "Next select the week you want flight at." % (context.user_data['origin'], destination),
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return WEEK


def week(update, context):
    week = update.message.text
    context.user_data['week'] = week
    update.message.reply_text(f"You select the week on {week}")
    flights(update, context)
    # return FLIGHTS


def flights(update, context):
    origin = context.user_data['origin']
    destination = context.user_data['destination']
    week_days = context.user_data['week'].split(' ')

    logger.info("user select origin=%s and destination=%s", origin, destination)

    flights = get_flights_by_day(origin, destination, week_days[0], week_days[1])
    # TODO short list used for testing
    for flight in flights[:3]:
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

    conv_select_route = ConversationHandler(
        entry_points=[CommandHandler('origin', select_origin)],

        states={
            ORIGIN_QUERY: [MessageHandler(Filters.text, find_origin), CallbackQueryHandler(station_btn_callback)],
            # ORIGIN_RESULT: [MessageHandler(Filters.text, find_origin),
            #                CallbackQueryHandler(station_btn_callback)],
            DESTINATION_QUERY: [MessageHandler(Filters.text, find_destination),
                                CallbackQueryHandler(departure_buttons)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('weekplanner', week_planner)],

        states={
            ORIGIN: [MessageHandler(Filters.text, origin)],

            DESTINATION: [MessageHandler(Filters.text, select_week)],

            WEEK: [MessageHandler(Filters.text, week)],
            #           CommandHandler('skip', skip_location)],

            FLIGHTS: [MessageHandler(Filters.text, flights)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(conv_select_route)

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # dp.add_handler(CallbackQueryHandler(departure_buttons))

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
