from ansible.constants import BECOME_METHODS


class Connection(object):

    def __init__(self, runner, host, port, *args, **kwargs):
        self.runner = runner
        self.host = host
        self.port = port
        self.has_pipelining = False
        self.container = runner.inventory.get_host(host).vars['container']

    def connect(self, port=None):
        return self

    def close(self):
        pass

    def exec_command(self, cmd, tmp_path, become_user, sudoable=False,
            executable='/bin/sh', in_data=None):
        if (sudoable and self.runner.become and
                self.runner.become_method not in BECOME_METHODS):
            raise NotImplementedError()
        exit_code, stdout, stderr = self.container.execute(
            [executable, '-c', cmd],
            stdin=in_data
        )
        return exit_code, '', stdout, stderr

    def put_file(self, in_path, out_path):
        with open(in_path, 'r') as input_file:
            self.exec_command(
                'cat > {}'.format(out_path),
                '/tmp',
                None,
                in_data=input_file
            )

    def fetch_file(self, in_path, out_path):
        with open(out_path, 'w') as output:
            output.write(self.container.read_file(in_path))
