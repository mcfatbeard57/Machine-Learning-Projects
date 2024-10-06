Processing Log File MML Comamnd Script
-----------------------------------

Settings
--------
To configure destination server details, transfer files path details on
source and destination servers, use `settings.py` file.

a) To set destination server ip, set value of test_ip label,
b) To set destination server username, set value of test_username label,
c) To set destination server password, set value of test_password label,
d) To set destination server port, set value of test_port label,
e) To chnage the filtering conditions of MML commands, set the value of response_code, user or log_type label
f) To specify input folder location where input will be generated from cornJob command, set value of InputTargetDirectory label,
g) By default it will create logs in same directory as in the input folder generated from cornJob command
h) To change the housekeeping time change houseKeepingTime label
i) Change TIMEDELTA label to change in starttime and endtime of cornJob command

Usage
-----
To execute the script, use below command:
/usr/sshCommand/pyENM/bin/python mmlPexpect.py
Here,
/usr/sshCommand/pyENM/bin/python is the path where our python (with pexpect package) is located
mmlPexpect23.py is the name of the main script

pyENM package
-------------
Put pyENM package in the node(perferabely same place where the script is)
Both paramiko and pexpect package is installed in the pyENM directory.
Use python of pyENM directory only i.e. pyENM/bin/python

Flow mmlPexpect
---------------
It will fire the cornJob commadn to create input file and then unzip csv files.
Read each csv file and filter out the failed mml commands based on given conditions.
Fire each mml command and log the output and close the connection.
Call House Keeping Funciton.

HouseKeeping
------------
Do the HouseKeeping i.e. delete input directories which is older than 7 days( this is configurable by changing houseKeepingTime label)