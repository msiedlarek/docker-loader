from __future__ import print_function

import sys
import json
import logging

from docker_loader.container import Container
from docker_loader.image import Image


logger = logging.getLogger(__name__)


class ImagePullError(Exception):
    pass


class Builder:

    DEFAULT_COMMAND = '/bin/sh'

    def __init__(self, client, image_definition):
        self.client = client
        self.definition = image_definition

    def run(self, **additional_configuration):
        self.definition.validate()
        container_args = (
            self.client,
            self.definition.base,
        )
        container_kwargs = {
            'build_volumes': self.definition.build_volumes,
            'environment': self.definition.environment,
            'entrypoint': self.definition.entry_point,
            'hostname': self.definition.hostname,
            'domainname': self.definition.domainname,
        }
        container_kwargs.update(additional_configuration)
        if self.definition.pull_base:
            self._pull_image(self.definition.base)
        with Container(*container_args, **container_kwargs) as container:
            self.provision(container)
            return self.commit(container)

    def provision(self, container):
        try:
            for provisioner in self.definition.provisioners:
                logger.info("Provisioning: {}".format(provisioner))
                provisioner.provision(container)
            for provisioner in reversed(self.definition.provisioners):
                provisioner.cleanup(container)
        except Exception as error:
            logger.error(str(error))
            sys.exit(1)

    def commit(self, container, additional_configuration=None):
        base_config = self.client.inspect_image(self.definition.base)
        logger.info("Commiting container {}...".format(container))
        config = {}
        if self.definition.exposed_ports:
            config['ExposedPorts'] = {
                '/'.join(map(str, port)): {}
                for port in self.definition.exposed_ports
            }
        if self.definition.volumes:
            config['Volumes'] = {
                volume: {} for volume in self.definition.volumes
            }
        if self.definition.environment:
            config['Env'] = [
                '='.join((name, value))
                for name, value in self.definition.environment.items()
            ]
        if self.definition.user:
            config['User'] = self.definition.user
        else:
            config['User'] = base_config['Config']['User']
        if self.definition.working_directory:
            config['WorkingDir'] = self.definition.working_directory
        if self.definition.command:
            config['Cmd'] = self.definition.command
        else:
            config['Cmd'] = base_config['Config'].get(
                'Cmd',
                self.DEFAULT_COMMAND
            )
        if additional_configuration is not None:
            config.update(additional_configuration)
        result = self.client.commit(
            container.id,
            author=self.definition.maintainer,
            conf=config
        )
        image = Image(self.client, result['Id'])
        logger.info("Commited container {container} to image {image}.".format(
            container=container,
            image=image
        ))
        return image

    def _pull_image(self, image):
        parts = self.definition.base.split(':', 1)
        repository = parts[0]
        tag = (parts[1] if len(parts) > 1 else 'latest')

        logger.info("Pulling base image: {repository}:{tag}".format(
            repository=repository,
            tag=tag
        ))
        log_stream = self.client.pull(
            repository,
            tag=tag,
            stream=True
        )
        allow_progress = sys.stdout.isatty()
        showing_progress = False
        for line in log_stream:
            line = json.loads(line)
            if 'progress' in line:
                if allow_progress:
                    sys.stdout.write('\r{}: {}'.format(
                        line['id'],
                        line['progress']
                    ))
                    showing_progress = True
            else:
                if showing_progress:
                    sys.stdout.write('\n')
                    showing_progress = False
                if 'id' in line:
                    print('{}: {}'.format(line['id'], line['status']))
                elif 'error' in line:
                    raise ImagePullError(line['error'])
                elif 'status' in line:
                    print(line['status'])
                else:
                    print(line)
