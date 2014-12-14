import sys
import inspect
import logging

import docker

from docker_loader.builder import Builder


def build(image_definition, client=None, repository=None, tag=None,
        verbose=True):
    if verbose:
        logging.basicConfig(
            format='%(asctime)s %(levelname)s: %(message)s',
            level=logging.INFO,
            stream=sys.stdout,
        )
    if inspect.isclass(image_definition):
        image_definition = image_definition()
    if client is None:
        client = docker.Client()
    builder = Builder(client, image_definition)
    image = builder.run()
    if repository:
        image.tag(repository, tag=tag)
    return image
