from datetime import date, datetime
from xkcdpass import xkcd_password as xp
from pathlib import Path
from prettytable import PrettyTable
from collections import namedtuple
import warnings
import os
import sys
import getopt
import json
import click
from openstack_bridge import OpenstackBridge
from view import View


yes  = set(['yes', 'y', 'ye'])
no   = set(['no', 'n'])
edit = set(['e', 'edit'])
ARW  = ' >'

class Parser(object):

    def __init__(self, string):
        self.element = string

    def date(self):
        if (isinstance(self.element, unicode)):
            try:
                created = self.element[:self.element.rindex("T")+9]
                string = datetime.strptime(created, '%Y-%m-%dT%H:%M:%S')
            except:
                created = self.element[:self.element.rindex(" ")+9]
                string = datetime.strptime(created, '%Y-%m-%d %H:%M:%S')
            return string

        elif (isinstance(self.element, list)):
            a = []
            for e in self.element:
                a.append(Parser(e).date())
            return a

class User:

    name         = None
    email        = None
    password     = 'pass'

    user_id      = ''
    project_name = 'project'
    project_id   = ''
    domain       = 'default'
    ext_net      = ''
    enabled      = True
    created_at   = None

    history = None

    def __init__(self):
        self.name = None
        self.email = None
        self.created_at = datetime.today()
        self.history = History(self)

    def get_info(self):
        return { "username" : self.name, "email": self.email }

    def load(self, dict):
        self.name = dict['name']
        self.email = dict['email']
        self.user_id = dict['user_id']
        self.project_id = dict['project_id']
        self.enabled = dict['enabled']

        # Trata o parse de string para datetime
        self.created_at = Parser(dict['created_at']).date()
        self.history = History(self, dict['history'])


class History:

    user     = None
    enabled  = None
    disabled = None
    state    = None

    def __init__(self, user, str=None):
        self.user = user
        self.load(str)

    def register(self):
        if (self.user.enabled):
            self.enabled.append(datetime.today())
        else:
            self.disabled.append(datetime.today())

    def load(self, str):
        if str is not None:
            dict = json.loads(str)
            self.enabled = Parser(dict['enabled']).date()
            self.disabled = Parser(dict['disabled']).date()
        else:
            self.enabled = []
            self.disabled = []

    def last_seen(self):
        if (self.user.enabled is True):
            return self.enabled[-1]
        return self.disabled[-1]

    def activity(self):
        return (datetime.today() - self.last_seen()).days

    def date_handler(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            raise TypeError

    def to_dict(self):
        return json.dumps({ "enabled": self.enabled, "disabled": self.disabled }, default=self.date_handler)



class Wrapper:

    os   = None
    view = None
    db   = None
    user = None

    def __init__(self):
        self.os    = OpenstackBridge()
        self.user  = User()
        self.view  = View(self)
        self.db    = self.os.db

    def generate_user(self, name, email, enabled):
        self.user.name = name
        self.user.email = email
        self.user.enabled = enabled

        project_name = (self.user.name).title() + "'s project"
        password     = self.generate_password()

        self.user.project_name = project_name
        self.user.password = password

    def verify(self, name, email, enabled):
        self.generate_user(name, email, enabled)
        self.confirmation()

    def automatic(self, name, email, enabled):
        self.generate_user(name, email, enabled)
        self.view.show_keystone_full()
        self.create_user()

    def generate_password(self):
        wordfile = xp.locate_wordfile()
        mywords  = xp.generate_wordlist(wordfile=wordfile, min_length=4, max_length=5)
        new_pass = xp.generate_xkcdpassword(mywords,delimiter=".",numwords=4)
        return new_pass

    def add_user(self):
        db = self.db
        db.insert_record(self.user)

    def create_user(self):
        print
        warnings.filterwarnings("ignore")
        self.view.info('Keystone: ', 3)
        # self.os.register_user(self.user)
        self.view.info('Neutron: ', 4)
        # self.os.create_network(self.user)
        self.user.history.register()
        # print self.user.history.to_dict()
        self.add_user()
        self.view.notify(5)

    def retrieve_user(self, email):
        db = self.db
        load = db.select_by_email(email)
        self.user.load(load)
        self.view.show_account()

    def confirmation(self):
        add = ''
        self.view.show_keystone_full()
        while (add not in yes) and (add not in no):
            add = self.view.input_add()
            if (add not in yes) and (add not in no):
                self.view.error(1)
                sys.exit()
            if add in yes:
                self.create_user()
            else:
                self.view.error(2)
                sys.exit()

    def list(self):
        db = self.db
        fetch = db.select_all()
        t = PrettyTable(['ID', 'Name', 'Email', 'Created At', 'Uptime'])
        for row in fetch:
            created = row['created_at']
            if (isinstance(created, unicode)):
                created = row['created_at'][:row['created_at'].rindex(" ")+9]
                created = datetime.strptime(created, '%Y-%m-%d %H:%M:%S')
            t.add_row([row['id'], row['name'], row['email'], created,
                     (datetime.today() - created).days])
        print t
