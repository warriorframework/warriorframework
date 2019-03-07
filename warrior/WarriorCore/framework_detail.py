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

import time
import os
import platform
import re
import getpass
import subprocess
from Framework.Utils.print_Utils import print_info, print_notype
from Framework.Utils import file_Utils
from Framework.Utils.testcase_Utils import pNote


def warrior_banner():
    """This prints banner of warrior. The font is standard
    """
    print_notype("  __        ___    ____  ____  ___ ___  ____  ")
    time.sleep(0.10)
    print_notype(r"  \ \      / / \  |  _ \|  _ \|_ _/ _ \|  _ \  ")
    time.sleep(0.10)
    print_notype(r"   \ \ /\ / / _ \ | |_) | |_) || | | | | |_) |  ")
    time.sleep(0.10)
    print_notype(r"    \ V  V / ___ \|  _ <|  _ < | | |_| |  _ <   ")
    time.sleep(0.10)
    print_notype(r"     \_/\_/_/   \_\_| \_\_| \_\___\___/|_| \_\  ")

def warrior_framework_details():
    """This gets framework details such the executing framework path, release
        & version details.
    """
    #The logic uses relative file path to locate Warrior framework and its\
    # release notes.Assumes the relative structure remains constant.
    release = False
    version = False
    version_file_path = os.path.normpath(os.path.join(__file__, "..{0}..{0}..".format(os.sep)))
    version_file = os.path.join(version_file_path, "version.txt")
    version_file_exists = file_Utils.fileExists(version_file)
    if version_file_exists:
        release_notes = open(version_file, "r")
        for line in release_notes:
            line = line.strip()
            #pattern matching Release:<>
            if re.match('(Release.*):(.*)', line):
                match = re.match(r'(Release.*):(.*)', line)
                release = match.group(2)
            #pattern matching Version:<>
            if re.match('(Version.*):(.*)', line):
                match = re.match(r'(Version.*):(.*)', line)
                version = match.group(2)
    user = getpass.getuser()
    proc1 = subprocess.Popen(['git', 'branch'], stdout=subprocess.PIPE)
    proc2 = subprocess.Popen(['grep', '*'], stdin=proc1.stdout,
                             stdout=subprocess.PIPE, stderr=None)
    proc1.stdout.close() # Allow proc1 to receive a SIGPIPE if proc2 exits.
    branch = proc2.communicate()[0]

    if release and version and version_file_path:
        pNote("========================== WARRIOR FRAMEWORK DETAILS ==========================",
              'notype')
        print_info('The Warrior framework used is {0}'.format(version_file_path))
        print_info('The Warrior framework user is {0}'.format(user))
        print_info('The Warrior framework Release is{0}'.format(release))
        print_info('The Warrior framework version is{0}'.format(version))
        print_info('The Warrior framework branch is{0}'.format(branch.strip('*')))
        print_info('The Warrior framework running on python version: {0} with OS: {1}'.
                   format(platform.python_version(), platform.platform()))
        pNote("========================== WARRIOR FRAMEWORK DETAILS ==========================",
              'notype')

    #Sleep for the user to view the console for a second on the framework detail
    time.sleep(2)
    return None
