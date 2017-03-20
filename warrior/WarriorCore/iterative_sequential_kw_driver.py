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

"""This is iterative sequential keyword driver which is used to execute
the keywords of a testcase in sequential order, where data_type = iterative"""

import traceback
import testcase_steps_execution
import Framework.Utils as Utils
from Framework.Utils.print_Utils import print_debug, print_error

def compute_system_resultfile(kw_resultfile_list, resultsdir, system_name):
    """Takes a list of steps as input and executes them in sequential
    order by sending them to testcase steps execution driver """

    system_results_dir = Utils.file_Utils.createDir(resultsdir,
                                                    'System_Results')
    system_resultfile = Utils.file_Utils.getCustomLogFile('system', system_results_dir,
                                                          system_name, '.xml')
    Utils.testcase_Utils.append_result_files(system_resultfile,
                                             kw_resultfile_list, dst_root='System')
    return system_resultfile

def execute_iterative_sequential(step_list, data_repository, tc_status, system_list):
    """ Executes all the steps in iterative sequential fashion """

    system_status_list = []
    system_resultfile_list = []

    for system in system_list:
        step_status_list, kw_resultfile_list, step_impact_list = testcase_steps_execution.main(step_list, data_repository, system_name=system)
        system_status = Utils.testcase_Utils.compute_status_using_impact(step_status_list,
                                                                         step_impact_list)
        system_resultfile = compute_system_resultfile(kw_resultfile_list, data_repository['wt_resultsdir'], system)
        system_status_list.append(system_status)
        system_resultfile_list.append(system_resultfile)

    tc_status = Utils.testcase_Utils.compute_status_without_impact(system_status_list)
    print_debug("Updating Testcase result file...")
    Utils.testcase_Utils.append_result_files(data_repository['wt_resultfile'], system_resultfile_list)

    return tc_status

def main(step_list, data_repository, tc_status, system_list):
    """Executes the list of steps in iterative fashion
    Computes and returns the testcase status"""
    try:
        testcase_status = execute_iterative_sequential(step_list, data_repository,
                                                       tc_status, system_list)
    except Exception:
        testcase_status = False
        print_error('unexpected error {0}'.format(traceback.format_exc()))
    return testcase_status
