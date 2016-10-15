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


def FRYELLOW(char):
    return Fore.YELLOW + str(char) + Style.RESET_ALL

def FRRED(char):
    return Fore.RED + str(char) + Style.RESET_ALL

def BGYELLOW(char):
    return Back.YELLOW + Fore.BLACK + str(char)

def BGRED(char):
    return Back.RED + Fore.BLACK + str(char)

def NORMAL():
    return Style.RESET_ALL

def FRDIM(char):
    return Fore.LIGHTBLACK_EX + str(char) + Style.RESET_ALL

    # Usado em ADD e SHOW
def MSG(content):
    print(Fore.BLUE + " . " + Style.RESET_ALL + content)

def PERSISTENT(msg):
    print(Fore.BLACK + DOT + FRDIM(msg))

def ERROR(intg):
    print(Fore.RED + DOT + Style.RESET_ALL + ERROR[intg])

def NOTIFY(intg):
    print(Fore.YELLOW + DOT +  Style.RESET_ALL + MSG[intg])

def INFO(intg):
    try:
        print(Fore.BLACK + DOT + Style.RESET_ALL + MSG[intg])
    except TypeError:
        print(Fore.BLACK + DOT + Style.RESET_ALL + intg)

def ENABLED(user):
    if (user.enabled):
        return (Fore.GREEN + "\033[1mTrue" + Style.RESET_ALL)
    return (Fore.RED + "\033[1mFalse" + Style.RESET_ALL)

def GET_INPUT(intg):
    raw = raw_input('\n' + Fore.BLACK + " : " + Style.RESET_ALL + MSG[intg])
    return raw

def show_basic_info(user):
    print('')
    MSG("Username:       %s" % user.name)
    MSG("Email:          %s" % user.email)

def show_full_info(user):
    show_basic_info(user)
    PERSISTENT("Project Name:   %s" % user.project_name)
    PERSISTENT("Password:       %s" % user.password)
    PERSISTENT("Enabled:        %s" % ENABLED(user))

def show_project(user, p):
    print('')
    INFO('Username:       %s' % user.name)
    INFO('Email:          %s' % user.email)
    INFO('Project Name:   %s' % p.name)
    INFO('P Description:  %s' % p.description)
    INFO('Enabled:        %s' % self.enabled(user))
    INFO('Expires at:     %s' % user.expiration.format("%d %b %Y"))
    print('')

    if user.enabled is True:
        INFO('Active for %s ' % user.history.activity())
    else:
        INFO('Deactivated for %s' % user.history.activity())

    print('')
