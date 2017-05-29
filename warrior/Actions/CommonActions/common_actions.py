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


"""common_actions module where keywords common to all products are developed"""
import time
import json
import Framework.Utils as Utils
import os
from Framework.Utils.print_Utils import print_info, print_error
from Framework.Utils.testcase_Utils import pNote
from Framework.Utils.data_Utils import get_object_from_datarepository, update_datarepository
from Framework.Utils.file_Utils import getAbsPath


class CommonActions(object):
    """class CommonActions having methods (keywords) that are common for all the products"""

    def __init__(self):
        self.resultfile = Utils.config_Utils.resultfile
        self.datafile = Utils.config_Utils.datafile
        self.logsdir = Utils.config_Utils.logsdir
        self.filename = Utils.config_Utils.filename
        self.logfile = Utils.config_Utils.logfile

    def wait_for_timeout(self, timeout):
        """waits (sleeps) for the time provided

        :Arguments:
            1. resultfile(string) = full path to the result file
            2. step_num(string) = step_num in string
            3. timeout= time to wait in seconds

        :Returns:
            1. status (bool)
        """

        WDesc = "Waits for the timeout provided"
        Utils.testcase_Utils.pSubStep(WDesc)
        pNote(self.datafile)
        pNote('Starting Time Out of ' + timeout + 'secs')
        time.sleep(float(timeout))
        pNote('Ending Time Out of ' + timeout + 'secs')
        pNote('********Below Testing occured after Timeout *********')

        status = True
        Utils.testcase_Utils.report_substep_status(status)
        return status

    def get_system_type(self, system_name):
        """Finds the system name in the datafile and returns the system type
        :Arguments:
            1. system_name = system name in the datafile
        :Returns:
            1. status (boolean)
            2. system_type (dict element): name=system_type, value=type of the system_name (string).
        """

        WDesc = "Find the system type from datafile"
        Utils.testcase_Utils.pSubStep(WDesc)
        Utils.testcase_Utils.pNote(self.datafile)
        Utils.testcase_Utils.pNote(system_name)
        output_dict = {}

        system_type = Utils.data_Utils.getSystemData(self.datafile, system_name, 'system_type')

        if system_type is not None and system_type is not False:
            msg = print_info('system_type is: {0}'.format(system_type))
            Utils.testcase_Utils.pNote(msg)
            status = True
            output_dict['system_type'] = system_type
        else:
            status = False

        Utils.testcase_Utils.report_substep_status(status)
        return status, output_dict

    def verify_resp_data(self, resp_ref, resp_pat, object_key):
        """Verify 'resp_pat' exist in the data repository
        :Argument:
            resp_ref = response reference tag in testdatafile
            resp_pat = response pattern to be check in testdatafile
            object_key = the object key name in the data repository
              Ex: cli send by title, object_key=<title name>
                  cli send by tiele_rownum, object key=<tilte_name><row_name>
        :Returns:
            status (boolean)
        """
        wDesc = "Verify if response pattern exist in response data_repository"
        Utils.testcase_Utils.pNote(wDesc)

        status = True
        result = Utils.data_Utils.get_object_from_datarepository(object_key)
        if result is not None and result is not False:
            if resp_pat == result[resp_ref]:
                pNote("Found resp_pat={0} for resp_ref={1} in the data "\
                      "repository".format(resp_pat, resp_ref))
            else:
                status = False
                pNote("NOT found resp_pat={0} for resp_ref={1} in the data "\
                      "repository!!".format(resp_pat, resp_ref), "warning")
        Utils.testcase_Utils.report_substep_status(status)
        return status

    def store_in_repo(self, datavar, datavalue, type='str'):
        """For storing datavalue in datavar datarepository
        :Argument:
            datavar = var in data repository in which to store
            datavalue = the value to be stored
            type = type of datavalue (string/int/float)
        """
        if type == 'int':
            value = int(datavalue)
        elif type == 'float':
            value = float(datavalue)
        else:
            value = datavalue
        update_datarepository({datavar: value})
        return True

    def verify_data(self, expected, object_key, type='str', comparison='eq'):
        """Verify value in 'object_key' in the data repository matches
        with expected
        :Argument:
            expected = the value to be compared with
            object_key = the object in the data repository to be compared
            type = the type of this expected (str/int/float)
            comparison = actual comparison (eq/ne/gt/ge/lt/le)
                eq - check if both are same(equal)
                ne - check if both are not same(not equal)
                gt - check if object_key is greater than expected
                ge - check if object_key is greater than or equal to expected
                lt - check if object_key is lesser than expected
                le - check if object_key is lesser than or equal to expected
        :Returns:
            status (boolean)
        """
        wDesc = "Verify if value of object_key in data_repository "
        "matches with expected"
        Utils.testcase_Utils.pNote(wDesc)

        result = Utils.data_Utils.verify_data(expected, object_key,
                                              type, comparison)
        if result == "FALSE":
            value = get_object_from_datarepository(object_key)
            print_error("Expected: {0} {1} {2} but found {0}={3}".format(
                object_key, comparison, expected, value))
        if result == "TRUE":
            return True
        else:
            return False

    def set_env_var(self, var_key=None, var_value=None, filepath=None,
                    jsonkey="environmental_variables"):
        """create a temp environment variable
        the value will only stay for this run
        :Argument:
            var_key = key of the environment variable
            var_value = value of the environment variable
            filepath = Json file where Environmental variables are defined
            jsonkey = The key where all the ENV variable & values are defined
        With jsonkey arg, Users can call same file to set various ENV Variable

        Variable File :
        Sample environmental_variable file is available under
        Warriorspace/Config_file/Samples/Set_ENV_Variable_Sample.json
        """
        status = False
        if not any([var_key, var_value, filepath]):
            print_error('Either Provide values to arguments \"var_key\" & \"var_value\" or to argument \"filepath\"')

        if var_key is not None and var_value is not None:
            os.environ[var_key] = var_value
            if os.environ[var_key] == var_value:
                print_info('Set ENV variable {0} with value '
                           '{1}'.format(var_key, var_value))
                status = True
        if filepath is not None:
            testcasefile_path = get_object_from_datarepository('wt_testcase_filepath')
            try:
                filepath=getAbsPath(filepath, os.path.dirname(testcasefile_path))
                with open(filepath, "r") as json_handle:
                    get_json = json.load(json_handle)
                    if jsonkey in get_json:
                        env_dict = get_json[jsonkey]
                        for var_key, var_value in env_dict.items():
                            os.environ[var_key] = var_value
                            if os.environ[var_key] == var_value:
                                print_info('Set ENV variable {0} with value '
                                           '{1}'.format(var_key, var_value))
                                status = True
                    else:
                        print_error('The {0} file is missing the key '
                                    '\"environmental_variables\", please refer to '
                                    'the Samples in Config_files'.format(filepath))
                        status = False
            except ValueError:
                print_error('The file {0} is not a valid json '
                            'file'.format(filepath))
                status = False
            except IOError:
                print_error('The file {0} does not exist'.format(filepath))
                status = False
            except Exception as error:
                print_error('Encountered {0} error'.format(error))
                status = False

        return status


