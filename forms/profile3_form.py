import copy

from constants import *
from forms.form import Form
from helpers.bot_helper import BotHelper
from helpers.db_postgres import Db

# TODO - генерировать пункты и заголовки меню в зависимости от типа пользователя
profile3_menu = {
    "method": "sendmessage",
    "chat_id": 0,
    "protect_content": False,
    "text": "Удостоверение личности:",
    "reply_markup": {
        "inline_keyboard": [
            [
                {"text": "Вид", "callback_data": "input_text_form|document_type"},
                {"text": "Серия", "callback_data": "input_text_form|document_series"},
                {"text": "Номер", "callback_data": "input_text_form|document_number"}
            ],
            [
                {"text": "📅 Дата выдачи", "callback_data": "input_text_form|document_date"}
            ],
            [
                {"text": "⏮️ Назад", "callback_data": PROFILE2_FORM},
                {"text": "🏠 В начало", "callback_data": MAIN_FORM}
            ]
        ]
    }
}


class Profile3Form(Form):

    def name(self) -> str:
        return PROFILE3_FORM

    def show(self, user_id: int, context: dict, upd: dict, json=None):
        context[CURRENT_FORM] = self.name()
        self.push(context, self.name())
        message = copy.deepcopy(profile3_menu)
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

        if data[0] == BACK:  # Возвращаемся на предыдущую форму (или на главную)
            next_form_name = self.pop(context)
            next_form = self.forms.get(next_form_name) or self.forms.get(MAIN_FORM)
        else:  # Переходим на следующую форму (или на главную)
            next_form = self.forms.get(data[0])
            if next_form is None:
                self.forms.get(MAIN_FORM).show(user_id, context, upd)
                return
            self.push(context, self.name())
        next_form.show(user_id, context, upd)
