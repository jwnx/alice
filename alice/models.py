from datetime import date, datetime
import ast

class User:

    username     = None
    email        = None
    password     = 'pass'

    user_id      = ''
    project_name = 'project'
    project_id   = ''
    domain       = 'default'
    ext_net      = ''
    enabled      = True

    history = None

    def __init__(self):
        self.username = None
        self.email = None
        self.history = History(self)

    def get_info(self):
        return { 'username' : self.username, 'email': self.email }


class History:

    user     = None
    enabled  = None
    disabled = None
    state    = None

    def __init__(self, user, str=None):
        self.user = user

        if str is not None:
            dict = ast.literal_eval(str)
            self.enabled = dict['enabled']
            self.disabled = dict['disabled']
        else:
            self.enabled = []
            self.disabled = []

    def register(self):
        if (self.user.enabled):
            self.enabled.append(datetime.today())
        else:
            self.disabled.append(datetime.today())

    def to_dict(self):
        return { 'enabled': self.enabled, 'disabled': self.disabled }
