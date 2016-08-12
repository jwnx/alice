from datetime import date, datetime
import json

class User:

    name         = None
    email        = None
    password     = 'pass'

    user_id      = ''
    project_name = 'project'
    project_id   = ''
    domain       = 'default'
    ext_net      = ''
    enabled      = True
    created_at   = None

    history = None

    def __init__(self):
        self.name = None
        self.email = None
        self.created_at = datetime.today()
        self.history = History(self)

    def get_info(self):
        return { "username" : self.name, "email": self.email }

# OrderedDict([('id', 10), ('created_at', u'2016-08-10 14:49:07.032305'), ('user_id', u''), ('email', u'teste55'), ('name', u'teste55'), ('project_id', u''), ('enabled', True), ('history', u"{'disabled': [], 'enabled': [datetime.datetime(2016, 8, 10, 14, 49, 6, 998099)]}")])

    def load(self, dict):
        self.name = dict['name']
        self.email = dict['email']
        self.user_id = dict['user_id']
        self.project_id = dict['project_id']
        self.enabled = dict['enabled']
        self.created_at = dict['created_at']
        self.history = History(self, dict['history'])
        

class History:

    user     = None
    enabled  = None
    disabled = None
    state    = None

    def __init__(self, user, str=None):
        self.user = user
        self.load(str)

    def register(self):
        if (self.user.enabled):
            self.enabled.append(datetime.today())
        else:
            self.disabled.append(datetime.today())

    def load(self, str):
        if str is not None:
            dict = json.loads(str)
            self.enabled = dict['enabled']
            self.disabled = dict['disabled']
        else:
            self.enabled = []
            self.disabled = []

    def date_handler(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            raise TypeError

    def to_dict(self):
        return json.dumps({ "enabled": self.enabled, "disabled": self.disabled }, default=self.date_handler)
