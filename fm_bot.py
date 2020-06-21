from config import *
import telebot
import fine_folio_2
import re
import datetime as dt
import flask

user_capital_1 = 0

bot = telebot.TeleBot(TOKEN_TEST)

keyboard1 = telebot.types.ReplyKeyboardMarkup()
keyboard1.row('50 000 рублей', '100 000 рублей', '150 000 рублей', '200 000 рублей', '300 000 рублей', '400 000 рублей',
              '500 000 рублей', '1 000 000 рублей')

keyboard2 = telebot.types.ReplyKeyboardMarkup()
keyboard2.row('Голубые Фишки', 'Первая Тридцатка Компаний')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, я бот, который поможет Вам вложить деньги в портфель ценных '
                                      'бумаг на московской бирже. '
                                      'Для начала давай поймем сколько денег Вы хотите вложить в портфель?',
                     reply_markup=keyboard1)


@bot.message_handler(content_types=['text'])
def send_text(message):
    global user_capital_1
    if type(send_text_0(message)) == int:
        if send_text_0(message) > 0:
            user_capital_1 = send_text_0(message)
            send_text_2(message)
    else: send_text_1(message, user_capital_1)

def send_text_0(message, user_capital_from_message=0):
    res = bool(re.findall('\d+', message.text))
    if res == True:
        try:
            user_capital_from_message = get_capital(message.text)
        except IndexError:
            bot.send_message(message.chat.id, 'Нужно вести цифры, деньги любят счет.')
        if user_capital_from_message >= 30000:
            return user_capital_from_message
        else:
            bot.send_message(message.chat.id, 'Боюсь, это слишком мало, у большинства брокеров минимальный порог входа 30 000 рублей.'
                                                'Вы только подумайте одна акция комапнии Норникел (GMKN) стоит около 18 000 рублей. '
                                              'Попробуйте выбрать из варинатов на клавиатуре ниже.', reply_markup= keyboard1)

@bot.message_handler(content_types=['text'])
def send_text_2(message):
    bot.send_message(message.chat.id, 'Отлично, с вашим капиталом мы определились, '
                                      'теперь нужно решить из каких акций московской биржи мы соберем Ваш портфель '
                                      '- из голубых фишек или из TOP-30? '
                                      'Кстати, сейчас Вы можете поменять решение о капитале введя цифру в ответном сообщении.', reply_markup=keyboard2)

@bot.message_handler(content_types=['text'])
def send_text_1(message, user_capital, moex_list='moex_list', blue='blue_chips_moex'):
    if message.text.lower() == 'голубые фишки':
        bot.send_message(message.chat.id,
                         'Я начал просчитывать оптимальный портфель, это займет 5-10 минут. '
                         'Можете пока выпить чай или кофе. В экселе мой создатель делал это часами. :-)')
        opt_distrib = fine_folio_2.fine_folio_core(blue, user_capital, start=dt.datetime(2018, 6, 19), end=dt.datetime(2019, 6, 19))
        bot.send_message(message.chat.id, 'Ваш оптимальный портфель на 2020 год (%): {}'.format(opt_distrib[1]))
        new_capital = fine_folio_2.backtest(blue, opt_distrib[0], user_capital, start_b=dt.datetime(2019, 6, 19), end_b = dt.datetime(2020, 6, 19))
        bot.send_message(message.chat.id, 'Если бы вы вложили тот объем денег год назад, '
                                          'сейчас у вас бы было {} рублей'.format(new_capital))
    elif message.text.lower() == 'первая тридцатка компаний':
        bot.send_message(message.chat.id, 'Я начал просчитывать оптимальный портфель, это займет некоторое время. '
                                          'Минут 5-10. Сможете успеть посмотреть короткое видео на YouTube :-)')
        opt_distrib = fine_folio_2.fine_folio_core(moex_list, user_capital, start=dt.datetime(2018, 6, 19), end=dt.datetime(2019, 6, 19)).optimal_weights_2
        bot.send_message(message.chat.id, 'Ваш оптимальный портфель на 2020 год (%): {}'.format(opt_distrib[1]))
        new_capital = fine_folio_2.backtest(moex_list, opt_distrib[0], user_capital, start_b=dt.datetime(2019, 6, 19), end_b = dt.datetime(2020, 6, 19))
        bot.send_message(message.chat.id, 'Если бы вы вложили тот объем денег год назад, '
                                          'сейчас у вас бы было {} рублей'.format(new_capital))


def get_capital(user_capital):
    user_capital = user_capital.replace(" ", "")
    user_capital = re.findall('\d+', user_capital)
    user_capital = int(user_capital[0])
    return user_capital


bot.polling()
