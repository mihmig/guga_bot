import copy

from constants import *
from forms.form import Form
from helpers.bot_helper import BotHelper
from helpers.db_postgres import Db

# TODO - генерировать главное меню в зависимости от типа пользователя
main_menu = {
    "method": "sendmessage",
    "chat_id": 0,
    "protect_content": False,
    "text": "Главное меню",
    "reply_markup": {
        "inline_keyboard": [
            [{"text": "📋 Заполнить анкету", "callback_data": FILL_PROFILE_FORM}],
            [{"text": "📝 Редактировать анкету", "callback_data": PROFILE1_FORM}],
            [{"text": "❓ О боте", "callback_data": ABOUT_FORM}]
        ]
    }
}


class MainForm(Form):
    def __init__(self, db: Db, bot_helper: BotHelper):
        super().__init__(db, bot_helper)

    def name(self) -> str:
        return MAIN_FORM

    def show(self, user_id: int, context: dict, upd: dict, json=None):
        context[CURRENT_FORM] = self.name()
        context[FORMS_STACK] = [self.name()]  # При переходе на главную форму "обнуляем" стек
        message = copy.deepcopy(main_menu)
        message['chat_id'] = user_id
        message_id = self.bot_helper.edit_or_send_message(context.get('last_bot_message_id'), message)
        context['last_bot_message_id'] = message_id

    def apply(self, user_id: int, context: dict, upd: dict):
        if upd['type'] != 'callback_query':
            # Удаляем сообщение пользователя, в данном контексте оно неуместно
            self.bot_helper.delete_message(user_id, upd['message_id'])
            return
        # Выбрали какой-то пункт главного меню
        data = upd.get('data').split('|')
        next_form = self.forms.get(data[0])
        if next_form is None:
            return
        # Удаляем текущую форму перед показом следующей
        # self.bot_helper.delete_message(user_id, context.get('last_bot_message_id'))
        context[FORMS_STACK] = [MAIN_FORM]
        next_form.show(user_id, context, upd)
