#!/usr/bin/python
"""
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
"""
import traceback
import WarriorCore.step_driver as step_driver
import WarriorCore.onerror_driver as onerror_driver
import WarriorCore.exec_type_driver as exec_type_driver
import Framework.Utils as Utils
from WarriorCore import common_execution_utils
from Framework.Utils.testcase_Utils import pNote
from Framework.Utils.print_Utils import print_info, print_warning, print_error, print_normal
from Framework.Utils.datetime_utils import wait_for_timeout

"""This module is used for sequential execution of testcase steps """


def get_system_console_log(filename, logsdir, console_name):
    """Assign seperate console logfile for each system in parallel execution """

    console_logfile = Utils.file_Utils.getCustomLogFile(filename, logsdir, console_name)
    print_info("************ This is parallel execution... console logs for {0} will be logged "
               "in {1} ************".format(console_name, console_logfile))
    Utils.config_Utils.debug_file(console_logfile)
    return console_logfile


def execute_steps(step_list, data_repository, system_name, parallel, queue, skip_invoked=True, step_num=None):
    """
        Take in a list of steps
        iterate through each of them and decide if each should run (pre-run check)
        get status and report to term and log
    """
    default_error_action = data_repository['wt_def_on_error_action']
    default_error_value = data_repository['wt_def_on_error_value']

    goto_stepnum = False
    kw_resultfile_list = []
    step_status_list = []
    step_impact_list = []

    if parallel is True:
        system_console_log = get_system_console_log(data_repository['wt_filename'],
                                                    data_repository['wt_logsdir'],
                                                    '{0}_consoleLogs'.format(system_name))
    if step_num is None:
        step_num = 0
        while step_num < len(step_list):
            step_num, kw_resultfile_list, data_repository, step_status_list, step_impact_list, \
            goto_stepnum, do_continue = _execute_step(step_list, step_num, goto_stepnum,
                                                      kw_resultfile_list, data_repository,
                                                      default_error_action, default_error_value,
                                                      step_status_list, step_impact_list, system_name,
                                                      parallel, queue, skip_invoked=skip_invoked)
            if do_continue == "break":
                break
    else:
        for _step_num in step_num:
            if 0 <= _step_num < len(step_list):
                _, kw_resultfile_list, data_repository, step_status_list, step_impact_list, \
                goto_stepnum, do_continue = _execute_step(step_list, _step_num, goto_stepnum,
                                                          kw_resultfile_list, data_repository,
                                                          default_error_action, default_error_value,
                                                          step_status_list, step_impact_list,
                                                          system_name,
                                                          parallel, queue, skip_invoked=skip_invoked)
            else:
                print_error("Step number {0} does not exist. Skipping.".format(_step_num+1))

    if parallel is True:
        try:
            # put result into multiprocessing queue and later retrieve in corresponding driver
            # parallel testcase sequenial keywords
            queue.put((step_status_list, kw_resultfile_list, system_name, step_impact_list,
                       data_repository['wt_junit_object']))
        except Exception as e:
            print_error(e)

    else:
        if skip_invoked:
            return step_status_list, kw_resultfile_list, step_impact_list
        else:
            return step_status_list, kw_resultfile_list, step_impact_list, data_repository, do_continue


def _execute_step(step_list, step_num, goto_stepnum, kw_resultfile_list, data_repository,
                  default_error_action, default_error_value, step_status_list, step_impact_list,
                  system_name, parallel, queue, skip_invoked=True):
    """
    This function executes the determined step - step_num (integer index) from the step_list. This
    function is called either from the while loop (normal execution) in function execute_steps() or
    from a for loop (invoked execution)
    """
    step = step_list[step_num]
    # execute steps
    step_num += 1

    run_current_step = False
    # Decide whether or not to execute keyword
    # First decide if this step should be executed in this iteration
    if not goto_stepnum or goto_stepnum == str(step_num):
        # get Exectype information
        run_current_step, trigger_action = exec_type_driver.main(step, skip_invoked=skip_invoked)
        if not run_current_step:
            return _report_step_as_not_run(step, data_repository, system_name, step_num,
                                           kw_resultfile_list, trigger_action, skip_invoked,
                                           step_status_list, step_impact_list, goto_stepnum)

    if not goto_stepnum or goto_stepnum == str(step_num):
        step_status, kw_resultfile, step_impact, goto_stepnum = _execute_step_on_goto(step, step_num, data_repository, system_name)
    else:
        # Skip because of goto
        return _skip_because_of_goto(step, data_repository, system_name, step_num,
                                     kw_resultfile_list,
                                     step_status_list, step_impact_list, goto_stepnum)

    step_status_list.append(step_status)
    kw_resultfile_list.append(kw_resultfile)
    step_impact_list.append(step_impact)
    runmode, value, runmode_timer = common_execution_utils.get_runmode_from_xmlfile(step)
    retry_type, retry_cond, retry_cond_value, retry_value, retry_interval = \
        common_execution_utils.get_retry_from_xmlfile(step)

    if runmode is not None:
        return _execute_runmode_step(runmode_timer, runmode, step_status, value, step,
                                     default_error_action, default_error_value, step_num,
                                     kw_resultfile_list, data_repository, step_status_list,
                                     step_impact_list, goto_stepnum, skip_invoked=skip_invoked)

    elif retry_type is not None:
        return _execute_retry_type_step(retry_type, data_repository, retry_cond, retry_cond_value,
                                        retry_interval, retry_value, step_num, kw_resultfile_list,
                                        step_status_list, step_impact_list, goto_stepnum)
    else:
        return _execute_step_otherwise(step_list, system_name, step_status, step,
                                       default_error_action, default_error_value, step_num,
                                       kw_resultfile_list, data_repository, step_status_list,
                                       step_impact_list, goto_stepnum, parallel, queue, skip_invoked=skip_invoked)


