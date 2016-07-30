from __future__ import print_function
from colorama import Fore, Back, Style, init
from pathlib import Path
import readline, glob

from variables import *

class View:

    c = None

    def __init__(self, bridge):
        self.c = bridge
        init(autoreset=True)

    def __complete(self, text, state):
        return (glob.glob(text+'*')+[None])[state]


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


    def is_enabled(self):
        if (self.c.get('enabled')):
            return (Fore.GREEN + "\033[1mTrue" + Style.RESET_ALL)
        return (Fore.RED + "\033[1mFalse" + Style.RESET_ALL)


    def input_format(self, char, var, content):

        # readline.set_completer_delims(' \t\n;')
        # readline.parse_and_bind("tab: complete")
        # readline.set_completer(self.__complete)

        new_var = raw_input(Fore.BLUE + " > " + Style.RESET_ALL + content + Style.BRIGHT)
        print(Style.RESET_ALL, end="")

        if (new_var == "" and var == 'public_key'):
            new_var = '~/.ssh/id_rsa.pub'

        self.c.set(var, new_var)

    def show_keystone_basic(self):
        self.print_yellow(ARW, "Username:     ", self.c.get('username'))
        self.print_yellow(ARW, "Email:        ", self.c.get('email'))


    def show_keystone_full(self):
        self.show_keystone_basic()
        self.print_black(ARW, "Project Name: ", self.c.get('project_name'))
        self.print_black(ARW, "Password:     ", self.c.get('password'))
        self.print_black(ARW, "Enabled:      ", self.is_enabled())
