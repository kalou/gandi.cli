""" Virtual hosts namespace commands. """

import click

from gandi.cli.core.cli import cli
from gandi.cli.core.utils import output_generic, output_vhost
from gandi.cli.core.params import pass_gandi


@cli.command()
@click.option('--limit', help='Limit number of results.', default=100,
              show_default=True)
@click.option('--id', help='Display ids.', is_flag=True)
@click.option('--names', help='Display names.', is_flag=True)
@pass_gandi
def list(gandi, limit, id, names):
    """ List vhosts. """
    options = {
        'items_per_page': limit,
    }

    output_keys = ['name', 'state', 'date_creation']
    if id:
        # When we will have more than paas vhost, we will append rproxy_id
        output_keys.append('paas_id')

    paas_names = {}
    if names:
        output_keys.append('paas_name')
        paas_names = gandi.paas.list_names()

    result = gandi.vhost.list(options)
    for num, vhost in enumerate(result):
        paas = paas_names.get(vhost['paas_id'])
        if num:
            gandi.separator_line()
        output_vhost(gandi, vhost, paas, output_keys)

    return result


@cli.command()
@click.option('--id', help='Display ids.', is_flag=True)
@click.argument('resource', nargs=-1, required=True)
@pass_gandi
def info(gandi, resource, id):
    """ Display information about a vhost.

    Resource must be the vhost fqdn.
    """
    output_keys = ['name', 'state', 'date_creation', 'paas_name']

    if id:
        # When we will have more than paas vhost, we will append rproxy_id
        output_keys.append('paas_id')

    paas_names = gandi.paas.list_names()

    ret = []
    paas = None
    for num, item in enumerate(resource):
        vhost = gandi.vhost.info(item)
        paas = paas_names.get(vhost['paas_id'])
        if num:
            gandi.separator_line()
        ret.append(output_vhost(gandi, vhost, paas, output_keys))

    return ret


@cli.command()
@click.option('--paas', required=True,
              help='PaaS instance on which to create it.')
@click.option('--alter-zone', help='Will update the domain zone.',
              is_flag=True)
@click.option('--bg', '--background', default=False, is_flag=True,
              help='Run command in background mode (default=False).')
@click.argument('vhost', required=True)
@pass_gandi
def create(gandi, paas, alter_zone, background, vhost):
    """ Create a new vhost. """
    result = gandi.vhost.create(paas, vhost, alter_zone, background)

    if not result:
        return

    if background:
        gandi.pretty_echo(result)

    return result


@cli.command()
@click.option('--force', '-f', is_flag=True,
              help='This is a dangerous option that will cause CLI to continue'
                   ' without prompting. (default=False).')
@click.option('--bg', '--background', default=False, is_flag=True,
              help='Run command in background mode (default=False).')
@click.argument('resource', required=True)
@pass_gandi
def delete(gandi, resource, force, background):
    """ Delete a vhost. """
    output_keys = ['name', 'paas_id', 'state', 'date_creation']
    if not force:
        proceed = click.confirm('Are you sure to delete vhost %s?' %
                                resource)

        if not proceed:
            return

    opers = gandi.vhost.delete(resource, background)
    if background:
        for oper in opers:
            output_generic(gandi, oper, output_keys)

    return opers

@cli.command()
@click.argument('resource', required=True)
@click.argument('directory', default=None, required=False)
@pass_gandi
def clone(gandi, resource, directory):
    """ Clone this vhost in a local directory """
    return gandi.vhost.clone(resource, directory)

@cli.command()
@click.argument('resource', required=True)
@pass_gandi
def attach(gandi, resource):
    """ Add a remote for a vhost to the local git repository """
    return gandi.vhost.attach(resource)

@cli.command(root=True)
@click.argument('resource', required=False)
@click.argument('gitref', required=False)
@pass_gandi
def deploy(gandi, resource, gitref):
    """Deploy code on a remote vhost."""

    return gandi.vhost.deploy(resource, gitref)
