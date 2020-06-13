from config import *
import telebot
import fine_folio_1
import os
import flask

bot = telebot.TeleBot(TOKEN)

keyboard1 = telebot.types.ReplyKeyboardMarkup()
keyboard1.row('50 000 рублей', '100 000 рублей', '150 000 рублей', '200 000 рублей', '300 000 рублей', '400 000 рублей', '500 000 рублей', '1 000 000 рублей')

keyboard2 = telebot.types.ReplyKeyboardMarkup()
keyboard2.row('голубые фишки', 'топ-30')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, я бот который поможет тебе вложить деньги в портфель ценных '
                                      'бумаг на московской бирже. '
                                      'Для начала давай поймем сколько денегь ты хочешь вложить в портфель?',
                     reply_markup=keyboard1)


@bot.message_handler(content_types=['text'])

def send_text(message, moex_list='moex_list', blue='blue_chips_moex'):
    res = "рублей" in message.text
    if str(res) == True:
        user_capital = message.text.lower().replace(" ", "")
        user_capital = user_capital.replace("рублей", "")
        user_capital = int(user_capital)
        bot.send_message(message.chat.id, 'Отлично, с вашим капиталом мы определились, '
                                          'теперь нужн решить из каких акций московской биржи мы соберем ваш портфель '
                                          '- из голубых фишек или из TOP-30?', reply_markup=keyboard2)
        if message.text.lower() == 'голубые фишки':
            bot.send_message(message.chat.id,
                             'Я начал просчитывать оптимальный портфель, это займет 5-10 минут. '
                             'Можете пока выпить чай или кофе.'
                             ' В экселе мой создатель делал это часами. :-)')
            opt_distrib = fine_folio_1.fine_folio_core(blue, user_capital)
            bot.send_message(message.chat.id, 'Ваш оптимальный портфель на 2020 год (%): {}'.format(opt_distrib))
        elif message.text.lower() == 'топ-30':
            bot.send_message(message.chat.id, 'Я начал просчитывать оптимальный портфель, это займет некоторое время.')
            opt_distrib = fine_folio_1.fine_folio_core(moex_list, user_capital)
            bot.send_message(message.chat.id, 'Ваш оптимальный портфель на 2020 год (%): {}'.format(opt_distrib))
        else: bot.send_message('Боюсь, что-то пошло не так. Я сообщу о проблеме, но пока портфель посчитать не получится')
    else: bot.send_message('Что-то опять не так. Мы займемся эти , но пока ничего не получится.')

#bot.polling()

