try:
    from collections.abc import Sequence, Mapping
except ImportError:
    from collections import Sequence, Mapping


class ImageDefinition:

    base = None
    pull_base = True
    maintainer = None
    hostname = None
    domainname = None
    exposed_ports = tuple()
    volumes = tuple()
    environment = {}
    user = None
    working_directory = None
    entry_point = None
    command = None

    provisioners = tuple()

    def validate(self):
        def _validate_string(string):
            assert isinstance(string, str)
            assert string

        def _validate_command(command):
            assert isinstance(command, Sequence)
            assert len(command) > 0
            for element in command:
                assert isinstance(element, str)

        _validate_string(self.base)
        assert isinstance(self.pull_base, bool)

        if self.maintainer is not None:
            _validate_string(self.maintainer)

        if self.hostname is not None:
            _validate_string(self.hostname)
        if self.domainname is not None:
            _validate_string(self.domainname)

        assert isinstance(self.exposed_ports, Sequence)
        for port in self.exposed_ports:
            assert isinstance(port, Sequence)
            assert len(port) == 2
            assert isinstance(port[0], int)
            assert port[0] > 0
            assert port[0] < 2 ** 16
            _validate_string(port[1])
            assert port[1] in ('tcp', 'udp')

        assert isinstance(self.volumes, Sequence)
        for volume in self.volumes:
            assert isinstance(volume, str)
            assert volume

        assert isinstance(self.environment, Mapping)
        for name, value in self.environment.items():
            assert isinstance(name, str)
            assert name
            assert isinstance(value, str)

        if self.user is not None:
            _validate_string(self.user)

        if self.working_directory is not None:
            _validate_string(self.working_directory)

        if self.entry_point is not None:
            _validate_command(self.entry_point)
        if self.command is not None:
            _validate_command(self.command)

        assert isinstance(self.provisioners, Sequence)
