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



import json
import os

import Framework.Utils as Utils
from Framework.Utils.print_Utils import print_info, print_error
from Framework.Utils.testcase_Utils import pNote
from Framework.Utils.data_Utils import get_object_from_datarepository, update_datarepository
from Framework.Utils.file_Utils import getAbsPath
from Framework.Utils import datetime_utils


class CommonActions(object):
    """class CommonActions having methods (keywords) that are common for all the products"""

    def __init__(self):

        """
            Constructor
        """

        self.resultfile = Utils.config_Utils.resultfile
        self.datafile = Utils.config_Utils.datafile
        self.logsdir = Utils.config_Utils.logsdir
        self.filename = Utils.config_Utils.filename
        self.logfile = Utils.config_Utils.logfile

    def wait_for_timeout(self, timeout):
        """waits (sleeps) for the time provided

        :Arguments:
            1. timeout= time to wait in seconds

        :Returns:
            1. status (bool)
        """

        WDesc = "Waits for the timeout provided"
        Utils.testcase_Utils.pSubStep(WDesc)
        status = datetime_utils.wait_for_timeout(timeout)
        pNote('********Below Testing occured after Timeout *********')
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
                      this could be dot separated to store in nested fashion
                      i.e., if var is k1.k2.k3 then the data value would be
                      stored as a value in datarepository[k1][k2][k3]
            datavalue = the value to be stored
            type = type of datavalue (string/int/float)
        """
        def get_dict_to_update(var, val):
            """

            The function creates a dictionary with Variable and value. If Variable has "." seperated
            keys then the value is updated at appropriate level of the nested dictionary.
            :param var: Dictionary Key or Key seperated with "." for nested dict keys.
            :param val: Value for the Key.

            :return: Dictionary

            """
            dic = {}
            if '.' in var:
                [key, value] = var.split('.', 1)
                dic[key] = get_dict_to_update(value, val)
            else:
                dic[var] = val
            return dic
        if type == 'int':
            value = int(datavalue)
        elif type == 'float':
            value = float(datavalue)
        else:
            value = datavalue
        dict_to_update = get_dict_to_update(datavar, value)
        update_datarepository(dict_to_update)
        print_info("Value: {0} is stored in a Key:{1} of Warrior "
                   "data_repository ".format(datavalue, datavar))
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
        result, value = Utils.data_Utils.verify_data(expected, object_key, type, comparison)
        if result not in ["FALSE", "TRUE"]:
            return result
        elif result == "FALSE":
            print_error("Expected: {0} {1} {2} but found {0}={3}".format(
                object_key, comparison, expected, value))
            return False
        elif result == "TRUE":
            print_info("Expected: {0} {1} {2} found the same".format(
                object_key, comparison, expected, value))
            return True


    def set_env_var(self, var_key=None, var_value=None, filepath=None,
                    jsonkey="environmental_variables", overwrite="yes"):
        """Create a temp environment variable, the value will only stay for the current Execution
        :Argument:
            var_key = key of the environment variable
            var_value = value of the environment variable
            filepath = Json file where Environmental variables are defined
            jsonkey = The key where all the ENV variable & values are defined
        With jsonkey arg, Users can call same file to set various ENV Variable
            overwrite = Yes-Will overwrite ENV variables set earlier via terminal or other means
                        No -Will not overwrite the ENV variables set earlier with the ones passed
                            through this keyword.

        Variable File :
        Sample environmental_variable file is available under
        Warriorspace/Config_file/Samples/Set_ENV_Variable_Sample.json
        """
        overwrite = overwrite.upper()
        status = False
        if not any([var_key, var_value, filepath]):
            print_error('Either Provide values to arguments \"var_key\" & \"var_value\" or to '
                        'argument \"filepath\"')
        if overwrite == "NO" and os.getenv(var_key):
            print_info("Using ENV variable {0} set earlier with "
                       "value '{1}'".format(var_key, os.getenv(var_key)))
        elif var_key is not None and var_value is not None and overwrite in ["YES", "NO"]:
            os.environ[var_key] = var_value
            if os.environ[var_key] == var_value:
                print_info("Set ENV variable {0} with value '{1}'".format(var_key, var_value))
                status = True
        else:
            print_error('The attribute overwrite can only accept values either yes or no')
        if filepath is not None:
            testcasefile_path = get_object_from_datarepository('wt_testcase_filepath')
            try:
                filepath = getAbsPath(filepath, os.path.dirname(testcasefile_path))
                with open(filepath, "r") as json_handle:
                    get_json = json.load(json_handle)
                    if jsonkey in get_json:
                        env_dict = get_json[jsonkey]
                        for var_key, var_value in env_dict.items():
                            if overwrite == "NO" and os.getenv(var_key):
                                print_info('Using ENV variable {0} set earlier with value '
                                           '{1}'.format(var_key, os.getenv(var_key)))
                                status = True
                            elif overwrite in ["YES", "NO"]:
                                os.environ[var_key] = str(var_value)
                                if os.environ[var_key] == var_value:
                                    print_info('Setting ENV variable {0} with value '
                                               '{1}'.format(var_key, var_value))
                                    status = True
                            else:
                                print_error('The attribute overwrite can only accept values either '
                                            'yes or no')
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
