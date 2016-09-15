from history import History
from user    import User
from dateparser import DateParser


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
from alice.openstack_bridge import OpenstackBridge
from alice.view import View
import ast

yes  = set(['yes', 'y', 'ye'])
no   = set(['no', 'n'])
edit = set(['e', 'edit'])
ARW  = ' >'


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


    def generate_user_data(self, name, email, enabled, expire):

        user = User()

        user.name = name
        user.email = email
        user.enabled = enabled

        if (self.represent_int(expire)):
            expire = str(expire) + "d"

        user.expiration = (timestring.Range("next " + expire)).end

        project_name = (user.name).title() + "'s project"
        password     = self.generate_password()

        user.project_name = project_name
        user.password = password

        return user
        

    def add(self, name, email, enabled, expire, yes):
        user = self.generate_user_data(name, email, enabled, expire)
        self.view.show_full_info(user)

        if not yes:
            self.confirmation()
        self.create_user(user)

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

    def migrate(self):
        db = self.db

        all_users = self.os.get_all_users()

        services = ['ceilometer', 'nova', 'neutron', 'glance', 'keystone', 'admin']

        for user in all_users.list():
            if user.name not in services:
                try:
                    found = db.select_by_email(user.email)

                    if found is None:
                        u = User()

                        u.user_id = user.id
                        u.project_id = user.default_project_id
                        u.email = user.email
                        u.enabled = user.enabled
                        u.name = user.name
                        u.expiration = (timestring.Range("next 30d")).end
                        u.history.register()

                        db.insert_record(u)
                except:
                    continue


    def db_add_user(self, user):
        db = self.db
        db.insert_record(user)

    def create_user(self, user):
        print
        warnings.filterwarnings("ignore")

        self.view.info(3)
        # self.os.register_user(user)
        self.view.info(4)
        # self.os.create_network(user)
        user.history.register()
        self.db_add_user(user)

        # if (user.enabled is False):
        #     self.os.update_user({'user_id':user.user_id,
        #                          'project_id': user.project_id,
        #                          'enabled':False })

        self.view.notify(5)

    def update_user(self, id, dict):

        db = self.db
        u  = self.get_user(id)

        user = User()
        user.load(u)

        dict['project_id'] = user.project_id
        dict['user_id']    = user.user_id

        if 'name' in dict:
            user.name = dict['name']

        if 'email' in dict:
            user.email = dict['email']

        if 'enabled' in dict:
            if (isinstance(dict['enabled'], unicode)):
                try:
                    v = ast.literal_eval(dict['enabled'].title())
                    setattr(user, 'enabled', v)
                    dict['enabled'] = v
                except:
                    sys.exit(0)
            else:
                user.enabled = dict['enabled']
            user.history.register()

        if 'expiration' in dict:
            if user.enabled:
                exp = timestring.Date(user.expiration) + str(dict['expiration'])
                user.expiration = exp
            else:
                print " . user %s is not enabled." % (user.name)
                return

        # self.os.update_user(dict)
        self.db.update(user)

    def retrieve_user(self, email):
        db = self.db
        load = self.get_user(email)

        if load is None:
            print "No user found"
            sys.exit()
        else:
            self.user.load(load)
            # p = self.os.get_project(self.user)
            self.view.show_project(self.user, p)
            # self.view.show_project(self.user)

    def confirmation(self):
        add = ''
        while (add not in yes) and (add not in no):
            add = self.view.question()
            if (add not in yes) and (add not in no):
                self.view.error(1)
                sys.exit()
            if add in yes:
                return true
            else:
                self.view.error(2)
                sys.exit()

    def list(self, highlight, filter):

        status = ''
        db     = self.db
        fetch  = None

        if filter is not None and filter != "disabled":
            fetch = db.find_enabled(True)
        elif (filter == "disabled"):
            fetch = db.find_enabled(False)
        else:
            fetch  = db.select_all()

        t      = PrettyTable(['ID', 'Name', 'Email', 'Status', 'Expires in'])
        status = None

        t.borders = False
        t.vrules  = 2

        for row in fetch:

            u = User()
            u.load(row)


            if u.expiration is None and u.enabled is True:
                exp = u.history.last_seen() + "30d"
                self.db.add_expiration(u.id, exp)
                u.expiration = exp

            if u.enabled is True:

                elapsed = (u.history.time_left()).elapse
                try:
                    elapsed = elapsed[:elapsed.index("hour") + 5]
                except:
                    elapsed = elapsed[:elapsed.index("min") + 7]

                state = DateParser(u.history.time_left()).state

                v = [u.id, u.name, u.email, state.title(), elapsed]

                if highlight is True:
                    if state == 'expired':
                        v[0] = self.view.RED(v[0])
                        v[-1] = self.view.RED(v[-1]) + self.view.NORMAL()
                    if state == 'hold':
                        v[0] = self.view.YELLOW(v[0])
                        v[-1] = self.view.YELLOW(v[-1]) + self.view.NORMAL()
                else:
                    if state == 'expired':
                        for i in range(0, len(v)):
                            v[i] = self.view.red(v[i])
                    if state == 'hold':
                        for i in range(0, len(v)):
                            v[i] = self.view.yellow(v[i])

                if str(filter) == state or filter is None or filter == "enabled":
                    t.add_row(v)

            else:
                status = 'Disabled'
                t.add_row([self.view.dim(u.id),
                          self.view.dim(u.name),
                          self.view.dim(u.email),
                          self.view.dim(status),
                          self.view.dim("---")])


        print t
