from __future__ import print_function
from colorama import Fore, Back, Style, init
from pathlib import Path
import readline, glob

from variables import *


DOT  = ' . '
ARW  = ' :'

ERROR = ["Admin? Please, source openrc to get admin privileges",
         "Wrong input. Aborting...",
         "Quiting..."]

MSG   = ["Wrong input",
         "Checking missing variables..\n",
         "Do you want to add the above user? (y/n) ",
         "Registering user..",
         "Creating base network settings..",
         "Done\n"]


class View:

    c = None
    user = None

    def __init__(self, wrapper):
        self.c    = wrapper.os
        self.user = wrapper.user
        init(autoreset=True)


    # Usado em LIST
    def blue(self, char):
        return Fore.BLUE + str(char) + Style.RESET_ALL

    def magenta(self, char):
        return Fore.MAGENTA + str(char) + Style.RESET_ALL

    def dim(self, char):
        return Fore.LIGHTBLACK_EX + str(char) + Style.RESET_ALL

    # Usado em ADD e SHOW
    def message(self, content):
        print(Fore.BLUE + " . " + Style.RESET_ALL + content)

    def persistent(self, msg):
        print(Fore.BLACK + DOT + Fore.LIGHTBLACK_EX + str(msg) + Style.RESET_ALL)

    def error(self, intg):
        print(Fore.RED + DOT + Style.RESET_ALL + ERROR[intg])

    def notify(self, intg):
        print(Fore.YELLOW + DOT +  Style.RESET_ALL + MSG[intg])

    def info(self, intg):
        try:
            print(Fore.BLACK + DOT + Style.RESET_ALL + MSG[intg])
        except TypeError:
            print(Fore.BLACK + DOT + Style.RESET_ALL + intg)

    def enabled(self, user = None):
        if (user is None):
            user = self.user

        if (user.enabled):
            return (Fore.GREEN + "\033[1mTrue" + Style.RESET_ALL)
        return (Fore.RED + "\033[1mFalse" + Style.RESET_ALL)

    def question(self):
        raw = raw_input('\n' + Fore.BLACK + " : " + Style.RESET_ALL + MSG[2])
        return raw

    def show_keystone_basic(self):
        print('')
        self.message("Username:       %s" % self.user.name)
        self.message("Email:          %s" % self.user.email)

    def show_keystone_full(self):
        self.show_keystone_basic()
        self.persistent("Project Name:   %s" % self.user.project_name)
        self.persistent("Password:       %s" % self.user.password)
        self.persistent("Enabled:        %s" % self.enabled())

    def show_project(self, user, p):
        print('')

        self.info('Username:   %s' % user.name)
        self.info('Email:      %s' % user.email)
        self.info('Enabled:    %s' % self.enabled(user))
        print('')
        self.info('Project Name:   %s' % p.name)
        self.info('Description:    %s' % p.email)
        self.info('Enabled:        %s' % self.enabled(p))

        print('')

        if user.enabled is True:
            self.info('Active for %d days ' % user.history.activity())
        else:
            self.info('Deactivated for %d days' % user.history.activity())
