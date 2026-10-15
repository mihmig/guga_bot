# Модуль взаимодействия с базой данных
import psycopg2
import psycopg2.extras
from typing import List


class Db:
    def __init__(self, config, autocommit=True):
        self.conn = psycopg2.connect(dbname=config['dbname'],
                                     user=config['user'],
                                     password=config['password'],
                                     host=config['host'],
                                     port=config['port'])

        self.conn.autocommit = autocommit

    def commit(self):
        self.conn.commit()

    # Получение одного значения
    def get_value(self, query: str, params: list = None) -> str | None:
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        if row is None:
            return None
        return row[0]

    # Получение одного кортежа
    def get_line(self, query: str, params: list = None) -> psycopg2.extras.NamedTupleCursor | None:
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
        cursor.execute(query, params)
        row = cursor.fetchone()
        cursor.close()
        return row

    # Получение одного столбца
    def get_column(self, query: str, params: list = None) -> List:
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        result = list()
        for row in rows:
            result.append(row[0])
        cursor.close()
        return result

    # Получение словаря (набор id->value)
    def get_dict(self, query: str, params: list = None):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        result = {}
        records = cursor.fetchall()
        for r in records:
            result[r[0]] = r[1]
        cursor.close()
        return result

    # Получение множества строк (именованные кортежи)
    def get_data(self, query: str, params: list = None):
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
        cursor.execute(query, params)
        return cursor.fetchall()

    # Выполнение произвольного запроса к БД
    def execute(self, query: str, params: list = None) -> object:
        cursor = self.conn.cursor()
        result = cursor.execute(query, params)
        cursor.close()
        return result

    # Вставка строки в таблицу с автогенерируемым столбцом (id) и возврат полученного значения id
    def insert(self, query: str, params: list = None) -> str:
        return self.get_value(query, params)
