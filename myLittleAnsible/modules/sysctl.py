from mylittleansible.modules.base import BaseModule
from mylittleansible.core.logger import get_logger


logger = get_logger(__name__)


class SysctlModule(BaseModule):
    """
    Run sysctl commands on the remote host.
    """

    def process(self, ssh_manager) -> None:
        """
        Execute a sysctl command with ssh client.

        :param ssh_manager: The SSH manager.
        :type ssh_manager: SSHManager
        """
        full_command = ""

        attribute = self.params.get("attribute")
        permanent = self.params.get("permanent")
        value = self.params.get("value")

        full_command = f"sudo sysctl -w {attribute}={value}"

        if self.dry_run:
            logger.info(
                f"DRY_RUN [{self.index}] host={ssh_manager.hostname} op={self.name} attribute={attribute} value={value} permanent={permanent}"
            )
            return

        try:
            stdin, stdout, stderr = ssh_manager.run_command(full_command, pty=True)
        except Exception as e:
            logger.error(f"Error while executing command: {e}")
            return

        if self.params.get("permanent") == "true":
            if self.dry_run:
                logger.info(
                    f"DRY_RUN [{self.index}] host={ssh_manager.hostname} op={self.name} attribute={attribute} value={value} permanent={permanent}"
                )
                return

            stdin, stdout, stderr = ssh_manager.run_command("sudo sysctl -p", pty=True)

        password = ssh_manager.password
        stdin.write(f"{password}\n")
        stdin.flush()

        exit_status = stdout.channel.recv_exit_status()

        if exit_status != 0:
            logger.error(f"Error while executing command: {stderr}")

        logger.info(
            f"[{self.index}] host={ssh_manager.hostname} op={self.name} attribute={attribute} value={value} permanent={permanent}"
        )
