import os
from datetime import datetime
import datetime

# Filename and path
InputTargetDirectory = '/usr/sshcommand/' 
keyword = 'proclog'

# TIMEDELTA
TIMEDELTA = datetime.timedelta(days= 1, hours=0, minutes=0)

houseKeepingTime = 7 * 24 * 60 * 60


# Filtering conditions of mml command from logs
user = 'upguser'
response_code = ['13','14']
log_type = 'northbound'


# Test user username, password , IP and port
test_ip = '10.201.130.110'	
test_port = 8111
test_username = 'test'
test_password = 'Test@123'