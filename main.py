from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler
from config import TOKEN
import logging
from functions import get_iata, get_url

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TYPING_DEPARTURE, TYPING_ARRIVAL = range(2)


def start(update, context):
    user = update.message.from_user
    logger.info("User %s has said that her name %s.", user.first_name)
    update.message.reply_text("Привет, " + user.first_name + "! Введи город отправления")
    return TYPING_DEPARTURE


def input_departure(update, departure_iata):
    user = update.message.from_user
    departure_city = update.message.text
    city = get_iata(departure_city) #MOW
    if city is None:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Кажется, я не знаю этот город. Может быть вы выберете другой город поблизости?")
        logger.info("User %s  has sent an incorrect departure city %s.", user.first_name, departure_city)
        return TYPING_DEPARTURE
    departure_iata = city
    logger.info("User %s has sent a departure city %s.", user.first_name, departure_city)
    update.message.reply_text(f'{user.first_name}, город вылета - {departure_city}, код аэропорта - {departure_iata}. Введите город прилета.')
    return TYPING_ARRIVAL


def input_arrival(update, arrival_iata):
    user = update.message.from_user
    arrival_city = update.message.text #HSE
    city = get_iata(arrival_city)
    if city is None:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Похоже, я не знаю этот город. Может быть вы выберете другой город поблизости?")
        logger.info("User %s  has sent an incorrect destination %s.", user.first_name, arrival_city)
        return TYPING_ARRIVAL
    arrival_iata = city
    logger.info("User %s has sent a destination city %s.", user.first_name, arrival_city)
    update.message.reply_text(f'{user.first_name}, Введите дату поездки через "-" (2010-01-31)')
    return TYPING_DEPARTURE


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('До свидания.\n'
                              'Отправьте /start, чтобы снова начать разговор.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(update, error, _: CommandHandler):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def unknown(update, context):
    logger.warning('Update "%s" is unknown', update.message.text)
    bot.send_message(chat_id=update.message.chat_id,
                     text="Извините, не совсем вас понимаю. Не могли бы вы сформулировать по-другому?")


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={

            TYPING_DEPARTURE: [MessageHandler(Filters.text, input_departure, pass_user_data=True)],

            TYPING_ARRIVAL: [MessageHandler(Filters.text, input_arrival, pass_user_data=True)],
        },

        fallbacks=[CommandHandler('cancel', cancel), MessageHandler(Filters.text, unknown)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
