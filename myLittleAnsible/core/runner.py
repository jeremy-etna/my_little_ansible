from typing import Any, Dict, Type
from mylittleansible.core.logger import get_logger
from mylittleansible.core.ssh import SSHManager
from mylittleansible.modules.apt import AptModule
from mylittleansible.modules.command import CommandModule
from mylittleansible.modules.service import ServiceModule
from mylittleansible.modules.sysctl import SysctlModule
from mylittleansible.modules.copy import CopyModule
from mylittleansible.modules.template import TemplateModule
from mylittleansible.modules.base import BaseModule

logger = get_logger(__name__)


class Runner:
    """
    Manages the execution of tasks on hosts defined in the inventory.
    """

    def __init__(self, inventory: Dict[str, Any], todos: Dict[str, Any], dry_run) -> None:
        self.inventory = inventory
        self.todos = todos
        self.dry_run = dry_run

    def run(self) -> None:
        """
        Executes each task defined in todos on appropriate hosts.
        """
        for i, todo in enumerate(self.todos):
            module = self._load_module(todo["module"], todo["params"], i + 1)
            self._execute_on_all_hosts(module)

    def _execute_on_all_hosts(self, module: BaseModule) -> None:
        """
        Helper method to execute a given module on all hosts in the inventory.

        :param module: The module to execute on all hosts.
        :type module: BaseModule
        """
        for host_name, host_details in self.inventory["hosts"].items():
            with SSHManager(
                hostname=host_details["ssh_address"],
                port=host_details.get("ssh_port", 22),
                username=host_details.get("ssh_user"),
                password=host_details.get("ssh_password"),
                key_filename=host_details.get("ssh_key_file"),
            ) as ssh_client:
                ssh_client.connect()
                module.process(ssh_client)

    def _load_module(self, module_name: str, params: Dict[str, Any], index: int) -> BaseModule:
        """
        Dynamically loads the module based on the module_name.

        :param module_name: The name of the module to load.
        :param params: The parameters to pass to the module.
        :param index: The index of the module in the list of tasks.
        :return: An instance of the specified module class.
        """
        modules: Dict[str, Type[BaseModule]] = {
            "command": CommandModule,
            "apt": AptModule,
            "service": ServiceModule,
            "sysctl": SysctlModule,
            "copy": CopyModule,
            "template": TemplateModule,
        }
        if module_name in modules:
            return modules[module_name](params, index, self.dry_run)
        else:
            logger.error(f"Unknown module: {module_name}")
            raise ValueError(f"Unknown module: {module_name}")
