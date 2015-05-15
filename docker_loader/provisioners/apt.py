from docker_loader.provisioner import Provisioner


class AptProvisioner(Provisioner):
    APT_GET = 'apt-get'


class AptUpdate(AptProvisioner):

    def __str__(self):
        return "Update APT cache."

    def provision(self, container):
        container.run([self.APT_GET, 'update'])


class AptClear(AptProvisioner):

    def __str__(self):
        return "Clear APT cache."

    def provision(self, container):
        container.run([self.APT_GET, 'clean'])
        container.run(['rm', '-rf', '/var/lib/apt/lists/*'])


class AptInstall(AptProvisioner):

    def __init__(self, packages, build_only=False):
        self.packages = packages
        self.build_only = build_only

    def __str__(self):
        return "Install packages {detail}: {packages}".format(
            detail=("for build only" if self.build_only else "permanently"),
            packages=', '.join(self.packages)
        )

    def provision(self, container):
        container.run([self.APT_GET, 'install', '-y'] + list(self.packages))

    def cleanup(self, container):
        if self.build_only:
            container.run([self.APT_GET, 'purge', '-y'] + list(self.packages))
            container.run([self.APT_GET, 'autoremove', '-y'])


class AptAutoremove(AptProvisioner):

    def __str__(self):
        return "Remove unused APT packages."

    def provision(self, container):
        container.run([self.APT_GET, 'autoremove', '-y'])
