from mylittleansible.modules.base import BaseModule

from mylittleansible.core.logger import get_logger


logger = get_logger(__name__)


class ServiceModule(BaseModule):
    """
    Run service commands on the remote host.
    """

    def process(self, ssh_manager) -> None:
        """
        Execute a service command with ssh client.

        :param ssh_manager: The SSH manager.
        :type ssh_manager: SSHManager
        """
        name = self.params.get("name")
        state = self.params.get("state")
        full_command = None

        if state == "start":
            full_command = f"sudo service {name} {state} start"
        elif state == "stop":
            full_command = f"sudo service {name} {state} stop"
        elif state == "restart":
            full_command = f"sudo service {name} {state} restart"

        if self.dry_run:
            logger.info(f"DRY_RUN [{self.index}] host={ssh_manager.hostname} op={self.name} name={name} state={state}")
            return

        stdin, stdout, stderr = ssh_manager.run_command(full_command, pty=True)
        password = ssh_manager.password
        stdin.write(f"{password}\n")
        stdin.flush()
        exit_status = stdout.channel.recv_exit_status()

        if exit_status != 0:
            logger.error(f"Error while executing command: {stderr}")

        logger.info(f"[{self.index}] host={ssh_manager.hostname} op={self.name} name={name} state={state}")
