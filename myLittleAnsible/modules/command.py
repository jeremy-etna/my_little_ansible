from mylittleansible.modules.base import BaseModule
from mylittleansible.core.logger import get_logger

logger = get_logger(__name__)


class CommandModule(BaseModule):
    """
    Run any commands based on the todo file definition on the remote host.
    """

    def process(self, ssh_manager) -> None:
        """
        Execute a command with ssh client.

        :param ssh_manager: The SSH manager.
        :type ssh_manager: SSHManager
        """
        command_name = self.params.get("command")

        if self.dry_run:
            logger.info(f"DRY_RUN [{self.index}] host={ssh_manager.hostname} op={self.name} name={command_name}")
            return

        stdin, stdout, stderr = ssh_manager.run_command(command_name, pty=False)
        exit_status = stdout.channel.recv_exit_status()
        stderr_content = stderr.read()

        if exit_status != 0:
            logger.error(f"Error while executing command: {stderr_content[:200]}")

        logger.info(f"[{self.index}] host={ssh_manager.hostname} op={self.name} name={command_name}")
