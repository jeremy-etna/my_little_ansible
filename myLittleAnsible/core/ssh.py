import os
from typing import Optional

import paramiko

from mylittleansible.core.logger import get_logger


logger = get_logger(__name__)


class SSHManager:
    """
    Manage SSH connections to execute commands on remote hosts.
    """

    client: Optional[paramiko.SSHClient] = None

    def __init__(
        self,
        hostname: str,
        username: Optional[str] = None,
        port: int = 22,
        password: Optional[str] = None,
        key_filename: Optional[str] = None,
    ) -> None:
        """
        Initializes the SSHManager instance with server connection settings.

        :param hostname: The hostname or IP address of the remote server.
        :type hostname: str
        :param port: The port number to connect to on the remote server. Defaults to 22.
        :type port: int
        :param username: The username for authentication. Optional.
        :type username: str, optional
        :param password: The password for authentication. Optional.
        :type password: str, optional
        :param key_filename: The path to the SSH private key file. Optional.
        :type key_filename: str, optional
        """
        self.hostname: str = hostname
        self.port: int = port
        self.username: Optional[str] = username
        self.password: Optional[str] = password
        self.key_filename: Optional[str] = key_filename

    def connect(self) -> None:
        """
        Establishes an SSH connection to the specified server using either password, key file, or default SSH config.
        """
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if self.username and self.password:
                self.client.connect(self.hostname, port=self.port, username=self.username, password=self.password)
            elif self.username and self.key_filename:
                self.client.connect(
                    self.hostname, port=self.port, username=self.username, key_filename=self.key_filename
                )
            else:
                self.client.load_system_host_keys()
                default_username = os.getlogin()
                self.client.connect(self.hostname, port=self.port, username=default_username)

        except Exception as e:
            logger.error(f"Error while connecting to {self.hostname}: {e}")
            raise

    def run_command(self, command, pty=False) -> tuple:
        """
        Run the command passed in parameter.

        :param command: The command to run on the remote server.
        :type command: str
        :param pty: Request a pseudo-terminal for the command. Defaults to False.
        :type pty: bool
        """
        if self.client is None:
            self.connect()
        return self.client.exec_command(command, get_pty=pty)

    def close(self) -> None:
        """
        Closes the SSH connection.
        """
        if self.client:
            self.client.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
