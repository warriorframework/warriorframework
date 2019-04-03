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

    def wait_for_timeout(self, timeout, notify_count=4):
        """waits (sleeps) for the time provided

        :Arguments:
            1. timeout= time to wait in seconds
            2. notify_count= number of times, the user needs to be notified
                             during wait time. Default value is 4.
                             Ex: If the notify_count=4 and timeout=400
                             the timeout is divided into 4 partitions
                             each as 100 and notified to user as
                             100(25%),200(50%),300(75%),400(100%)
        :Returns:
            1. status (bool)
        """

        WDesc = "Waits for the timeout provided"
        Utils.testcase_Utils.pSubStep(WDesc)
        print_info("Command timeout for {0} seconds".format(timeout))
        status = datetime_utils.wait_for_timeout(timeout, notify_count=notify_count)
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

    def store_in_repo(self, datavar=None, datavalue=None, type='str',
                      filepath=None, jsonkey="repo_variables", bool_store_all=False):
        """Stores datavalue in datavar of datarepository
        :Argument:
            1. datavar = Key to be used to store datavalue in data_repository,
                         this could be dot separated to store in nested fashion
                            i.e., if var is k1.k2.k3 then the data value would be
                            stored as a value in datarepository[k1][k2][k3]
            2. datavalue = Value to be stored
            3. type = Type of datavalue(string/int/float)
            4. filepath = Json file where datarepository variables are defined.
                          It is to store multiple key,value pairs in datarepository.
            5. jsonkey = The key where all the REPO variables & values are
                         defined in the filepath
            6. bool_store_all = Set to True to store whole json file content to data repository.
                       keys from the json file will be used as it is to store in repo if this
                       value is set to True.
                       default value is set to False.

            Sample JSON file:
                 {
                     "repo_variables": {
                         "var1": {"type": "int", "value": "10"},
                         "var2.var3": {"value": "10"},
                         "var4.var5": "1"
                         },
                     "user_defined_tag":{
                         "var6" : {"type": "int", "value": "40"}
                         }
                 }
            All three formats in the above sample block are allowed. If 'type'
            is not provided, value will be converted as string by default.
        """
        status = False
        pass_msg = "Value: {0} is stored in a Key: {1} of Warrior data_repository"

        if datavar is not None and datavalue is not None:
            if type == 'int':
                datavalue = int(datavalue)
            elif type == 'float':
                datavalue = float(datavalue)
            dict_to_update = Utils.dict_Utils.get_dict_to_update(datavar, datavalue)
            update_datarepository(dict_to_update)
            print_info(pass_msg.format(datavalue, datavar))
            status = True

        if filepath is not None:
            testcasefile_path = get_object_from_datarepository('wt_testcase_filepath')
            try:
                filepath = getAbsPath(filepath, os.path.dirname(testcasefile_path))
                with open(filepath, "r") as json_handle:
                    json_doc = json.load(json_handle)
                #if bool_store_all is set to True, all content of given json file will be
                #stored in data repository
                if isinstance(bool_store_all, bool) and bool_store_all is True:
                    print_info("bool_store_all is set to True, all content of given"
                               " json file will be stored in data repository")
                    update_datarepository(json_doc)
                    print_info("{0} dictionary stored in Warrior data_repository".
                               format(json_doc))
                    status = True
                elif not isinstance(bool_store_all, bool):
                    print_error("invalid value : {0} given for bool_store_all,"
                                "valid value: boolean True or False".format(bool_store_all))
                    status = False
                elif jsonkey in json_doc:
                    dict_to_update = {}
                    repo_dict = json_doc[jsonkey]
                    for var_key, var_value in repo_dict.items():
                        if isinstance(var_value, dict):
                            if var_value.get('type') == 'int':
                                value = int(var_value['value'])
                            elif var_value.get('type') == 'float':
                                value = float(var_value['value'])
                            else:
                                value = str(var_value['value'])
                        else:
                            value = str(var_value)
                        build_dict = Utils.dict_Utils.get_dict_to_update(var_key, value)
                        Utils.dict_Utils.verify_key_already_exists_and_update\
                            (orig_dict=dict_to_update, new_dict=build_dict)
                    update_datarepository(dict_to_update)
                    print_info("{0} dictionary stored in Warrior data_repository".\
                        format(dict_to_update))
                    status = True
                else:
                    print_error('The {0} file is missing the key '
                                '\"repo_variables\", please refer to '
                                'the Samples in Config_files'.format(filepath))
                    status = True
            except ValueError:
                print_error('The file {0} is not a valid json '
                            'file'.format(filepath))
            except IOError:
                print_error('The file {0} does not exist'.format(filepath))
            except Exception as error:
                print_error('Encountered {0} error'.format(error))

        if (type is None or datavalue is None) and filepath is None:
            print_error('Either Provide values to arguments \"datavar\" & '
                        '\"datavalue\" or to argument \"filepath\"')

        return status

    def fetch_in_repo(self, datavar):
        """Prints value of datavar in datarepository
        :Argument:
            1. datavar = Key to fetch value in data_repository,
                         this could be dot separated to fetch in nested fashion
                            i.e., if var is k1.k2.k3 then the value would be
                            fetched as a value in datarepository[k1][k2][k3]
        :Returns:
            status (boolean True)

        """
        wDesc = "Print the  value of given key in data_repository "
        Utils.testcase_Utils.pNote(wDesc)
        status = True
        pass_msg = "Value: {0} is stored in a Key: {1} of Warrior data_repository"
        value = get_object_from_datarepository(datavar)
        if value:
            print_info(pass_msg.format(value, datavar))
        return status #always returns True, just prints warning if key is not present.

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

    def verify_arith_exp(self, expression, expected, comparison='eq', repo_key='exp_op'):
        """ Verify the output of the arithmetic expression matches the expected(float comparison)
            Note : Binary floating-point arithmetic holds many surprises.
            Please refer to link, https://docs.python.org/2/tutorial/floatingpoint.html
            This Keyword inherits errors in Python float operations.
            :Arguments:
                1. expression: Arithmetic expression to be compared with expected.
                    This can have env & data_repo values embedded in it.
                        Ex. expression: "10+${ENV.x}-${REPO.y}*10"
                    Expression will be evaluated based on python operator precedence
                2. expected: Value to be compared with the expression output
                    This can be a env or data_repo or any numeral value.
                3. comparison: Type of comparison(eq/ne/gt/ge/lt/le)
                    eq - check if both are same(equal)
                    ne - check if both are not same(not equal)
                    gt - check if expression output is greater than expected
                    ge - check if expression output is greater than or equal to expected
                    lt - check if expression output is lesser than expected
                    le - check if expression output is lesser than or equal to expected
                4. repo_key: Name of the key to be used to save the expression_output
                   in the warrior data repository
                    Ex. If repo_key is 'exp_op' & expression_output is 10.0
                        It will be stored in data_repo in the below format
                        data_repo = {
                                        ...
                                        verify_arith_exp: {'exp_op': 10.0},
                                        ...
                                    }
                        This value can be retrieved from data_repo using
                        key : 'verify_arith_exp.exp_op'.
            :Returns:
                1. status(boolean)
        """
        wDesc = "Verify if the output of the arithmetic expression matches the expected"
        Utils.testcase_Utils.pNote(wDesc)
        status = Utils.data_Utils.verify_arith_exp(expression, expected,
                                                   comparison, repo_key)
        return status

    def get_current_timestamp(self, current_time="current_time"):
        """Returns system current timestamp.
           :Arguments:
                  1. current_time (string) : name of the key to store in data repository

           :Returns:
                1. status(boolean)
                2. current_time (dict element) : name = current_time given in the argument,
                    value = Current System Time in the  object format of Year, Month, Date,
                    Time(without microseconds)
                     Ex :datetime.datetime(2018, 10, 22, 5, 51, 21)

        """
        wdesc = "To get the current timestamp in the format of yyyy-mm-dd hh:mm:ss"
        Utils.testcase_Utils.pNote(wdesc)
        currentdate = datetime_utils.get_current_timestamp()
        print_info("current timestamp : {0}".format(currentdate))
        output_dict = {current_time: currentdate}
        status = True
        return status, output_dict

    def get_time_delta(self, start_time, end_time=None, time_diff="time_diff"):
        """Returns time difference between two timestamps in seconds.
           :Arguments:
                1. start_time = start time key in the data repository,
                                  value should be datetime object in data repo.
                                  Ex: 'timestamp1'

                2. end_time(optional) = end time key in the data repository,
                                          value should be datetime object in data repo.
                                          Ex: 'timestamp2'

                  3. time_diff(optional) = time diff key in the data repository

           :Returns:
                  1. status(boolean)
                  2. time_diff (dict element) : name = time_diff, value = difference between the
                     given start time and end time in seconds (ex: 212342.0)

        """
        wdesc = "To get time difference between two timestamps"
        Utils.testcase_Utils.pNote(wdesc)
        start_time = Utils.data_Utils.get_object_from_datarepository(start_time)
        if end_time:
            end_time = Utils.data_Utils.get_object_from_datarepository(end_time)
        time_delta = datetime_utils.get_time_delta(start_time=start_time, end_time=end_time)
        print_info("delta between given timestamps : {0} seconds".format(time_delta))
        output_dict = {time_diff: time_delta}
        status = True
        return status, output_dict
