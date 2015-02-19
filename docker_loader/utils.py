from __future__ import print_function

import sys
import json
import logging


logger = logging.getLogger(__name__)


class ImagePullError(Exception):
    pass


def pull_image(client, image):
    parts = image.split(':', 1)
    repository = parts[0]
    tag = (parts[1] if len(parts) > 1 else 'latest')
    logger.info("Pulling image: {repository}:{tag}".format(
        repository=repository,
        tag=tag
    ))
    log_stream = client.pull(
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
