import os
import platform
from pathlib import Path

from mylittleansible.modules.base import BaseModule
from mylittleansible.core.logger import get_logger

logger = get_logger(__name__)


class CopyModule(BaseModule):
    """
    Transferring files and directories over SFTP.
    """

    sftp_session = None

    def process(self, ssh_manager) -> None:
        """
        Execute the file or directory copy command using an SSH client.

        :param ssh_manager: The SSH manager.
        :type ssh_manager: SSHManager
        """
        try:
            source_path = self.params.get("src")
            destination_path = self.params.get("dest")
            make_backup = self.params.get("backup")
            self.sftp_session = ssh_manager.client.open_sftp()

            if self.dry_run:
                logger.info(
                    f"DRY_RUN [{self.index}] host={ssh_manager.hostname} op={self.name} src={source_path} dest={destination_path} backup={make_backup}"
                )
                return

            if os.path.isfile(source_path):
                logger.debug(
                    f"[{self.index}] host={ssh_manager.hostname} Copying file: {source_path} to {destination_path}"
                )

                if make_backup is True:
                    self._backup_file(ssh_manager)
                if self._is_needed_permissions(ssh_manager):
                    self._change_destination_permissions(ssh_manager, "777")
                    self._copy_file_to_remote(ssh_manager, source_path, destination_path)
                    self._change_destination_permissions(ssh_manager, "755")
                    logger.info(
                        f"[{self.index}] host={ssh_manager.hostname} op={self.name} src={source_path} dest={destination_path} backup={make_backup}"
                    )
                    return
                self._copy_file_to_remote(ssh_manager, source_path, destination_path)
                logger.info(
                    f"[{self.index}] host={ssh_manager.hostname} op={self.name} src={source_path} dest={destination_path} backup={make_backup}"
                )
            elif os.path.isdir(source_path):
                logger.debug(
                    f"[{self.index}] host={ssh_manager.hostname} Transferring directory: {source_path} to {destination_path}"
                )
                if make_backup is True:
                    self._backup_directory(ssh_manager)
                if self._is_needed_permissions(ssh_manager):
                    self._change_destination_permissions(ssh_manager, "777")
                    self._copy_directory_to_remote(source_path, destination_path)
                    self._change_destination_permissions(ssh_manager, "755")
                    logger.info(
                        f"[{self.index}] host={ssh_manager.hostname} op={self.name} src={source_path} dest={destination_path} backup={make_backup}"
                    )
                    return
                self._copy_directory_to_remote(source_path, destination_path)
            else:
                logger.error("The specified path does not exists.")
            logger.info(
                f"[{self.index}] host={ssh_manager.hostname} op={self.name} src={source_path} dest={destination_path} backup={make_backup}"
            )

        except FileNotFoundError:
            logger.error(f"[{self.index}] host={ssh_manager.hostname} The local file was not found.")
        except Exception as e:
            logger.error(f"[{self.index}] host={ssh_manager.hostname} Unexpected error: {str(e)}")
        finally:
            if self.sftp_session:
                self.sftp_session.close()

    def _copy_file_to_remote(self, ssh_manager, local_filepath, remote_filepath) -> None:
        """
        Copy a single file to a remote location.

        :param ssh_manager: The SSH manager.
        :type ssh_manager: SSHManager
        :param local_filepath: The local file path.
        :type local_filepath: str
        :param remote_filepath: The remote file path.
        :type remote_filepath: str
        """
        try:
            full_remote_path = os.path.join(remote_filepath, os.path.basename(local_filepath)).replace("\\", "/")
            self.sftp_session.put(local_filepath, full_remote_path)
            logger.debug(f"[{self.index}] host={ssh_manager.hostname} File copy success")
        except FileNotFoundError:
            logger.error("The local file was not found.")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")

    def _ensure_remote_directory(self, remote_directory):
        """
        Ensure that the remote directory exists, creating it if necessary.
        """
        try:
            self.sftp_session.chdir(remote_directory)
        except IOError:
            logger.debug(f"Creating remote directory: {remote_directory}")
            self.sftp_session.mkdir(remote_directory)
            self.sftp_session.chdir(remote_directory)

    def _copy_directory_to_remote(self, local_directory, remote_directory) -> None:
        """
        Recursively transfer a directory to a remote location.

        :param local_directory: The local directory path.
        :type local_directory: str
        :param remote_directory: The remote directory path.
        :type remote_directory: str
        """
        self._ensure_remote_directory(remote_directory)

        for item in Path(local_directory).rglob("*"):
            local_path = str(item)
            if platform.system() == "Windows":
                local_path = local_path.replace("\\", "/")

            relative_path = item.relative_to(Path(local_directory))
            if platform.system() == "Windows":
                relative_path = str(relative_path).replace("\\", "/")

            remote_path = os.path.join(remote_directory, str(relative_path))
            if platform.system() == "Windows":
                remote_path = remote_path.replace("\\", "/")

            if item.is_dir():
                logger.debug(f"Creating remote directory: {remote_path}")
                self._ensure_remote_directory(remote_path)
            else:
                logger.debug(f"Copying file: {local_path} to {remote_path}")
                self.sftp_session.put(local_path, remote_path)

    def _is_needed_permissions(self, ssh_manager) -> bool:
        """
        Check the permissions of the destination_path file or directory.

        :param ssh_manager: The SSH manager.
        :type ssh_manager: SSHManager
        :return: True if the permissions are not 755, False otherwise.
        :rtype: bool
        """
        dest = self.params.get("dest")
        stat_command = f"stat -c '%a %n' {dest}"
        stdin, stdout, stderr = ssh_manager.run_command(stat_command, pty=True)
        output = stdout.read().decode().strip()
        return True if "755" in output else False

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
        logger.debug(f"[{self.index}] host={ssh_manager.hostname} dest={dest} permission_code={permissions_code}")

    def _backup_file(self, ssh_manager) -> None:
        """
        Make a make_backup of the destination_path file.

        :param ssh_manager: The SSH manager.
        :type ssh_manager: SSHManager
        """
        source_path = self.params.get("src")
        destination_path = self.params.get("dest")
        file_name = os.path.basename(source_path)
        full_path = os.path.join(destination_path, file_name).replace("\\", "/")
        if self._check_remote_file_exists(ssh_manager, full_path):
            move_command = f"mkdir -p /tmp{destination_path} && sudo mv {destination_path}{file_name} /tmp{destination_path}{file_name}.backup"
            stdin, stdout, stderr = ssh_manager.run_command(move_command, pty=True)
            stdin.write(f"{ssh_manager.password}\n")
            stdin.flush()
            if stdout.channel.recv_exit_status() != 0:
                logger.error(f"Error while executing command: {stderr[:200]}")
        logger.debug(f"[{self.index}] host={ssh_manager.hostname} Backup done in /tmp/...")

    def _check_remote_file_exists(self, ssh_manager, file_path) -> bool:
        """
        Check if a file exists on the remote server.

        :param ssh_manager: The SSH manager.
        :type ssh_manager: SSHManager
        :param file_path: The file path.
        :type file_path: str
        """
        command = f"test -f {file_path} && echo 'Exists' || echo 'Not exists'"
        stdin, stdout, stderr = ssh_manager.run_command(command)
        result = stdout.read().decode().strip()
        return result == "Exists"

    def _backup_directory(self, ssh_manager) -> None:
        """
        Make a backup of the destination_path directory.

        :param ssh_manager: The SSH manager.
        :type ssh_manager: SSHManager
        """
        destination_path = self.params.get("dest")
        backup_path = f"/tmp{destination_path}"
        move_command = f"mkdir -p {backup_path} && mv {destination_path} {backup_path}.backup"
        stdin, stdout, stderr = ssh_manager.run_command(move_command)
        if stdout.channel.recv_exit_status() != 0:
            logger.error(f"Error while executing command: {stderr.read().decode()}")
        logger.debug(f"[{self.index}] host={ssh_manager.hostname} Directory backup done in /tmp/...")

    def _check_remote_directory_exists(self, ssh_manager, directory_path) -> bool:
        """
        Check if a directory exists on the remote server.

        :param ssh_manager: The SSH manager.
        :type ssh_manager: SSHManager
        :param directory_path: The directory path.
        :type directory_path: str
        :rtype: bool
        """
        command = f"test -d {directory_path} && echo 'Exists' || echo 'Not exists'"
        stdin, stdout, stderr = ssh_manager.run_command(command)
        result = stdout.read().decode().strip()
        return result == "Exists"
