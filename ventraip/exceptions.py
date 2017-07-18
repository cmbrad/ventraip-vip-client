class VipClientError(Exception):
    def __repr__(self):
        return f'{self.__class__.__name__} ({self.__dict__})'


class DnsRecordActionError(VipClientError):
    def __init__(self, message, url, params):
        self.message = message
        self.url = url
        self.params = params

        super().__init__(message)


class DnsRecordCreateFailedError(DnsRecordActionError):
    pass


class DnsRecordRemoveFailedError(DnsRecordActionError):
    pass
