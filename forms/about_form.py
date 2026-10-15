import copy

from constants import *
from forms.form import Form
from helpers.bot_helper import BotHelper
from helpers.db_postgres import Db

about_menu = {
    "method": "sendmessage",
    "chat_id": 0,
    "protect_content": False,
    "text": "Бот для сбора данных студентов и абитуриентов СПБГУ ГА имени А.А. Новикова",
    "reply_markup": {
        "inline_keyboard": [
            [
                {"text": "🏠 В начало", "callback_data": MAIN_FORM}
            ]
        ]
    }
}


class AboutForm(Form):
    def __init__(self, db: Db, bot_helper: BotHelper):
        super().__init__(db, bot_helper)

    def name(self) -> str:
        return ABOUT_FORM

    def show(self, user_id: int, context: dict, upd: dict, json=None):
        context[CURRENT_FORM] = self.name()
        message = copy.deepcopy(about_menu)
        message['chat_id'] = user_id
        # message_id = self.bot_helper.send_message(message)
        message_id = self.bot_helper.edit_or_send_message(context.get('last_bot_message_id'), message)
        context['last_bot_message_id'] = message_id

    def apply(self, user_id: int, context: dict, upd: dict):
        if upd['type'] != 'callback_query':
            # Удаляем сообщение пользователя, в данном контексте оно неуместно
            self.bot_helper.delete_message(user_id, upd['message_id'])
            return

        # Выбрали какой-то пункт меню
        data = upd.get('data').split('|')
        # Удаляем текущую форму перед показом следующей
        # self.bot_helper.delete_message(user_id, context.get('last_bot_message_id'))
        next_form = self.forms.get(data[0]) or MAIN_FORM
        next_form.show(user_id, context, upd)
