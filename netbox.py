#!/usr/bin/env python3

import json
import requests

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

NETBOX_URL = 'http://192.168.1.4:8000/'
NETBOX_TOKEN = 'f3a4e67b106f234bde2c6851768fe7943c0294d7'
FILTER_TAGS = ['ANSIBLE']

headers = {
    'Accept': 'application/json',
    'Authorization': f'Token {NETBOX_TOKEN}',
}

def get_data(api_url):
    data = []
    while api_url:
        response = requests.get(api_url, headers=headers, verify=False)
        response_data = response.json()
        data.extend(response_data.get('results', []))
        api_url = response_data.get('next')
    return data

def create_inventory(device_data, interface_data, ip_data):
    inventory = {'_meta': {'hostvars': {}}}
    tag_types = ['site', 'rack', 'platform', 'tenant']

    # Mapping IP addresses to device names
    ip_to_device_map = {ip.split('/')[0]: device['name'] for device in device_data for ip in [device.get('primary_ip4', {}).get('address')] if ip}

    # Group interfaces by device
    interfaces_by_device = {}
    for interface in interface_data:
        device_name = interface['device']['name']
        interfaces_by_device.setdefault(device_name, []).append(interface)

    for device in device_data:
        primary_ip = device.get('primary_ip4', {}).get('address')
        if primary_ip:
            hostname = primary_ip.split('/')[0]
            inventory['_meta']['hostvars'][hostname] = {}
            for tag_type in tag_types:
                if tag_type in device and device[tag_type]:
                    tag_slug = device[tag_type]['slug']
                    inventory.setdefault(tag_slug, {'hosts': []})['hosts'].append(hostname)
                    inventory['_meta']['hostvars'][hostname].setdefault('tags', {})[tag_type] = tag_slug
            if device['tags']:
                for tag_item in device['tags']:
                    inventory.setdefault(tag_item['name'], {'hosts': []})['hosts'].append(hostname)
                    inventory['_meta']['hostvars'][hostname].setdefault('tags', {})[tag_item['name']] = True
            
            inventory['_meta']['hostvars'][hostname]['static_hostname'] = device['name']
            
            if device['name'] in interfaces_by_device:
                for interface in interfaces_by_device[device['name']]:
                    interface_name = interface['name']
                    ip_routes = []
                    routing_policy = []
                    if 'config_context' in device:
                        if 'ifname_routes' in device['config_context'] and interface_name in device['config_context']['ifname_routes']:
                            ip_routes = device['config_context']['ifname_routes'][interface_name]
                        if 'ifname_routing_policy' in device['config_context'] and interface_name in device['config_context']['ifname_routing_policy']:
                            routing_policy = device['config_context']['ifname_routing_policy'][interface_name]
                    ip_addresses = [ip['address'] for ip in ip_data if ip['assigned_object'] and ip['assigned_object']['device']['name'] == device['name'] and ip['assigned_object']['name'] == interface_name]                       
                    mac_address = interface.get('mac_address', '').lower()
                    inventory['_meta']['hostvars'][hostname].setdefault('interfaces', []).append({
                        'name': interface_name,
                        'mac_address': mac_address,
                        'enabled': interface['enabled'],
                        'ip': ip_addresses,
                        'routes': ip_routes,
                        'routing_policy': routing_policy
                    })
                    
            if 'config_context' in device:
                inventory['_meta']['hostvars'][hostname]['config_context'] = device['config_context']
                
        

    for device_name, device_vars in inventory['_meta']['hostvars'].items():
        for iface in device_vars.get('interfaces', []):
            if not iface.get('ip'):
                iface['ip'] = []
                

    return inventory

device_data = get_data(f'{NETBOX_URL}/api/dcim/devices/')
interface_data = get_data(f'{NETBOX_URL}/api/dcim/interfaces/')
ip_data = get_data(f'{NETBOX_URL}/api/ipam/ip-addresses/')

inventory = create_inventory(device_data, interface_data, ip_data)

print(json.dumps(inventory, indent=2))