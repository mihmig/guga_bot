# Телеграм-бот для сбора информации от студентов
import copy
import json
import re

from constants import *
from forms.about_form import AboutForm
from forms.fill_profile_form import FillProfileForm
from forms.main_form import MainForm
from forms.profile1_form import Profile1Form
from forms.profile2_form import Profile2Form
from forms.profile3_form import Profile3Form
from forms.input_text_form import InputTextForm
from helpers.bot_helper import BotHelper, parse_update
from helpers.db_postgres import Db
from helpers.context_helper import ContextHelper
from data.config import config

db = Db(config)
bot_helper = BotHelper(config['bot_token'], db)
context_helper = ContextHelper(db, bot_helper)

phone_number_regexp = re.compile(r'[8,9]?\d{10}')

# Словарь с доступными формами
# TODO сделать автоматическое заполнение
all_forms = {
    MAIN_FORM: MainForm(db, bot_helper),
    ABOUT_FORM: AboutForm(db, bot_helper),
    FILL_PROFILE_FORM: FillProfileForm(db, bot_helper),
    PROFILE1_FORM: Profile1Form(db, bot_helper),
    PROFILE2_FORM: Profile2Form(db, bot_helper),
    PROFILE3_FORM: Profile3Form(db, bot_helper),
    INPUT_TEXT_FORM: InputTextForm(db, bot_helper)
}
for form in all_forms.values():
    form.forms = all_forms


def process_update(update):
    # print(json.dumps(update))
    upd = parse_update(update)
    if upd is None or upd['chat_id'] < 0:  # Работа в групповых чатах пока не поддерживается
        return
    bot_helper.update_user(upd.get('user'))
    user_id = upd['user_id']
    context = context_helper.load(user_id)
    current_form = context.get(CURRENT_FORM)
    data = upd.get('data')

    if upd['type'] == 'callback_query':
        bot_helper.send_answer_callback_query(upd['callback_query_id'], '', False)

    if data in ('start', '/start'):  # В начале общения оставляем не удаляемое сообщение
        message = copy.deepcopy(WELCOME_MESSAGE)
        message['chat_id'] = user_id
        welcome_message_id = bot_helper.send_message(message)
        # Стартовое сообщение пользователя же - удаляем
        bot_helper.delete_message(user_id, upd.get('message_id'))
        all_forms[MAIN_FORM].show(user_id, context, upd)
    elif current_form is None or data == MAIN_FORM:
        # Удаляем сообщение пользователя
        if upd['type'] != 'callback_query':
            # Удаляем сообщение пользователя, в данном контексте оно неуместно
            bot_helper.delete_message(user_id, upd['message_id'])
        # bot_helper.delete_message(user_id, upd.get('message_id'))
        # bot_helper.delete_message(user_id, context.get('last_bot_message_id'))
        all_forms[MAIN_FORM].show(user_id, context, upd)
    else:
        current_form_class = all_forms.get(current_form)
        if current_form_class is None:
            return
        current_form_class.apply(user_id, context, upd)

    if context is not None:
        context_helper.save(user_id, context)


while True:
    updates = bot_helper.get_updates()
    for next_update in updates:
        process_update(next_update)
