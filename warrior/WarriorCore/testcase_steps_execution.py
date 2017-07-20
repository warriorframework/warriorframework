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

"""This module is used for sequential execution of testcase steps """

import sys
import os
import time
import traceback
import WarriorCore.step_driver as step_driver
import WarriorCore.onerror_driver as onerror_driver
from WarriorCore import common_execution_utils
import Framework
import Framework.Utils as Utils
from Framework.Utils.testcase_Utils import pNote
from Framework.Utils.print_Utils import print_info, print_debug, print_warning, print_error

def get_system_console_log(filename, logsdir, console_name):
        """Assign seperate console logfile for each system in parallel execution """

        console_logfile = Utils.file_Utils.getCustomLogFile(filename, logsdir, console_name)
        print_info ("************ This is parallel execution... console logs for {0} will be logged in {1} ************".format(console_name, console_logfile))
        Utils.config_Utils.debug_file(console_logfile)

        return console_logfile

def execute_steps(step_list, data_repository, system_name, parallel, queue):
    """Executes the teststep(provided as a xml test case)"""
    default_error_action = data_repository['wt_def_on_error_action']
    default_error_value = data_repository['wt_def_on_error_value']

    goto_stepnum        = False
    kw_resultfile_list  = []
    step_status_list    = []
    step_impact_list    = []
    step_num            = 0

    if parallel is True:
        system_console_log = get_system_console_log(data_repository['wt_filename'],
                                                    data_repository['wt_logsdir'],
                                                    '{0}_consoleLogs'.format(system_name))
    while step_num < len(step_list):
        step = step_list[step_num]
        # execute steps
        step_num += 1

        if not goto_stepnum:
            try:
                result = step_driver.main(step, step_num, data_repository, system_name)
                step_status = result[0]
                kw_resultfile = result[1]
                step_impact = result[2]
                exec_type_onerror = result[3]
                # print "exec_type_onerror:", exec_type_onerror

            except Exception, e:
                print_error('unexpected error %s' % str(e))
                step_status = False
                kw_resultfile = None
                step_impact = Utils.testcase_Utils.get_impact_from_xmlfile(step)
                print_error('unexpected error {0}'.format(traceback.format_exc()))

        elif (goto_stepnum and goto_stepnum == str(step_num)):
                try:
                    result = step_driver.main(step, step_num, data_repository, system_name)
                    step_status = result[0]
                    kw_resultfile = result[1]
                    step_impact = result[2]
                    exec_type_onerror = result[3]
                    # print "exec_type_onerror:", exec_type_onerror

                except Exception,e:
                    print_error('unexpected error %s' % str(e))
                    step_status = False
                    kw_resultfile = None
                    step_impact = Utils.testcase_Utils.get_impact_from_xmlfile(step)
                    print_error('unexpected error {0}'.format(traceback.format_exc()))
                goto_stepnum = False

        else:
            keyword = step.get('Keyword')
            kw_resultfile = step_driver.get_keyword_resultfile(data_repository, system_name,
                                                               step_num, keyword)
            Utils.config_Utils.set_resultfile(kw_resultfile)
            Utils.testcase_Utils.pKeyword(keyword, step.get('Driver'))
            Utils.testcase_Utils.reportStatus('Skip')
            step_description = Utils.testcase_Utils.get_description_from_xmlfile(step)
            kw_resultfile_list.append(kw_resultfile)
            data_repository['wt_junit_object'].update_count("skipped", "1", "tc",
                                                            data_repository['wt_tc_timestamp'])
            data_repository['wt_junit_object'].update_count("keywords", "1", "tc",
                                                            data_repository['wt_tc_timestamp'])
            kw_start_time = Utils.datetime_utils.get_current_timestamp()
            step_impact = Utils.testcase_Utils.get_impact_from_xmlfile(step)
            impact_dict = {"IMPACT": "Impact", "NOIMPACT": "No Impact"}
            data_repository['wt_junit_object'].\
                add_keyword_result(data_repository['wt_tc_timestamp'], step_num, keyword, "SKIPPED",
                                   kw_start_time, "0", "skipped",
                                   impact_dict.get(step_impact.upper()), "N/A", step_description)
            continue

        step_status_list.append(step_status)
        kw_resultfile_list.append(kw_resultfile)
        step_impact_list.append(step_impact)
        runmode, value = common_execution_utils.get_runmode_from_xmlfile(step)
        retry_type, retry_cond, retry_cond_value, retry_value, retry_interval = common_execution_utils.get_retry_from_xmlfile(step)
        if runmode is not None:
            # if runmode is 'ruf' & step_status is False, skip the repeated
            # execution of same TC step and move to next actual step
            if not exec_type_onerror and runmode == "RUF" and step_status is False:
                goto_stepnum = str(value)
            # if runmode is 'rup' & step_status is True, skip the repeated
            # execution of same TC step and move to next actual step
            elif runmode =="RUP" and step_status is True:
                goto_stepnum = str(value)
            else:
                if step_status is False or str(step_status).upper() == "ERROR" \
                        or str(step_status).upper() == "EXCEPTION" or exec_type_onerror is True:
                    goto_stepnum = onerror_driver.main(step, default_error_action,
                                                       default_error_value, exec_type_onerror)
                    if goto_stepnum in ['ABORT', 'ABORT_AS_ERROR']:
                        break
        elif retry_type is not None:
            if retry_type.upper() == 'IF':
                try:
                    if data_repository[retry_cond] == retry_cond_value:
                        condition_met = True
                        pNote("Wait for {0}sec before retrying".format(retry_interval))
                        pNote("The given condition '{0}' matches the expected "
                              "value '{1}'".format(data_repository[retry_cond], retry_cond_value))
                        time.sleep(int(retry_interval))
                    else:
                        condition_met = False
                        print_warning("The condition value '{0}' does not match with the "
                                      "expected value '{1}'".format(data_repository[retry_cond],
                                                                    retry_cond_value))
                except KeyError:
                    print_warning("The given condition '{0}' do not exists in "
                                  "the data repository".format(retry_cond_value))
                    condition_met = False
                if condition_met == False:
                    goto_stepnum = str(retry_value)
            else:
                if retry_type.upper() == 'IF NOT':
                    try:
                        if data_repository[retry_cond] != retry_cond_value:
                            condition_met = True
                            pNote("Wait for {0}sec before retrying".format(retry_interval))
                            pNote("The condition value '{0}' does not match with the expected "
                                  "value '{1}'".format(data_repository[retry_cond],
                                                       retry_cond_value))
                            time.sleep(int(retry_interval))
                        else:
                            condition_met = False
                    except KeyError:
                        condition_met = False
                        print_warning("The given condition '{0}' is not there in the data repository".format(retry_cond_value))
                    if condition_met == False:
                        pNote("The given condition '{0}' matched with the "
                              "value '{1}'".format(data_repository[retry_cond],
                                                   retry_cond_value))
                        goto_stepnum = str(retry_value)
        else:
            if step_status is False or str(step_status).upper() == "ERROR" \
                    or str(step_status).upper() == "EXCEPTION" or exec_type_onerror is True:
                goto_stepnum = onerror_driver.main(step, default_error_action, default_error_value, exec_type_onerror)
                if goto_stepnum in ['ABORT', 'ABORT_AS_ERROR']:
                    break
                # when 'onError:goto' value is less than the current step num,
                # change the next iteration point to goto value
                elif goto_stepnum and int(goto_stepnum) < step_num:
                    step_num = int(goto_stepnum)-1
                    goto_stepnum = False

    if parallel is True:
        try:
            # put result into multiprocessing queue and later retrieve in corresponding driver
            # parallel testcase sequenial keywords
            queue.put((step_status_list, kw_resultfile_list, system_name, step_impact_list, data_repository['wt_junit_object']))
        except Exception,e:
            print_info(traceback.format_exc())

    else:
        return  step_status_list, kw_resultfile_list, step_impact_list


def main(step_list, data_repository, system_name=None, parallel=False, queue=False):
    """ Executes a testcase """
    steps_execution_status = execute_steps(step_list, data_repository, system_name, parallel, queue)
    return steps_execution_status
