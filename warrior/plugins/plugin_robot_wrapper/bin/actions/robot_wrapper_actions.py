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


""" robot_wrapper_actions module that has all robot framework related keywords """

import os
import time
from subprocess import Popen, PIPE

from Framework.Utils import config_Utils
from Framework.Utils.testcase_Utils import pNote
from Framework.Utils.data_Utils import get_object_from_datarepository,\
 get_session_id, getSystemData, get_credentials
from Framework.Utils.file_Utils import getAbsPath, get_modified_files,\
 get_file_from_remote_server
from plugins.plugin_robot_wrapper.bin.utils import robot_wrapper_utils


class RobotWrapperActions(object):
    """ RobotWrapperActions class which has methods(keywords) related to Robot Framework """

    def __init__(self):
        self.resultfile = config_Utils.resultfile
        self.datafile = config_Utils.datafile
        self.logsdir = config_Utils.logsdir
        self.filename = config_Utils.filename
        self.logfile = config_Utils.logfile

    def execute_robot_wrapper(self, file_path, output_dir, system_name,
                              session_name=None, prompt=".*(%|#|\$)"):
        """
        This keyword is to execute python scripts which internally calls robot scripts.
        :Arguments:
            1. file_path(string) - Path of python script to be executed
            2. output_dir(string) - Directory path used as outputdir for robot
                                    scripts available in the python script
            3. system_name(string) - Name of the system/subsystem in the datafile
            4. session_name(string) - name of the session to the system
            5. prompt(string) - prompt expected in the terminal
        :Returns:
            1. status(bool)= True/False
        :Datafile usage:
            Tags or attributes to be used in input datafile for the system/subsystem
            If both tag and attribute is provided the attribute will be used
            1. ip = IP address of the system
                Default value for ip type is ip, it can take any type of ip's
                to connect to (like ipv4, ipv6, dns etc)
                Users can provide tag/attribute for any ip_type under the
                system in the input datafile and specify the tag/attribute name
                as the value for ip_type argument, then the connection will be
                established using that value
            2. username = username for the session
            3. password = password for the session
            4. prompt = prompt expected when the connection is successful
            5. remote = 'yes' when executed in remote system & 'no'(default)
                when executed in local system
            6. local_output_dir = path of the directory where the robot output
                files will be stored in the local system. If this tag is
                available or left empty, results will be stored in
                'home/<username>/robot_wrapper_opdir' directory.
        """

        session_id = get_session_id(system_name, session_name)
        session_object = get_object_from_datarepository(session_id)
        end_prompt = getSystemData(self.datafile, system_name, "prompt")
        if end_prompt:
            prompt = end_prompt

        testcasefile_path = get_object_from_datarepository('wt_testcase_filepath')
        abs_filepath = getAbsPath(file_path, os.path.dirname(testcasefile_path))
        abs_output_dir = getAbsPath(output_dir, os.path.dirname(testcasefile_path))

        current_time = time.time()
        if os.path.isfile(abs_filepath):
            command = "python " + abs_filepath
            status = session_object.send_command(".*", prompt, command)[0]
            if status is True:
                pNote("Robot_wrapper script: '{}' execution is successful".format(abs_filepath))
            else:
                pNote("Robot_wrapper script: '{}' execution failed".format(abs_filepath),
                      'warning')
        else:
            pNote("Robot_wrapper script: '{}' does not exist".format(abs_filepath), 'warning')
            status = False

        credentials = get_credentials(self.datafile, system_name,
                                      ['ip', 'username', 'password', 'remote',
                                       'local_output_dir'])

        # When executed in remote machine
        if credentials['remote'] and credentials['remote'].upper() == "YES":

            if credentials['local_output_dir']:
                data_directory = os.path.dirname(self.datafile)
                local_output_dir = getAbsPath(credentials['local_output_dir'], data_directory)
            else:
                local_output_dir = "~/robot_wrapper_opdir"
            get_file_from_remote_server(credentials['ip'], credentials['username'],
                                        credentials['password'], abs_output_dir, local_output_dir)
            abs_output_dir = local_output_dir + os.sep + os.path.basename(abs_output_dir)
        # Get the modified xml files in the output_dir
        modified_list = get_modified_files(abs_output_dir, current_time, ".xml")
        # Get the robot xml files from the modified list of files
        robot_xml_list = robot_wrapper_utils.get_robot_xml_files(modified_list)
        # Get results from robot xml files
        robot_test_results = robot_wrapper_utils.get_results_from_robot_xml(robot_xml_list)
        # Create junit for robot tests
        robot_wrapper_utils.create_case_junit(robot_test_results)

        return status
