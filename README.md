# My Little Ansible

## Description

My Little Ansible is a lightweight automation tool designed to simplify and streamline the execution of tasks across multiple hosts. Utilizing Python and the `click` library, it processes inventory and tasks from YAML files to execute predefined actions on specified hosts. This tool is ideal for small to medium-scale automation tasks where quick setup and ease of use are important.

## Features

- **Inventory Management**: Easily manage host configurations with a simple YAML format.
- **Todo Execution**: Perform a series of tasks defined in YAML files across multiple hosts.

## Installation

Follow these steps to get My Little Ansible up and running on your system:

1. **Clone the repository:**
   ```bash
   git clone https://rendu-git.etna-alternance.net/module-9615/activity-51952/group-1031945.git

2. **Navigate to the project directory:**
   ```bash
   cd group-1031945

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt

4. **Make package:**
   ```bash
   python setup.py sdist

5. **Install package:**
```bash
   pip install .

6. **Add bin to PATH**
   ```bash
   export PATH=$PATH:~/.local/bin

7. **Run program:**
   ```bash
   mla -t todos.yml -i inventory.yml