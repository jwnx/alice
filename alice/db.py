from datetime import datetime
import sqlite3
from psycopg2 import connect
import dataset
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sqlalchemy

class DBManager():

    db = None
    location = 'postgresql://alice@localhost:5432/alice'

    def __init__(self):
        self.connect()

    def connect(self):
        self.db = dataset.connect()

    def drop(self):
        self.db['user'].drop()

    def insert_record(self, user):
        today = datetime.today()
        self.db.begin()
        try:
            self.db['user'].insert(dict(name=user['username'],
                                        email=user['email'],
                                        user_id=user['user_id'],
                                        created_at=today))
            self.db.commit()
        except:
            self.db.rollback()

    def select_all(self):
        return self.db['user']
