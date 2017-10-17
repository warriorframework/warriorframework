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
import os
import time
from Framework import Utils
from Framework.Utils import data_Utils, file_Utils
from Framework.Utils.testcase_Utils import pNote
from Framework.Utils.print_Utils import print_error


class CIregressionActions(object):
    """
        This class contains keywords that are used in warrior regression test
    """

    def __init__(self):
        """
            constructor
        """
        self.resultfile = Utils.config_Utils.resultfile
        self.datafile = Utils.config_Utils.datafile
        self.logsdir = Utils.config_Utils.logsdir
        self.filename = Utils.config_Utils.filename
        self.logfile = Utils.config_Utils.logfile

    def write_to_file(self, key, system_name):
        """
            Here we are writing to the file which keyword ran and on which system

            Argument:
                Key: It is basically the keyword name followed by step num in the test case
                system_name: It is the system_name on which the step ran
            Returns:
                True
        """
        data_Utils.update_datarepository({"output_file":self.logfile})
        with open(self.logfile,"a+") as fo:
            fo.write("\n"+"****************************")
            fo.write("\n"+key+" ran")
            fo.write("\n"+"Ran on "+system_name)
            fo.write("\n"+"****************************"+"\n")
        return True

    def once_per_tc_with_system_name_given(self, system_name, step_num):
        """
            It is used to test the functionality of once per tc with system name given in the test case
            Arguments:
                system_name: Name of the system on which it needs to be run
                step_num: It is the step_num in the test case file
            Returns:
                Returns True
        """

        wdesc = "Once per tese case with system name given"
        pNote(wdesc)
        key = 'once_per_tc_with_system_name_given_'+str(step_num)
        self.write_to_file(key, system_name)
        return True

    def once_per_tc_with_no_name_given(self, system_name, step_num):
        """
            It is used to test the functionality of once per tc with no system name given in the test case
            Arguments:
                system_name: Name of the system on which it needs to be run
                step_num: It is the step_num in the test case file
            Returns:
                Returns True
        """

        wdesc = "Once per testcase with system name not given"
        pNote(wdesc)
        key = 'once_per_tc_with_no_name_given_'+str(step_num)
        self.write_to_file(key, system_name)
        return True

    def once_per_tc_with_error(self, system_name, step_num):
        """
            It is used to test the functionality of once per tc with error in the test case
            Arguments:
                system_name: Name of the system on which it needs to be run
                step_num: It is the step_num in the test case file
            Returns:
                Returns True
        """

        wdesc = "Once per testcase with error"
        pNote(wdesc)
        key = 'once_per_tc_with_error_'+str(step_num)
        self.write_to_file(key, system_name)
        raise Exception("This is raised in CIregressionActions.once_per_tc_with_error")
        return False

    def standard_with_system_name_given(self, system_name, step_num):
        """
            It is used to test the functionality of standard with system name given in the test case
            Arguments:
                system_name: Name of the system on which it needs to be Running
                step_num: It is the step_num in the test case file
            Returns:
                Returns True
        """

        wdesc = "Standard with system name given"
        pNote(wdesc)
        key = 'standard_with_system_name_given_'+str(step_num)
        self.write_to_file(key, system_name)
        return True

    def standard_with_system_name_not_given(self, system_name, step_num):
        """
            It is used to test the functionality of standard with no system name given in the test case
            Arguments:
                system_name: Name of the system on which it needs to be run
                step_num: It is the step_num in the test case file
            Returns:
                Returns True
        """

        wdesc = "Standard with system name not given"
        pNote(wdesc)
        key = 'standard_with_system_name_not_given_'+str(step_num)
        self.write_to_file(key, system_name)
        return True

    def standard_with_error(self, system_name, step_num):
        """
            It is used to test the functionality of standard with error in the test case
            Arguments:
                system_name: Name of the system on which it needs to be run
                step_num: It is the step_num in the test case file
            Returns:
                Returns True
        """
        wdesc = "Standard with error"
        pNote(wdesc)
        key = 'standard_with_error_'+str(step_num)
        self.write_to_file(key, system_name)
        raise Exception("This is raised in CIregressionActions.standard_with_error")
        return False

    def end_of_tc_with_system_name_given(self, system_name, step_num):
        """
            It is used to test the functionality of end of tc with system name given in the test case
            Arguments:
                system_name: Name of the system on which it needs to be run
                step_num: It is the step_num in the test case file
            Returns:
                Returns True
        """
        wdesc = "End of testcase with system name given"
        pNote(wdesc)
        key = 'end_of_tc_with_system_name_given_'+str(step_num)
        self.write_to_file(key, system_name)
        return True

    def end_of_tc_with_system_name_not_given(self, system_name, step_num):
        """
            It is used to test the functionality of end of tc with no system name given in the test case
            Arguments:
                system_name: Name of the system on which it needs to be run
                step_num: It is the step_num in the test case file
            Returns:
                Returns True
        """
        wdesc = "End of testcase with system name not given"
        pNote(wdesc)
        key = 'end_of_tc_with_system_name_not_given_'+str(step_num)
        self.write_to_file(key, system_name)
        return True

    def end_of_tc_with_error(self, system_name, step_num):
        """
            It is used to test the functionality of end of tc with error given in the test case
            Arguments:
                system_name: Name of the system on which it needs to be run
                step_num: It is the step_num in the test case file
            Returns:
                Returns True
        """
        wdesc = "End of testcase with error"
        pNote(wdesc)
        key = 'end_of_tc_with_error_'+str(step_num)
        self.write_to_file(key, system_name)
        raise Exception("This is raised in CIregressionActions.end_of_tc_with_error")
        return False

    def compare_hybrid_tc_result(self,input_file):
        """
            It takes the input file path which is the expected result and compares with the log file and
            returns True if both matches else False and prints the difference to console.

            Arguments:
                input_file: It takes expected result file path as input
        """
        wdesc = "Compares the test case result file with expected result file"
        pNote(wdesc)
        output_file = data_Utils.get_object_from_datarepository("output_file")

        f = open(output_file)
        f1 = open(input_file)
        output_content = f.readlines()
        input_content = f1.readlines()
        if output_content == input_content:
            return True
        output_set = set([tuple([i]) for i in output_content])
        input_set = set([tuple([i]) for i in input_content])
        output_set_count = len(output_set)
        input_set_count = len(input_set)
        if output_set_count > input_set_count:
            diff = output_set.difference(input_set)
            result_content = output_content
        else:
            diff = input_set.difference(output_set)
            result_content = input_content
        pNote("**************The difference between the files is******************")
        for j in diff:
            s = str(j[0])
            index = result_content.index(s)
            last_index = result_content.index("****************************\n",index)
            start_index = last_index-2
            for i in range(start_index-1,last_index+1):
                pNote(result_content[i].strip("\n"))
        return False

    def increase_value(self, key, status, max_value, max_status):
        """
        write to a value in datarepo and return status
        if value == max, return max_status instead
        """
        value = data_Utils.get_object_from_datarepository(key)
        if key == False:
            num = 1
        else:
            if isinstance(value, int):
                num = value + 1
            else:
                num = 1
        if num == int(max_value):
            status = max_status

        if status == "pass":
            status = True
        elif status == "fail":
            status = False
        else:
            raise Exception("This is raised in ci_regression_actions.increase_value")

        output_dict = {key: num}
        return status, output_dict

    def local_data_test(self, desired_status):
        """For testing/demo/placeholder
        return true/false/exception based on input
        :Argument:
            desired_status = user desired status
            input pass->true, fail->false and everything else ->exception
        """
        # print "desired_status: " + desired_status
        if desired_status == "pass":
            return True
        elif desired_status == "fail":
            return False
        else:
            raise Exception("This is raised in ci_regression_actions.local_data_test")

    def create_tmp_dir(self):
        """
            Create a temp directory for parallel execution test
        """
        path = file_Utils.createDir(file_Utils.getDirName(self.logsdir), "tmp")
        return True, {"parallel_exec_tmp_dir": os.path.join(file_Utils.getDirName(self.logsdir), "tmp")} if path else False

    def create_sub_tmp_file(self, system_name="", filename="", delete="yes"):
        """
            Create temp file for parallel execution test
        """
        path = data_Utils.get_object_from_datarepository("parallel_exec_tmp_dir")
        if system_name != "" and filename == "":
            filename = data_Utils.getSystemData(self.datafile, system_name, "filename")
        elif system_name == "" and filename == "":
            pNote("No system or filename found, needs to provide at least one", "error")
        f = open(os.path.join(path, filename), "w")
        f.write("This is a test string")
        f.close()
        time.sleep(10)
        status = False
        if delete == "yes":
            try:
                file_Utils.delFile(os.path.join(path, filename))
                status = True
            except OSError:
                pNote("Cannot remove tmp file, no write access to {}".format(path), "error")
        else:
            status = True
        return status

    def tmp_file_count(self, int_count):
        """ count how many files are under the temp dir """
        time.sleep(5)
        path = data_Utils.get_object_from_datarepository("parallel_exec_tmp_dir")
        content = os.listdir(path)
        pNote(content)
        pNote(str(len(content)) + str(int_count))
        return len(content) == int_count

    def check_tmp_file_exists(self, system_name="", filename=""):
        """ check if temp folder exist in the parallel execution result tmp dir """
        if system_name != "" and filename == "":
            filename = data_Utils.getSystemData(self.datafile, system_name, "filename")
        elif system_name == "" and filename == "":
            pNote("No system or filename found, needs to provide at least one", "error")
        path = data_Utils.get_object_from_datarepository("parallel_exec_tmp_dir")
        path = os.path.join(path, filename)
        return file_Utils.fileExists(path)

    def delete_tmp_dir(self):
        """
            Delete temp directory for parallel execution test
        """
        path = data_Utils.get_object_from_datarepository("parallel_exec_tmp_dir")
        return file_Utils.delFolder(path)

    def check_kw_arg_type_prefix(self, str_value, int_value, float_value, bool_value,
                          list_value, tuple_value, dict_value, file_value):
        """This keyword is intended to test the type prefix for keyword arguments
        when an argument name has a type_ prefix, the variable type will become
        the type specified in the type_ prefix
        :Argument:
            1. str_value - expected to be string
            2. int_value - expected to be int
            3. float_value - expected to be float
            4. bool_value - expected to be bool
            5. list_value - expected to be list
            6. tuple_value - expected to be tuple
            7. dict_value - expected to be dict
            8. file_value - expected to be file
        """
        file_contents = "Checking file datatype in wtags"
        status = True
        err_msg = "{} is not an {} value but of type {}"
        if type(str_value) is not str:
            # this block checks if str_value is string type
            print_error(err_msg.format(str_value, "str", type(str_value)))
            status = False
        if type(int_value) is not int:
            # this block checks if int_value is int type
            print_error(err_msg.format(int_value, "int", type(int_value)))
            status = False
        if type(float_value) is not float:
            # this block checks if float_value is float type
            print_error(err_msg.format(float_value, "float", type(float_value)))
            status = False
        if type(bool_value) is not bool:
            # this block checks if bool_value is bool type
            print_error(err_msg.format(bool_value, "bool", type(bool_value)))
            status = False
        if type(list_value) is not list:
            # this block checks if list_value is list type
            print_error(err_msg.format(list_value, "list", type(list_value)))
            status = False
        if type(tuple_value) is not tuple:
            # this block checks if tuple_value is tuple type
            print_error(err_msg.format(tuple_value, "tuple", type(tuple_value)))
            status = False
        if type(dict_value) is not dict:
            # this block checks if dict_value is dict type
            print_error(err_msg.format(dict_value, "dict", type(dict_value)))
            status = False
        if type(file_value) is not file:
            # this block checks if file_value is file type
            print_error(err_msg.format(file_value, "file", type(file_value)))
            status = False
        else:
            actual_contents = file_value.read().strip()
            if actual_contents != file_contents:
                # this block checks if the contents of file type variable is expected
                print_error("contents of the file {} is <<{}>> which does not match expected"
                            " <<{}>>".format(file_value, actual_contents, file_contents))
                status = False
        return status

    def check_values_from_datafile(self, system_name, strvar, langs, states,
                                   currencys, ramspace, configfile, intvar,
                                   anotherfile):
        """Verify the datatype of the value read from the datafile using either
        the tag or wtag feature
        :Argument:
            1. system_name = system name in the datafile
            2. strvar = string variable
            3. langs = list variable (should get from data file using wtag)
            4. states = tuple variable
            5. currencys = dict variable
            6. ramspace = boolean variable
            7. configfile = file variable
            8. intvar = int variable
            9. anotherfile = file variable
        """
        def check_type(var, varname, datatype):
            """check that vars are of correct datatype
            """
            vartype = type(var)
            status = True
            if vartype is not datatype:
                print_error('{} is expected to be {} type, but found to be of '
                            '{} type'.format(varname, datatype, vartype))
                status = False
            return status
        status = True
        datafile = Utils.config_Utils.datafile
        tc_filepath = os.path.dirname(data_Utils.get_object_from_datarepository(
                                            'wt_testcase_filepath'))
        # this block checks if strvar is string type
        status = check_type(strvar, "strvar", str) and status
        # this block checks if langs is list type
        status = check_type(langs, "langs", list) and status
        # this block checks if states is tuple type
        status = check_type(states, "states", tuple) and status
        # this block checks if currencys is dict type
        status = check_type(currencys, "currencys", dict) and status
        # this block checks if ramspace is bool type
        status = check_type(ramspace, "ramspace", bool) and status
        file_err = '{} is not a file, please check'
        try:
            # check if tag is present and its functionality is not broken
            if anotherfile.startswith('tag'):
                anotherfile = data_Utils.resolve_argument_value_to_get_tag_value(
                                        datafile, system_name, anotherfile)
            # this checks if configfile and anotherfile are valid files
            # by getting the absolute path of the file
            if not os.path.isabs(configfile):
                configfile = file_Utils.getAbsPath(configfile, tc_filepath)
            if not os.path.isabs(anotherfile):
                anotherfile = file_Utils.getAbsPath(anotherfile, tc_filepath)
            if not os.path.isfile(configfile):
                print_error(file_err.format(configfile))
            if not os.path.isfile(anotherfile):
                print_error(file_err.format(anotherfile))
        except AttributeError:
            print_error('configfile and anotherfile are expected to be files')
            print_error('type of configfile is {}'.format(type(configfile)))
            print_error('type of anotherfile is {}'.format(type(anotherfile)))
            status = False
        if type(intvar) is str and intvar.startswith('tag'):
            intvar = data_Utils.resolve_argument_value_to_get_tag_value(
                                    datafile, system_name, intvar)
        else:
            status = check_type(intvar, "intvar", int) and status

        return status
