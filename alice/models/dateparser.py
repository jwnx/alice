class DateParser(object):

    range = None

    def __init__(self, obj):
        self.range = obj

    def plural(self, int):
        if int > 1:
            return "s"
        else:
            return ""

    @property
    def state(self):
        if '-' in self.range.elapse:
            if len(self.range) >= 604800:
                return 'expired'
            else:
                return 'hold'
        return 'active'

    @property
    def elapsed(self):
        # NOT YET IMPLEMENTED
        return
