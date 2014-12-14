import gzip
import shutil
import logging


logger = logging.getLogger(__name__)


class Image:

    def __init__(self, client, id):
        self.client = client
        self.id = id
        self.repository_tag = None

    def __str__(self):
        return self.repository_tag or self.id[:12]

    def tag(self, repository, tag=None, force=None, **kwargs):
        if tag is None:
            tag = 'latest'
        if force is None and tag == 'latest':
            force = True
        logger.info("Tagging image {image} as {repository}:{tag}...".format(
            image=self,
            repository=repository,
            tag=tag
        ))
        self.client.tag(
            self.id,
            repository=repository,
            tag=tag,
            force=force,
            **kwargs
        )
        self.repository_tag = ':'.join((repository, tag))
        return self

    def remove(self, **kwargs):
        logger.info("Removing image: {}".format(self))
        self.client.remove_image(self.id, **kwargs)

    def get(self):
        if self.repository_tag:
            return self.client.get_image(self.repository_tag)
        else:
            return self.client.get_image(self.id)

    def save(self, path, compress=False):
        logger.info("Saving image {image} to: {file}".format(
            image=self,
            file=path
        ))
        if compress:
            open_func = gzip.open
        else:
            open_func = open
        with open_func(path, 'wb') as output:
            shutil.copyfileobj(self.get(), output)
        return self
