import re
import sys
import os
import time
import pexpect
from datetime import datetime,date
from re import search


# Unloading commands
unload_NodeA = 'FDSRequestSender -u compcontrol -p compcontrol SOG_NODE_A_UNLOAD.xml'
unload_NodeB = 'FDSRequestSender -u compcontrol -p compcontrol SOG_NODE_B_UNLOAD.xml'
load_NodeA = 'FDSRequestSender -u compcontrol -p compcontrol SOG_NODE_A_START.xml'
load_NodeB = 'FDSRequestSender -u compcontrol -p compcontrol SOG_NODE_B_START.xml'


# backup command
# today = date.today().strftime("%d%m%Y")
# backup_copy_command= 'cp -p /var/opt/fds/config/plugin/PSC-SogInterface/Config.cfg /var/opt/fds/config/plugin/PSC-SogInterface/Config.cfg_bkp_' + date.today().strftime("%d%m%Y")
# script 2
backup_copy_command2 = 'cp -p /var/opt/fds/config/plugin/PSC-SogInterface/Config.cfg_bkp_' + date.today().strftime("%d%m%Y") + ' ' + '/var/opt/fds/config/plugin/PSC-SogInterface/Config.cfg'


# Config file path
# cofig_file_path = '/var/opt/fds/config/plugin/PSC-SogInterface/Config.cfg'

# countdown funciton
# def countdown(t):
#     while t:
#         mins, secs = divmod(t, 60)
#         timer = '{:02d}:{:02d}'.format(mins, secs)
#         print('Node A will start in : ',timer, end="\r")
#         time.sleep(1)
#         t -= 1

try:

    # Step 1 STOP SOG in A node 
    #print('logging in and passing the inital unloading command fro Node B') 
    # child = pexpect.spawn(unload_NodeA)
    #pexpect.run(unload_NodeB)

    print('logging in and STOP SOG IN NODE A') 
    pexpect.run(unload_NodeA)
    # pexpect.run(unload_NodeB)

    print('Unload complete of Node A; closing spawn')

    # Step 2 revert back the config file changes
    print('Run backup revert command')
    pexpect.run(backup_copy_command2)
    print('backup complete please check and confirm')

    # Step 3	Start SOG component in both node
    # Start the Node A and B
    print('adding 10 second wait')
    time.sleep(10)
    print('loading Node A')
    pexpect.run(load_NodeA)
    print('Node A started, moving on to Node B')
    pexpect.run(load_NodeB)
    print('Loading complete')

    print('Script 2 ends.\nCurrent datetime is:\n', datetime.now().strftime("%d/%m/%Y %H-%M"))


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