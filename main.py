import datetime
import re
import threading
import uuid
from multiprocessing.context import Process

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler, \
    CallbackQueryHandler
from config import TOKEN
import logging
from functions import get_iata, get_url, get_iata_be, get_city_by_coords
from chat_utils import *

# set russian locale
import locale

locale.setlocale(locale.LC_ALL, 'ru_RU')

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# State list
TYPING_DEPARTURE, \
TYPING_ARRIVAL, \
PARSE_CITY, \
CHOOSE_CITY_BUTTON, \
CITY_BUTTON, \
CHOOSE_CITY, \
CHOOSE_DATE, \
PARSE_DATE, \
SHOW_FLIGHTS, \
END_CONV = range(10)

_sync = {}

def start(update, context):
    user = update.message.from_user

    # cleanup lock state as finished
    if 'src' in context.user_data:
        del context.user_data['src']
    if 'dest' in context.user_data:
        del context.user_data['dest']
    if 'out_date' in context.user_data:
        del context.user_data['out_date']

    logger.info("User started interaction: %s (%s)", user.id, user.first_name)
    update.message.reply_text(
        "Привет, " + user.first_name + "! Введи город отправления или отправь свою геопозицию",
        reply_markup=kbrd_send_location()
    )
    return CHOOSE_CITY_BUTTON


def choose(update, context):
    _loc = update.message.location
    if _loc is not None:
        user = update.message.from_user
        logger.info(
            "Parsed coords for user %s (%s) are %f, %f",
            user.id, user.first_name, _loc.latitude, _loc.longitude
        )
        city = get_city_by_coords(_loc.latitude, _loc.longitude)
        context.user_data['src'] = city
        update.message.reply_text(
            "Твоей точкой отправления будет {}! Куда отправимся?".format(city['value']),
            reply_markup=ReplyKeyboardRemove()
        )
        return PARSE_CITY
    else:
        update.message.reply_text(
            "Хорошо, введи город отправления:",
            reply_markup=ReplyKeyboardRemove()
        )
        return PARSE_CITY


def parse_city(update, context):
    query = update.message.text

    # input validation
    if len(query) < 4:
        update.message.reply_text("Пожалуйста, сформулируйте запрос более подробно")
        return PARSE_CITY
    elif len(re.sub('[A-Za-zА-Яа-я-]+', '', query)) >= len(query) / 2 - 1:
        update.message.reply_text("Город введен некорректно :( Попробуй ещё раз!")
        return PARSE_CITY

    guesses = get_iata_be(query)

    if len(guesses) == 0:
        logger.info("Can't found city by query %s", query)
        update.message.reply_text("К сожалению, не могу найти такой город... Попробуем ещё раз?")
        update.message.reply_text(get_ch_city_text(context))
        return PARSE_CITY
    if len(guesses) == 1:
        logger.info("Found single city by query %s: %s", query, guesses[0]['value'])
        if "src" not in context.user_data:
            context.user_data['src'] = guesses[0]
            update.message.reply_text(
                "Отлично! Отправляемся из {} Куда отправимся?".format(guesses[0]['value'])
            )
            return PARSE_CITY
        else:
            if context.user_data['src']['id'] == guesses[0]['id']:
                update.message.reply_text("Выбери, пожалуйста, другой город")
                return PARSE_CITY
            context.user_data['dest'] = guesses[0]
            update.message.reply_text(
                "Замечательно! Летим в {} Теперь нужно выбрать дату вылета:".format(guesses[0]['value']),
                reply_markup=kbrd_pick_date()
            )
            return CHOOSE_DATE


    logger.info("Too many cities were found by query %s: %d", query, len(guesses))
    context.user_data['city_guesses'] = guesses
    update.message.reply_text(
        "Я нашел несколько городов по твоему запросу, выбери верный :)",
        reply_markup=kbrd_markup_for_correction(guesses)
    )
    return CHOOSE_CITY


