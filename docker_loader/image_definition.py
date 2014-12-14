try:
    from collections.abc import Sequence, Mapping
except ImportError:
    from collections import Sequence, Mapping


class ImageDefinition:

    base = None
    """Equivalent of Dockerfile's FROM."""

    pull_base = True
    """
    Whether to pull the base image before the build, or expect it to be
    already present in required version.
    """

    maintainer = None
    """Equivalent of Dockerfile's MAINTAINER."""

    hostname = None
    """Container's hostname."""

    domainname = None
    """Container's domainname."""

    exposed_ports = tuple()
    """Equivalent of Dockerfile's EXPOSE. A sequence of integers."""

    volumes = tuple()
    """Equivalent of Dockerfile's VOLUME. A sequence of volume paths."""

    environment = {}
    """
    Equivalent of multiple Dockerfile's ENV statements. A mapping of
    environment variable names to their values.
    """

    user = None
    """Equivalent of Dockerfile's USER."""

    working_directory = None
    """Equivalent of Dockerfile's WORKDIR."""

    entry_point = None
    """Equivalent of Dockerfile's ENTRYPOINT."""

    command = None
    """Equivalent of Dockerfile's CMD."""

    build_volumes = {}
    """
    Specifies the volumes that shall be mounted in the container, but only for
    the time of the build.

    Example::

        build_volumes = {
            '/path/on/host': {
                'bind': '/path/on/container',
                'ro': True,
            }
        }
    """

    provisioners = tuple()
    """
    Sequence of Provisioner instances, which will be run in the order provided.
    The cleanup methods will be run in reverse order.
    """

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

        assert isinstance(self.build_volumes, Mapping)
        for path, binding in self.build_volumes.items():
            _validate_string(path)
            assert set(binding.keys()).issubset({'bind', 'ro'})
            _validate_string(binding['bind'])
            if 'ro' in binding:
                assert isinstance(binding['ro'], bool)

        assert isinstance(self.provisioners, Sequence)
