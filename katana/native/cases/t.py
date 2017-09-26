
import os, sys, json

import re

import katana_utils
from katana_utils import *

#print get_action_dirlist('/home/khusain/Projects/forDemo/warriorframework/warrior/ProductDrivers/cli_driver.py')
#print mkactiondirs('/home/khusain/Projects/forDemo/warriorframework/warrior/ProductDrivers/cli_driver.py')
path_to_pythonsrc = '/home/khusain/Projects/forDemo/warriorframework/warrior'; 
driver  = 'cloudshell_driver'
keyword = 'cloudshell_actions'

driver  = 'fw9500_driver'
keyword = 'login'
details = py_file_details(path_to_pythonsrc);
#for k in details.keys(): print len(json.dumps(details[k][0]))
print "-----------------"
print details[driver][0]
print "------------------"
print json.dumps(details[driver][0] )
