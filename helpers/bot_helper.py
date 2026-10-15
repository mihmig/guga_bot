# Модуль взаимодействия с сервером Телеграма
import json
from datetime import datetime

import requests
import time
import re
from helpers.db_postgres import Db


# Разбор поступившего JSON от сервера телеграма
def parse_update(update: dict) -> dict | None:
    upd = {}
    if "message" in update:
        upd['type'] = 'message'
        message = update['message']
        upd['message'] = message
        upd['user'] = message['from']
        upd['user_id'] = message['from']['id']
        upd['chat_id'] = message['chat']['id']
        upd['message_id'] = message['message_id']
        upd['language_code'] = message['from'].get('language_code')
        if 'contact' in message:
            upd['command'] = 'contact'
            upd['data'] = re.sub(r'\D', '', message['contact']['phone_number'])
        elif 'text' in message:
            upd['type'] = 'text'
            upd['data'] = message['text']
        return upd
    elif "callback_query" in update:
        upd['type'] = 'callback_query'
        callback_query = update['callback_query']
        upd['message'] = callback_query['message']
        upd['user'] = callback_query['from']
        upd['user_id'] = callback_query['from']['id']
        upd['chat_id'] = callback_query['message']['chat']['id']
        upd['message_id'] = callback_query['message']['message_id']
        upd['callback_query_id'] = callback_query['id']
        if 'data' in callback_query:
            upd['data'] = callback_query['data']
        return upd

    return None


class BotHelper:
    def __init__(self, token: str, db: Db):
        self.send_message_url = f"https://api.telegram.org/bot{token}/"
        self.delete_message_url = f"https://api.telegram.org/bot{token}/deletemessage"
        self.get_updates_url = f"https://api.telegram.org/bot{token}/getUpdates?timeout=300&offset="
        self.send_answer_callback_query_url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
        self.db = db
        self.last_update_id = 0
        self.get_last_update_id()

    def get_updates(self, timeout=60) -> list:
        try:
            response = requests.get(self.get_updates_url + str(self.last_update_id + 1), timeout=timeout)
            if response.status_code != 200:
                time.sleep(2)
                return list()
        except Exception as e:
            print(str(e.args[0]))
            time.sleep(2)
            return list()
        updates = response.json()['result']
        if len(updates) == 0:
            return list()
        self.last_update_id = updates[-1]['update_id']
        return updates

    # Получаем последний update от бота (сообщения, отправленные пользователями раньше старта бота игнорируем)
    def get_last_update_id(self):
        updates = self.get_updates(timeout=2)
        if len(updates) == 0:
            return
        last_update_id = updates[-1]['update_id']
        print(f'retrieved last update id = {last_update_id}')
        self.last_update_id = int(last_update_id)

    # Обновляет информацию о пользователе в БД
    def update_user(self, user: dict):
        if user is None:
            return
        exist = self.db.get_value('SELECT id FROM "user" WHERE id = %s', [user.get('id')])
        if exist:
            self.db.execute("""
                UPDATE "user" SET username = %s, first_name = %s, last_name = %s, last_message_received = %s
                WHERE id = %s
            """,
                            [user.get('username'), user.get('first_name'), user.get('last_name'), datetime.now(),
                             user.get('id')])
        else:
            self.db.execute('INSERT INTO "user" (id, username, first_name, last_name) VALUES (%s, %s, %s, %s)',
                            [user['id'], user.get('username'), user.get('first_name'), user.get('last_name')])

    # Отправка команды (сообщения, клавиатуры, меню и т.п.) на сервер Телеграма.
    # Возвращает id отправленного сообщения
    def send_message(self, message: dict) -> int | None:
        try:
            response = requests.post(self.send_message_url, json=message)
            self.db.execute('UPDATE "user" SET last_message_sent = NOW() WHERE id = %s', [message.get('chat_id')])
            return int(response.json()['result']['message_id'])
        except Exception as e:
            print("Ошибка отправки сообщения: ")
            print(json.dumps(message))
            print(str(e.args[0]))
            return None

    # Изменение ранее отправленного сообщения
    # (если изменить не удалось - отправляем новое сообщение)
    def edit_or_send_message(self, message_id: int, message: dict) -> int | None:
        if message_id is None:
            return self.send_message(message)
        try:
            message["method"] = "editmessagetext"
            message["message_id"] = message_id
            response = requests.post(self.send_message_url, json=message)
            return int(response.json()['result']['message_id'])
        except Exception as e:
            print(f"Ошибка изменения ранее отправленного сообщения сообщения: {str(e.args[0])}")
        message["method"] = "sendmessage"
        return self.send_message(message)

    # Удаление ранее отправленного сообщения
    def delete_message(self, chat_id: int, message_id: int) -> None:
        if chat_id is None or message_id is None:
            return
        try:
            requests.post(self.delete_message_url, json={"chat_id": chat_id, "message_id": message_id})
        except Exception as e:
            print("Ошибка удаления сообщения: " + str(e.args[0]))
            print(str(e.args[0]))


    # Всплывающее сообщение в ответ на выбор пункта меню
    def send_answer_callback_query(self, callback_query_id: str, text: str, show_alert: bool = False):
        try:
            requests.post(self.send_answer_callback_query_url, json={'callback_query_id': callback_query_id,
                                                                     'text': text,
                                                                     'show_alert': show_alert})
        except Exception as e:
            print("Ошибка отправки answer_callback_query: ")
            print(callback_query_id)
            print(str(e.args[0]))
            return None

    def make_contact_request(self, chat_id: int) -> dict|None:
        contact_request = {
            'method': 'sendmessage',
            'chat_id': chat_id,
            'text': 'Предоставьте свой номер телефона',
            "reply_markup": {
                "one_time_keyboard": True,
                "keyboard": [[{
                    'text': 'Отправить номер', 'request_contact': True
                }], ["Cancel"]]
            }
        }
        try:
            requests.post(self.send_answer_callback_query_url, json=contact_request)
        except Exception as e:
            print("Ошибка отправки запроса на контактную информацию: ")
            print(f'chat_id = {chat_id}')
            print(str(e.args[0]))
            return None