def choose_city(update, context):
    text = update.message.text
    guess = next(filter(lambda g: g['value'] == text, context.user_data['city_guesses']), None)

    if guess is None or guess == NO_CORRECT_BUTTON:
        logger.info("User failed or refused to select city, text provided: %s", text)
        update.message.reply_text("Пожалуйста, попробуй ввести город снова")
        update.message.reply_text(
            get_ch_city_text(context),
            reply_markup=ReplyKeyboardRemove()
        )
        return PARSE_CITY

    # set src or dest and proceed
    logger.info("User selected %s city", guess['value'])
    if "src" not in context.user_data:
        context.user_data['src'] = guess
        update.message.reply_text(
            "Отлично! Куда отправимся?",
            reply_markup=ReplyKeyboardRemove()
        )
        return PARSE_CITY

    if context.user_data['src']['id'] == guess['id']:
        update.message.reply_text(
            "Выбери, пожалуйста, другой город (используй клавиатуру)",
            reply_markup=ReplyKeyboardRemove()
        )
        return PARSE_CITY
    context.user_data['dest'] = guess
    update.message.reply_text(
        "Замечательно! Теперь нужно выбрать дату вылета:",
        reply_markup=kbrd_pick_date()
    )
    return CHOOSE_DATE


def choose_date(update, context):
    text = update.message.text
    today = datetime.date.today()

    if text == TODAY_BUTTON:
        timedelta = 0
    elif text == TOMORROW_BUTTON:
        timedelta = 1
    elif text == DATOMORROW_BUTTON:
        timedelta = 2
    else:
        if text == CHOOSE_DATE_BUTTON:
            descr = "Хорошо, введи время вылета сам, как пример - {}, или даже так - {}"
        else:
            descr = "Такого времени я не знаю :/\nПопробуй ввести время вручную, например {} или {}"
        update.message.reply_text(
            descr.format(today.strftime("%d.%m.%Y"), today.strftime("%d.%m")),
            reply_markup=ReplyKeyboardRemove()
        )
        return PARSE_DATE

    update.message.reply_text(
        "Супер! Поищем билеты на {}... ".format(text.lower()),
        reply_markup=ReplyKeyboardRemove()
    )
    context.user_data['out_date'] = today + datetime.timedelta(days=timedelta)
    logger.info(
        "Parameter out_date set to %s",
        context.user_data['out_date'].strftime("%d.%m.%Y")
    )

    # start flight search in parallel
    _id = uuid.uuid1()
    _search = threading.Thread(target=find_flights_for_context, args=(update, context, _sync, _id,))
    _search.start()
    _search.join()

    if _id not in _sync:
        raise Exception("Search process was never finished")
    _result = _sync[_id]
    del _sync[_id]
    return _result


def parse_date(update, context):
    text = update.message.text
    decline_reason = "Не удалось прочитать введенную дату"

    try:
        dot_count = text.count('.')
        if dot_count == 2:
            p_date = datetime.datetime.strptime(text, "%d.%m.%Y").date()
        elif dot_count == 1:
            p_date = datetime.datetime.strptime(text, "%d.%m").date()
            p_date = p_date.replace(year=datetime.date.today().year)
        else:
            raise ValueError("Invalid date")

        if p_date < datetime.date.today():
            decline_reason = "Дата вылета не может быть в прошлом"
            raise Exception(decline_reason)

        context.user_data["out_date"] = p_date
        # start flight search in parallel
        _id = uuid.uuid1()
        _search = threading.Thread(target=find_flights_for_context, args=(update, context, _sync, _id,))
        _search.start()
        _search.join()

        if _id not in _sync:
            raise Exception("Search process was never finished")
        _result = _sync[_id]
        del _sync[_id]
        return _result
    except Exception as exc:
        # inform about exception and retry
        logger.error(exc)
        update.message.reply_text(
            "{} :(\nПожалуйста, попробуй ввести ее ещё раз:".format(decline_reason)
        )
        return PARSE_DATE


# lock user at the end of conversation
def end_conversation(update, context):
    update.message.reply_text("Спасибо за пользование нашим ботом!\nЧтобы начать новый поиск, введи /start!")
    return END_CONV


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    context.user_data = {}
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

            CHOOSE_CITY_BUTTON: [MessageHandler((Filters.text | Filters.location), choose, pass_user_data=True)],

            PARSE_CITY: [MessageHandler(Filters.text, parse_city, pass_user_data=True)],

            CHOOSE_CITY: [MessageHandler(Filters.text, choose_city, pass_user_data=True)],

            CHOOSE_DATE: [MessageHandler(Filters.text, choose_date, pass_user_data=True)],

            PARSE_DATE: [MessageHandler(Filters.text, parse_date, pass_user_data=True)],

            END_CONV: [MessageHandler(Filters.text, end_conversation, pass_user_data=True)]

        },

        fallbacks=[CommandHandler('cancel', cancel), MessageHandler(Filters.text, unknown)],

        allow_reentry=True

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
