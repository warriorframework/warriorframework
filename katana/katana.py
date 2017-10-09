#!/usr/bin/env python
"""
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import os
import sys
from  utils import warrior_interface_utils

try:
    import django
except:
    print """
    Whoops! You don't have django on your system. 

    Please install django on your system. Try
    sudo pip install django  

    For more information on how to install django, please visit 
    https://docs.djangoproject.com/en/1.11/topics/install/ 
    
    """
    sys.exit(-1); 

if __name__ == "__main__":

    """
    This file is a wrapper file to run manage.py via katana.py.

    This wrapper file was introduced to maintain backward compatibility between katana running on
    the bottle server amd katana running on Django

    The commands accepted are:

    - python katana.py : This would start the server at localhost:5000
    - python katana.py -p <port> : This would start the server at localhost:<port>

    katana.py can also be run from a different directory : python /path/to/katana.py [-p <port>]

    """

    args = sys.argv[1:]
    directory = os.path.dirname(sys.argv[0])

    python_executable = sys.executable

    if not python_executable:
        command = "python"
    else:
        command = python_executable

    port = 5000
    runserver = "runserver"
    filepath = "manage.py"

    if directory is not "":
        filepath = directory + os.sep + filepath

    for i in range(0, len(args)):
        if args[i] == "-p":
            if i+1 >= len(args):
                print "No port number given. Exiting."
                sys.exit()
            else:
                port = args[i+1]
            break
    
    # below two lines are to write katana url information to w_settings file
    katana_url = "http://localhost:{0}/katana".format(port)
    warrior_interface_utils.set_katana_location(katana_url)
    
    os.system("{0} {1} {2} {3}".format(command, filepath, runserver, port))
    
    
    