def _report_step_as_not_run(step, data_repository, system_name, step_num, kw_resultfile_list,
                            trigger_action, skip_invoked, step_status_list, step_impact_list, goto_stepnum):
    """
    This function handles reporting of a step as not run.
    """
    keyword = step.get('Keyword')
    kw_resultfile = step_driver.get_keyword_resultfile(data_repository, system_name,
                                                       step_num, keyword)
    Utils.config_Utils.set_resultfile(kw_resultfile)
    Utils.testcase_Utils.pKeyword(keyword, step.get('Driver'))
    Utils.testcase_Utils.reportStatus('Skip')
    kw_resultfile_list.append(kw_resultfile)
    data_repository['wt_junit_object'].update_count("skipped", "1", "tc",
                                                    data_repository['wt_tc_timestamp'])
    data_repository['wt_junit_object'].update_count("keywords", "1", "tc",
                                                    data_repository['wt_tc_timestamp'])
    kw_start_time = Utils.datetime_utils.get_current_timestamp()
    step_impact = Utils.testcase_Utils.get_impact_from_xmlfile(step)
    impact_dict = {"IMPACT": "Impact", "NOIMPACT": "No Impact"}
    data_repository['wt_junit_object'].add_keyword_result(
        data_repository['wt_tc_timestamp'], step_num, keyword,
        "SKIPPED", kw_start_time, "0", "skipped",
        impact_dict.get(step_impact.upper()), "N/A")
    data_repository['step_{}_result'.format(step_num)] = "SKIPPED"

    if trigger_action.upper() in ['ABORT', 'ABORT_AS_ERROR']:
        return step_num, kw_resultfile_list, data_repository, step_status_list, step_impact_list, goto_stepnum, "break"
    elif trigger_action.upper() in ['SKIP', 'NEXT']:
        return step_num, kw_resultfile_list, data_repository, step_status_list, step_impact_list, goto_stepnum, "continue"
    elif trigger_action == "SKIP_INVOKED":
        if skip_invoked:
            print_info("Skipping this step as it is an invoked step.")
            return step_num, kw_resultfile_list, data_repository, step_status_list, step_impact_list, goto_stepnum,"continue"
    # when 'onError:goto' value is less than the current step num,
    # change the next iteration point to goto value
    elif trigger_action and int(trigger_action) < step_num:
        step_num = int(trigger_action) - 1
    return step_num, kw_resultfile_list, data_repository, step_status_list, step_impact_list, goto_stepnum, "continue"


def _execute_step_on_goto(step, step_num, data_repository, system_name):
    """
    This function actually executes a given step and returns necessary details about that step.
    """
    try:
        result = step_driver.main(step, step_num, data_repository, system_name)
        step_status = result[0]
        kw_resultfile = result[1]
        step_impact = result[2]
    except Exception as e:
        print_error('unexpected error %s' % str(e))
        step_status = False
        kw_resultfile = None
        step_impact = Utils.testcase_Utils.get_impact_from_xmlfile(step)
        print_error('unexpected error {0}'.format(traceback.format_exc()))
    goto_stepnum = False
    return step_status, kw_resultfile, step_impact, goto_stepnum


def _skip_because_of_goto(step, data_repository, system_name, step_num, kw_resultfile_list,
                          step_status_list, step_impact_list, goto_stepnum):
    """
    This function would skip step because of goto
    """
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
    data_repository['wt_junit_object']. \
        add_keyword_result(data_repository['wt_tc_timestamp'], step_num, keyword, "SKIPPED",
                           kw_start_time, "0", "skipped",
                           impact_dict.get(step_impact.upper()), "N/A", step_description)
    data_repository['step_{}_result'.format(step_num)] = "SKIPPED"
    return step_num, kw_resultfile_list, data_repository, step_status_list, step_impact_list, goto_stepnum, "continue"


