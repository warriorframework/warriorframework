
import os, sys, json

import re

import katana_utils
from katana_utils import *

#print get_action_dirlist('/home/khusain/Projects/forDemo/warriorframework/warrior/ProductDrivers/cli_driver.py')
#print mkactiondirs('/home/khusain/Projects/forDemo/warriorframework/warrior/ProductDrivers/cli_driver.py')
path_to_pythonsrc = '/home/khusain/Projects/forDemo/warriorframework/warrior'; 
driver  = 'fw9500_driver'
keyword = 'login'
driver  = 'cloudshell_driver'
keyword = 'cloudshell_actions'
details = py_file_details(path_to_pythonsrc);
print json.dumps(details[driver][0] )
