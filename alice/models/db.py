from datetime import datetime
import sqlite3
from psycopg2 import connect
import dataset
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sqlalchemy

class DBManager():

    db = None
    # location = 'postgresql://alice@localhost:5432/alice'

    def __init__(self):
        self.connect()

    def connect(self):
        self.db = dataset.connect()

    def drop(self):
        self.db['user'].drop()

    def find_enabled(self, enabled):
        return self.db['user'].find(enabled=enabled)

    def insert(self, user):
        self.db.begin()
        try:
            self.db['user'].insert(dict(name=user.name,
                                        email=user.email,
                                        user_id=user.user_id,
                                        created_at=user.created_at,
                                        project_id=user.project_id,
                                        enabled=user.enabled,
                                        expiration=user.expiration,
                                        history=user.history.json()))
            self.db.commit()
        except:
            self.db.rollback()

    def select_all(self):
        return self.db['user']

    def update(self, user):
        self.db.begin()

        try:
            self.db['user'].update(dict(id=user.id,
                                        name=user.name,
                                        email=user.email,
                                        enabled=user.enabled,
                                        expiration=user.expiration,
                                        history=user.history.json()), ['id'])
            self.db.commit()
        except:
            self.db.rollback()

    def select_by_email(self, content):
        return self.db['user'].find_one(email=content)

    def select_by_name(self, content):
        return self.db['user'].find_one(name=content)

    def select_by_id(self, id):
        return self.db['user'].find_one(id=id)

    def add_expiration(self, id, expiration):
        self.db.begin()

        try:
            self.db['user'].update(dict(id=id,
                                        expiration=expiration), ['id'])
            self.db.commit()
        except:
            self.db.rollback()
