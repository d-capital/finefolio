import telebot
import fine_folio_1
import os
import flask
from flask import Flask, request
TOKEN = '826034158:AAHWvRWLuZ2K0FPimIllOIwHIJl8x7h1QUw'

bot = telebot.TeleBot(TOKEN)

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
        bot.send_message(message.chat.id, 'Я начал просчитывать оптимальный портфель, это займет 3-5 минут. В экселе мой создатель делал это часами. :-)')
        opt_distrib = fine_folio_1.fine_folio_core(blue)
        bot.send_message(message.chat.id, 'Ваш оптимальный портфель на 2020 год (%): {}'.format(opt_distrib))
    elif message.text.lower() == 'топ-30':
        bot.send_message(message.chat.id, 'Я начал просчитывать оптимальный портфель, это займет некоторое время.')
        opt_distrib = fine_folio_1.fine_folio_core(moex_list)
        bot.send_message(message.chat.id, 'Ваш оптимальный портфель на 2020 год (%): {}'.format(opt_distrib))


#bot.polling()

server = flask.Flask(__name__)

@server.route('/' + TOKEN, methods=['POST'])
def get_message():
    bot.process_new_updates([types.Update.de_json(
        flask.request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route('/', methods=["GET"])
def index():
    bot.remove_webhook()
    bot.set_webhook(url="https://{}.herokuapp.com/{}".format(APP_NAME, TOKEN))
    return "Hello from Heroku!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))