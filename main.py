import telebot
from currency_converter import CurrencyConverter
import requests
from telebot import types

# Телеграм-бот
bot = telebot.TeleBot("7184733237:AAFQmbAYC6egQD0JeDnzHrmWo04uSo-dDeE")
currency = CurrencyConverter()
amount = 0

# API для конвертації валют
API_KEY = '91548e41c1d0a0326fb29017'
BASE_URL = 'https://v6.exchangerate-api.com/v6'

def get_exchange_rate(api_key, base_currency, target_currency):
    url = f"{BASE_URL}/{api_key}/latest/{base_currency}"
    response = requests.get(url)
    data = response.json()
    if data['result'] == 'success':
        return data['conversion_rates'][target_currency]
    else:
        raise Exception('API request failed with message: ' + data['error-type'])

def convert_currency(api_key, amount, base_currency, target_currency):
    rate = get_exchange_rate(api_key, base_currency, target_currency)
    return amount * rate

# Обробник стартової команди
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Привіт, введіть суму")
    bot.register_next_step_handler(message, summa)

# Обробник введення суми
def summa(message):
    global amount
    try:
        amount = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, "Невірний формат. Впишіть суму")
        bot.register_next_step_handler(message, summa)
        return

    if amount > 0:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("USD/EUR", callback_data="usd/eur")
        btn2 = types.InlineKeyboardButton("EUR/USD", callback_data="eur/usd")
        btn3 = types.InlineKeyboardButton("USD/GBP", callback_data="usd/gbp")
        btn4 = types.InlineKeyboardButton("Друге значення", callback_data="else")
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, "Виберіть кілька валют", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Число має бути більшим за 0. Впишіть суму")
        bot.register_next_step_handler(message, summa)

# Обробник натискання кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data != "else":
        values = call.data.upper().split("/")
        res = convert_currency(API_KEY, amount, values[0], values[1])
        bot.send_message(call.message.chat.id, f"Виходить: {round(res, 2)}. Можете заново вписати суму")
        bot.register_next_step_handler(call.message, summa)
    else:
        bot.send_message(call.message.chat.id, "Введіть пару значень через слеш")
        bot.register_next_step_handler(call.message, my_currency)

# Обробник введення власних значень
def my_currency(message):
    try:
        values = message.text.upper().split("/")
        res = convert_currency(API_KEY, amount, values[0], values[1])
        bot.send_message(message.chat.id, f"Виходить: {round(res, 2)}. Можете заново вписати суму")
        bot.register_next_step_handler(message, summa)
    except Exception:
        bot.send_message(message.chat.id, "Щось не так. Впишіть значення заново")
        bot.register_next_step_handler(message, my_currency)

bot.polling(none_stop=True)
