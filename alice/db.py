import sqlite3
from datetime import date

class DBManager():

    conn     = None
    cursor   = None
    location = '/etc/alice/alice.db'
    table_name = 'users'

    def __init__(self):
        self.connect()

    def create_database(self):
        sql = 'create table if not exists ' + self.table_name + ' (id integer not null primary key autoincrement, \
                       name text not null,  \
                       email text not null, \
                       user_id text not null, \
                       created_at date not null)'

        self.cursor.execute(sql)
        self.conn.commit()

    def connect(self):
        self.conn   = sqlite3.connect(self.location, detect_types=sqlite3.PARSE_DECLTYPES)
        self.cursor = self.conn.cursor()

    def clear_database(self):
        sql = 'drop table ' + table_name
        self.c.execute(sql)
        self.conn.commit()

    def remake():
        clear_database()
        create_database()
        insert_record(1)
        self.conn.commit()

    def insert_record(self, user):
        today = date.today()
        sql = 'insert into ' + self.table_name +  ' (name, email, user_id, created_at) values (?, ?, ?, ?)'
        self.cursor.execute(sql, (user['username'], user['email'], user['user_id'], today))
        self.conn.commit()

    def reconnect(self):
        self.close()
        self.connect()

    def select_all(self):
        self.cursor.execute('select * from ' + self.table_name)
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()
