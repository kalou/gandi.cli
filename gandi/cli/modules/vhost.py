""" Vhost commands module. """

from click import UsageError

from gandi.cli.modules.paas import Paas
from gandi.cli.core.base import GandiModule


class PaasAccess:
    git_remote = None
    ssh_remote = None

    def __init__(self, git_remote=None, ssh_remote=None):
        self.git_remote = git_remote
        self.ssh_remote = ssh_remote


class Vhost(GandiModule):

    """ Module to handle CLI commands.

    $ gandi vhost create
    $ gandi vhost delete
    $ gandi vhost info
    $ gandi vhost list

    """

    @classmethod
    def list(cls, options=None):
        """ List paas vhosts (in the future it should handle iaas vhosts)."""
        options = options or {}
        return cls.call('paas.vhost.list', options)

    @classmethod
    def info(cls, name):
        """ Display information about a vhost. """
        return cls.call('paas.vhost.info', name)

    @classmethod
    def create(cls, paas, vhost, alter_zone, background):
        """ Create a new vhost. """
        if not background and not cls.intty():
            background = True

        paas_id = Paas.usable_id(paas)
        params = {'paas_id': paas_id,
                  'vhost': vhost,
                  'zone_alter': alter_zone}
        result = cls.call('paas.vhost.create', params, dry_run=True)

        if background:
            return result

        cls.echo('Creating a new vhost.')
        cls.display_progress(result)
        cls.echo('Your vhost %s has been created.' % vhost)

        return result

    @classmethod
    def delete(cls, resources, background=False):
        """ Delete this vhost. """
        if not isinstance(resources, (list, tuple)):
            resources = [resources]

        opers = []
        for item in resources:
            oper = cls.call('paas.vhost.delete', item)
            opers.append(oper)

        if background:
            return opers

        cls.echo('Deleting your vhost.')
        cls.display_progress(opers)

    @classmethod
    def get_remote(cls, vhost):
        """Return remote information for given vhost"""
        paas = Paas.info(vhost)
        git_server = paas['git_server']
        # hack for dev
        if 'dev' in paas['console']:
            git_server = 'git.hosting.dev.gandi.net'

        paas_access = '%s@%s' % (paas['user'], git_server)

        if 'php' not in paas['type']:
            remote = 'ssh+git://%s/default.git' % paas_access
        else:
            remote = 'ssh+git://%s/%s.git' % (paas_access, vhost)

        return PaasAccess(git_remote=remote, ssh_remote=paas_access)

    @classmethod
    def attach(cls, vhost):
        """Attach a vhost to a remote from the local
        repository"""
        remote = cls.get_remote(vhost).git_remote

        return cls.execute('git remote add %s %s' % (vhost, remote,))

    @classmethod
    def clone(cls, vhost, directory=None):
        """Clone this vhost in a local git repository"""

        remote = cls.get_remote(vhost)

        if not directory:
            directory = vhost

        git_command = 'git clone %s %s' % (remote.git_remote, directory)

        return cls.execute(git_command)
