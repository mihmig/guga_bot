# Помощник по заполнению параметров пользователя
# В зависимости от параметра (и ранее введённых других параметров) выдаёт форму ввода (JSON)
# из БД, или заранее заданных форм
from helpers.db_postgres import Db
from helpers.param_forms import speciality_fle, speciality_faitop


def find_first_none(d: dict):
    """Находит первый незаполненный параметр в словаре"""
    for k, value in d.items():
        if value is None:
            return k
    return None


class ParameterHelper:
    def __init__(self, db: Db):
        self.db = db

    def get_user_parameters(self, user_id: int) -> dict:
        user_parameters = self.db.get_dict("""
                SELECT p."name", up.value
                FROM "parameter" p
                LEFT JOIN user_parameter up on p.id = up.parameter_id AND up.user_id = %s
                WHERE p."order" IS NOT NULL
                ORDER BY p.order;
                """, [user_id])
        return user_parameters

    def store_user_parameter(self, user_id: int, name: str, value: str) -> bool:
        """Сохранить присланный пользователем параметр в БД"""
        parameter = self.db.get_line('SELECT * FROM "parameter" WHERE "name" = %s', [name])
        if parameter is None:
            print(f'Введён неизвестный параметр: {name}')
            return False

        # Проверяем, корректные ли данные (соответствуют ли шаблону)
        # if parameter.check_regexp is not None:
        #     regexp = re.compile(parameter.check_regexp)

        # Добавляем/обновляем данные в БД
        self.db.execute("""
                    INSERT INTO user_parameter (user_id, parameter_id, "value") VALUES (%s, %s, %s)
                    ON CONFLICT (user_id, parameter_id) DO UPDATE SET "value" = %s, updated = now()
                """,
                        [user_id, parameter.id, value, value])
        return True

    def get_next_unfilled_param(self, user_id: int) -> (str | None, dict | None):
        """
        Извлекает следующий незаполненный параметр пользователя
        С учётом, что некоторые параметры не имеют смысла (например - номер группы для абитуриентов)
        тогда такой параметр заполняется символом '-' и ищется следующий
        """
        user_parameters = self.get_user_parameters(user_id)
        parameter = find_first_none(user_parameters)
        if parameter is None:
            return None, None
        if parameter == 'faculty':
            if user_parameters.get('status') != 'student':  # Факультет имеет смысл только для студентов
                user_parameters['faculty'] = '-'
                self.store_user_parameter(user_id, 'faculty', '-')
                user_parameters['speciality'] = '-'
                self.store_user_parameter(user_id, 'speciality', '-')
                user_parameters['group'] = '-'
                self.store_user_parameter(user_id, 'group', '-')
                user_parameters['admission_year'] = '-'
                self.store_user_parameter(user_id, 'admission_year', '-')

                return self.get_next_unfilled_param(user_id), user_parameters
            return parameter, user_parameters

        if parameter == 'speciality':
            if user_parameters.get('faculty') not in ['fle', 'faitop']:
                # Специальность указывается только для студентов этих факультетов
                user_parameters['speciality'] = '-'
                self.store_user_parameter(user_id, 'speciality', '-')
                return self.get_next_unfilled_param(user_id), user_parameters

        return parameter, user_parameters

    def get_parameter_input_form(self, user_id: int, parameter: str, user_parameters: dict) -> dict | None:
        """
        Возвращает форму ввода параметра с учётом значения других параметров
        (например - ввод специальности в зависимости от ранее введённого факультета)
        """
        if parameter == 'speciality':
            match user_parameters.get('faculty'):
                case 'fle':
                    return speciality_fle
                case 'faitop':
                    return speciality_faitop
        return None
