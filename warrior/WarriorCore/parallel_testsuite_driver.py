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

"""This is  parallel suite driver which is used to execute
the suites of a project in parallel """

import os
import traceback
from collections import OrderedDict

import Framework.Utils as Utils
import WarriorCore.testsuite_driver as testsuite_driver
from Framework.Utils.print_Utils import print_error, print_debug
from WarriorCore.multiprocessing_utils import create_and_start_process_with_queue, \
 get_results_from_queue, update_pj_junit_resultfile
from WarriorCore import testsuite_utils


def execute_parallel_testsuites(testsuite_list, project_repository, data_repository,
                                auto_defects=False, ts_parallel=True):
    """Takes a list of suites as input and executes them in parallel by
    creating separate process of testsuite_driver for each of these suite """

    jobs_list = []
    output_q = None
    impact_dict = {"IMPACT": "Impact", "NOIMPACT": "No Impact"}
    project_error_action = project_repository['def_on_error_action']
    project_filepath = project_repository['project_filepath']
    project_dir = os.path.dirname(project_filepath)
    wp_results_execdir = project_repository['wp_results_execdir']
    wp_logs_execdir = project_repository['wp_logs_execdir']
    jiraproj = data_repository["jiraproj"]

    for testsuite in testsuite_list:
        target_module = testsuite_driver.main
        testsuite_rel_path = testsuite_utils.get_path_from_xmlfile(testsuite)
        if testsuite_rel_path is not None:
            testsuite_path = Utils.file_Utils.getAbsPath(testsuite_rel_path, project_dir)
        else:
            testsuite_path = str(testsuite_rel_path)
        testsuite_impact = Utils.testcase_Utils.get_impact_from_xmlfile(testsuite)
        data_repository['wt_ts_impact'] = testsuite_impact
        ts_onError_action = Utils.xml_Utils.get_attributevalue_from_directchildnode(testsuite,
                                                                                    'onError',
                                                                                    'action')
        ts_onError_action = ts_onError_action if ts_onError_action else project_error_action

        tc_args_dict = OrderedDict([("testsuite_filepath", testsuite_path),
                                    ("data_repository", data_repository),
                                    ("from_project", True),
                                    ("auto_defects", auto_defects),
                                    ("jiraproj", jiraproj),
                                    ("res_startdir", wp_results_execdir),
                                    ("logs_startdir", wp_logs_execdir),
                                    ("ts_onError_action", ts_onError_action),
                                    ("output_q", output_q),
                                    ("ts_parallel", ts_parallel)])

        process, jobs_list, output_q = create_and_start_process_with_queue(target_module,
                                                                           tc_args_dict,
                                                                           jobs_list, output_q)

        print_debug("process: {0}".format(process))

    for job in jobs_list:
        job.join()

    result_list = get_results_from_queue(output_q)

    ts_status_list = []
    ts_impact_list = []
    ts_timestamp_list = []
    # Get the junit object of each suite, extract the information from it
    # and combine with project junit object
    ts_junit_list = []

    for result in result_list:
        ts_status_list.append(result[0])
        ts_impact_list.append(result[1])
        ts_timestamp_list.append(result[2])
        ts_junit_list.append(result[3])

    for i in range(len(ts_junit_list)):
        ts_junit_list[i].update_attr("impact", impact_dict.get(ts_impact_list[i].upper()),
                                     "ts", ts_timestamp_list[i])
        # onerror is not applicable for parallel execution
        ts_junit_list[i].update_attr("onerror", "N/A", "ts", ts_timestamp_list[i])

    # parallel suites generate multiple suite junit result files
    # each files log the result for one suite and not integrated
    # update project junit result file with individual suite result files
    data_repository['wt_junit_object'] = update_pj_junit_resultfile(
     data_repository['wt_junit_object'], ts_junit_list)

    project_status = Utils.testcase_Utils.compute_status_using_impact(ts_status_list,
                                                                      ts_impact_list)
    return project_status


def main(testsuite_list, project_repository, data_repository,
         auto_defects=False, ts_parallel=True):
    """Executes the list of testcases in parallel
    Computes and returns the testsuite status"""
    try:
        project_status = execute_parallel_testsuites(testsuite_list, project_repository,
                                                     data_repository, auto_defects, ts_parallel)
    except Exception:
        project_status = False
        print_error('unexpected error {0}'.format(traceback.format_exc()))
    return project_status
