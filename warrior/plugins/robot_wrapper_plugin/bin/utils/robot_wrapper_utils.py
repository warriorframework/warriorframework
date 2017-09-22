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
import datetime

from Framework.Utils import xml_Utils, config_Utils, datetime_utils
from Framework.Utils.print_Utils import print_warning
from WarriorCore.step_driver import add_keyword_result


def get_robot_xml_files(input_list):
    """
    Find robot xml files from the list of files.
    :Arguments:
        1. input_list(list) - list of file names
    :Return:
        1. output_list(list) - list of robot xml files
    """

    output_list = []
    if input_list:
        for filename in input_list:
            try:
                root = xml_Utils.getRoot(filename)
                if root.tag == 'robot':
                    output_list.append(filename)
            except Exception:
                print_warning("{} is not a valid xml file".format(filename))

    return output_list


def get_results_from_robot_xml(input_list):
    """
    Get the tests(and setup/teardown) executed by robot from the robot result xml file
    :Arguments:
        1. input_list(list) - Robot result xml files
    :Return:
        1. robot_tests(list) - Robot test xml elements
    """

    robot_tests = []
    for xml_file in input_list:
        suites = xml_Utils.getElementListWithSpecificXpath(xml_file, './/suite[@source]')
        for suite in suites:
            tests = suite.getchildren()
            for test in tests:
                if test.tag == "test" or test.tag == "kw":
                    robot_tests.append(test)
    return robot_tests


def create_case_junit(robot_tests):
    """ Add robot test results into Warrior Junit XML object
    :Argument:
        1. robot_tests(list) - Robot test xml elements
    """

    data_repository = config_Utils.data_repository
    tc_junit_object = data_repository['wt_junit_object']
    for test_elem in robot_tests:
        test_name = test_elem.get('name')

        tc_start_time = xml_Utils.get_attributevalue_from_directchildnode(
         test_elem, 'status', 'starttime')
        tc_start_time = datetime.datetime.strptime(
         tc_start_time, "%Y%m%d %H:%M:%S.%f").replace(microsecond=0)
        tc_timestamp = str(tc_start_time)
        tc_end_time = xml_Utils.get_attributevalue_from_directchildnode(
         test_elem, 'status', 'endtime')
        tc_end_time = datetime.datetime.strptime(
         tc_end_time, "%Y%m%d %H:%M:%S.%f").replace(microsecond=0)
        tc_duration = datetime_utils.get_time_delta(tc_start_time, tc_end_time)
        tc_status = xml_Utils.get_attributevalue_from_directchildnode(test_elem, 'status','status')

        tc_junit_object.create_testcase(location="from testsuite", timestamp=tc_timestamp,
                                        ts_timestamp=data_repository['wt_ts_timestamp'],
                                        classname=data_repository['wt_suite_name'],
                                        name=test_name,
                                        testcasefile_path=data_repository['wt_testcase_filepath'])
        tc_junit_object.add_property("resultsdir",
                                     os.path.dirname(data_repository['wt_resultsdir']),
                                    "tc", tc_timestamp)
        tc_junit_object.add_property("logsdir", os.path.dirname(data_repository['wt_logsdir']),
                                    "tc", tc_timestamp)
        tc_junit_object.update_attr("title", test_name, "tc", tc_timestamp)

        string_status = {"PASS": "TRUE", "FAIL": "FALSE"}
        # Convert robot test results
        if str(tc_status).upper() in string_status.keys():
            tc_status = string_status[str(tc_status).upper()]
        tc_junit_object.update_count(tc_status, "1", "ts", data_repository['wt_ts_timestamp'])
        tc_junit_object.update_count("tests", "1", "ts", data_repository['wt_ts_timestamp'])
        tc_junit_object.update_count("tests", "1", "pj", "not appicable")
        tc_junit_object.update_attr("status", str(tc_status), "tc", tc_timestamp)
        tc_junit_object.update_attr("time", str(tc_duration), "tc", tc_timestamp)
        tc_junit_object.add_testcase_message(tc_timestamp, tc_status)

        keywords = test_elem.getchildren()
        step_num = 1
        for kw_elem in keywords:
            if kw_elem.tag == "kw":
                kw_name = kw_elem.get('name')
                kw_start_time = xml_Utils.get_attributevalue_from_directchildnode(
                 kw_elem, 'status', 'starttime')
                kw_start_time = datetime.datetime.strptime(
                 kw_start_time, "%Y%m%d %H:%M:%S.%f").replace(microsecond=0)
                kw_end_time = xml_Utils.get_attributevalue_from_directchildnode(
                 kw_elem, 'status', 'endtime')
                kw_end_time = datetime.datetime.strptime(
                 kw_end_time, "%Y%m%d %H:%M:%S.%f").replace(microsecond=0)
                kw_duration = datetime_utils.get_time_delta(kw_start_time, kw_end_time)

                kw_status = xml_Utils.get_attributevalue_from_directchildnode(
                 kw_elem, 'status', 'status')

                kw_desc = xml_Utils.get_text_from_direct_child(kw_elem, 'doc')
                if kw_desc is False:
                    kw_desc = "No doc/desc provided"

                # Convert robot keyword results
                if str(kw_status).upper() in string_status.keys():
                    kw_status = string_status[str(kw_status).upper()]

                add_keyword_result(tc_junit_object, tc_timestamp, step_num,
                                   kw_name, kw_status, kw_start_time,
                                   kw_duration, "skipped", "Impact", "Next", kw_desc)
                step_num += 1
