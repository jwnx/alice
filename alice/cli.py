from xkcdpass import xkcd_password as xp
from pathlib import Path
import readline, glob
import os
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

    # create_user: Method responsible for calling
    # both keystone and neutron methods for Creating
    # an OpenStack user account.
    def create_user(self):

        self.v.print_black(DOT, '', MSG['REGK'])

        try:
            self.c.register_user()
        except Exception as e:
            print 'EXCEPTION KEYSTONE ', e
            sys.exit()

        self.v.print_black(DOT, '', MSG['REGN'])

        try:
            self.c.create_network()
        except Exception as e:
            print 'EXCEPTION NEUTRON ', e
            sys.exit()

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

    def get_input(self):
        options, remainder = getopt.getopt(sys.argv[1:], 'u:e:lk:d',
                             ['username=',
                              'email=',
                              'public-key=',
                              'set-limits',
                              'disable'])

        for opt, arg in options:
            if opt in ('-u', '--username'):
                cli.c.set('username', arg)
            elif opt in ('-e', '--email'):
                cli.c.set('email', arg)
            elif opt in ('-k', '--public-key'):
                cli.c.set('public_key', arg)
            elif opt == '--disable':
                cli.c.set('enabled', False)

        self.check_user_data()
