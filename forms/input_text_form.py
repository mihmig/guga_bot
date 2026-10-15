import copy

from constants import *
from forms.form import Form
from helpers.bot_helper import BotHelper
from helpers.db_postgres import Db
from helpers.param_forms import input_text_menu


class InputTextForm(Form):

    def name(self) -> str:
        return INPUT_TEXT_FORM

    def show(self, user_id: int, context: dict, upd: dict, json=None):
        context[CURRENT_FORM] = self.name()
        data = upd.get('data').split('|')
        if len(data) < 2:
            self.forms.get(MAIN_FORM).show(user_id, context, upd)
            return
        current_param = data[1]
        context[CURRENT_PARAM] = current_param
        parameter = self.db.get_line("SELECT * FROM parameter WHERE name = %s", [current_param])
        context[CURRENT_PARAM_TYPE] = parameter.type
        if json is not None:  # JSON формы ввода передан в параметре
            message = json
        elif parameter.json is not None: # JSON формы ввода задан в поле "json" в БД
            message = parameter.json
        else:  # # JSON формы ввода не указан - подставляем строчку из поля в БД
            message = copy.deepcopy(input_text_menu)
            message['text'] = parameter.prompt
        message['chat_id'] = user_id
        message_id = self.bot_helper.edit_or_send_message(context.get('last_bot_message_id'), message)
        context['last_bot_message_id'] = message_id
        return context

    def apply(self, user_id: int, context: dict, upd: dict):
        data = upd.get('data').split('|')
        if upd['type'] == 'callback_query': # Выбрали какой-то пункт меню.
            if data[0] == VALUE:  # Данные пользователя пришли в callback-е
                stored = self.parameter_helper.store_user_parameter(user_id, context[CURRENT_PARAM], data[1])
                if not stored:  # Сохранить почему-то не удалось...
                    print(f'Не удалось сохранить параметр {context[CURRENT_PARAM]}, user_id = {user_id}, data={data}')
                    return
                next_form_name = self.pop(context)
            else:  # Нажали кнопку перехода на другую форму ("Назад", "Домой" или "Пропустить")
                if data[0] == BACK:  # Возвращаемся на предыдущую форму (или на главную, если предыдущей нет)
                    next_form_name = self.pop(context)
                else:  # Переходим на следующую форму (или главную, если следующей нет)
                    # Сохраняем название текущей формы в стеке (на случай возврата)
                    self.push(context, self.name())
                    next_form_name = data[0]

            # Удаляем текущую форму перед показом следующей
            # self.bot_helper.delete_message(user_id, context.get('last_bot_message_id'))
            # Если форму почему-то не нашли - показываем главную
            next_form = self.forms.get(next_form_name) or self.forms.get(MAIN_FORM)
            next_form.show(user_id, context, upd)
            return

        # Удаляем сообщение пользователя
        self.bot_helper.delete_message(user_id, upd.get('message_id'))
        if context.get(CURRENT_PARAM_TYPE) == 'select':  # Форма для выбора значения, ввести своё нельзя
            return

        stored = self.parameter_helper.store_user_parameter(user_id, context[CURRENT_PARAM], data[0])
        if stored:
            # Удаляем текущую форму перед показом следующей
            # self.bot_helper.delete_message(user_id, context.get('last_bot_message_id'))

            # Возвращаемся на предыдущую форму (или на главную)
            next_form_name = self.pop(context)
            next_form = self.forms.get(next_form_name) or self.forms.get(MAIN_FORM)
            next_form.show(user_id, context, upd)
