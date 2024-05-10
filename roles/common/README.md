# Role Name

This Ansible role is designed to handle all configuration tasks after the operating system installation is completed.

## Description

The role encompasses various configuration tasks necessary for setting up a server or system environment after the base operating system has been installed. It ensures that the system is properly configured and ready for its intended use.

## Requirements

This role assumes that the base operating system is already installed on the target system. Additionally, ensure that Ansible is installed on the control node from which you will be running the playbook.

## Role Variables

This role utilizes the following files and variables:

1. `vars/main.yml`: Contains role-specific variables and configurations.
2. `config_context`: Information retrieved from NetBox, such as interface details and network settings.
3. `defaults/main.yml`: Default values for variables used within the role.

## Playbooks

This role consists of various tasks organized into separate playbooks:

- `01_add_repository_for_toolchain.yml`
- `02_install_kitware.yml`
- `03_install_packages.yml`
- `04_install_python_packages.yml`
- `05_disable_ufw.yml`
- `06_disable_apport.yml`
- `07_configure_kernel_core_pattern.yml`
- `08_configure_sshd.yml`
- `09_set_kernel_grub_parameters.yml`
- `10_stop_and_disable_irqbalance.yml`
- `11_update_editor_to_vim.yml`
- `12_set_tuned_profile.yml`
- `13_add_group_showpid.yml`
- `14_mount_fstab.yml`
- `15_replace_directory_mode_conf.yml`
- `16_remove_execute_permission_update_motd.yml`
- `17_set_timezone.yml`
- `18_remove_landscape_unattended_upgrades.yml`
- `19_set_default_target_multi_user.yml`
- `20_setup_root_cronjobs.yml`
- `21_install_exanic.yml`
- `22_ipc.yml`
- `main.yml`: Contains all tasks.

## Dependencies

List any other roles hosted on Galaxy that are required by this role. Include details regarding parameters that may need to be set for other roles or variables used from other roles.

## Example Playbook

```yaml
- name: Configure Network Interfaces
  hosts: <server_ip>
  tasks:
    - import_role:
        name: common
```

## Author Information

This Ansible role was created by Manav Sagwadiya for use in the Aakraya infrastructure. 