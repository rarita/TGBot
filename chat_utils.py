import time

import telegram
from telegram import KeyboardButton

from main import *

# constants
NO_CORRECT_BUTTON = "Нужного нет в списке"
TODAY_BUTTON = "Сегодня"
TOMORROW_BUTTON = "Завтра"
DATOMORROW_BUTTON = "Послезавтра"
CHOOSE_DATE_BUTTON = "Укажу дату вылета сам"


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


# defines rendering behavior to draw a single itinerary
def itinerary_renderer(itin):
    return


# sends messages to user representing found flights
def render_flights_data(update, context):
    return


# find flights for user-defined context and display it
def find_flights_for_context(update, context):
    update.message.reply_text("Начинаю искать перелеты по твоему запросу...")
    time.sleep(2.5)

    # cleanup lock state as finished
    del context.user_data['src']
    del context.user_data['dest']
    del context.user_data['out_date']
    update.message.reply_text("Спасибо за пользование нашим ботом!\nЧтобы начать новый поиск, введи /start!")
    return END_CONV
