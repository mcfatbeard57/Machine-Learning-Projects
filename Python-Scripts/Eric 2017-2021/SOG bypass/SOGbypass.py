import re
import sys
import os
# from pathlib import Path
import time
import pexpect
from datetime import datetime,date
from re import search
# import datetime
# import csv
# import shutil
# import logging
# import paramiko
# from pexpect import pxssh
# from lxml import etree
# import xml.etree.ElementTree as ET


# What about the xml files?Should we put it manually or create it thru the python script
# Create four xml files with below names 
# path /opt/tmp

'''
[root@kksdp45a temp]# cat SOG_NODE_A_START.xml
<Request Operation=Start Specific=Member1 SessionId=2ABM8LJZ Origin=GUI MO=FDSController>
<LogicalComponent>PSC-SogInterface/8.2/A/1</LogicalComponent>
</Request>
[root@kksdp45a temp]#
[root@kksdp45a temp]# cat SOG_NODE_B_START.xml
<Request Operation=Start Specific=Member2 SessionId=2ABM8LJZ Origin=GUI MO=FDSController>
<LogicalComponent>PSC-SogInterface/8.2/A/2</LogicalComponent>
</Request>
[root@kksdp45a temp]#
[root@kksdp45a temp]# cat SOG_NODE_A_UNLOAD.xml
<Request Operation=Unload Specific=Member1 SessionId=2ABM8LJZ Origin=GUI MO=FDSController>
<LogicalComponent>PSC-SogInterface/8.2/A/1</LogicalComponent>
</Request>
[root@kksdp45a temp]#
[root@kksdp45a temp]# cat SOG_NODE_B_UNLOAD.xml
<Request Operation=Unload Specific=Member2 SessionId=2ABM8LJZ Origin=GUI MO=FDSController>
<LogicalComponent>PSC-SogInterface/8.2/A/2</LogicalComponent>
</Request>
'''

# Step 0
# Check if xml command files exist, if not create them

# xml command file names and path
xml_command_file_path = '/opt/tmp/'
filename_load_A = 'SOG_NODE_A_START.xml'
filename_unload_A = 'SOG_NODE_A_UNLOAD.xml'

filename_load_B = 'SOG_NODE_B_START.xml'
filename_unload_B = 'SOG_NODE_B_UNLOAD.xml'

# If not file not exist create one

# SOG_NODE_A_START.xml
SOG_NODE_A_START = (os.path.join(xml_command_file_path + filename_load_A))
try:
	if not os.path.exists(SOG_NODE_A_START):
		f = open(filename_load_A, "w")
		f.write("<Request Operation=Start Specific=Member1 SessionId=2ABM8LJZ Origin=GUI MO=FDSController>\n\
<LogicalComponent>PSC-SogInterface/8.2/A/1</LogicalComponent>\n\
</Request>")
		f.close()
except Exception as e:
    print('error ',e)

# SOG_NODE_A_UNLOAD.xml
SOG_NODE_A_UNLOAD = (os.path.join(xml_command_file_path + filename_unload_A))
try:
	if not os.path.exists(SOG_NODE_A_UNLOAD):
		f = open(filename_unload_A, "w")
		f.write('<Request Operation=Unload Specific=Member1 SessionId=2ABM8LJZ Origin=GUI MO=FDSController>\n\
<LogicalComponent>PSC-SogInterface/8.2/A/1</LogicalComponent>\n\
</Request>')
		f.close()
except Exception as e:
    print('error ',e)

# SOG_NODE_B_START.xml
SOG_NODE_B_START = (os.path.join(xml_command_file_path + filename_load_B))
try:
	if not os.path.exists(SOG_NODE_B_START):
		f = open(filename_load_B, "w")
		f.write('<Request Operation=Start Specific=Member2 SessionId=2ABM8LJZ Origin=GUI MO=FDSController>\n\
<LogicalComponent>PSC-SogInterface/8.2/A/2</LogicalComponent>\n\
</Request>')
		f.close()
except Exception as e:
    print('error ',e)

# SOG_NODE_B_UNLOAD.xml
SOG_NODE_B_UNLOAD = (os.path.join(xml_command_file_path + filename_unload_B))
try:
	if not os.path.exists(SOG_NODE_B_UNLOAD):
		f = open(filename_unload_B, "w")
		f.write('<Request Operation=Unload Specific=Member2 SessionId=2ABM8LJZ Origin=GUI MO=FDSController>\n\
<LogicalComponent>PSC-SogInterface/8.2/A/2</LogicalComponent>\n\
</Request>')
		f.close()
