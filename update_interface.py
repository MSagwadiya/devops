#!/usr/bin/env python3

import os
import json
import netaddr
import subprocess
import pynetbox
import sys
import argparse
import logging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


logfile = 'netboxapp.log'
log_format = ('[%(asctime)s] %(levelname)-8s %(message)s')

logging.basicConfig(
    level=logging.WARNING,
    format=log_format,
    handlers=[
        logging.FileHandler(logfile),
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger("my_logger")


parse = argparse.ArgumentParser(description='Populate netbox interfaces from ansible facts')
parse.add_argument('--ip', required=True, help='IP Address of the device')
parse.add_argument("-d", "--dry", help="Don't update netbox", action="store_true")
group = parse.add_mutually_exclusive_group()
group.add_argument('-f', '--file', help="File containing netbox token", type=str, default="netbox_token")
group.add_argument('-t', '--token', help="Authentication token for netbox", type=str)
args = parse.parse_args()

if args.token:
    token_value = args.token
else:
    token_path = args.file
    if os.path.exists(token_path) and os.path.getsize(token_path) > 0:
        f = open(token_path, "r")
        token_value = f.read().strip()
    else:
        logger.error(f"Please provide netbox token or file containing netbox token as argument or save it to default file: {os.path.abspath(token_path)}")
        sys.exit(0)

nb = pynetbox.api('http://192.168.1.4:8000', token=token_value)
cmd = f"ansible -u root -i {args.ip}, {args.ip} -m gather_facts | sed '0,/.*{{/s//{{/'"

fact = subprocess.check_output(cmd , shell=True)
data = json.loads(fact)

hostname = data['ansible_facts']['ansible_hostname']
    
logger.info(f"Checking for Device: {hostname}")
try:
    nbhost = nb.dcim.devices.get(name=hostname)
except pynetbox.RequestError as e:
    logger.error(e)
    sys.exit(0)
except ValueError as e:
    logger.error(e)
    sys.exit(0)
if nbhost:
    if nbhost.config_context.get('ifname_bridge_interface'):
        pri_if = nbhost.config_context.get('ifname_bridge_interface')
    else:
        pri_if = "lan0"
    bridged_if = 0
    if any("brintf" == tag.name for tag in nbhost.tags):
        bridged_if = 1
    nb_interfaces = nb.dcim.interfaces.filter(device=nbhost.name)
    ansible_interfaces = []
    host_facts = json.loads(fact)
    if not 'ansible_facts' in host_facts.keys():
        logger.critical(f"Error for Host {hostname}: {host_facts['msg']}")
        sys.exit(0)
    host = host_facts['ansible_facts']
    if host.get('ansible_default_ipv4'):
        default_ip = host['ansible_default_ipv4']['address']
    else:
        default_ip = None
    for i in host['ansible_interfaces']:
        if i.startswith(('vb', 'virb', 'veth')):
            continue
        i_r = i.replace("-", "_")
        if host.get('ansible_' + i_r):
            if host['ansible_' + i_r].get('macaddress'):
                if_type = host['ansible_' + i_r].get('type')
                if if_type != "ether":
                    continue
                ansible_interfaces.append(i)
                mac = host['ansible_' + i_r].get('macaddress')
                mtu = host['ansible_' + i_r].get('mtu',None)
                active = host['ansible_' + i_r].get('active',None)
                ips = []
                if host['ansible_' + i_r].get('ipv4', None):
                    ip = host['ansible_' + i_r]['ipv4']
                    if default_ip == ip['address']:
                        is_primary = True
                    else:
                        is_primary = False
                    ips.append({
                        'address': '%s/%s' % (ip['address'], netaddr.IPAddress(ip['netmask']).netmask_bits()),
                        'is_primary': is_primary
                    })
                if host['ansible_' + i_r].get('ipv4_secondaries', None):
                    for ip in host['ansible_' + i_r]['ipv4_secondaries']:
                        if default_ip == ip['address']:
                            is_primary = True
                        else:
                            is_primary = False
                        ips.append({
                            'address': '%s/%s' % (ip['address'], netaddr.IPAddress(ip['netmask']).netmask_bits()),
                            'is_primary': is_primary
                        })
                if i == pri_if and bridged_if:
                    if len(ips) > 0:
                        logger.critical(f"Device: {nbhost.name} Interface: {i} Error occured: IPs available in bridged interface")
                        break
                    br_if = "br0"
                    if host.get('ansible_' + br_if):
                        if host['ansible_' + br_if].get('ipv4', None):
                            ip = host['ansible_' + br_if]['ipv4']
                            is_primary = False
                            if default_ip == ip['address']:
                                is_primary = True
                            ips.append({
                                'address': '%s/%s' % (ip['address'], netaddr.IPAddress(ip['netmask']).netmask_bits()),
                                'is_primary': is_primary
                            })
                        if host['ansible_' + br_if].get('ipv4_secondaries', None):
                            for ip in host['ansible_' + br_if]['ipv4_secondaries']:
                                is_primary = False
                                if default_ip == ip['address']:
                                    is_primary = True
                                ips.append({
                                    'address': '%s/%s' % (ip['address'], netaddr.IPAddress(ip['netmask']).netmask_bits()),
                                    'is_primary': is_primary
                                })
                    else:
                        logger.critical(f"Device: {nbhost.name} Interface: {i} Error occured: bridge interface not found for tagged device")
                logger.info(f"Interface: {i}")
                logger.info(f"List of IPs on interface: {ips}")
                if args.dry:
                    print("%s\t%s\t%s\t%s\t%s\t%s" % (hostname, i, mac, mtu, active, 1000), end="")
                    for ip in ips:
                        print("\t%s\t%s" % (ip['address'], ip['is_primary']), end="")
                    print()
                interface_type = "1000base-t"
                nb_status = "NOTFOUND"
                for m in nb_interfaces:
                    if m.name == i:
                        interface = m
                        change_flag = 0
                        nb_status = "FOUND"
                        logger.info(f"Interface exist: {i}")
                        nb_if_ips = nb.ipam.ip_addresses.filter(device=nbhost.name, interface=m.name)
                        for x in nb_if_ips:
                            logger.info(f"IP on interface {x}")
                            present_flag=1
                            for ip in ips:
                                if str(x) == ip['address']:
                                    present_flag=0
                                    break
                            if present_flag == 1:
                                logger.warning(f"Device: {nbhost.name} Interface: {m.name} Deleting IP: {x}")
                                if not args.dry:
                                    x.delete()
                        if m.mac_address.lower() != mac:
                            logger.warning(f"Device: {nbhost.name} Interface: {m.name} NOT Updating MAC from {m.mac_address} to {mac}")
                            #m.mac_address = mac
                            #change_flag = 1
                        if m.mtu != mtu:
                            logger.warning(f"Device: {nbhost.name} Interface: {m.name} Updating MTU from {m.mtu} to {mtu}")
                            m.mtu = mtu
                            change_flag = 1
                        if m.enabled != active:
                            logger.warning(f"Device: {nbhost.name} Interface: {m.name} Updating Active status from {m.enabled} to {active}")
                            m.enabled = active
                            change_flag = 1
                        if change_flag == 1:
                            if not args.dry:
                                if m.type == None:
                                    m.type = interface_type
                                m.save()
                if nb_status == "NOTFOUND":
                    logger.warning(f"Device: {nbhost.name} Creating Interface: {i}")
                    if not args.dry:
                        interface = nb.dcim.interfaces.create(device=nbhost.id, name=i, mac_address=mac, mtu=mtu, enabled=active, type=interface_type)
                for ip in ips:
                    object_type = "dcim.interface"
                    actual_ip = ip['address']
                    try:
                        ip_obj = nb.ipam.ip_addresses.get(address=actual_ip)
                    except ValueError as e:
                        logger.exception(f"IP: {actual_ip} multiple IP exist")
                        ip_obj_list = nb.ipam.ip_addresses.filter(device=nbhost.name, address=actual_ip)
                        if len(ip_obj_list) == 1:
                            ip_obj = ip_obj_list[0]
                        else:
                            logger.critical(f"Device: {nbhost.name} Interface: {m.name} Getting error on getting IP: {actual_ip}")
                    if ip_obj:
                        logger.info(f"IP {actual_ip} found")
                        if not ip_obj.assigned_object:
                            logger.warning(f"Attaching IP {actual_ip} to Device: {nbhost.name} Interface: {m.name}")
                            ip_obj.assigned_object_id = interface.id
                            if not args.dry:
                                ip_obj.save()
                        if ip_obj.assigned_object_id != interface.id:
                            logger.warning(f"Attaching IP {actual_ip} from Device: {ip_obj.assigned_object.device.name} Interface: {ip_obj.assigned_object.name} to Device: {nbhost.name} Interface: {m.name}")
                            if not args.dry:
                                ip_obj.assigned_object_id = interface.id
                                ip_obj.save() 
                    else:
                        logger.warning(f"Device: {nbhost.name} Interface: {interface.name} Creating IP {actual_ip}")
                        if not args.dry:
                            ip_obj = nb.ipam.ip_addresses.create(assigned_object_type=object_type, assigned_object_id=interface.id, address= ip['address'])
                    if ip['is_primary']:
                        if nbhost.primary_ip4:
                            if str(nbhost.primary_ip4) != str(ip_obj):
                                logger.warning(f"Device: {nbhost.name} Updating primary IP from {nbhost.primary_ip4} to {ip_obj}")
                                nbhost.primary_ip4 = ip_obj
                                if not args.dry:
                                    nbhost.save()
                        else:
                            logger.warning(f"Device: {nbhost.name} Setting primary IP from None to {ip_obj}")
                            nbhost.primary_ip4 = ip_obj
                            if not args.dry:
                                nbhost.save()
    logger.info(f"Ansible Interfaces: {ansible_interfaces}")
    logger.info(f"Netbox Interfaces:  {nb_interfaces}")
    for nb_if in nb_interfaces:
        found_flag = 0
        for an_if in ansible_interfaces:
            if str(nb_if) == str(an_if):
                logger.info(f"Device: {nbhost.name} NB Interface: {nb_if.name} exist in ansible facts")
                found_flag = 1
                break
        if not found_flag:
            logger.warning(f"Device: {nbhost.name} NB Interface: {nb_if.name} does not exist in ansible facts, Deleted")
            if not args.dry:
                nb_if.delete() 
else:
    logger.warning(f"Device: {hostname} not found in netbox")