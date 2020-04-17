import logging

import telegram
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from data import getFlightsByDay
from reply import createReply


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def start(update, context):
    update.message.reply_text("""
Hey!
Looking for a fly with Evrowings.       
Then let us start with the date you want to fly

Example: CGN,TXL,2020-12-12 
    """, parse_mode=telegram.ParseMode.MARKDOWN)

def echo(update, context):
    message = update.edited_message if (update.edited_message) else update.message
    #logger.info(message.text)
    
    #context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

    #destination, origin, date = message.text.split(',', 2)
    #if (len(destination) != 3 or len(origin) != 3):
    #    message.reply_text("use TLC to set the airports")
    #    return
    flights = getFlightsByDay()
    for flight in flights:
        #context.bot.send_message
        message.reply_text(createReply(flight))
    #update.message.reply_text(destination)
    #update.message.reply_text(origin)

def updateMsg(update, context):
    logger.info("update")

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def init():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("SET TOKEN HERE", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    #dp.add_handler(MessageHandler(Filters.update, updateMsg))

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