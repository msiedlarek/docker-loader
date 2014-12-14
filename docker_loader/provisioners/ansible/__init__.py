from __future__ import absolute_import

import os

from ansible.playbook import PlayBook
from ansible.callbacks import (
    PlaybookCallbacks,
    PlaybookRunnerCallbacks,
    AggregateStats,
)
from ansible.utils.plugins import connection_loader
from ansible.inventory import Inventory

from docker_loader.provisioner import Provisioner, ProvisioningError
from docker_loader.provisioners.ansible import ansible_plugins


connection_loader.add_directory(
    os.path.dirname(ansible_plugins.__file__),
    with_subdir=True
)


class AnsiblePlayBook(Provisioner):

    def __init__(self, playbook, **additional_options):
        self.playbook = playbook
        self.additional_options = additional_options

    def __str__(self):
        return "Run Ansible playbook: {}".format(self.playbook)

    def provision(self, container):
        host = container.id[:12]
        stats = AggregateStats()
        inventory = Inventory(host_list=[host])
        inventory.get_host(host).set_variable('container', container)
        playbook = PlayBook(
            playbook=self.playbook,
            host_list=[host],
            transport='docker',
            inventory=inventory,
            callbacks=PlaybookCallbacks(),
            runner_callbacks=PlaybookRunnerCallbacks(stats=stats),
            stats=stats,
            **self.additional_options
        )
        result = playbook.run()
        if result[host]['unreachable'] or result[host]['failures']:
            raise ProvisioningError(
                "Errors occurred while running an Ansible playbook."
            )
