""" Domain namespace commands. """

import click

from gandi.cli.core.cli import cli
from gandi.cli.core.utils import output_contact_info, output_domain
from gandi.cli.core.params import pass_gandi


@cli.command()
@click.option('--limit', help='Limit number of results.', default=100,
              show_default=True)
@pass_gandi
def list(gandi, limit):
    """List domains."""
    options = {'items_per_page': limit}
    domains = gandi.domain.list(options)
    for domain in domains:
        gandi.echo(domain['fqdn'])

    return domains


@cli.command()
@click.argument('resource')
@pass_gandi
def info(gandi, resource):
    """Display information about a domain."""
    output_keys = ['fqdn', 'nameservers', 'services', 'zone_id', 'tags',
                   'created', 'expires', 'updated']
    contact_field = ['owner', 'admin', 'bill', 'tech', 'reseller']

    result = gandi.domain.info(resource)
    output_contact_info(gandi, result['contacts'], contact_field, justify=12)
    output_domain(gandi, result, output_keys, justify=12)

    return result


@cli.command()
@click.option('--domain', default=None, prompt=True,
              help='Name of the domain.')
@click.option('--duration', default=1, prompt=True,
              type=click.IntRange(min=1, max=10),
              help='Registration period in years, between 1 and 10.')
@click.option('--owner', default=None,
              help='Registrant handle.')
@click.option('--admin', default=None,
              help='Administrative contact handle.')
@click.option('--tech', default=None,
              help='Technical contact handle.')
@click.option('--bill', default=None,
              help='Billing contact handle.')
@click.option('--bg', '--background', default=False, is_flag=True,
              help='Run command in background mode (default=False).')
@pass_gandi
def create(gandi, domain, duration, owner, admin, tech, bill, background):
    """Buy a domain."""
    result = gandi.domain.create(domain, duration, owner, admin, tech, bill,
                                 background)
    if background:
        gandi.pretty_echo(result)

    return result


@cli.command()
@click.option('--duration', default=1, prompt=True,
              type=click.IntRange(min=1, max=10),
              help='Registration period in years, between 1 and 10.')
@click.option('--bg', '--background', default=False, is_flag=True,
              help='Run command in background mode (default=False).')
@click.argument('domain')
@pass_gandi
def renew(gandi, domain, duration, background):
    """Renew a domain."""
    result = gandi.domain.renew(domain, duration, background)
    if background:
        gandi.pretty_echo(result)

    return result
