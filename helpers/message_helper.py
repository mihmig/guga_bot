# Формирователь сообщений телеграм

def make_message(chat_id, text, parse_mode='markdown') -> dict:
    return {
        'method': 'sendmessage',
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode
    }


def make_reply(chat_id, text, reply_to_message_id) -> dict:
    return {
        'method': 'sendmessage',
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'markdown',
        'reply_to_message_id': reply_to_message_id
    }


def make_menu_message(chat_id: int, caption: str, menu: dict):
    message = make_message(chat_id, caption)
    inline_keyboard = list()
    for key, value in menu.items():
        line = list()
        line.append({'text': value, 'callback_data': key})
        inline_keyboard.append(line)
    message['reply_markup'] = {"inline_keyboard": inline_keyboard}
    return message


def make_contact_request(chat_id) -> dict:
    return {
        'method': 'sendmessage',
        'chat_id': chat_id,
        'text': 'Предоставьте свой номер телефона',
        "reply_markup": {
            "one_time_keyboard": True,
            "keyboard": [[{
                'text': 'Отправить номер', 'request_contact': True
            }], ["Cancel"]]
        }
    }


def make_keyboard(chat_id: int, text: str, labels: list) -> dict:
    message = make_message(chat_id, text)
    keyboard = list()
    for label in labels:
        line = list()
        line.append({'text': label, 'callback_data': label})
        keyboard.append(line)
    message['reply_markup'] = {"one_time_keyboard": True, "keyboard": keyboard}
    return message
