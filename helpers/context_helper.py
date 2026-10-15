# Модуль хранения контекста бота
import json

from helpers.bot_helper import BotHelper
from helpers.db_postgres import Db


class ContextHelper:
    def __init__(self, db: Db, bot_helper: BotHelper):
        self.db = db
        self.bot_helper = bot_helper

    # Сохраняет (обновляет) контекст текущего диалога с пользователем в БД
    def save(self, user_id: int, context: dict) -> dict:
        context_str = json.dumps(context)
        self.db.execute("""
        INSERT INTO context(user_id, context) VALUES(%s, %s)
        ON CONFLICT (user_id) DO UPDATE SET context = %s, updated = now()
        """, [user_id, context_str, context_str])
        return context

    # Получает контекст текущего диалога с пользователем
    def load(self, user_id: int) -> dict:
        context = self.db.get_value("SELECT context FROM context WHERE user_id = %s", [user_id])
        if context is None:
            return {}
        return context

    # Удаляет контекст пользователя
    def clear(self, user_id: int, context: dict) -> None:
        if context is None:
            return
        last_bot_message_id = context.get('last_bot_message_id')
        if last_bot_message_id is not None:
            self.bot_helper.delete_message(user_id, last_bot_message_id)
        last_user_message_id = context.get('last_user_message_id')
        if last_user_message_id is not None:
            self.bot_helper.delete_message(user_id, last_user_message_id)

        self.db.execute("DELETE FROM context WHERE user_id = %s", [user_id])
