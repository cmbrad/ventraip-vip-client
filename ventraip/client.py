import re
import logging
import requests

from bs4 import BeautifulSoup

from ventraip.dns_record import DnsRecord
from ventraip.domain import Domain
from ventraip.exceptions import DnsRecordCreateFailedError, DnsRecordRemoveFailedError


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
        res = self._session.post('https://vip.ventraip.com.au', data={
            'email': email,
            'password': password,
            'request': '0123456789'  # set in the original request, but providng dummy data seems to work
        })

        self.logger.info(f'Logged in to {email}')

        return self

    def domains(self):
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
            domains.append(Domain(hostname=cols_text[1], internal_id=domain_id))

        return domains

    def dns_records(self, domain_id):
        res = self._session.get(f'https://vip.ventraip.com.au/home/domain/{domain_id}/service')
        soup = BeautifulSoup(res.content, 'html.parser')
        table = soup.find('p', attrs={'class': 'title'}, text='DNS Records').findNext('table')
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')

        records = []
        for row in rows:
            record_id = row.find('form').find('input').get('value')
            cols_text = [self._clean(ele.text) for ele in row.find_all('td')]

            records.append(DnsRecord(internal_id=record_id, hostname=cols_text[0], ip_address=cols_text[2], record_type=cols_text[3], ttl=cols_text[4]))

        return records

    def _clean(self, s):
        s = re.sub(r'[\t\n]+', '', s)
        s = re.sub(r'[ ]+', ' ', s)
        return s.strip()

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
            'dnsttl': 3600,
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
