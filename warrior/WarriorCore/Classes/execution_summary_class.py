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

"""Class which generates the consolidated test cases result in console at the
end of Test Suite or Project Execution """
import os
from Framework.Utils import xml_Utils
from Framework.Utils.print_Utils import print_info


class ExecutionSummary():
    """Warrior execution summary class"""
    def __init__(self, junit_file=None):
        """ Constructor """
        self.junit_file = junit_file

    def project_summary(self, junit_file):
        """To get the project name, project status and it's location"""
        tree = xml_Utils.get_tree_from_file(self.junit_file)
        for names in tree.iter('testsuites'):
            proj_detail = names.attrib
            proj_name = proj_detail.get('name')
            file_type = self.get_file_type(junit_file)
            project_status = proj_detail.get('status')
            proj_loc = []
            for properties in tree.iter('property'):
                project_details = properties.attrib
                if project_details.get('name') == 'location':
                    proj_loc.append(project_details.get('value'))
                    proj_location = proj_loc[0]
            print_info("{0:10}{1:50}{2:10}{3:30}".format(file_type, proj_name, project_status,
                                                         proj_location))

    def suite_summary(self, junit_file):
        """ To get the name, status and location of both test suite and test case"""
        tree = xml_Utils.get_tree_from_file(self.junit_file)
        for values in tree.iter('testsuite'):
            suite_detail = values.attrib
            suite_name = suite_detail.get('name')
            suite_status = suite_detail.get('status')
            suite_location = suite_detail.get('suite_location')
            suite_result_dir = suite_detail.get('resultsdir')
            if suite_location is not None:
                print_info("{0:10}{1:50}{2:10}{3:30}".format("Suites", suite_name, suite_status,
                                                             suite_location))
            for value in tree.iter('testcase'):
                testcase_details = value.attrib
                testcase_status = testcase_details.get('status')
                testcase_name = testcase_details.get('name')+".xml"
                testcase_location = testcase_details.get('testcasefile_path')
                case_result_dir_with_tc_name = testcase_details.get('resultsdir')
                if case_result_dir_with_tc_name is not None:
                    case_result_dir = os.path.dirname(case_result_dir_with_tc_name)
                    # suite junit element will not have resultsdir attrib for case execution
                    if suite_result_dir is None or suite_result_dir == case_result_dir:
                        print_info("{0:10}{1:50}{2:10}{3:30}".format("Testcase", testcase_name,
                                                                     testcase_status,
                                                                     testcase_location))

    def get_file_type(self, junit_file):
        """To get the file type which is given for execution"""
        tree = xml_Utils.get_tree_from_file(self.junit_file)
        for names in tree.iter('testsuites'):
            file_detail = names.attrib
            file_val = file_detail.get('name')
            if file_val == "customProject_independant_testcase_execution":
                file_type = "Suites"
            else:
                file_type = "Project"
        return file_type

    def print_result_in_console(self, junit_file):
        """To print the consolidated test cases result in console at the end of Test Case/Test
           Suite/Project Execution"""
        file_type = self.get_file_type(junit_file)
        print_info("+++++++++++++++++++++++++++++++++++++++++++++++++ Execution Summary +++++++++++++++++++++++++++++++++++++++++++++++++")
        print_info("{0:10}{1:50}{2:10}{3:50}".format('Type', 'Name', 'Status', 'Path'))
        if file_type == "Project":
            self.project_summary(junit_file)
            self.suite_summary(junit_file)
        elif file_type == "Suites":
            self.suite_summary(junit_file)
        print_info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
