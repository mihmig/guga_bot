from abc import ABCMeta, abstractmethod

from constants import FORMS_STACK, MAIN_FORM
from helpers.bot_helper import BotHelper
from helpers.db_postgres import Db
from helpers.parameter_helper import ParameterHelper


# базовый класс формы ввода пользователем
class Form:
    __metaclass__ = ABCMeta
    __slots__ = ('db', 'bot_helper', 'forms')

    def __init__(self, db: Db, bot_helper: BotHelper):
        self.db = db
        self.bot_helper = bot_helper
        self.forms = {}
        self.parameter_helper = ParameterHelper(db)

    @abstractmethod
    def name(self) -> str:
        """Вернуть имя формы"""

    @abstractmethod
    def show(self, user_id: int, context: dict, upd: dict, json=None):
        """Показать форму"""

    @abstractmethod
    def apply(self, user_id: int, context: dict, upd: dict):
        """Обработать поступившее от пользователя сообщение"""

    def push(self, context: dict, form_name: str) -> None:
        """Поместить имя (текущей) формы в стек"""
        stack = context.get(FORMS_STACK, [])
        stack.append(form_name)
        context[FORMS_STACK] = stack

    def pop(self, context: dict) -> str | None:
        """Получить имя предыдущей формы из стека"""
        stack = context.get(FORMS_STACK, [])
        if len(stack) == 0:
            return MAIN_FORM
        form_name = stack.pop()
        context[FORMS_STACK] = stack
        return form_name


