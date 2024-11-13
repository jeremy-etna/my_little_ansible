class BaseModule:
    """
    Base class for all modules.
    """

    def __init__(self, params, index, dry_run=False):
        """
        Initializes the module with the given parameters.

        :param params: The parameters to use for the module.
        :type params: dict
        :param index: The index of the module in the list of tasks.
        :type index: int
        """
        self.params = params
        self.index = index
        self.name = self.__class__.__name__.replace("Module", "")
        self.dry_run = dry_run

    def process(self, ssh_manager) -> None:
        """
        Apply the action to `ssh_client` using `params`.

        :param ssh_manager: The SSHManager instance to use to execute the action.
        :type ssh_manager: SSHManager
        """
        raise NotImplementedError("This method must be implemented by the subclass.")
