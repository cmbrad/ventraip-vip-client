import re
import logging
from typing import List, Optional

import requests

from bs4 import BeautifulSoup


class Domain(object):
    def __init__(self, internal_id, name):
        self.internal_id = internal_id
        self.name = name

    def __repr__(self):
        return f'{self.__class__.__name__} ({self.__dict__})'


class DnsRecord(object):
    def __init__(self, internal_id, hostname, destination, record_type, ttl, domain: Domain):
        self.internal_id = internal_id
        self.hostname = hostname
        self.destination = destination
        self.record_type = record_type
        self.ttl = ttl
        self.domain = domain

    def fqdn(self):
        return f'{self.hostname}.{self.domain.name}'

    def __repr__(self):
        return f'{self.__class__.__name__} ({self.__dict__})'


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


class VipClient(object):
    _dns_record_add_key = {
        'A': 'dnsadda',
        'AAAA': 'dnsadda6',
        'CNAME': 'dnsaddcname',
        'TXT': 'dnsaddtxt'
        # 'MX': 'dnsaddmx',  # TODO: Add this
        # 'SRV': '',  # TODO: Add this
        # 'NS': ''  # TODO: Add this
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._session = requests.Session()

    def login(self, email, password):
        self._session.post('https://vip.ventraip.com.au', data={
            'email': email,
            'password': password,
            'request': '0123456789'  # set in the original request, but providng dummy data seems to work
        })

        self.logger.info(f'Logged in to {email}')

        return self

    def domains(self) -> List[Domain]:
        res = self._session.get('https://vip.ventraip.com.au/home/domain/')
        soup = BeautifulSoup(res.content, 'html.parser')
        table = soup.find(id='domtbl')
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')

        domains = []
        for row in rows:
            # Domains have a hidden ID input which contains the ID
            # which ventraip references them as
            domain_id = row.find('input').get('value')

            # All domain info is in a table. For now only the domain name will be filled
            # the expiry date is fetched later via ajax
            cols_text = [ele.text.strip() for ele in row.find_all('td')]
            # Domain name is in the 2nd cell of thr row
            domains.append(Domain(name=cols_text[1], internal_id=domain_id))

        return domains

    def domain(self, domain_name) -> Optional[Domain]:
        domains = self.domains()
        for domain in domains:
            if domain.name == domain_name:
                return domain

        return None

    def dns_record(self, hostname, domain_name, record_type):
        domains = self.domains()
        for domain in domains:
            if domain.name == domain_name:
                dns_records = self.dns_records(domain.internal_id)

                for dns_record in dns_records:
                    if dns_record.hostname == hostname and record_type == record_type:
                        return dns_record

        return None

    def dns_records(self, domain_id) -> List[DnsRecord]:
        def _clean(s):
            s = re.sub(r'[\t\n]+', '', s)
            s = re.sub(r'[ ]+', ' ', s)
            return s.strip()

        res = self._session.get(f'https://vip.ventraip.com.au/home/domain/{domain_id}/service')
        soup = BeautifulSoup(res.content, 'html.parser')
        table = soup.find('p', attrs={'class': 'title'}, text='DNS Records').findNext('table')
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')

        domain_name = [ele.text for ele in soup.find_all('h1') if 'Domain Name Service -' in ele.text][0]
        domain_name = domain_name.replace('Domain Name Service - ', '')
        domain = Domain(internal_id=domain_id, name=domain_name)


        records = []
        for row in rows:
            record_id = row.find('form').find('input').get('value')
            cols_text = [_clean(ele.text) for ele in row.find_all('td')]

            records.append(DnsRecord(internal_id=record_id, hostname=cols_text[0].replace(domain_name, '').rstrip('.'),
                                     destination=cols_text[1], record_type=cols_text[2], ttl=cols_text[3],
                                     domain=domain))

        return records

    def remove_dns_record(self, domain_id, dns_record_id):
        url = f'https://vip.ventraip.com.au/home/domain/{domain_id}/service'
        data = {
            'id': dns_record_id,
            'deldns': 'Remove'
        }
        res = self._session.post(url=url, data=data)

        soup = BeautifulSoup(res.content, 'html.parser')
        # All successful requests will have one div with a success class
        if soup.find('div', {'class': 'success'}) is None:
            self.logger.error(f'Failed to remove DNS record with params: {data}')
            raise DnsRecordRemoveFailedError(message=soup.find('div', {'class': 'error'}).text, url=url, params=data)

        self.logger.info(f'Removed DNS record with params: {data}')

        # Chaining
        return self

    def add_dns_record(self, domain_id, hostname, destination, ttl, record_type):
        url = f'https://vip.ventraip.com.au/home/domain/{domain_id}/service'
        data = {
            'dnshostname': hostname,
            'dnsdest': destination,
            'dnsttl': ttl,
            self._dns_record_add_key[record_type]: 'Add'
        }
        res = self._session.post(url=url, data=data)

        soup = BeautifulSoup(res.content, 'html.parser')
        # All successful requests will have one div with a success class
        if soup.find('div', {'class': 'success'}) is None:
            self.logger.error(f'Failed to create DNS record with params: {data}')
            raise DnsRecordCreateFailedError(message=soup.find('div', {'class': 'error'}).text, url=url, params=data)

        self.logger.info(f'Created DNS record with params: {data}')

        # Chaining
        return self
