# -*- coding: utf-8 -*-
import os
import telebot
import constants
from datetime import datetime


bot = telebot.TeleBot(constants.token)
print(bot.get_me())

def log(message, answer):
    print("\n ------")
    print(datetime.now())
    print("Сообщение от " + str(message.from_user.first_name) + " " + str(message.from_user.last_name) + ". id = " + str(message.from_user.id) + ".\nID сообщения - " + str(message.message_id) + " Текст - " + str(message.text)+"")
    print("Ответ - " + answer)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('/start', 'Локация', 'Документ')
    user_markup.row('Консультация с специалистом', 'Вопросы к секретарю')
    bot.send_message(message.chat.id, 'Привет! Я бот компании Росинформзащита!', reply_markup=user_markup)


@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'Бот хорошо работает')


@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == 'Документ':
        directory = 'D:\PycharmProjects\TelegramBot\static\document'
        all_files_in_directory = os.listdir(directory)
        print(all_files_in_directory)
        for files in all_files_in_directory:
            document = open(directory + '/' + files, 'rb')
            bot.send_chat_action(message.chat.id, 'upload_document')
            answer = "Отправка документов"
            log(message, answer)
            bot.send_document(message.chat.id, document)
            document.close()
    if message.text == 'Локация':
        answer = 'Отправка локации'
        log(message, answer)
        bot.send_chat_action(message.chat.id, 'find_location')
        bot.send_venue(message.chat.id, 62.0302836, 129.7617328, "Росинформзащита", "Ларионова, 10")

    if message.text == 'Консультация с специалистом':
        answer = "Уважаемый пользователь! Задайте свой вопрос."
        log(message, answer)
        bot.send_message(message.chat.id, "Уважаемый пользователь! Задайте свой вопрос.")
        markup = telebot.types.ReplyKeyboardMarkup(True, False, row_width=2)
        numberButton = telebot.types.KeyboardButton('Дай свой номер', request_contact=True)
        markup.add(numberButton)
        print(numberButton.request_contact)
        bot.send_message(message.chat.id, "Укажи свой номер:", reply_markup=markup)

    if message.text == 'Вопросы к секретарю':
        answer = "Уважаемый пользователь!Для осуществления консультации необходимо, чтобы Вы отправили номер телефона. Когда номер будет получен, задайте свой вопрос повторно."
        log(message, answer)
        bot.send_message(message.chat.id, "Уважаемый пользователь!Для осуществления консультации необходимо, чтобы Вы отправили номер телефона. Когда номер будет получен, задайте свой вопрос повторно.")

    answer = "Просто текст"
    log(message, answer)


@bot.message_handler(content_types=['document'])
def handle_document(message):
    print('Пришел документ')


@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    print('Пришла аудиозапись')


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    print('Пришло изображение')


@bot.message_handler(content_types=['sticker'])
def handle_sticker(message):
    print('Пришел стикер')


@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    print('Пришел контакт')
    phone_number = message.contact.phone_number
    print(phone_number)
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('/start', 'Локация', 'Документ')
    user_markup.row('Консультация с специалистом', 'Вопросы к секретарю')
    bot.send_message(message.chat.id, 'Привет! Я специалист Росинформзащита!', reply_markup=user_markup)

try:
    bot.polling()
except Exception as e:
    print(e)
    pass