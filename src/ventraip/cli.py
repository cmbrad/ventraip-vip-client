import click as click

from tabulate import tabulate

from ventraip import VipClient


@click.group()
@click.option('--username', '-u', required=True)
@click.option('--password', '-p', required=True)
@click.pass_context
def cli(ctx, username, password):
    vip_client = VipClient()
    vip_client.login(email=username, password=password)

    ctx.obj = vip_client


@cli.command()
@click.pass_obj
def list(vip_client: VipClient):
    data = []
    headers = ['Domain Name', 'Hostname', 'Destination', 'Record Type', 'TTL']

    for i, domain in enumerate(vip_client.domains()):
        for j, dns_record in enumerate(vip_client.dns_records(domain.internal_id)):
            data.append([domain.name, dns_record.hostname, dns_record.destination, dns_record.record_type,
                         dns_record.ttl])

    print(tabulate(data, headers=headers))


@cli.command()
@click.argument('hostname', required=True)
@click.argument('domain_name', required=True)
@click.argument('destination', required=True)
@click.argument('ttl', required=True)
@click.argument('record-type', required=True)
@click.option('--delete-existing/--no-delete-existing', default=True)
@click.pass_obj
def add(vip_client: VipClient, hostname, domain_name, destination, ttl, record_type, delete_existing):
    domain = vip_client.domain(domain_name=domain_name)
    dns_record = vip_client.dns_record(hostname, domain_name, record_type)

    if dns_record and delete_existing:
        print('Found existing record. Deleting old record to allow for update')
        vip_client.remove_dns_record(dns_record.domain.internal_id, dns_record.internal_id)

    vip_client.add_dns_record(domain.internal_id, hostname, destination, ttl, record_type)

    print(f'Set {hostname}.{domain_name} to point to {destination}')


@cli.command(name='rm')
@click.argument('hostname', required=True)
@click.argument('domain_name', required=True)
@click.argument('record_type', required=True)
@click.pass_obj
def remove(vip_client: VipClient, hostname, domain_name, record_type):
    dns_record = vip_client.dns_record(hostname=hostname, domain_name=domain_name, record_type=record_type)

    vip_client.remove_dns_record(dns_record.domain.internal_id, dns_record.internal_id)

    print(f'Deleted {hostname}.{domain_name}')


def main():
    cli()
