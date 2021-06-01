import datetime
import logging
import time

import telegram
from telegram import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from functions import get_itineraries_be, filter_itineraries_be, total_price_for_ticket, get_address_from_coords, \
    get_iata_be

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# constants
from main import END_CONV

NO_CORRECT_BUTTON = "Нужного нет в списке"
TODAY_BUTTON = "Сегодня"
TOMORROW_BUTTON = "Завтра"
DATOMORROW_BUTTON = "Послезавтра"
CHOOSE_DATE_BUTTON = "Укажу дату вылета сам"
LOCATION_BUTTON = "Отправить свою локацию 🗺️"
FROMSELF_BUTTON = "Введу самостоятельно"


def kbrd_send_location():
    kbrd = [
        [KeyboardButton(LOCATION_BUTTON, request_location=True)],
        [KeyboardButton(FROMSELF_BUTTON)]
    ]
    return telegram.ReplyKeyboardMarkup(
        kbrd,
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_ch_city_text(context):
    if "src" not in context.user_data:
        return "Откуда отправляемся?"
    return "Куда летим?"


# produce a keyboard markup for CHOOSE_CITY action
# todo add country flags to it
def kbrd_markup_for_correction(guesses):
    kbrd = list(map(lambda guess: [KeyboardButton(guess['value'])], guesses))  # callback_data=guess
    kbrd.append([KeyboardButton(NO_CORRECT_BUTTON)])
    return telegram.ReplyKeyboardMarkup(
        kbrd,
        resize_keyboard=True,
        one_time_keyboard=True
    )


def kbrd_pick_date():
    kbrd = [
        [
            KeyboardButton(TODAY_BUTTON),
            KeyboardButton(TOMORROW_BUTTON),
            KeyboardButton(DATOMORROW_BUTTON)
        ],
        [KeyboardButton(CHOOSE_DATE_BUTTON)]
    ]
    return telegram.ReplyKeyboardMarkup(
        kbrd,
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_departure_flavor(dep_time):
    delta = dep_time.date() - datetime.date.today()

    if delta.days == 0:
        return "сегодня"
    elif delta.days == 1:
        return "завтра"
    elif delta.days == 2:
        return "послезавтра"

    return "через {} дней".format(delta.days)


def list_to_py_datetime(src):
    return datetime.datetime(src[0], src[1], src[2], src[3], src[4])


def get_itin_price(itin):
    price = total_price_for_ticket(itin)
    base_price = total_price_for_ticket(itin, 'baseCost')
    return "{} {} ({} {})".format(
        "RUB", price,
        "EUR", base_price  # itin['itin'][0]['currencyCode']
    )


def get_airport_flavor(airport):
    return "{} ({})".format(airport['name_RU'], airport['code'])


def get_itin_route(itin):
    accum = []
    for it in itin['itin']:

        src_txt = get_airport_flavor(it['source'])
        dst_txt = get_airport_flavor(it['destination'])

        if len(accum) == 0:
            accum.append(src_txt)
            accum.append(dst_txt)
        else:
            if accum[-1] != src_txt:
                accum.append(src_txt)
            accum.append(dst_txt)

    return "-".join(accum)


def get_itin_route_flavor(itin):
    itin_size = len(itin['itin'])
    if itin_size == 1:
        return "без пересадок"
    elif itin_size == 2:
        return "1 пересадка"
    else:
        # should not be more than 4 transfers
        return "{} пересадки".format(itin_size - 1)


def itin_to_btn(itin):
    text = "Купить билет {} - {} за {} {}".format(
        get_airport_flavor(itin['source']),
        get_airport_flavor(itin['destination']),
        "EUR",
        itin['baseCost']
    )
    return [InlineKeyboardButton(text, url=itin['bookingLink'])]


# defines rendering behavior to draw a single itinerary
def render_itinerary(itin, update):
    dep_time = list_to_py_datetime(itin['itin'][0]['departureTime'])
    arr_time = list_to_py_datetime(itin['itin'][-1]['arrivalTime'])
    src = itin['src']
    dst = itin['dst']
    c_src = itin['c_src']
    c_dst = itin['c_dst']

    m_text_template = """
{} - {}
Отправление {} ({})
Прибытие {}
Цена: {}
    
Маршрут: {} ({})
    """.format(
        src['name_RU'] + ', ' + c_src['name_RU'],
        dst['name_RU'] + ', ' + c_dst['name_RU'],
        dep_time.strftime("%c"),
        get_departure_flavor(dep_time),
        arr_time.strftime("%c"),
        get_itin_price(itin),
        get_itin_route(itin),
        get_itin_route_flavor(itin)
    )

    kbrd = list(map(itin_to_btn, itin['itin']))

    update.message.reply_text(
        m_text_template,
        reply_markup=InlineKeyboardMarkup(list(kbrd))
    )


# find flights for user-defined context and display it
def find_flights_for_context(update, context, _sync, _id):
    udata = context.user_data
    user = update.message.from_user
    logger.info("Searching flights for user %s (%s)", user.id, user.first_name)
    update.message.reply_text("Начинаю искать перелеты по твоему запросу...")

    try:
        raw_itins = get_itineraries_be(
            udata['src']['id'],
            udata['dest']['id'],
            udata['out_date'],
            udata['out_date']
        )
        logger.info("Found flights for user %s (%s)", user.id, user.first_name)
        logger.info("Found %d raw itineraries by user query", len(raw_itins))

        filt_itins = filter_itineraries_be(raw_itins)

        if len(filt_itins) == 0:
            update.message.reply_text("К сожалению, по указанному запросу перелетов не найдено :(")

        for itin in filt_itins:
            render_itinerary(itin, update)

    except Exception as exc:
        logger.error("Exception occurred during itinerary search", exc)
        # todo retry one time, then fail miserably

    # cleanup lock state as finished
    del context.user_data['src']
    del context.user_data['dest']
    del context.user_data['out_date']
    update.message.reply_text("Спасибо за пользование нашим ботом!\nЧтобы начать новый поиск, введи /start!")
    logger.info("Goodbye (END_CONV) for user %s (%s)", user.id, user.first_name)
    _sync[_id] = END_CONV
    return
