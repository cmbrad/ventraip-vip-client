class Domain(object):
    def __init__(self, internal_id, hostname):
        self.internal_id = internal_id
        self.hostname = hostname

    def __repr__(self):
        return f'{self.__class__.__name__} ({self.__dict__})'
