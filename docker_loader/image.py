import gzip
import shutil
import logging


logger = logging.getLogger(__name__)


class Image:

    def __init__(self, client, id):
        self.client = client
        self.id = id

    def __str__(self):
        return self.id[:12]

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
        return self

    def remove(self, **kwargs):
        logger.info("Removing image: {}".format(self))
        self.client.remove_image(self.id, **kwargs)

    def get(self):
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
