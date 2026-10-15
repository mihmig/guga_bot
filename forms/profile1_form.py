import copy

from constants import *
from forms.form import Form
from helpers.bot_helper import BotHelper
from helpers.db_postgres import Db

# TODO - генерировать пункты и заголовки меню в зависимости от типа пользователя
profile1_menu = {
    "method": "sendmessage",
    "chat_id": 0,
    "protect_content": False,
    "text": "Выберите пункт анкеты:",
    "reply_markup": {
        "inline_keyboard": [
            [
                {"text": "1️⃣ Фамилия", "callback_data": "input_text_form|last_name"},
                {"text": "2️⃣ Имя", "callback_data": "input_text_form|first_name"},
                {"text": "3️⃣ Отчество", "callback_data": "input_text_form|middle_name"}
            ],
            [
                {"text": "Пол 👨/👩", "callback_data": "input_text_form|gender"},
                {"text": "📱 Контактный телефон", "callback_data": "input_text_form|phone"},
                {"text": "📅 Дата рождения", "callback_data": "input_text_form|birth_date"}
            ],
            [
                {"text": "📰 Факультет", "callback_data": "input_text_form|faculty"},
                {"text": "📰 Специальность", "callback_data": "input_text_form|speciality"},
                {"text": "📰 Группа", "callback_data": "input_text_form|group"}
            ],
            [
                {"text": "📧 e-mail", "callback_data": "input_text_form|email"},
                {"text": "📏 Рост", "callback_data": "input_text_form|height"},
                {"text": "📏 Размер обуви", "callback_data": "input_text_form|shoe_size"}
            ],
            [
                {"text": "⏮️ Назад", "callback_data": BACK},
                {"text": "🏠 В начало", "callback_data": MAIN_FORM},
                {"text": "Далее ⏭️", "callback_data": PROFILE2_FORM}
            ]
        ]
    }
}


class Profile1Form(Form):

    def name(self) -> str:
        return PROFILE1_FORM

    def show(self, user_id: int, context: dict, upd: dict, json=None):
        context[CURRENT_FORM] = self.name()
        message = copy.deepcopy(profile1_menu)
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
