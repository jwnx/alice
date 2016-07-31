from xkcdpass import xkcd_password as xp
from pathlib import Path
import readline, glob
import os
import sys
import getopt
import sys

from variables import *
from openstack_bridge import OpenstackBridge

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
        print(MSG['CHECK'] + '\n')
        var = self.c.get_var()
        if (var['username'] == None or var['email'] == None):
            self.update_user_data()
        self.create_user_profile()
        self.keystone_confirmation()



    def add_user_to_db(self):
        db = self.c.db
        db.connect()
        db.create_database()
        db.insert_record(self.c.user)
        db.close()

    # create_user: Method responsible for calling
    # both keystone and neutron methods for Creating
    # an OpenStack user account.
    def create_user(self):

        self.v.print_black(DOT, '', MSG['REGK'])

        # try:
        #     self.c.register_user()
        # except Exception as e:
        #     print 'EXCEPTION KEYSTONE ', e
        #     sys.exit()

        self.v.print_black(DOT, '', MSG['REGN'])

        # try:
        #     self.c.create_network()
        # except Exception as e:
        #     print 'EXCEPTION NEUTRON ', e
        #     sys.exit()

        self.add_user_to_db()
        self.v.print_yellow(DOT, '', "Done! \n")


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
        print("alice --add -u=username -e=email")
        print("alice --list")

    def keystone_confirmation(self):
        add = ''
        self.v.show_keystone_full()
        while (add not in yes) and (add not in no):
            add = raw_input(MSG['ADD'])
            if (add not in yes) and (add not in no):
                self.v.print_yellow(DOT, '', MSG['CERROR'])
            if add in yes:
                self.create_user()
            else:
                self.v.print_red(DOT, '', MSG['ABORT'] + '\n')
                sys.exit()

    def list(self):
        db = self.c.db
        db.connect()
        fetch = db.select_all()
        for linha in fetch:
            print linha

    def get_input(self):

        ADD_FLAG  = False
        LIST_FLAG = False

        try:
            options, remainder = getopt.getopt(sys.argv[1:], 'au:e:ldh',
                             ['add',
                              'username=',
                              'email=',
                              'list',
                              'help',
                              'disable'])
            if not options:
                print 'No options supplied'
                self.usage()

        except getopt.GetoptError,e:
            print e
            self.usage()
            sys.exit(2)

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

        if(ADD_FLAG != LIST_FLAG):
            if(ADD_FLAG):
                self.check_user_data()
            if(LIST_FLAG):
                self.list()
        else:
            self.usage()
