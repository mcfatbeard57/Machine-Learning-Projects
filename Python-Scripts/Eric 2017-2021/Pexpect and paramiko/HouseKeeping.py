import re
import sys
import os
from datetime import datetime
import datetime
import shutil
import time

timeYear = '2020'
TargetDirectory = '/data_transfer/destinations/ENMDEST/Ready' 

houseKeepingTime = 7 * 24 * 60 * 60

def houseKeeping():

	now = time.time()

	houseKeepingFiles = []

	for file in os.listdir(InputTargetDirectory):

	    if not (file.endswith(".py") or file.endswith(".txt") or file.endswith(".csv")):

	    	if timeYear in file:

	    		f = os.path.join(InputTargetDirectory, file)

	    		if os.stat(f).st_mtime < now - houseKeepingTime:

	    			houseKeepingFiles.append(file)

	    			shutil.rmtree(f)

	print('Houskeeping Finished, Deleted files are')

	print(houseKeepingFiles)