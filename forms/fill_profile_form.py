# Первоначальная форма заполнения анкетных данных.
# 1. Формирует список параметров, которые ещё не заполнены.
#    Только те, у которых заполнен атрибут order.
# 2. Вызывает форму ввода данных
import copy

from constants import *
from forms.form import Form
from helpers.bot_helper import BotHelper
from helpers.db_postgres import Db
from helpers.param_forms import profile_filled
from helpers.parameter_helper import ParameterHelper


class FillProfileForm(Form):

    def __init__(self, db: Db, bot_helper: BotHelper):
        self.parameter_helper = ParameterHelper(db)
        super().__init__(db, bot_helper)

    def name(self) -> str:
        return FILL_PROFILE_FORM

    def show(self, user_id: int, context: dict, upd: dict, json=None):
        # Получаем следующий незаполненный параметр и список всех параметров пользователя
        # Какие-то заполнены, какие-то - нет
        next_parameter, user_parameters = self.parameter_helper.get_next_unfilled_param(user_id)
        if next_parameter is None:
            # Все необходимые параметры заполнены, отображаем дополнительное меню
            message = copy.deepcopy(profile_filled)
            message['chat_id'] = user_id
            message_id = self.bot_helper.edit_or_send_message(context.get('last_bot_message_id'), message)
            context['last_bot_message_id'] = message_id
            context[FORMS_STACK] = [MAIN_FORM]  # На эту форму уже не вернёмся - только на главную
            return
        # Помещаем текущую форму в стек, чтобы вернуться к ней после заполнения параметра
        self.push(context, self.name())
        upd['data'] = INPUT_TEXT_FORM + '|' + next_parameter
        # У параметра может быть собственная JSON форма
        form_json = self.parameter_helper.get_parameter_input_form(user_id, next_parameter, user_parameters)
        self.forms.get(INPUT_TEXT_FORM).show(user_id, context, upd, form_json)

    def apply(self, user_id: int, context: dict, upd: dict):
        """Форма не отображается, метод не имеет смысла"""
        pass
