from __future__ import print_function
from colorama import Fore, Back, Style, init
from pathlib import Path
import readline, glob

from variables import *


DOT  = ' :'
ARW  = ' >'

ERROR = ["Admin? Please, source openrc to get admin privileges",
         "Wrong input. Aborting...",
         "Quiting..."]

MSG   = ["Wrong input",
         "Checking missing variables..\n",
         "Do you want to add the above user? (y/n) ",
         "Registering user in keystone",
         "Creating base network settings",
         "Done!"]

# MSG = {'CHECK' : '\n : Checking missing variables.. ',
#        'ADD'   : '\n : Do you want to add the above user? (y/n) ',
#        'CERROR': 'Wrong input',
#        'ABORT' : 'Aborting...',
#        'REGK'  : 'Registering user in keystone...',
#        'REGN'  : 'Creating base network settings...'}

class View:

    c = None

    def __init__(self, bridge):
        self.c = bridge
        init(autoreset=True)


    def print_yellow(self, char, title, content):
        print(Fore.YELLOW + char + " " +
              Style.RESET_ALL + Style.BRIGHT +
              title + Style.NORMAL + content)


    def print_black(self, char, title, content):
        print(Fore.BLACK + char + " " +
              Style.RESET_ALL + title +
              Style.DIM + content + Style.RESET_ALL)


    def print_red(self, char, title, content):
        print(Fore.RED + char + " " +
              Style.RESET_ALL + Style.BRIGHT +
              title + Style.NORMAL + content)


    def error(self, intg):
        self.print_red('\n' + DOT, '', ERROR[intg])

    def notify(self, intg):
        self.print_yellow(DOT, '', MSG[intg])

    def info(self, title, intg):
        self.print_black(DOT, title , MSG[intg])

    def process(self, intg):
        print('\n' + DOT + ' ' + MSG[intg])


    def is_enabled(self):
        if (self.c.get('enabled')):
            return (Fore.GREEN + "\033[1mTrue" + Style.RESET_ALL)
        return (Fore.RED + "\033[1mFalse" + Style.RESET_ALL)


    def input_format(self, char, var, content):
        new_var = raw_input(Fore.BLUE + " > " + Style.RESET_ALL + content + Style.BRIGHT)
        print(Style.RESET_ALL, end="")
        self.c.set(var, new_var)

    def input_add(self):
        raw = raw_input('\n' + Fore.BLACK + " > " + Style.RESET_ALL + MSG[2])
        return raw

    def show_keystone_basic(self):
        self.print_yellow(ARW, "Username:     ", self.c.get('username'))
        self.print_yellow(ARW, "Email:        ", self.c.get('email'))


    def show_keystone_full(self):
        self.show_keystone_basic()
        self.print_black(ARW, "Project Name: ", self.c.get('project_name'))
        self.print_black(ARW, "Password:     ", self.c.get('password'))
        self.print_black(ARW, "Enabled:      ", self.is_enabled())
