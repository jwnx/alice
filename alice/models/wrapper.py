from history     import History
from user        import User
from bridge      import OpenstackBridge
from db          import DBManager
from dateparser  import DateParser
from xkcdpass    import xkcd_password as xp
from prettytable import PrettyTable
from alice.view  import *

import timestring
import warnings
import sys
import json
import ast


def is_int(obj):
    try:
        int(obj)
        return True
    except ValueError:
        return False

class Wrapper:

    os   = None
    db   = None

    def __init__(self):
        self.os    = OpenstackBridge()
        self.db    = DBManager()

    def __generate_user_data(self, name, email, enabled, expire):

        user = User()

        user.name = name
        user.email = email
        user.enabled = enabled

        if (is_int(expire)):
            expire = str(expire) + "d"

        user.expiration = (timestring.Range("next " + expire)).end

        project_name = (user.name).title() + "'s project"
        password     = __generate_password()

        user.project_name = project_name
        user.password = password

        return user

    def __generate_password(self):
        wordfile = xp.locate_wordfile()
        mywords  = xp.generate_wordlist(wordfile=wordfile,
                                        min_length=4,
                                        max_length=5)
        new_pass = xp.generate_xkcdpassword(mywords,
                                            delimiter=".",
                                            numwords=4)
        return new_pass

    #  __get_user_data
    #  Receives an ID, which can be a name, email or INT, and
    #  returns the data associated.
    def __get_user_data(self, obj):
        db = self.db
        data = None

        if (is_int(obj)):
            data = db.select_by('id', obj)
        elif obj.find('@') >= 0:
            data = db.select_by('email', obj)
        else:
            data = db.select_by('name', obj)

        if data is None:
            sys.exit(0)

        return data


    def __db_add_user(self, user):
        db = self.db
        db.insert(user)

    def __create_user(self, user):
        print
        warnings.filterwarnings("ignore")

        INFO(3)
        # self.os.register_user(user)
        INFO(4)
        # self.os.create_network(user)
        user.history.register()
        self.__db_add_user(user)

        # if (user.enabled is False):
        #     self.os.update_user({'user_id':user.user_id,
        #                          'project_id': user.project_id,
        #                          'enabled':False })

        NOTIFY(5)


    def __update_user(self, id, dict):

        db = self.db
        u  = self.__get_user_data(id)

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
                exp = timestring.Date(dict['expiration'])
                user.expiration = exp
            else:
                MSG("user "+ user.name + " is not enabled")
                return

        # self.os.update_user(dict)
        self.db.update(user)


    def __confirmation(self):

        yes  = set(['yes', 'y', 'ye'])
        no   = set(['no', 'n'])

        add = ''
        while (add not in yes) and (add not in no):
            add = GET_INPUT(2)
            if (add not in yes) and (add not in no):
                ERROR(1)
                sys.exit()
            if add in yes:
                break
            else:
                ERROR(2)
                sys.exit()

    def __line_highlight(self, line, color):
        line[0] = color(line[0])
        line[-1] = color(line[-1]) + NORMAL()

    def __line_color(self, line, color):
        for i in range(0, len(line)):
            line[i] = FRRED(line[i])

    #  ADD
    #  Generates user information given name and email.
    #  Gets confirmation if needed and adds user to the
    #  database.
    def add(self, name, email, enabled, expire, yes):

        user = __generate_user_data(name, email, enabled, expire)

        show_full_info(user)
        if not yes:
            self.__confirmation()
        self.__create_user(user)

    #  SHOW
    #  Displays user information retrieved from the database.
    #  Receives an id, which can be a name, an email or an INT.
    def show(self, id):

        u  = User()
        load = self.__get_user_data(id)
        u.load(load)
        show_full_info(u)
        # p = self.os.get_project(u)
        # show_project(u, p)
        # show_project(u)

    #  DELETE
    #  Deletes one or multiple users from the database.
    #  Receives an id, which can be a name, an email or an INT.
    #  TODO: Delete Openstack credentials.
    def delete(self, list):

        for id in list:
            u = self.__get_user_data(id)
            # self.db.delete(u)

    #  MODIFY
    #  Modifies users information, both from database and Openstack.
    #  Receives an id, which can be a name, an email or an INT, and
    #  a dictionary with fields to modify.
    def modify(self, id, dict):
        self.__update_user(id, dict)


    #  MIGRATE
    #  Takes users who are in Openstacks database and copies them
    #  over Alice database. Ignores duplicates, services and admin.
    def migrate(self):
        db = self.db

        all_users = self.os.get_user()

        services = ['ceilometer', 'nova', 'neutron', 'glance', 'keystone', 'admin']

        for user in all_users:
            if user.name not in services:
                try:
                    found = db.select_by('email', user.email)

                    if found is None:
                        u = User()

                        u.user_id = user.id
                        u.project_id = user.default_project_id
                        u.email = user.email
                        u.enabled = user.enabled
                        u.name = user.name
                        u.expiration = (timestring.Range("next 30d")).end
                        u.history.register()

                        db.insert(u)
                except:
                    continue

    #  LIST
    #  Retrieves users given a filter from the database and displays
    #  in a table manner.
    def list(self, highlight, filter):

        db     = self.db
        fetch  = None

        # List filter select
        if filter is not None and filter != "disabled":
            fetch = db.find_enabled(True)
        elif (filter == "disabled"):
            fetch = db.find_enabled(False)
        else:
            fetch = db.select_all()

        t = PrettyTable(['ID', 'Name', 'Email', 'Status', 'Expires in'])

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

                # String too long
                try:
                    elapsed = elapsed[:elapsed.index("hour") + 5]
                except:
                    elapsed = elapsed[:elapsed.index("min") + 7]

                # On hold, expired or active
                state = DateParser(u.history.time_left()).state

                v = [u.id, u.name, u.email, state.title(), elapsed]

                # Enables highlight
                if highlight is True:
                    if state == 'expired': self.__line_highlight(v, BGRED)
                    if state == 'hold':    self.__line_highlight(v, BGYELLOW)
                else:
                    if state == 'expired': self.__line_color(v, FRRED)
                    if state == 'hold':    self.__line_color(v, FRYELLOW)

                if str(filter) == state or filter is None or filter == "enabled":
                   t.add_row(v)

            else:
                state = 'Disabled'
                t.add_row([FRDIM(u.id),
                          FRDIM(u.name),
                          FRDIM(u.email),
                          FRDIM(state),
                          FRDIM("---")])


        print t
