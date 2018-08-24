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

#!/usr/bin/python

import os
import traceback
from collections import OrderedDict

import testcase_driver
import Framework.Utils as Utils
from Framework.Utils.print_Utils import print_error, print_debug
from WarriorCore.multiprocessing_utils import create_and_start_process_with_queue, \
 get_results_from_queue, update_ts_junit_resultfile
from WarriorCore import testsuite_utils


"""This is  parallel testcase driver which is used to execute
the testcases of a suite in parallel """


def execute_parallel_testcases(testcase_list, suite_repository,
                               data_repository, from_project, tc_parallel=True,
                               auto_defects=False, iter_ts_sys=None):
    """Takes a list of testcase as input and executes them in parallel by
    creating separate process of testcase_driver for each of these testcase """

    jobs_list = []
    output_q = None
    suite = suite_repository['suite_name']
    testsuite_filepath = suite_repository['testsuite_filepath']
    suite_error_action = suite_repository['def_on_error_action']
    jiraproj = data_repository["jiraproj"]
    testsuite_dir = os.path.dirname(testsuite_filepath)

    for testcase in testcase_list:
        target_module = testcase_driver.main
        tc_rel_path = testsuite_utils.get_path_from_xmlfile(testcase)
        if tc_rel_path is not None:
            tc_path = Utils.file_Utils.getAbsPath(tc_rel_path, testsuite_dir)
        else:
            tc_path = str(tc_rel_path)
        tc_runtype = testsuite_utils.get_runtype_from_xmlfile(testcase)
        tc_impact = Utils.testcase_Utils.get_impact_from_xmlfile(testcase)
        tc_context = Utils.testcase_Utils.get_context_from_xmlfile(testcase)
        suite_step_data_file = testsuite_utils.get_data_file_at_suite_step(testcase,
                                                                           suite_repository)
        tc_onError_action = Utils.xml_Utils.get_attributevalue_from_directchildnode(testcase,
                                                                                    'onError',
                                                                                    'action')
        tc_onError_action = tc_onError_action if tc_onError_action else suite_error_action
        if suite_step_data_file is not None:
            data_file = Utils.file_Utils.getAbsPath(suite_step_data_file, testsuite_dir)
            data_repository[tc_path] = data_file

        data_repository['wt_tc_impact'] = tc_impact

        # instead of using args_list, we need to use an ordered dict
        # for tc args because intially q will be none and
        # we need to cange it after creating a new q
        # then we need to maintain the position of arguments
        # before calling the testcase driver main function.

        tc_args_dict = OrderedDict([("tc_path", tc_path),
                                    ("data_repository", data_repository),
                                    ("tc_context", tc_context),
                                    ("tc_runtype", tc_runtype),
                                    ("tc_parallel", tc_parallel),
                                    ("auto_defects", auto_defects),
                                    ("suite", suite),
                                    ("tc_onError_action", tc_onError_action),
                                    ("iter_ts_sys", iter_ts_sys),
                                    ("output_q", output_q),
                                    ("jiraproj", jiraproj)])

        process, jobs_list, output_q = create_and_start_process_with_queue(target_module,
                                                                           tc_args_dict,
                                                                           jobs_list, output_q)

    print_debug("process: {0}".format(process))
    for job in jobs_list:
        job.join()

    result_list = get_results_from_queue(output_q)

    tc_status_list = []
    tc_name_list = []
    tc_impact_list = []
    tc_duration_list = []
    # Get the junit object of each testcase, extract the information from it and
    # combine with testsuite junit object
    tc_junit_list = []

    for result in result_list:
        tc_status_list.append(result[0])
        tc_name_list.append(result[1])
        tc_impact_list.append(result[2])
        tc_duration_list.append(result[3])
        if len(result) > 4:         
            tc_junit_list.append(result[4])
    
    # parallel testcases generate multiple testcase junit result files
    # each files log the result for one testcase and not intergrated
    # update testsuite junit result file with individual testcase result files
    data_repository['wt_junit_object'] = update_ts_junit_resultfile(
        data_repository['wt_junit_object'], tc_junit_list,
        data_repository['wt_ts_timestamp'])
    testsuite_status = Utils.testcase_Utils.compute_status_using_impact(tc_status_list,
                                                                        tc_impact_list)
    return testsuite_status


def main(testcase_list, suite_repository, data_repository, from_project, tc_parallel=True,
         auto_defects=False, iter_ts_sys=None):
    """Executes the list of testcases in parallel
    Computes and returns the testsuite status"""
    try:
        testsuite_status = execute_parallel_testcases(testcase_list, suite_repository,
                                                      data_repository,
                                                      from_project, tc_parallel,
                                                      auto_defects, iter_ts_sys)
    except Exception:
        testsuite_status = False
        print_error('unexpected error {0}'.format(traceback.format_exc()))
    return testsuite_status
