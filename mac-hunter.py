"""
AUTHOR: IPvZero
DATE: 21 Oct 2020

"""

import os
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from rich import print as rprint

nr = InitNornir(config_file="config.yaml")
break_list = []

CLEAR = "clear"
os.system(CLEAR)
target = input("Enter the mac address you wish to find: ")


def pull_info(task):

    """
    1) If MAC address is present, identify Device and Interface
    """

    result = task.run(
        task=netmiko_send_command, command_string="show interfaces", use_genie=True
    )
    task.host["facts"] = result.result
    interfaces = task.host["facts"]
    for interface in interfaces:
        mac_addr = interfaces[interface]["mac_address"]
        if target == mac_addr:
            break_list.append(target)
            intf = interface
            print_info(task, intf)


def print_info(task, intf):

    """
    Execute show cdp neighbor and show version commands
    on target device. Parse information and return output
    """

    rprint("\n[green]*** TARGET IDENTIFIED ***[/green]")
    print(f"MAC ADDRESS: {target} is present on {task.host}'s {intf}")
    rprint("\n[cyan]GENERATING DETAILS...[/cyan]")
    cdp_result = task.run(
        task=netmiko_send_command, command_string="show cdp neighbors", use_genie=True
    )
    task.host["cdpinfo"] = cdp_result.result
    index = task.host["cdpinfo"]["cdp"]["index"]
    for num in index:
        local_intf = index[num]["local_interface"]
        if local_intf == intf:
            dev_id = index[num]["device_id"]
            port_id = index[num]["port_id"]
    ver_result = task.run(
        task=netmiko_send_command, command_string="show version", use_genie=True
    )
    task.host["verinfo"] = ver_result.result
    version = task.host["verinfo"]["version"]
    serial_num = version["chassis_sn"]
    oper_sys = version["os"]
    uptime = version["uptime"]
    version_short = version["version_short"]
    print(f"DEVICE MGMT IP: {task.host.hostname}")
    print(f"DEVICE SERIAL NUMBER: {serial_num}")
    print(f"DEVICE OPERATING SYSTEM: {oper_sys}")
    print(f"DEVICE UPTIME: {uptime}")
    print(f"DEVICE VERSION: {version_short}\n")
    if dev_id:
        rprint("[cyan]REMOTE CONNECTION DETAILS...[/cyan]")
        print(f"Connected to {port_id} on {dev_id}\n")


results = nr.run(task=pull_info)
if target not in break_list:
    rprint("[red]TARGET NOT FOUND[/red]")
