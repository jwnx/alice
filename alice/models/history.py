import timestring
import json


class History:

    user     = None
    enabled  = None
    disabled = None
    state    = None

    def __init__(self, user, str=None):
        self.user = user
        self.load(str)

    # Registra o momento no historico
    def register(self):
        if (self.user.enabled is True):
            self.enabled.append(str(timestring.Date('now')))
        else:
            self.disabled.append(str(timestring.Date('now')))
            self.user.expiration = None


    # Retorna o ultimo registro feito no historico do usuario
    def last_seen(self):
        if (self.user.enabled is True):
            return timestring.Date(self.enabled[-1])
        return timestring.Date(self.disabled[-1])


    def time_left(self):
        if (self.user.enabled is True):
            # e = timestring.Date(self.user.expiration)
            tl = timestring.Range("now", self.user.expiration)
            return tl

    # Calcula o numero de dias ativo ou inativo
    def activity(self):
        r = timestring.Range(self.last_seen(), timestring.Date("now"))
        return r.elapse[:r.elapse.find("hour")+5]


    # Parse a lista de datas apos acessar o banco de dados
    def parse(self, list):
        a = []
        for element in list:
            a.append(timestring.Date(element))
        return a

    # Encoda a lista de datas para entrar no banco de dados
    def encode(self, list):
        a = []
        for element in list:
            a.append(str(element))
        return a

    # Metodo que converte o objeto em json
    def json(self):
        enabled = self.encode(self.enabled)
        disabled = self.encode(self.disabled)
        return json.dumps({ "enabled": enabled, "disabled": disabled })

    # Carrega uma string em json
    def load(self, str):
        if str is not None:
            dict = json.loads(str)
            self.enabled  = self.parse(dict['enabled'])
            self.disabled = self.parse(dict['disabled'])
        else:
            self.enabled = []
            self.disabled = []
