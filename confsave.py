#!/usr/bin/env python3
# ^ Change to whatever your python 3.5 is named

import os, netmiko, pexpect, sys
from getpass import getpass
from datetime import datetime

def devices():
	inf = {
    	'device_type': 'cisco_ios',
    	'ip': ip,
    	'username': user,
    	'password': pw,
		'secret': enable}
	return inf

def writefile(con, output):
	date = datetime.now().strftime("%Y-%m-%d_%H:%M")
	if con is not None:
		filename = con.find_prompt()[:-1].strip() + "_"  + date + ".conf"
	else:
		filename = ip + "_" + date + ".conf"
	cdir = os.getcwd()
	with open(filename, 'w') as f:
		f.write(output)
		f.close()
	print('The config saved as: "{}"\nDirectory: "{}"'.format(filename, cdir))

def telnet():
	try:
		connect_telnet = "telnet {}".format(ip)
		tn = pexpect.spawnu(connect_telnet, logfile=open(".templog", "w"))
	except:
		print("Couldnt connect via telnet either, check your connection")
		os.remove('.templog')
		exit()

	prompt = tn.expect(['Press any key to continue',
						'Username:','Password','.*\>','.*\#'],3)
	print("Success! Getting config via Telnet.. ")
	while prompt is not 4:
            # While not the prompt is in priveleged mode, it tries to find it
			# if not found, times out in 3 sec
		with open(".templog","r") as f:
			log_file = f.read()
			f.close()
		line_split = log_file.split('\n')
		for line in line_split:
			if "% " in line:
				print("Error occured: {}".format(line))
				os.remove('.templog')
				exit()
		if prompt == 0:
				tn.sendline('')
				prompt = tn.expect(['Press any key to continue',
						'Username:','Password','.*\>','.*\#'],3)
		elif prompt == 1:
				tn.sendline(user)
				prompt = tn.expect(['Press any key to continue',
						'Username:','Password','.*\>','.*\#'],3)
		elif prompt == 2:
				tn.sendline(pw)
				prompt = tn.expect(['Press any key to continue',
						'Username:','Password','.*\>','.*\#'],3)
		elif prompt == 3:
				tn.sendline('en')
				prompt = tn.expect(['Press any key to continue',
						'Username:','Password','.*\>','.*\#'],3)
	tn.sendline("sh run")
	moretest = tn.expect(['.*\#', '\ --More--\ '],3)
	while moretest == 1:
		tn.send(' ')
		moretest = tn.expect(['.*\#', '\ --More--\ '],3)
	with open(".templog","r") as f:
		log_file = f.read()
		f.close()
	log_file = log_file.split('Building configuration...\n')[1]
	log_file = log_file[:log_file.rfind('\n')]
	os.remove('.templog')
	writefile(None, log_file)

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
		writefile(net_connect, output)

if __name__ == '__main__':
	sys.tracebacklimit = None
	ip = input("Enter IP address: ")
	user = input("Enter Username: ")
	pw = getpass("Enter Password: ")
	enable = getpass("Enter enable password(if none, just hit enter): ")
	ssh()
