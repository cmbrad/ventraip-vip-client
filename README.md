# VentraIP VIP Client

A Python 3.6 compatible library to manage DNS entries registered with VentraIP.

## Installation
### Production

```bash
pip install ventraip-vip-client
```

### Development

```bash
git clone git@github.com:cmbrad/ventraip-vip-client.git
pip install -e .
```

## Usage

### CLI

```bash
# View help for the CLI
ventraip --help

# List all domains
ventraip -u myusername -p mypassword list

# Add a domain
ventraip -u myusername -p mypassword add myhost example.com 127.0.0.1 3600 A

# Delete a domain
ventraip -u myusername -p mypassword rm myhost example.com A
```

### Library
```python
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
```

## Disclaimer

I have no relation to the VentraIP company and any use of this software is not endorsed by them in any way.
