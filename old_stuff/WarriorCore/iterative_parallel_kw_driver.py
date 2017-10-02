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

"""This is iterative parallel keyword driver which is used to execute
the keywords of a testcase in parallel where data_type = iterative"""

import traceback
from collections import OrderedDict


import WarriorCore.testcase_steps_execution as testcase_steps_execution
import Framework.Utils as Utils
from Framework.Utils.print_Utils import print_debug, print_error
from WarriorCore.multiprocessing_utils import create_and_start_process_with_queue, \
get_results_from_queue, update_tc_junit_resultfile
from Framework.Utils import testcase_Utils

def execute_iterative_parallel(step_list, data_repository, tc_status, system_list):
    """Takes a list of steps as input and executes them in parallel by
    creating separate process of step_driver for each of these steps """

    jobs_list = []
    output_q = None
    for system_name in system_list:
        target_module = testcase_steps_execution.main
        #args_list = [step_list, data_repository, system_name, True]
        args_dict = OrderedDict([("step_list", step_list),
                                  ("data_repository", data_repository),
                                  ("system_name", system_name),
                                  ("kw_parallel", True),
                                  ("output_q", output_q),
                                  ]) 


        process, jobs_list, output_q = create_and_start_process_with_queue(target_module, args_dict,
                                                                           jobs_list, output_q)

    print_debug("process: {0}".format(process))
    for job in jobs_list:
        job.join()

    result_list = get_results_from_queue(output_q)

    system_status_list = []
    system_resultfile_list = []
    step_impact_list = []
    tc_junit_list = []

    for result in result_list:
        step_status_list = result[0]
        kw_resultfile_list = result[1]
        system_name = result[2]
        step_impact_list = result[3]
        tc_junit_list.append(result[4])
        system_status = testcase_Utils.compute_status_using_impact(step_status_list,
                                                                   step_impact_list)
        system_resultfile = testcase_Utils.compute_system_resultfile(kw_resultfile_list,
                                                                     data_repository['wt_resultsdir'],
                                                                     system_name)
        system_status_list.append(system_status)
        system_resultfile_list.append(system_resultfile)

    tc_status = Utils.testcase_Utils.compute_status_without_impact(system_status_list)
    # parallel keywords generate multiple keyword junit result files
    # each files log the result for one keyword and not intergrated
    # update testcase junit result file with individual keyword result files
    data_repository['wt_junit_object'] = update_tc_junit_resultfile(data_repository['wt_junit_object'], tc_junit_list, data_repository['wt_tc_timestamp'])
    print_debug("Updating Testcase result file...")
    Utils.testcase_Utils.append_result_files(data_repository['wt_resultfile'], system_resultfile_list)

    return tc_status

def main(step_list, data_repository, tc_status, system_list):
    """Executes the list of keyword in iterative parallel fashion
    Computes and returns the testcase status"""
    try:
        testcase_status = execute_iterative_parallel(step_list, data_repository,
                                                     tc_status, system_list)
    except Exception:
        testcase_status = False
        print_error('unexpected error {0}'.format(traceback.format_exc()))
    return testcase_status