except Exception as e:
    print('error ',e)

# Unloading commands
load_NodeA = 'FDSRequestSender -u compcontrol -p compcontrol SOG_NODE_A_START.xml'
unload_NodeA = 'FDSRequestSender -u compcontrol -p compcontrol SOG_NODE_A_UNLOAD.xml'

load_NodeB = 'FDSRequestSender -u compcontrol -p compcontrol SOG_NODE_B_START.xml'
unload_NodeB = 'FDSRequestSender -u compcontrol -p compcontrol SOG_NODE_B_UNLOAD.xml'

# backup command
# today = date.today().strftime("%d%m%Y")
backup_copy_command= 'cp -p /var/opt/fds/config/plugin/PSC-SogInterface/Config.cfg /var/opt/fds/config/plugin/PSC-SogInterface/Config.cfg_bkp_' + date.today().strftime("%d%m%Y")
# script 2
# backup_copy_command2 = 'cp -p /var/opt/fds/config/plugin/PSC-SogInterface/Config.cfg_bkp_' + date.today().strftime("%d%m%Y") + '/var/opt/fds/config/plugin/PSC-SogInterface/Config.cfg'

# Config file path
cofig_file_path = '/var/opt/fds/config/plugin/PSC-SogInterface/Config.cfg'

# countdown funciton
# def countdown(t):
# 	while t:
# 		mins, secs = divmod(t, 60)
# 		timer = '{:02d}:{:02d}'.format(mins, secs)
# 		# print('Node A will start in : ', timer, end ='\r')
# 		print(timer)
# 		time.sleep(1)
# 		t -= 1

try:

    # Step 1	STOP SOG IN BOTH NODES A/B  
    print('logging in and STOP SOG IN NODES A') 
    pexpect.run(unload_NodeA)

    print('logging in and STOP SOG IN NODES B') 
    # child = pexpect.spawn(unload_NodeA)
    pexpect.run(unload_NodeB)

    print('Unload complete of both Nodes; closing spawn')

    # Step 2	Take Backup of below files in NodeA
    print('Taking Backup of Config files in NodeA')
    pexpect.run(backup_copy_command)
    print('backup complete please check and confirm')

    # Step 3 Edit the Config.cfg file and remove the command only( do not remove tags) in NodeA
    # find the lines need to be changed in the config file
    print('Editing the Config file')
    flag = False
    a_file = open(cofig_file_path, "r")
    list_of_lines = a_file.readlines()
    for i,myline in enumerate(list_of_lines):
    	if search('<CAI>', myline):
    		flag = True
    	if search('</CAI>', myline):
    		flag = False
    	if flag == True:
    		if search('<smsMTBlock>', myline):
    			list_of_lines[i] = '<smsMTBlock></smsMTBlock>\n'
    		if search('<smsMTUnBlock>', myline):
    			list_of_lines[i] = '<smsMTUnBlock></smsMTUnBlock>\n'
    		if search('<TVoiceBlock>', myline):
    			list_of_lines[i] = '<TVoiceBlock></TVoiceBlock>\n'
    		if search('<TVoiceUnBlock>', myline):
    			list_of_lines[i] = '<TVoiceUnBlock></TVoiceUnBlock>\n'

    # edit the Config file
    a_file = open(cofig_file_path, "w")
    a_file.writelines(list_of_lines)
    a_file.close()

    print('Editing Complete')

    # Adding sleep for 10 seconds
    # print('Node will restart in 10 seconds')
    #countdown(int(10))

    print('adding 10 second wait')
    time.sleep(10)

	# Step 4 Start SOG Component of NodeA only
    # Start the Node A
    print('Restart the Node A')
    pexpect.run(load_NodeA)
    # print('Restart the Node B')
    # pexpect.run(load_NodeB)
    print('Load completes')

    print('Script 1 ends')

    # Script 1 ends

    # Script 2 begins
    # print('logging in and passing the inital unloading command for Node A') 
    # pexpect.run(unload_NodeA)  

    # print('Run backup copy command 2')
    # pexpect.run(backup_copy_command2)

    # Run Load commands for Node A and Node B

## =============================================


except pexpect.EOF as e:
    print('EOF')
    print(e)
    print(str(child))
except pexpect.TIMEOUT as e:
    print('TIMEOUT')
    print(e)
except Exception as e:
    print('error ',e)