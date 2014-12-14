from docker_loader.provisioner import Provisioner


class AptUpdate(Provisioner):

    def __str__(self):
        return "Update APT cache."

    def provision(self, container):
        container.run('apt-get update')

    def cleanup(self, container):
        container.run('apt-get clean')
        container.run('rm -rf /var/lib/apt/lists/*')


class AptInstall(Provisioner):

    def __init__(self, packages, build_only=False):
        self.packages = packages
        self.build_only = build_only

    def __str__(self):
        return "Install packages {detail}: {packages}".format(
            detail=("for build only" if self.build_only else "permanently"),
            packages=', '.join(self.packages)
        )

    def provision(self, container):
        container.run(['apt-get', 'install', '-y'] + list(self.packages))

    def cleanup(self, container):
        if self.build_only:
            container.run(['apt-get', 'purge', '-y'] + list(self.packages))
            container.run(['apt-get', 'autoremove', '-y'])
