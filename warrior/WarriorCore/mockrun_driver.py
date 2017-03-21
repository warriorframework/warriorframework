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

"""This is the library for mockrun tool which checks the
script errors in the xml files"""
import sys
import subprocess
from xml.etree import ElementTree
from WarriorCore.Classes.mockrun_class import MockRun
from WarriorCore.Classes.war_cli_class import WarriorCliClass
from Framework.Utils.print_Utils import print_info


mockrun_obj = MockRun()

def main(parameter_list):
    """Check the script errors of testcase/testuite/project xml files"""
    args = sys.argv[1:]
    debug, summary = False, False

    if args[0] == '-debug':
        debug = True
        args = args[1:]

    if args[0] == '-summary':
        summary = True
        args = args[1:]
    cmd = 'python Warrior -cmdprint %s' % (' '.join(parameter_list))
    print_info("Executing %s" % cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    out, err = p.communicate()

    if err:
        print_info("Following Error occurred while running Warrior")
        print_info(err)
        print_info("Check and re-run the script")
        exit(1)

    if summary:
        mockrun_obj.print_summary(out)
        exit(0)

    result = out.split('\n')
    for lin in result:
        pats = ['Keyword:', 'System:', '  File ', "'title':",
                '-E-', 'Traceback', 'Error:', 'failed:', 'variable config',
                'not found in', 'could not find', 'does not exist',
                'Starting execution', 'Executing testsuite', 'Title:', 'Row:']
        if debug:
            print_info("Processing <<%s>>" % lin)
        if ':CMD:' in lin:
            print_info(lin.split(':CMD:')[1])
        elif any(map(lambda x: x in lin, pats)):
            print_info(lin)
    print_info("Done executing Warrior")
