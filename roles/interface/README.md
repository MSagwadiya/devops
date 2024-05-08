# Role Name

This Ansible role is designed to configure network interfaces on hosts and synchronize them with NetBox in the Aakraya infrastructure.

## Description

This role ensures proper configuration of network interfaces on target hosts and ensures that the network settings are in sync with the NetBox inventory management system deployed in the Aakraya infrastructure.

## Requirements

To use this role effectively, ensure the following:

- Ansible is installed on the control node.
- Access to the target hosts where network interfaces need to be configured.
- Proper connectivity to the NetBox instance deployed in the Aakraya infrastructure.
- Access to necessary credentials or API tokens for interacting with NetBox.

## Role Variables

This role utilizes the following files and variables:

1. `vars/main.yml`: Contains role-specific variables and configurations.
2. `config_context`: Information retrieved from NetBox, such as interface details and network settings.
3. `defaults/main.yml`: Default values for variables used within the role.

## Example Playbook

```yaml
- name: Configure Network Interfaces
  hosts: <server_ip>
  tasks:
    - import_role:
        name: interface
```

## Author Information

This Ansible role was created by Manav Sagwadiya for use in the Aakraya infrastructure. 