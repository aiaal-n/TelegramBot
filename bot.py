# -*- coding: utf-8 -*-
import os
from datetime import datetime
import constants
import telebot
import users

bot = telebot.TeleBot(constants.token)
client_operator_chat = {}
TEAM_USER_LOGGING = 0
TEAM_USER_ACCEPTED = 1
team_users = users.TeamUserList()
user_step = {}

print(bot.get_me())


def log(message, answer):
    try:
        print("\n ------")
        print(datetime.now())
        print("Сообщение от " + str(message.from_user.first_name) + " " + str(message.from_user.last_name) + ". id = " + str(message.from_user.id) + ".\nID сообщения - " + str(message.message_id) + " Текст - " + str(message.text)+"")
        print("Ответ - " + answer)
    except ValueError:
        pass

# Реагирует на /start, /help, просто отдаёт приветственное сообщение
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('/start', '/location')
    user_markup.row('Консультация с специалистом', 'Вопросы к секретарю')
    bot.send_message(message.chat.id, "Добро пожаловать, чем вам помочь?",  reply_markup=user_markup)


# Авторизация операторов по паролю
@bot.message_handler(commands=['on'])
def login_operator(message):
    try:
        if message.chat.id in team_users:
            bot.reply_to(message, "Вы уже оператор")
        else:
            user_step[message.chat.id] = TEAM_USER_LOGGING
            bot.reply_to(message, "Введите секретный код:")
    except ValueError:
        pass

# Операторов введет пароль, чтобы авторизоваться
@bot.message_handler(func=lambda message: user_step.get(message.chat.id) == TEAM_USER_LOGGING)
def team_user_login(message):
    try:
        if message.text == 'password1':
            team_users.add(users.TeamUser(message.chat.id))
            user_step[message.chat.id] = TEAM_USER_ACCEPTED
            bot.reply_to(message, "Вы уже можете принимать сообщение, как оператор")
            answer = 'Новый оператор'
            log(message, answer)
        else:
            user_step[message.chat.id] = 1
            bot.reply_to(message, "Не правильно ввели пароль, повторите сначала набрать команду /on")
    except ValueError:
        pass

# Команда, по которой удаляешься из списка операторов
@bot.message_handler(commands=['off'])
def team_user_logout(message):
    try:
        if message.chat.id not in team_users:
            bot.reply_to(message, "Вы уже не оператор:(")
        else:
            team_users.remove_by_chat_id(message.chat.id)
            bot.reply_to(message, "Вы прекратили отвечать на сообщение")

        answer = 'Оператор отключился'
        log(message, answer)
    except ValueError:
        pass

# Команда показываюший местоположение
@bot.message_handler(commands=['location'])
def location_command(message):
    answer = 'Отправка локации'
    log(message, answer)
    bot.send_chat_action(message.chat.id, 'find_location')
    bot.send_venue(message.chat.id, 62.030357, 129.762587, "Росинформзащита", "Ларионова, 10")


# Рассылает  всем операторам сообщения от клиента
@bot.message_handler(func=lambda message: users.client_operator(message.chat.id))
def chat_with_operator(message):
    global client_operator_chat
    for user in team_users:
        bot.send_message(user.chat_id,  'Клиент {name} с номером чата /chat_{client_chat_id}  написал(а):\n{msg_text}'.format(
            name=str(message.from_user.first_name), client_chat_id=str(message.chat.id), msg_text=message.text))
        # Исключение для того чтобы сохранялся последний выбранный чат, а для новых операторов добавлялось значение None
        try:
            if client_operator_chat[int(user.chat_id)] is not None:
                continue
        except KeyError:
            client_operator_chat[int(user.chat_id)] = None  # добавляет всех новых операторов в словарь и значение None
    answer = "клиент"
    log(message, answer)

# Позволяет оператору выбрать чат с каким клиентом общаться
@bot.message_handler(regexp='\/chat_\d*$')
def set_chat_operator_to_client(message):
    try:
        client_operator_chat[message.chat.id] = users.message_num(message.text)
    except ValueError:
        pass


# Смотрит с кем выбрал общаться оператор и направляет сообщения от оператора - клиенту и всем оставшимся операторам
@bot.message_handler(func=lambda message: not users.client_operator(message.chat.id))
def chat_with_client(message):
    try:
        if client_operator_chat[message.chat.id] is None:
            bot.send_message(message.chat.id,
                             'для ответа нужному клиенту, необходимо нажать над его сообщением на /chat_...')
        else:
            bot.send_message(int(client_operator_chat[message.chat.id]), message.text)
            for user in team_users:
                if message.chat.id == int(user.chat_id):
                    continue
                else:
                    try:
                        bot.send_message(user.chat_id,
                                         'Оператор {operator_chat_id} ответил клиенту '
                                         '{client_chat_id}:\n{msg_text}'.format(
                                             operator_chat_id=str(message.chat.id),
                                             client_chat_id=str(client_operator_chat[message.chat.id]),
                                             msg_text=message.text))
                    except KeyError:
                        continue
    except KeyError:
        bot.send_message(message.chat.id, 'клиент ещё ничего не писал')
    answer = 'Оператор'
    log(message,answer)


# Запуск бота, стараемся не обращать внимания на ошибки
if __name__ == '__main__':
    bot.polling(none_stop=True)

    """
    @bot.message_handler(content_types=['text'])
    def handle_text(message):
        if message.text == 'Консультация с специалистом':
            answer = "Уважаемый пользователь! Задайте свой вопрос."
            log(message, answer)
            bot.send_message(message.chat.id, "Уважаемый пользователь! Задайте свой вопрос.")

        if message.text == 'Вопросы к секретарю':
            answer = "Уважаемый пользователь!Для осуществления консультации необходимо, чтобы Вы отправили номер телефона. Когда номер будет получен, задайте свой вопрос повторно."
            log(message, answer)
            bot.send_message(message.chat.id, "Уважаемый пользователь!Для осуществления консультации необходимо, чтобы Вы отправили номер телефона. Когда номер будет получен, задайте свой вопрос повторно.")

        answer = "Просто текст"
        log(message, answer)
    """