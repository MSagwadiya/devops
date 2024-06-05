# Ansible Role: node exporter

## Description

Deploy prometheus node exporter using ansible.

## Requirements

- Ansible >= 2.9

## Role Variables

All variables which can be overridden are stored in [defaults/main.yml](defaults/main.yml) 

## Example

### Playbook

Use it in a playbook as follows:
```yaml
- hosts: all
  roles:
    - node_exporter
```

### TLS config

Before running node_exporter role, the user needs to provision their own certificate and key.
```yaml
- hosts: all
  pre_tasks:
    - name: Create node_exporter cert dir
      file:
        path: "/etc/node_exporter"
        state: directory
        owner: root
        group: root

    - openssl_privatekey:
            path: /etc/node_exporter/tls.key
            size: 2048 
        
    - openssl_csr:
        path: /etc/node_exporter/tls.csr
        privatekey_path: /etc/node_exporter/tls.key
    
    - name: Create cert and key
      openssl_certificate:
        provider: selfsigned
        selfsigned_not_after: "+3650d"
        path: /etc/node_exporter/tls.cert
        privatekey_path: /etc/node_exporter/tls.key
        csr_path: /etc/node_exporter/tls.csr
  roles:
    - node_exporter
  vars:
    node_exporter_tls_server_config:
      cert_file: /etc/node_exporter/tls.cert
      key_file: /etc/node_exporter/tls.key
    node_exporter_basic_auth_users:
      randomuser: examplepassword
```

