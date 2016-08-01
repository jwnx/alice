from xkcdpass import xkcd_password as xp
from pathlib import Path
from prettytable import PrettyTable
import os
import sys
import getopt

from datetime import date, datetime
from openstack_bridge import OpenstackBridge

yes  = set(['yes', 'y', 'ye'])
no   = set(['no', 'n'])
edit = set(['e', 'edit'])

class Cli:

    c = None
    v = None

    def __init__(self):
        self.c = OpenstackBridge()
        self.v = self.c.v
        self.get_input()

    # check_user_data: This method checks if any user data
    # is missing and updates it if necessary
    def check_user_data(self):
        self.v.process(1)
        var = self.c.get_var()
        if (var['username'] == None or var['email'] == None):
            self.update_user_data()
        self.create_user_profile()
        self.keystone_confirmation()


    def add_user_to_db(self):
        db = self.c.db
        db.connect()
        db.insert_record(self.c.user)

    # create_user: Method responsible for calling
    # both keystone and neutron methods for Creating
    # an OpenStack user account.
    def create_user(self):

        print
        self.v.info('Keystone: ', 3)
        self.c.register_user()
        self.v.info('Neutron: ', 4)
        self.c.create_network()

        self.add_user_to_db()
        self.v.notify(5)


    def create_user_profile(self):
        project_name = self.c.get('username').title() + "'s project"
        password = self.generate_password()
        self.c.set('project_name', project_name)
        self.c.set('password', password)

    def generate_password(self):
        wordfile = xp.locate_wordfile()
        mywords = xp.generate_wordlist(wordfile=wordfile, min_length=4, max_length=5)
        new_pass = xp.generate_xkcdpassword(mywords,delimiter=".",numwords=4)
        return new_pass

    def update_user_data(self):
        user_var = self.c.get_var()
        for var in user_var:
            if user_var[var] is None:
                self.v.input_format(ARW, var, "%s: " % var.title())
        print

    def usage(self):
        print("usage: alice [-a] [-l] [-u USERNAME] [-e EMAIL]")
        print("\noptional arguments:")
        print(" -h, --help                 Shows this help message and exit.")
        print(" -a, --add                  Creates a new user and project in OpenStack.")
        print(" -u, --username USERNAME    Specify the USERNAME to be used when adding a new user.")
        print(" -e, --email    EMAIL       Specify the EMAIL to be used when adding a new user.")
        print("     --disable              Disables the user that is being created.")
        print(" -l, --list                 Lists all users added to Openstack by alice.")
        # print("LIST: " + sys.argv[0] + " --list")

    def keystone_confirmation(self):
        add = ''
        self.v.show_keystone_full()
        while (add not in yes) and (add not in no):
            add = self.v.input_add()
            if (add not in yes) and (add not in no):
                self.v.error(1)
                sys.exit()
            if add in yes:
                self.create_user()
            else:
                self.v.error(2)
                sys.exit()

    def list(self):
        db = self.c.db
        db.connect()
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

    def get_input(self):

        ADD_FLAG  = False
        LIST_FLAG = False
        HELP_FLAG = False

        try:
            options, remainder = getopt.getopt(sys.argv[1:], 'au:e:ldh',
                             ['add',
                              'username=',
                              'email=',
                              'list',
                              'help',
                              'disable'])
            if not options:
                self.usage()

        except getopt.GetoptError,e:
            print e
            self.usage()
            sys.exit()

        for opt, arg in options:
            if opt in ('-u', '--username'):
                self.c.set('username', arg)
            elif opt in ('-e', '--email'):
                self.c.set('email', arg)
            elif opt == '--disable':
                self.c.set('enabled', False)
            elif opt in ('-a','--add'):
                ADD_FLAG = True
            elif opt in ('-l', '--list'):
                LIST_FLAG = True
            elif opt in ('-h', '--help'):
                HELP_FLAG = True

        if(ADD_FLAG != LIST_FLAG):
            if(ADD_FLAG):
                self.check_user_data()
            if(LIST_FLAG):
                self.list()
        elif ((ADD_FLAG == True and ADD_FLAG == LIST_FLAG) or HELP_FLAG):
            self.usage()
