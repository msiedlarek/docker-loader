from docker_loader.provisioner import Provisioner


class ShellCommand(Provisioner):

    def __init__(self, command, cleanup_command=None,
            **additional_configuration):
        self.command = command
        self.cleanup_command = cleanup_command
        self.additional_configuration = additional_configuration

    def __str__(self):
        return "Run shell command: {}".format(self.command)

    def provision(self, container):
        container.run(self.command, **self.additional_configuration)

    def cleanup(self, container):
        if self.cleanup_command is not None:
            container.run(
                self.cleanup_command,
                **self.additional_configuration
            )


class ShellScript(Provisioner):

    def __init__(self, script_path, cleanup_script_path=None,
            **additional_configuration):
        self.script_path = script_path
        self.cleanup_script_path = cleanup_script_path
        self.additional_configuration = additional_configuration

    def __str__(self):
        return "Run shell script: {}".format(self.script_path)

    def provision(self, container):
        with open(self.script_path, 'r') as script_file:
            container.run(script_file, **self.additional_configuration)

    def cleanup(self, container):
        if self.cleanup_script_path is not None:
            with open(self.cleanup_script_path, 'r') as cleanup_script_file:
                container.run_script(
                    cleanup_script_file,
                    **self.additional_configuration
                )
