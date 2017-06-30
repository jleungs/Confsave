#!/usr/bin/env python3
# ^ Change to whatever your python 3.5 is named

import os
import sys
from getpass import getpass
from datetime import datetime
import netmiko
import pexpect

def devices():
    inf = {
        'device_type': DEVICE,
        'ip': IP_ADDRESS,
        'username': USERNAME,
        'password': PASSWORD,
        'secret': ENABLE_PASSWORD}
    return inf

def writefile(output):
    date = datetime.now().strftime("%Y-%m-%d_%H:%M")
    filename = IP_ADDRESS + "_" + date + ".conf"
    cdir = os.getcwd()
    with open(filename, 'w') as f:
        f.write(output)
        f.close()
    print('The config saved as: "{}"\nDirectory: "{}"'.format(filename, cdir))

def telnet():
    try:
        connect_telnet = "telnet {}".format(IP_ADDRESS)
        child = pexpect.spawnu(connect_telnet, logfile=open(".templog", "w"))
    except:
        print("Couldnt connect via telnet either, check your connection")
        os.remove('.templog')
        exit()

    prompt = child.expect(['Press any key to continue',
                           'Username:', 'Password', '.*\>', '.*\#'], 3)
    print("Success! Getting config via Telnet.. ")
    while prompt is not 4:
			# While not the prompt is in priveleged mode, it tries to find it
			# if not found, times out in 3 sec
        with open(".templog", "r") as f:
            log_file = f.read()
            f.close()
        line_split = log_file.split('\n')
        for line in line_split:
            if "% " in line:
                print("Error occured: {}".format(line))
                os.remove('.templog')
                exit()
            if prompt == 0:
                child.sendline('')
                prompt = child.expect(['Press any key to continue',
                                       'Username:', 'Password', '.*\>', '.*\#'], 3)
            elif prompt == 1:
                child.sendline(USERNAME)
                prompt = child.expect(['Press any key to continue',
                                       'Username:', 'Password', '.*\>', '.*\#'], 3)
            elif prompt == 2:
                child.sendline(PASSWORD)
                prompt = child.expect(['Press any key to continue',
                                       'Username:', 'Password', '.*\>', '.*\#'], 3)
            elif prompt == 3:
                child.sendline('en')
                prompt = child.expect(['Press any key to continue',
                                       'Username:', 'Password', '.*\>', '.*\#'], 3)
    child.sendline("sh run")
    moretest = child.expect(['.*\#', '\ --More--\ '], 3)
    while moretest == 1:
        child.send(' ')
        moretest = child.expect(['.*\#', '\ --More--\ '], 3)
    with open(".templog", "r") as f:
        log_file = f.read()
        f.close()
    log_file = log_file.split('Building configuration...\n')[1]
    log_file = log_file[:log_file.rfind('\n')]
    os.remove('.templog')
    writefile(log_file)

def ssh():
    inf = devices()
    print("Trying to connect via SSH..")
    try:
        net_connect = netmiko.ConnectHandler(**inf) # Trying SSH first
    except:
        print("Failed to connect via SSH, trying Telnet")
        telnet() # If SSH doesnt work, tries telnet
    else:
        print("Success! Getting config via SSH..")
        net_connect.enable()
        output = net_connect.send_command('sh run')
        writefile(output)

if __name__ == '__main__':
    sys.tracebacklimit = None
    DEVICE = input("IOS(1)\nASA(2)\nChoose device type(1/2): ")
    if DEVICE == "1":
        DEVICE = 'cisco_ios'
    elif DEVICE == "2":
        DEVICE = 'cisco_asa'
    else:
        print("Choose 1 or 2")
        exit()
    IP_ADDRESS = input("Enter IP address: ")
    USERNAME = input("Enter Username: ")
    PASSWORD = getpass("Enter Password: ")
    ENABLE_PASSWORD = getpass("Enter enable password(if none, just hit enter): ")
    ssh()
