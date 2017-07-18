ventraip-vip-client
===================
A Python 3.6 compatible library which can manage DNS entries registered with VentraIP

Installation
------------
Install the latest production release:

.. code-block:: bash

  pip install ventraip-vip-client

Install the latest development release:

.. code-block:: bash

  git clone git@github.com:cmbrad/ventraip-vip-client.git
  python setup.py install

Examples
--------

.. code-block:: python

  from ventraip import VipClient
  vip_client = VipClient()
  vip_client.login(email='your email/username', password='your password')

  # Fetch all domains associated with the account
  domains = vip_client.domains()
  for domain in domains:
      # Fetch all records associated with the domain
      dns_records = vip_client.dns_records(domain.internal_id)

      # For each record, delete it (DANGEROUS!!!)
      for dns_record in dns_records:
          vip_client.remove_dns_record(domain_id=domain.internal_id, dns_record_id=dns_record.internal_id)

TODO
----
* Add unit tests
* Publish to pypi
