import sys
import os
import logging
import tempfile
import shutil

import six
from six.moves import shlex_quote

if six.PY3:
    from collections.abc import Sequence
else:
    from collections import Sequence


logger = logging.getLogger(__name__)


class ContainerCommandError(Exception):

    def __init__(self, command, exit_code, stdout, stderr):
        self.command = command
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self):
        if isinstance(self.command, file):
            return "Script exited with code {exit_code}: {script}".format(
                exit_code=self.exit_code,
                script=self.command.name
            )
        else:
            return "Command exited with code {exit_code}: {command}".format(
                exit_code=self.exit_code,
                command=self.command
            )


class Container:

    TEMP_VOLUME = '/provisioning'
    COMMAND_FILE = 'command.sh'
    STDOUT_FILE = 'stdout'
    STDERR_FILE = 'stderr'

    SHELL = '/bin/sh'

    def __init__(self, client, image, encoding='utf-8', build_volumes=None,
            build_volumes_from=None, **container_configuration):
        self.client = client
        self.encoding = encoding
        self.container_configuration = container_configuration
        self.container_configuration['image'] = image
        self.container_configuration['user'] = 'root'
        self.container_configuration['stdin_open'] = True
        self.build_volumes = build_volumes or {}
        self.build_volumes_from = build_volumes_from or []
        self.id = None
        self.temp_dir = None

    def __str__(self):
        if self.id is not None:
            return self.id[:12]
        else:
            return '<new container>'

    def __enter__(self):
        self.create()
        return self

    def __exit__(self, *args, **kwargs):
        self.remove()

    def create(self):
        if self.temp_dir is None:
            self.temp_dir = tempfile.mkdtemp()
            os.chmod(self.temp_dir, 0777)
        result = self.client.create_container(
            command=[
                self.SHELL,
                '-c',
                '{command_file} >{stdout_file} 2>{stderr_file}'.format(
                    command_file='/'.join((
                        self.TEMP_VOLUME,
                        self.COMMAND_FILE
                    )),
                    stdout_file='/'.join((
                        self.TEMP_VOLUME,
                        self.STDOUT_FILE
                    )),
                    stderr_file='/'.join((
                        self.TEMP_VOLUME,
                        self.STDERR_FILE
                    )),
                ),
            ],
            **self.container_configuration
        )
        self.id = result['Id']
        logger.info("Created container: {}".format(self))

    def remove(self):
        if self.id:
            self.client.remove_container(
                self.id,
                v=True,
                force=True
            )
            logger.info("Removed container: {}".format(self))
            self.id = None
        if self.temp_dir is not None:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            self.temp_dir = None

    def run(self, command, **additional_configuration):
        if hasattr(command, 'read'):
            logger.info("Running script.")
            exit_code, stdout, stderr = self.execute(
                command,
                **additional_configuration
            )
        else:
            logger.info("Running: {}".format(
                command
                if isinstance(command, six.string_types)
                else ' '.join(command)
            ))
            exit_code, stdout, stderr = self.execute(
                command,
                **additional_configuration
            )
        if stdout:
            sys.stdout.write(stdout)
        if stderr:
            sys.stderr.write(stderr)
        if exit_code != 0:
            raise ContainerCommandError(command, exit_code, stdout, stderr)

    def execute(self, script, stdin=None, **additional_configuration):
        assert self.id is not None
        assert self.temp_dir is not None

        if isinstance(script, six.text_type):
            script = script.strip().encode(self.encoding) + b'\n'
        elif isinstance(script, six.binary_type):
            script = script.strip() + b'\n'
        elif isinstance(script, Sequence):
            script = six.text_type(' ').join(
                map(shlex_quote, map(six.text_type, script))
            )
            script = script.encode(self.encoding) + b'\n'
        elif not hasattr(script, 'read'):
            raise TypeError(
                "Invalid script type: must be a string, a sequence of strings"
                " or a file."
            )
        command_local_path = os.path.join(self.temp_dir, self.COMMAND_FILE)
        with open(command_local_path, 'w') as command_file:
            if hasattr(script, 'read'):
                shutil.copyfileobj(script, command_file)
            else:
                command_file.write(script)
        os.chmod(command_local_path, 0755)

        additional_configuration.setdefault('binds', {})
        additional_configuration['binds'].update(self.build_volumes)
        additional_configuration['binds'][self.temp_dir] = {
            'bind': self.TEMP_VOLUME,
            'ro': False,
        }
        if self.build_volumes_from:
            additional_configuration['volumes_from'] = self.build_volumes_from
        self.client.start(
            self.id,
            **additional_configuration
        )

        if stdin is not None:
            socket = self.client.attach_socket(
                self.id,
                params={
                    'stdout': 0,
                    'stderr': 0,
                    'stdin': 1,
                    'stream': 1,
                }
            )
            if hasattr(stdin, 'read'):
                stdin = stdin.read()
            if isinstance(stdin, six.text_type):
                stdin = stdin.encode(self.encoding)
            socket.sendall(stdin)
            socket.close()

        exit_code = self.client.wait(self.id)

        stdout_local_path = os.path.join(self.temp_dir, self.STDOUT_FILE)
        stderr_local_path = os.path.join(self.temp_dir, self.STDERR_FILE)
        with open(stdout_local_path, 'r') as stdout_file:
            stdout = stdout_file.read()
        with open(stderr_local_path, 'r') as stderr_file:
            stderr = stderr_file.read()

        return exit_code, stdout, stderr

    def read_file(self, path):
        return self.client.copy(
            self.id,
            path
        )
