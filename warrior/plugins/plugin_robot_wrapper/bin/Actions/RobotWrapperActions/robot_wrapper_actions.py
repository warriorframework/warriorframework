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
from subprocess import Popen, PIPE

import Framework.Utils as Utils
from Framework.Utils.print_Utils import print_info, print_warning
from Framework.Utils.testcase_Utils import pNote
from Framework.Utils.data_Utils import get_object_from_datarepository
from Framework.Utils.file_Utils import getAbsPath


class RobotWrapperActions(object):
    """ RobotWrapperActions class which has methods(keywords) related to Robot Framework """

    def __init__(self):
        self.resultfile = Utils.config_Utils.resultfile
        self.datafile = Utils.config_Utils.datafile
        self.logsdir = Utils.config_Utils.logsdir
        self.filename = Utils.config_Utils.filename
        self.logfile = Utils.config_Utils.logfile

    def execute_robot_wrapper(self, file_path, output_dir=None):
        """
        This keyword is to execute python scripts which internally calls robot scripts.
        :Arguments:
            1. file_path - Path of python script to be executed
            2. output_dir - Directory path used as outputdir for robot scripts
                            available in the python script
        """

        testcasefile_path = get_object_from_datarepository('wt_testcase_filepath')
        abs_filepath = getAbsPath(file_path, os.path.dirname(testcasefile_path))

        if os.path.isfile(abs_filepath):
            p = Popen("python " + file_path, stderr=PIPE, stdout=PIPE, shell=True)
            output, errors = p.communicate()
            print_info("Robot execution output:\n{}".format(output))
            if p.returncode or errors:
                print_warning("Something went wrong in the execution, "
                              "error logs below:\n{}".format(errors))
                status = False
            else:
                status = True
        else:
            pNote("Robot script: '{}' does not exist".format(abs_filepath), 'warning')
            status = False

        return status
