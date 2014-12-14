class ProvisioningError(RuntimeError):
    pass


class Provisioner:

    def __str__(self):
        raise NotImplementedError()

    def provision(self, container):
        raise NotImplementedError()

    def cleanup(self, container):
        pass
