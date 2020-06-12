import telebot
import fine_folio_1
import os
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



if "HEROKU" in list(os.environ.keys()):
    logger = telebot.logger
    telebot.logger.setLevel(logging.INFO)

    server = Flask(__name__)
    @server.route("/bot", methods=['POST'])
    def getMessage():
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "!", 200
    @server.route("/")
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(url="https://still-reaches-54835.herokuapp.com/") # этот url нужно заменить на url вашего Хероку приложения
        return "?", 200
    server.run(host="0.0.0.0", port=os.environ.get('PORT', 80))
else:
    # если переменной окружения HEROKU нету, значит это запуск с машины разработчика.
    # Удаляем вебхук на всякий случай, и запускаем с обычным поллингом.
    bot.remove_webhook()
    bot.polling(none_stop=True)