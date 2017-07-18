class DnsRecord(object):
    def __init__(self, internal_id, hostname, ip_address, record_type, ttl):
        self.internal_id = internal_id
        self.hostname = hostname
        self.ip_address = ip_address
        self.record_type = record_type
        self.ttl = ttl

    def __repr__(self):
        return f'{self.__class__.__name__} ({self.__dict__})'
