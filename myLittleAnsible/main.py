import yaml
import click
from typing import Any, Dict
from mylittleansible.core.logger import get_logger
from mylittleansible.core.runner import Runner

logger = get_logger(__name__)


def load_yaml_file(file_path: str, content_type: str) -> Dict[str, Any]:
    """
    Load and return the contents of a YAML file, validating it based on the type of content expected (inventory or todos).

    :param file_path: Path to the YAML file.
    :param content_type: Type of the content expected ('inventory' or 'todos').
    :type file_path: str
    :type content_type: str
    :return: Parsed YAML content as a dictionary.
    :rtype: dict
    """
    try:
        with open(file_path, encoding="utf-8") as file:
            content = yaml.safe_load(file)
            validate_yaml_content(content, content_type)
            return content
    except yaml.YAMLError as e:
        logger.error(f"YAML parsing error in file {file_path}: {e}")
        raise
    except FileNotFoundError:
        logger.error(f"The file {file_path} does not exist.")
        raise
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise


def validate_yaml_content(content: Dict[str, Any], content_type: str) -> None:
    """
    Validates the structure of the loaded YAML content based on the specified content type.

    :param content: YAML content to validate.
    :param content_type: Type of content ('inventory' or 'todos') to validate against.
    :type content: dict
    :type content_type: str
    :raises ValueError: If the YAML content does not meet the expected schema.
    """
    if content_type == "inventory" and "hosts" not in content:
        raise ValueError("The inventory content is missing the 'hosts' key.")
    elif content_type == "todos" and not isinstance(content, list):
        raise ValueError("The todos content should be a list of tasks.")


@click.command()
@click.option(
    "-i", "--inventory", "inventory_file", type=click.Path(exists=True), required=True, help="Inventory YAML file."
)
@click.option("-t", "--todos", "todos_file", type=click.Path(exists=True), required=True, help="Tasks YAML file.")
@click.option("--dry-run", is_flag=True, help="Run in dry-run mode (no actual execution).")
def main(inventory_file: str, todos_file: str, dry_run: bool) -> None:
    """
    Main execution function that parses the inventory and todos YAML files and executes tasks on hosts.

    :param inventory_file: Path to the inventory YAML file containing host information.
    :type inventory_file: str
    :param todos_file: Path to the tasks YAML file containing tasks to be executed.
    :type todos_file: str
    """
    inventory = load_yaml_file(inventory_file, "inventory")
    todos = load_yaml_file(todos_file, "todos")

    hosts = [host_details.get("ssh_address") for host_name, host_details in inventory.get("hosts", {}).items()]
    logger.info(f"Processing {len(todos)} task(s) on hosts: {hosts}")

    runner = Runner(inventory, todos, dry_run=dry_run)
    runner.run()

    logger.info(f"processing tasks on hosts: {hosts} -> DONE")


if __name__ == "__main__":
    main()
