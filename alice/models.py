# -*- coding: UTF-8 -*-

from xkcdpass import xkcd_password as xp
from pathlib import Path
from prettytable import PrettyTable
from collections import namedtuple
import timestring
import warnings
import os
import copy
import sys
import getopt
import json
import click
from openstack_bridge import OpenstackBridge
from view import View
import ast


yes  = set(['yes', 'y', 'ye'])
no   = set(['no', 'n'])
edit = set(['e', 'edit'])
ARW  = ' >'

class User:

    id           = 0
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
    description  = None

    history = None

    def __init__(self):
        self.name  = None
        self.email = None
        self.created_at = str(timestring.Date('today'))
        self.history    = History(self)

    def load(self, dict):
        self.id      = dict['id']
        self.name    = dict['name']
        self.email   = dict['email']
        self.user_id = dict['user_id']
        self.enabled = dict['enabled']
        self.project_id = dict['project_id']
        self.created_at = timestring.Date(dict['created_at'])
        self.history    = History(self, dict['history'])

class History:

    user     = None
    enabled  = None
    disabled = None
    state    = None

    def __init__(self, user, str=None):
        self.user = user
        self.load(str)

    # Registra o momento no historico
    def register(self):
        if (self.user.enabled is True):
            self.enabled.append(str(timestring.Date('now')))
        else:
            self.disabled.append(str(timestring.Date('now')))


    # Retorna o ultimo registro feito no historico do usuario
    def last_seen(self):
        if (self.user.enabled is True):
            return timestring.Date(self.enabled[-1])
        return timestring.Date(self.disabled[-1])


    # Calcula o numero de dias ativo ou inativo
    def activity(self):
        r = timestring.Range(self.last_seen(), timestring.Date("now"))
        return int(len(r)/86400)


    # Parse a lista de datas apos acessar o banco de dados
    def parse(self, list):
        a = []
        for element in list:
            a.append(timestring.Date(element))
        return a

    # Encoda a lista de datas para entrar no banco de dados
    def encode(self, list):
        a = []
        for element in list:
            a.append(str(element))
        return a

    # Metodo que converte o objeto em json
    def json(self):
        enabled = self.encode(self.enabled)
        disabled = self.encode(self.disabled)
        return json.dumps({ "enabled": enabled, "disabled": disabled })

    # Carrega uma string em json
    def load(self, str):
        if str is not None:
            dict = json.loads(str)
            self.enabled  = self.parse(dict['enabled'])
            self.disabled = self.parse(dict['disabled'])
        else:
            self.enabled = []
            self.disabled = []



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

    def represent_int(self, obj):
        try:
            int(obj)
            return True
        except ValueError:
            return False

    def generate_password(self):
        wordfile = xp.locate_wordfile()
        mywords  = xp.generate_wordlist(wordfile=wordfile, min_length=4, max_length=5)
        new_pass = xp.generate_xkcdpassword(mywords,delimiter=".",numwords=4)
        return new_pass


    def get_user(self, obj):
        db = self.db
        load = None
        if self.represent_int(obj):
            load = db.select_by_id(obj)
        elif obj.find('@') >= 0:
            load = db.select_by_email(obj)
        else:
            load = db.select_by_name(obj)
        return load


    def add_user(self):
        db = self.db
        db.insert_record(self.user)

    def create_user(self):
        print
        warnings.filterwarnings("ignore")

        self.view.info(3)
        self.os.register_user(self.user)
        self.view.info(4)
        self.os.create_network(self.user)
        self.user.history.register()
        self.add_user()

        if (self.user.enabled is False):
            self.os.update_user(self.user.user_id, self.user)

        self.view.notify(5)

    def update_user(self, id, dict):

        um = ['name', 'password', 'email', 'enabled']
        pm = ['description', 'project_name']

        umod = {'user':{}}
        pmod = {'project':{}}

        db = self.db
        u  = self.get_user(id)

        user = User()
        user.load(u)

        umod["user"]["id"] = user.user_id
        pmod["project"]["id"] = user.project_id

        if 'name' in dict:
            user.name = dict['name']

        if 'email' in dict:
            user.email = dict['email']

        if 'enabled' in dict:
            if (isinstance(dict[key], unicode)):
                try:
                    v = ast.literal_eval(dict[key].title())
                    setattr(user, key, v)
                    dict[key] = v
                except:
                    sys.exit(0)
            else:
                user.enabled = dict[key]
            user.history.register()

        for key in dict:
            if key in um:
                umod["user"][key] = dict[key]
            elif key in pm:
                pmod["project"][key] = dict[key]

        ju = json.dumps(umod)
        jp = json.dumps(pmod)

        self.os.update_user(ju, jp)
        self.db.update(user)

    def retrieve_user(self, email):
        db = self.db
        load = self.get_user(email)
        self.user.load(load)
        p = self.os.get_project(self.user)
        self.view.show_project(self.user, p)

    def confirmation(self):
        add = ''
        self.view.show_keystone_full()
        while (add not in yes) and (add not in no):
            add = self.view.question()
            if (add not in yes) and (add not in no):
                self.view.error(1)
                sys.exit()
            if add in yes:
                self.create_user()
            else:
                self.view.error(2)
                sys.exit()

    def list(self, enabled, disabled):

        status = ''
        db     = self.db
        fetch  = None

        if (enabled != disabled):
            fetch = db.find_enabled(enabled)
        else:
            fetch  = db.select_all()

        t      = PrettyTable(['ID', 'Name', 'Email', 'Status'])
        status = None

        t.borders = False
        t.vrules  = 2

        for row in fetch:
            u = User()
            u.load(row)

            if u.enabled is True:
                status = self.view.blue('Enabled')
                t.add_row([u.id,
                          u.name,
                          u.email,
                          status + ' for ' +
                          str(u.history.activity()) + ' days'])
            else:
                status = 'Disabled'
                t.add_row([self.view.dim(u.id),
                          self.view.dim(u.name),
                          self.view.dim(u.email),
                          self.view.dim(status + ' for ' +
                          str(u.history.activity()) + ' days')])


        print t
