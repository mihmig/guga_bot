# Модуль работы со свойствами системы, хранящимися в БД
from helpers.db_postgres import Db


class PropertyHelper:
    def __init__(self, config, db: Db):
        self.db = db
        self.config = config

    def update_one(self, key, value):
        path = key.split('.')
        if len(path) == 1:
            self.config[path[0]] = value
        elif len(path) == 2:
            if path[0] in self.config:
                self.config[path[0]][path[1]] = value
            else:
                self.config[path[0]] = {path[1]: value}

    def update(self):
        db_config = self.db.get_dict("SELECT name, value FROM property")
        for i, (key, value) in enumerate(db_config.items()):
            self.update_one(key, value)

    def set(self, key, value=None):
        exists = self.db.get_value('SELECT "name" FROM property WHERE "name" = %s', [key])
        if exists:
            self.db.execute('UPDATE property SET value = %s WHERE "name" = %s', [value, key])
        else:
            self.db.execute('INSERT INTO property ("name", value) VALUES (%s, %s) ', [key, value])
        self.update_one(key, value)
