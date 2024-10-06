#!/usr/sshComamnd/pyENM/bin/python
from settings import *
from HouseKeeping import *
import re
import csv
import sys
import os
import time
import logging
import pexpect
from pexpect import pxssh
from datetime import datetime
import datetime
import shutil


## ==================================================================================================================

# TimeVariable
currenttime = datetime.datetime.today()

# FOLDERNAME -- 2020-10-12_04.00.00_to_2020-10-13_08.00.00 
starttime = currenttime - TIMEDELTA
endtime = currenttime
FOLDERNAME = starttime.strftime("%Y-%m-%d_%H.%M.%S")  + "_to_" + endtime.strftime("%Y-%m-%d_%H.%M.%S") 
# TIMESTAMP
STARTTIME = starttime.strftime("%Y-%m-%d %H:%M:%S")
ENDTIME = endtime.strftime("%Y-%m-%d %H:%M:%S")
TIMESTAMP = STARTTIME + " " + ENDTIME

# Commands
cornjobComamnd = "/usr/local/pgngn/admin-tool-4.292.0.1/bin/proclog-admin-tool.sh -et " + '"' + TIMESTAMP + '"' + " -p " + InputTargetDirectory
cdCommand = InputTargetDirectory + FOLDERNAME


## =============================================

'''
Steps
1) /usr/local/pgngn/admin-tool-4.292.0.1/bin/proclog-admin-tool.sh -et "2020-10-12 04:00:00 2020-10-13 08:00:00" -p /usr/sshcommand/
2) cd FOLDERNAME
3) gzip -d proclog_2020-10-12_04.00.35.549_1.csv.gz
'''

# =============================================
 
try:

    # Step 1
    print('Creating Connection to CORNJOB') 
    # child = pexpect.spawn('/usr/local/pgngn/admin-tool-4.292.0.1/bin/proclog-admin-tool.sh -et "2020-10-16 04:00:00 2020-10-17 08:00:00" -p /usr/sshcommand/')
    child = pexpect.spawn(cornjobComamnd)

    # for LAB1
    # child = pexpect.spawn('/usr/local/pgngn/admin-tool-4.292.0.1/bin/proclog-admin-tool.sh -et "2020-10-13 04:00:00 2020-10-14 08:00:00" -p /usr/sshCommand/')

    time.sleep(10)
    child.expect('.*')
    child.sendline('yes')
    time.sleep(10)

    child.close()

## =============================================
    
    # Step 2        # Change the current working Directory

    try:
        os.chdir(cdCommand)
        print("Directory changed")
        # print("Current Working Directory " , os.getcwd())
    except OSError:
        print("Can't change the Current Working Directory")


## ================================


    # Step 2.2 fire gzip command
    # ZIP file name proclog_2020-10-12_04.00.35.549_1.csv.gz

    files = [file for file in os.listdir(os.curdir) if file.endswith(".gz")]
    for filename in files:
        if keyword in filename:
            CSVZIPFILENAME = filename
            print('file name ', CSVZIPFILENAME)

    gzipCommand = 'gzip -d ' + CSVZIPFILENAME

    print('Firing gzip command on file ', CSVZIPFILENAME)
    child= pexpect.spawn(gzipCommand)
    time.sleep(10)
    child.expect('.*')
    time.sleep(10)

    child.close()


## =============================================

except pxssh.ExceptionPxssh as e:
    print("pxssh failed on login.")
    print(e)
except pexpect.EOF as e:
    print('EOF')
    print(e)
    print(str(child))
except pexpect.TIMEOUT as e:
    print('TIMEOUT')
    print(e)
except Exception as e:
    print('error ',e)


## ==================================================================================================================

# Step 3


def read_proclogs():
    files = [file for file in os.listdir(os.curdir) if file.endswith(".csv")]
    for filename in files:
        if keyword in filename:
            with open('%s' %filename, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                line_count = 0
                for row in csv_reader:
                    if line_count == 0:
                        line_count += 1
                    else:
                        if (row[13] in response_code) and (row[7]==user) and (row[0]== log_type):
                            com = row[14]
                            com = ''.join((com,'\n'))
                            command_list.append(com)
                            line_count += 1
    return command_list

command_list = []
print('Reading Failed MML Commands from proclog')
command_list = read_proclogs()
print('printing comamnd list')
print(command_list)

logFilename = currenttime.strftime('Pexpect_proclog_MML_%Y_%m_%d_%H_%M_%S.log')
logging.basicConfig(filename=logFilename, 
                    format='%(asctime)s %(message)s', 
                    filemode='w')
logger=logging.getLogger() 
logger.setLevel(logging.INFO) 

try:

    print('Creating Connection')
    # child = pexpect.spawn('ssh ' + test_username + '@' + test_ip + ' -p ' + str(test_port))
    child = pexpect.spawn('ssh -o "UserKnownHostsFile /dev/null" -o "StrictHostKeyChecking no" '  + test_username + '@' + test_ip + ' -p ' + str(test_port)) 
    child.expect('.*')
    child.sendline(test_password)
    time.sleep(5)

    child.expect('[\s\S]+')
    logger.info(child.after)
    
    print('Firing commands on test lab')
    
    for com in command_list:
       child.sendline(com)
       time.sleep(5)
       child.expect('[\s\S]+')
       logger.info(child.after)
    print('Creating Log file')

    child.close()

except pxssh.ExceptionPxssh as e:
    print("pxssh failed on login.")
    print(e)
except pexpect.EOF as e:
    print('EOF')
    print(e)
    print(str(child))
except pexpect.TIMEOUT as e:
    print('TIMEOUT')
    print(e)
except Exception as e:
    print('error ',e)

print('Closing Connection. \nPlease check the log file.')


## ==================================================================================================================

# Housekeeping
print('Starting HouseKeeping')
houseKeeping()
print('Script ran succesfully.')