from __future__ import print_function
from colorama import Fore, Back, Style, init
from pathlib import Path
import readline, glob

from alice.config import *


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

    def __init__(self):
        init(autoreset=True)

    # Usado em LIST
    def blue(self, char):
        return Fore.BLUE + str(char) + Style.RESET_ALL

    def magenta(self, char):
        return Fore.MAGENTA + str(char) + Style.RESET_ALL

    def yellow(self, char):
        return Fore.YELLOW + str(char) + Style.RESET_ALL

    def red(self, char):
        return Fore.RED + str(char) + Style.RESET_ALL

    def YELLOW(self, char):
        return Back.YELLOW + Fore.BLACK + str(char)

    def RED(self, char):
        return Back.RED + Fore.BLACK + str(char)

    def NORMAL(self):
        return Style.RESET_ALL

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

    def enabled(self, user):
        if (user.enabled):
            return (Fore.GREEN + "\033[1mTrue" + Style.RESET_ALL)
        return (Fore.RED + "\033[1mFalse" + Style.RESET_ALL)

    def question(self):
        raw = raw_input('\n' + Fore.BLACK + " : " + Style.RESET_ALL + MSG[2])
        return raw

    def show_basic_info(self, user):
        print('')
        self.message("Username:       %s" % user.name)
        self.message("Email:          %s" % user.email)

    def show_full_info(self, user):
        self.show_basic_info(user)
        self.persistent("Project Name:   %s" % user.project_name)
        self.persistent("Password:       %s" % user.password)
        self.persistent("Enabled:        %s" % self.enabled(user))

    def show_project(self, user, p):
        print('')

        self.info('Username:       %s' % user.name)
        self.info('Email:          %s' % user.email)
        self.info('Project Name:   %s' % p.name)
        self.info('P Description:  %s' % p.description)
        self.info('Enabled:        %s' % self.enabled(user))
        self.info('Expires at:     %s' % user.expiration.format("%d %b %Y"))

        print('')

        if user.enabled is True:
            self.info('Active for %s ' % user.history.activity())
        else:
            self.info('Deactivated for %s' % user.history.activity())

        print('')
