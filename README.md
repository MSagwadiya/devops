## Installing the collection

Before using the Roles, you need to install collections using the below command:

```shell
ansible-galaxy collection install -r requirements.yml
```

# Directory Structure

The project consists of the following files and directories:

1. **roles**:
    - **common**: Contains common tasks and configurations applicable across all hosts.
    - **interfaces**: Manages network interfaces on hosts.

2. **ansible.cfg**:
    - Configuration file for Ansible.
    - Specifies the remote SSH port (currently set to 22, but can be customized).
    - Allows users to specify the remote user during runtime using the `-u` flag.
    - Provides options for runtime password usage and other dynamic configurations.

3. **netbox.py**:
    - Python script designed to fetch variables, names, IP addresses, and other relevant information from NetBox.
    - Organizes the retrieved data into a dynamic inventory, which can then be utilized in Ansible playbooks.

4. **update_interface.py**:
    - Automates the process of updating interface names in NetBox.
    - Retrieves interface names from hosts using Ansible and updates them in NetBox.
    - Facilitates the seamless integration of updated interface names into the Ansible workflow.

5. **update_netbox.py**:
    - In-progress script intended to update comprehensive information to NetBox.
    - Once completed, it will automate the process of updating various information, ensuring synchronization between the infrastructure and NetBox.

**Note**: While some tasks are currently manual, efforts are underway to automate them. Automation enhancements, such as those for updating interface names and synchronizing information with NetBox, are planned to streamline operations and improve efficiency.