def _execute_runmode_step(runmode_timer, runmode, step_status, value, step, default_error_action,
                          default_error_value, step_num, kw_resultfile_list, data_repository,
                          step_status_list, step_impact_list, goto_stepnum, skip_invoked=True):
    """
    This function will execute a runmode step
    """
    if runmode_timer is not None and \
            any([runmode == "RMT",
                 runmode == "RUF" and step_status is True,
                 runmode == "RUP" and step_status is False]):
        pNote("Wait for {0}sec before the next runmode attempt ".format(runmode_timer))
        wait_for_timeout(runmode_timer)
    # if runmode is 'ruf' & step_status is False, skip the repeated
    # execution of same TC step and move to next actual step
    elif runmode == "RUF" and step_status is False:
        goto_stepnum = str(value)
    # if runmode is 'rup' & step_status is True, skip the repeated
    # execution of same TC step and move to next actual step
    elif runmode == "RUP" and step_status is True:
        goto_stepnum = str(value)
    else:
        if step_status is False or str(step_status).upper() == "ERROR" \
                or str(step_status).upper() == "EXCEPTION":
            goto_stepnum = onerror_driver.main(step, default_error_action,
                                               default_error_value, skip_invoked=skip_invoked)
            if goto_stepnum in ['ABORT', 'ABORT_AS_ERROR']:
                return step_num, kw_resultfile_list, data_repository, step_status_list, step_impact_list, goto_stepnum, "break"
    return step_num, kw_resultfile_list, data_repository, step_status_list, step_impact_list, goto_stepnum, "continue"


def _execute_retry_type_step(retry_type, data_repository, retry_cond, retry_cond_value,
                             retry_interval, retry_value, step_num, kw_resultfile_list,
                             step_status_list, step_impact_list, goto_stepnum):
    """
    This function will execute a retry step

    """
    if retry_type.upper() == 'IF':
        try:
            if data_repository[retry_cond] == retry_cond_value:
                condition_met = True
                pNote("Wait for {0}sec before retrying".format(retry_interval))
                pNote("The given condition '{0}' matches the expected "
                      "value '{1}'".format(data_repository[retry_cond], retry_cond_value))
                wait_for_timeout(retry_interval)
            else:
                condition_met = False
                print_warning("The condition value '{0}' does not match with the "
                              "expected value '{1}'".format(data_repository[retry_cond],
                                                            retry_cond_value))
        except KeyError:
            print_warning("The given condition '{0}' do not exists in "
                          "the data repository".format(retry_cond_value))
            condition_met = False
        if condition_met is False:
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
                    wait_for_timeout(retry_interval)
                else:
                    condition_met = False
            except KeyError:
                condition_met = False
                print_warning(
                    "The given condition '{0}' is not there in the data repository".format(
                        retry_cond_value))
            if not condition_met:
                pNote("The given condition '{0}' matched with the "
                      "value '{1}'".format(data_repository[retry_cond],
                                           retry_cond_value))
                goto_stepnum = str(retry_value)
    return step_num, kw_resultfile_list, data_repository, step_status_list, step_impact_list, goto_stepnum, "continue"


def _execute_step_otherwise(steps_list, system_name, step_status, step, default_error_action,
                            default_error_value, step_num, kw_resultfile_list, data_repository,
                            step_status_list, step_impact_list, goto_stepnum, parallel, queue, skip_invoked=True):
    """

    This function will execute a step's onError functionality
    """
    if step_status is False or str(step_status).upper() == "ERROR" \
            or str(step_status).upper() == "EXCEPTION":
        goto_stepnum = onerror_driver.main(step, default_error_action, default_error_value, skip_invoked=skip_invoked)
        if goto_stepnum in ['ABORT', 'ABORT_AS_ERROR']:
            return step_num, kw_resultfile_list, data_repository, step_status_list, step_impact_list, goto_stepnum, "break"
        elif goto_stepnum is 'RESUME':
            return step_num, kw_resultfile_list, data_repository, step_status_list, step_impact_list, goto_stepnum, "resume"
        # when 'onError:goto' value is less than the current step num,
        # change the next iteration point to goto value
        elif isinstance(goto_stepnum, list):
            print_normal("\n----------------- Starting Invoked Steps Execution -----------------\n")
            temp_step_list = list(steps_list)
            for x in goto_stepnum:
                if 0 <= x < len(steps_list):
                    temp_step_list[x] = steps_list[x]
            temp_status_list, temp_kw_result_list, temp_impact_list, temp_data_repo, do_continue = execute_steps(temp_step_list, data_repository,
                                                                                    system_name, parallel,
                                                                                    queue, skip_invoked=False, step_num=goto_stepnum)
            step_status_list.extend(temp_status_list)
            kw_resultfile_list.extend(temp_kw_result_list)
            step_impact_list.append(temp_impact_list)
            data_repository.update(temp_data_repo)
            goto_stepnum = False
            print_normal("\n----------------- Invoked Steps Execution Finished -----------------\n")
        elif goto_stepnum and int(goto_stepnum) < step_num:
            step_num = int(goto_stepnum) - 1
            goto_stepnum = False
    return step_num, kw_resultfile_list, data_repository, step_status_list, step_impact_list, goto_stepnum, "continue"


def main(step_list, data_repository, system_name=None, parallel=False, queue=False):
    """ Executes a testcase """
    steps_execution_status = execute_steps(step_list, data_repository, system_name, parallel, queue)
    return steps_execution_status
