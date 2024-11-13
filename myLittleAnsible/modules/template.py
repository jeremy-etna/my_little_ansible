import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from mylittleansible.modules.base import BaseModule
from mylittleansible.core.logger import get_logger

logger = get_logger(__name__)


class TemplateModule(BaseModule):
    """
    Template module.
    """

    sftp_session = None

    def process(self, ssh_manager) -> None:
        """
        Execute the file command using an SSH client.

        :param ssh_manager: The SSH manager.
        :type ssh_manager: SSHManager
        """
        source = self.params.get("src")
        destination = self.params.get("dest")
        variables = self.params.get("vars")

        self.render_template(source, variables)
        self.sftp_session = ssh_manager.client.open_sftp()

        if self.dry_run:
            logger.info(f"DRY_RUN [{self.index}] host={ssh_manager.hostname} src={source} dest={destination}")
            return

        if self._is_needed_permissions(ssh_manager):
            self._change_destination_permissions(ssh_manager, "777")
            self._copy_file_to_remote("./default", destination)
            self._change_destination_permissions(ssh_manager, "644")
            os.remove("./default")
            logger.info(f"[{self.index}] host={ssh_manager.hostname} op={self.name} src={source} dest={destination}")
            return
        self._copy_file_to_remote("./default", destination)
        os.remove("./default")
        logger.info(f"[{self.index}] host={ssh_manager.hostname} op={self.name} src={source} dest={destination}")

    def _copy_file_to_remote(self, local_filepath, remote_filepath) -> None:
        """
        Copy a single file to a remote location.

        :param local_filepath: The local file path.
        :type local_filepath: str
        :param remote_filepath: The remote file path.
        :type remote_filepath: str
        """
        if not os.path.exists(local_filepath):
            logger.error(f"Local file not found: {local_filepath}")
            return
        self.sftp_session.put(local_filepath, remote_filepath)

    def _is_needed_permissions(self, ssh_manager) -> bool:
        """
        Check the permissions of the destination_path file or directory.

        :param ssh_manager: The SSH manager.
        :type ssh_manager: SSHManager
        :rtype: bool
        """
        dest = self.params.get("dest")

        stat_command = f"stat -c '%a %n' {dest}"
        stdin, stdout, stderr = ssh_manager.run_command(stat_command, pty=True)
        output = stdout.read().decode().strip()

        if "755" in output:
            return True
        if "644" in output:
            return True
        else:
            return False

    def _change_destination_permissions(self, ssh_manager, permissions_code) -> None:
        """
        Change the permissions of the destination_path file or directory.

        :param ssh_manager: The SSH manager.
        :type ssh_manager: SSHManager
        :param permissions_code: The permissions code.
        :type permissions_code: str
        """
        dest = self.params.get("dest")

        chmod_command = f"sudo chmod {permissions_code} {dest}"
        stdin, stdout, stderr = ssh_manager.run_command(chmod_command, pty=True)
        password = ssh_manager.password
        stdin.write(f"{password}\n")
        stdin.flush()

        exit_status = stdout.channel.recv_exit_status()

        if exit_status != 0:
            logger.error(f"Error while executing command: {stderr[:200]}")

    def render_template(self, template_path, variables) -> None:
        """
        Render a Jinja2 template and write it to a file.

        :param template_path: The path to the template file.
        :type template_path: str
        :param variables: The variables to render the template with.
        :type variables: dict
        """
        env = Environment(loader=FileSystemLoader("."))
        template = env.get_template(template_path)
        output = template.render(variables)

        with open("./default", "w") as f:
            f.write(output)
