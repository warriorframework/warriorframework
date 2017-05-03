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

import datetime
from Framework import Utils
from Framework.Utils import data_Utils, file_Utils
import os
from Framework.Utils.testcase_Utils import pNote

class CIregressionActions(object):
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
        print "**************The difference between the files is******************"
        for j in diff:
            s = str(j[0])
            index = result_content.index(s)
            last_index = result_content.index("****************************\n",index)
            start_index = last_index-2
            for i in range(start_index-1,last_index+1):
                print result_content[i].strip("\n")
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