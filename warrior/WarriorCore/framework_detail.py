'''
Copyright 2017, Fujitsu Network Communications, Inc.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

"""This file is used to define the framwork notype and retrieve the release,\
   version from licence or release notes.
"""
from datetime import datetime, timedelta
import time
import os
import sys
import re  
import platform
import subprocess
from Framework.Utils.print_Utils import print_info, print_notype
from Framework.Utils import file_Utils
from Framework.Utils.testcase_Utils import pNote


def warrior_banner():
    """This prints banner of warrior. The font is standard 
    """

    print(" __        ___    ____  ____  ___ ___  ____  ")
    time.sleep(0.10)
    print(" \ \      / / \  |  _ \|  _ \|_ _/ _ \|  _ \  ")
    time.sleep(0.10)
    print("  \ \ /\ / / _ \ | |_) | |_) || | | | | |_) |  ")
    time.sleep(0.10)
    print("   \ V  V / ___ \|  _ <|  _ < | | |_| |  _ <   ")
    time.sleep(0.10)
    print("    \_/\_/_/   \_\_| \_\_| \_\___\___/|_| \_\  ")
    print "\n"

def warrior_framework_details():
    """This gets framework details such the executing framework path, release 
        & version details. 
    """
    #The logic uses relative file path to locate Warrior framework and its\
    # release notes.Assumes the relative structure remains constant.
    release = False
    version = False
    possible_install_time = False
    path = os.path.realpath(__file__)
    current_path = path.rstrip('c')[:-32]
    version_file_path = current_path+"/version.txt"
    version_file = file_Utils.fileExists(version_file_path) 
    if version_file:
        release_notes =  open(version_file_path, "r")
        for line in release_notes:
            line = line.strip()
            #pattern matching Release:<>  
            if (re.match('(Release.*):(.*)', line)):
                m = re.match(r'(Release.*):(.*)', line)
                release = m.group(2)
            #pattern matching Version:<>
            if (re.match('(Version.*):(.*)', line)):
                m = re.match(r'(Version.*):(.*)', line)
                version = m.group(2)
        possible_install_time = time.ctime(os.path.getctime(version_file_path))
        current_time = time.strftime("%a %b %d %H:%M:%S %Y")
        current_time = datetime.strptime(current_time, "%a %b %d %H:%M:%S %Y")
        install_time = datetime.strptime(possible_install_time, "%a %b %d %H:%M:%S %Y")
        difference = current_time - install_time 
    if release and version and current_path:          
        pNote("========================== WARRIOR FRAMEWORK DETAILS ==========================", 'notype')
        print_info('The Warrior framework used is {0}'.format(current_path))
        print_info('The Warrior framework Release is{0}'.format(release))
        print_info('The Warrior framework version is{0}'.format(version))
        pNote("========================== WARRIOR FRAMEWORK DETAILS ==========================", 'notype')

    #Sleep for the user to view the console for a second on the framework detail
    time.sleep(2)
    return None
