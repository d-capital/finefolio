import telebot
import fine_folio_1
import os
from flask import Flask, request
TOKEN = '826034158:AAHWvRWLuZ2K0FPimIllOIwHIJl8x7h1QUw'

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

keyboard1 = telebot.types.ReplyKeyboardMarkup()
keyboard1.row('голубые фишки', 'топ-30')

@bot.message_handler(commands=['start'])

def start_message(message):
    bot.send_message(message.chat.id, 'Привет, я бот который поможет тебе вложить деньги в портфель ценных '
                                      'бумаг на московской бирже. Выбери на клавиатуре ниже какие бумаги '
                                      'ты хочешь использовать для создания портфела - голубые фишки или топ 30 акций московсой биржи?', reply_markup=keyboard1)

@bot.message_handler(content_types=['text'])
def send_text(message, moex_list = 'moex_list', blue = 'blue_chips_moex'):
    if message.text.lower() == 'голубые фишки':
        opt_distrib = fine_folio_1.fine_folio_core(blue)
        bot.send_message(message.chat.id, 'Ваш оптимальный портфель на 2020 год:{}'.format(opt_distrib))
    elif message.text.lower() == 'топ-30':
        opt_distrib = fine_folio_1.fine_folio_core(moex_list)
        bot.send_message(message.chat.id, 'Ваш оптимальный портфель на 2020 год:{}'.format(opt_distrib))


@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://your_heroku_project.com/' + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))