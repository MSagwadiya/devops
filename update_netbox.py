#!/usr/bin/env python3

import json
import subprocess
import sys
import argparse
import pynetbox
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    parser = argparse.ArgumentParser(description="Update NetBox with Ansible facts")
    parser.add_argument('--ip', required=True, help='IP Address of the device')
    parser.add_argument('--token', required=True, help='NetBox API Token')
    args = parser.parse_args()

    # Netbox URL
    URL = 'http://192.168.1.4:8000/'

    # Netbox API Token
    TOKEN = args.token

    # Ansible command to gather facts
    try:
        cmd = f"ansible -u root -i {args.ip}, {args.ip} -m gather_facts | sed '0,/.*{{/s//{{/'"
        fact = subprocess.check_output(cmd, shell=True)
        data = json.loads(fact)
        hostname = data["ansible_facts"]['ansible_hostname']
        print(data)
        
        # Initialize dictionary to store NetBox fields
        nb_fields = {
            'name': hostname,
            'status': 'active',
            'site': None,
            'device_type': None,
            'platform': None,
            'serial': None,
            'asset_tag': None,
            'rack': None,
            'position': None,
            'face': None
        }
        
        # Mapping Ansible facts to NetBox fields
        ansible_to_netbox_map = {
            'ansible_hostname': 'name',
            'ansible_distribution': 'platform',
            'ansible_distribution_version': 'platform',
            'ansible_product_name': 'Conso',
            'ansible_product_serial': 'serial',
            'ansible_product_asset_tag': 'asset_tag'
        }

        for ansible_fact, netbox_field in ansible_to_netbox_map.items():
            if ansible_fact in data['ansible_facts']:
                value = data['ansible_facts'][ansible_fact]
                print(value)
                print(ansible_fact)
                if netbox_field in ['asset_tag','serial']:
                    try:
                        value = int(value)
                    except ValueError:
                        value = ""
                nb_fields[netbox_field] = value

        site = input("Enter the site name: ")
        rack = input("Enter the rack name: ")
        position = input("Enter the position: ")
        face = input("Enter the face (front/back): ")

        nb_fields['site'] = site
        nb_fields['rack'] = rack
        nb_fields['position'] = position
        nb_fields['face'] = face

        nb = pynetbox.api(URL, token=TOKEN)
        nbhost = nb.dcim.devices.get(name=hostname)

        if not nbhost:
            nb_device = nb.dcim.devices.create(**nb_fields)
            
            print(f"Device '{hostname}' created in NetBox.")
        else:
            print("Device already exists in NetBox.")

    except subprocess.CalledProcessError as e:
        print(f"Error executing Ansible command: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except pynetbox.RequestError as e:
        print(f"NetBox API error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
