# Работа с данными пользователя
from helpers.bot_helper import BotHelper
from helpers.db_postgres import Db


class UserHelper:
    def __init__(self, db: Db, bot_helper: BotHelper):
        self.db = db
        self.bot_helper = bot_helper

    def create_or_update_user(self, user_info: dict) -> dict:
        user = self.db.get_line("SELECT * FROM user WHERE id = %s", [user_info.get('id')])
        if user is None:
            self.db.execute("""
                INSERT INTO user (id, username, first_name, last_name, language_code, last_message_received)
                VALUES (%s, %s, %s, %s, %s, now())
                """,
                            [user_info.get('id'), user_info.get('username'), user_info.get('first_name'),
                             user_info.get('last_name'),
                             user_info.get('language_code')]
                            )
        else:
            pass

    # Удаляет последнее принятое и последнее отправленное сообщение,
    # используется при смене экранной формы или очистке контекста по таймауту
    # (держим диалог с пользователем всегда пустым)
    def delete_last_messages(self, user_id):
        self.delete_last_message_received(user_id)
        self.delete_last_message_sent(user_id)
        pass

    # Удаляет последнее присланное сообщение от пользователя,
    # например, когда пользователь присылает что-то не то
    def delete_last_message_received(self, user_id):
        last_message_received = self.db.get_value("SELECT last_message_received FROM user WHERE id = %s", [user_id])
        if last_message_received is not None:
            self.bot_helper.delete_message(chat_id=user_id, message_id=last_message_received)

    # Удаляет последнее отправленное сообщение пользователю
    def delete_last_message_sent(self, user_id):
        last_message_sent = self.db.get_value("SELECT last_message_sent FROM user WHERE id = %s", [user_id])
        if last_message_sent is not None:
            self.bot_helper.delete_message(chat_id=user_id, message_id=last_message_sent)
