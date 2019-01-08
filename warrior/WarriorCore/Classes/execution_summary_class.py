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
        project_list = []
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
            project_list.append([file_type, proj_name, project_status, proj_location])
        return project_list

    def suite_summary(self, junit_file):
        """ To get the name, status and location of both test suite and test case"""
        tree = xml_Utils.get_tree_from_file(self.junit_file)
        suite_tc_list = []
        for values in tree.iter('testsuite'):
            suite_detail = values.attrib
            suite_name = suite_detail.get('name')
            suite_status = suite_detail.get('status')
            suite_location = suite_detail.get('suite_location')
            suite_result_dir = suite_detail.get('resultsdir')
            if suite_location is not None:
                suite_tc_list.append(["Suites", suite_name, suite_status, suite_location])
            #to add Setup results in suite summary
            for value in tree.iter('Setup'):
                setup_details = value.attrib
                setup_status = setup_details.get('status')
                setup_name = setup_details.get('name')+".xml"
                setup_location = setup_details.get('testcasefile_path')
                case_result_dir_with_tc_name = setup_details.get('resultsdir')
                if case_result_dir_with_tc_name is not None:
                    case_result_dir = os.path.dirname(case_result_dir_with_tc_name)
                    # suite junit element will not have resultsdir attrib for case execution
                    if suite_result_dir is None or suite_result_dir == case_result_dir:
                        suite_tc_list.append(["Setup", setup_name, setup_status, setup_location])
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
                        suite_tc_list.append(["Testcase", testcase_name, testcase_status,
                                              testcase_location])
            #to add Cleanup results in suite summary
            for value in tree.iter('Cleanup'):
                cleanup_details = value.attrib
                cleanup_status = cleanup_details.get('status')
                cleanup_name = cleanup_details.get('name')+".xml"
                cleanup_location = cleanup_details.get('testcasefile_path')
                case_result_dir_with_tc_name = cleanup_details.get('resultsdir')
                if case_result_dir_with_tc_name is not None:
                    case_result_dir = os.path.dirname(case_result_dir_with_tc_name)
                    # suite junit element will not have resultsdir attrib for case execution
                    if suite_result_dir is None or suite_result_dir == case_result_dir:
                        suite_tc_list.append(["Cleanup", cleanup_name, cleanup_status, cleanup_location])
        # suite_tc_list appends suites and test cases as per execution order
        return suite_tc_list

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
        # Formatting execution summary as project_summary and suite_summary returns the list values
        print_info("+++++++++++++++++++++++++++++++++++++++++++++++++ Execution Summary +++++++++++++++++++++++++++++++++++++++++++++++++")
        print_info("{0:10}{1:50}{2:10}{3:50}".format('Type', 'Name', 'Status', 'Path'))
        if file_type == "Project":
            project_exec = self.project_summary(junit_file)
            for proj in project_exec:
                print_info(("{0:10}{1:50}{2:10}{3:30}"
                            .format(proj[0], proj[1], proj[2], proj[3])))
            suite_tc_exec = self.suite_summary(junit_file)
            for suite_tc in suite_tc_exec:
                print_info(("{0:10}{1:50}{2:10}{3:30}"
                            .format(suite_tc[0], suite_tc[1], suite_tc[2], suite_tc[3])))
        elif file_type == "Suites":
            suite_tc_exec = self.suite_summary(junit_file)
            for suite_tc in suite_tc_exec:
                print_info(("{0:10}{1:50}{2:10}{3:30}"
                            .format(suite_tc[0], suite_tc[1], suite_tc[2], suite_tc[3])))
        print_info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
