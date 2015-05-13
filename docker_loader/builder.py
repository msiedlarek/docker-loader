import sys
import logging

from docker_loader.container import Container
from docker_loader.image import Image
from docker_loader.utils import pull_image


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
            'build_volumes_from': self.definition.build_volumes_from,
            'environment': self.definition.environment,
            'entrypoint': self.definition.entry_point,
            'hostname': self.definition.hostname,
            'domainname': self.definition.domainname,
        }
        container_kwargs.update(additional_configuration)
        if self.definition.pull_base:
            pull_image(self.client, self.definition.base)
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
        if self.definition.labels:
            config['Labels'] = self.definition.labels
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
