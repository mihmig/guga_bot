from constants import MAIN_FORM, PROFILE1_FORM, BACK

input_text_menu = {
    "method": "sendmessage",
    "chat_id": 0,
    "protect_content": False,
    "text": "Введите значение:",
    "reply_markup": {
        "inline_keyboard": [
            [
                {"text": "⏮️ Назад", "callback_data": BACK},
                {"text": "🏠 В начало", "callback_data": MAIN_FORM}
            ]
        ]
    }
}

speciality_fle = {
    "method": "sendmessage",
    "chat_id": 47254369,
    "protect_content": True,
    "text": "Укажите вашу специальность:",
    "reply_markup": {
        "inline_keyboard": [
            [
                {"text": "ОЛР", "callback_data": "value|olr"},
                {"text": "ЛГВС", "callback_data": "value|lgvs"},
                {"text": "ИВП", "callback_data": "value|ivp"}
            ],
            [
                {"text": "ОРАНО", "callback_data": "value|orano"},
                {"text": "ЭБАС", "callback_data": "value|ebas"}
            ],
            [
                {"text": "⏮️ Назад", "callback_data": "back"},
                {"text": "🏠 В начало", "callback_data": "main_form"}
            ]
        ]
    }
}

speciality_faitop = {
    "method": "sendmessage",
    "chat_id": 47254369,
    "protect_content": True,
    "text": "Укажите вашу специальность:",
    "reply_markup": {
        "inline_keyboard": [
            [
                {"text": "ОРТОП", "callback_data": "value|ortop"},
                {"text": "ОРТОР", "callback_data": "value|ortor"},
            ],
            [
                {"text": "ОПУФТ", "callback_data": "value|opuft"},
                {"text": "ОРАТ", "callback_data": "value|orat"}
            ],
            [
                {"text": "⏮️ Назад", "callback_data": "back"},
                {"text": "🏠 В начало", "callback_data": MAIN_FORM}
            ]
        ]
    }
}

profile_filled = {
    "method": "sendmessage",
    "chat_id": 0,
    "protect_content": False,
    "text": "Анкета полностью заполнена, спасибо.",
    "reply_markup": {
        "inline_keyboard": [
            [{"text": "🏠 В начало", "callback_data": MAIN_FORM}],
            [{"text": "📝 Редактировать анкету", "callback_data": PROFILE1_FORM}]
        ]
    }
}