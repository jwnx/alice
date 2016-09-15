from history import History
import timestring


class User:

    id           = 0
    name         = None
    email        = None
    password     = 'pass'

    user_id      = ''
    project_name = 'project'
    project_id   = ''
    domain       = 'default'
    enabled      = True
    description  = None
    expiration   = None

    # Auto Generated
    created_at   = None
    history = None

    def __init__(self):
        self.name  = None
        self.email = None
        self.created_at = str(timestring.Date('today'))
        self.history    = History(self)

    def load(self, dict):
        self.id      = dict['id']
        self.name    = dict['name']
        self.email   = dict['email']
        self.user_id = dict['user_id']
        self.enabled = dict['enabled']
        self.expiration = timestring.Date(dict['expiration'])
        self.project_id = dict['project_id']
        self.created_at = timestring.Date(dict['created_at'])
        self.history    = History(self, dict['history'])
