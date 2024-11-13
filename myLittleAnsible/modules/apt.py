from mylittleansible.modules.base import BaseModule
from mylittleansible.core.logger import get_logger

logger = get_logger(__name__)


class AptModule(BaseModule):
    """
    Install and uninstall packages via apt-get on Debian-based systems.
    """

    def process(self, ssh_manager) -> None:
        """
        Execute apt-get install or remove command using an SSH client.

        :param ssh_manager: The SSHManager instance to use to execute the action.
        :type ssh_manager: SSHManager
        """
        command_state = None

        if self.params.get("state") == "absent":
            command_state = "sudo apt -y remove"
        else:
            command_state = "sudo apt -y install"

        package_name = self.params.get("name")
        full_command = f"{command_state} {package_name}"

        if self.dry_run:
            logger.info(
                f"DRY_RUN [{self.index}] host={ssh_manager.hostname} op={self.name} name={package_name} state={self.params.get('state')}"
            )
            return

        stdin, stdout, stderr = ssh_manager.run_command(full_command, pty=True)
        password = ssh_manager.password
        stdin.write(f"{password}\n")
        stdin.flush()
        exit_status = stdout.channel.recv_exit_status()

        if exit_status != 0:
            logger.error(f"Error while executing command: {stderr}")

        logger.info(
            f"[{self.index}] host={ssh_manager.hostname} op={self.name} name={package_name} state={self.params.get('state')}"
        )
