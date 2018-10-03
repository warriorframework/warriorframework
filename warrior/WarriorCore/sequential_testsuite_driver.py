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

# !/usr/bin/python

import os
import time
import traceback

from Framework import Utils
from WarriorCore import testsuite_utils, common_execution_utils
from Framework.Utils.print_Utils import print_info, print_error, print_debug, print_warning
from WarriorCore import exec_type_driver
import WarriorCore.testsuite_driver as testsuite_driver
import WarriorCore.onerror_driver as onerror_driver
from Framework.Utils.testcase_Utils import pNote

"""This is sequential suite driver which is used to execute
the suites of a project in sequential order"""


def execute_sequential_testsuites(testsuite_list, project_repository,
                                  data_repository, auto_defects):
    """ Executes suites in a project sequentially """

    suite_cntr = 0
    goto_testsuite = False
    ts_status_list = []
    ts_impact_list = []
    impact_dict = {"IMPACT": "Impact", "NOIMPACT": "No Impact"}

    project_error_action = project_repository['def_on_error_action']
    project_filepath = project_repository['project_filepath']
    project_dir = os.path.dirname(project_filepath)
    wp_results_execdir = project_repository['wp_results_execdir']
    wp_logs_execdir = project_repository['wp_logs_execdir']
    project_error_value = project_repository['def_on_error_value']
    data_repository['wt_ts_timestamp'] = None
    jiraproj = data_repository['jiraproj']
    pj_junit_object = data_repository['wt_junit_object']

    while suite_cntr < len(testsuite_list):
        testsuite = testsuite_list[suite_cntr]
        suite_cntr += 1

        testsuite_rel_path = testsuite_utils.get_path_from_xmlfile(testsuite)
        if testsuite_rel_path is not None:
            testsuite_path = Utils.file_Utils.getAbsPath(testsuite_rel_path,
                                                         project_dir)
        else:
            testsuite_path = str(testsuite_rel_path)
        print_info("\n")
        print_debug("<<<< Starting execution of Test suite: {0}>>>>".format(testsuite_path))
        action, testsuite_status = exec_type_driver.main(testsuite)
        testsuite_impact = Utils.testcase_Utils.get_impact_from_xmlfile(testsuite)
        testsuite_name = Utils.file_Utils.getFileName(testsuite_path)
        testsuite_nameonly = Utils.file_Utils.getNameOnly(testsuite_name)
        ts_onError_action = Utils.xml_Utils.get_attributevalue_from_directchildnode(testsuite,
                                                                                    'onError',
                                                                                    'action')
        ts_onError_action = ts_onError_action if ts_onError_action else project_error_action
        if testsuite.find("runmode") is not None and \
           testsuite.find("runmode").get("attempt") is not None:
                # condition to print the start of runmode execution
                if testsuite.find("runmode").get("attempt") == 1:
                    print_info("\n----------------- Start of Testsuite Runmode Execution"
                               " -----------------\n")
                print_info("RUNMODE ATTEMPT: {0}"
                           .format(testsuite.find("runmode").get("attempt")))
        if Utils.file_Utils.fileExists(testsuite_path) or action is False:
            if not goto_testsuite and action is True:

                testsuite_result = testsuite_driver.main(testsuite_path,
                                                         data_repository=data_repository,
                                                         from_project=True,
                                                         auto_defects=auto_defects,
                                                         jiraproj=jiraproj,
                                                         res_startdir=wp_results_execdir,
                                                         logs_startdir=wp_logs_execdir,
                                                         ts_onError_action=ts_onError_action)
                testsuite_status = testsuite_result[0]

            elif goto_testsuite and goto_testsuite == str(suite_cntr)\
                    and action is True:
                testsuite_result = testsuite_driver.main(testsuite_path,
                                                         data_repository=data_repository,
                                                         from_project=True,
                                                         auto_defects=auto_defects,
                                                         jiraproj=jiraproj,
                                                         res_startdir=wp_results_execdir,
                                                         logs_startdir=wp_logs_execdir,
                                                         ts_onError_action=ts_onError_action)
                goto_testsuite = False
                testsuite_status = testsuite_result[0]

            else:
                msg = print_info('skipped testsuite: {0} '.format(testsuite_path))
                tmp_timestamp = str(Utils.datetime_utils.get_current_timestamp())
                time.sleep(2)
                pj_junit_object.create_testsuite(
                    location=os.path.dirname(testsuite_path),
                    name=testsuite_nameonly, timestamp=tmp_timestamp,
                    **pj_junit_object.init_arg())
                pj_junit_object.update_attr("status", "SKIPPED", "ts", tmp_timestamp)
                pj_junit_object.update_attr("skipped", "1", "pj", tmp_timestamp)
                pj_junit_object.update_count("suites", "1", "pj", tmp_timestamp)
                data_repository['testsuite_{}_result'.format(suite_cntr)] = "SKIP"
                pj_junit_object.update_attr("impact", impact_dict.get(testsuite_impact.upper()),
                                            "ts", tmp_timestamp)
                pj_junit_object.update_attr("onerror", "N/A", "ts", tmp_timestamp)
                pj_junit_object.output_junit(wp_results_execdir, print_summary=False)
                continue

        else:

            msg = print_error("Test suite does not exist in "
                              "provided path: {0}".format(testsuite_path))
            testsuite_status = 'ERROR'
            if goto_testsuite and goto_testsuite == str(suite_cntr):
                goto_testsuite = False
            elif goto_testsuite and goto_testsuite != str(suite_cntr):
                data_repository['testsuite_{}_result'.format(suite_cntr)] = "ERROR"
                continue

        goto_testsuite_num = onerror_driver.main(testsuite,
                                                 project_error_action,
                                                 project_error_value)
        if goto_testsuite_num is False:
            onerror = "Next"
        elif goto_testsuite_num == "ABORT":
            onerror = "Abort"
        else:
            onerror = "Goto:" + str(goto_testsuite_num)
        pj_junit_object.update_attr("impact", impact_dict.
                                    get(testsuite_impact.upper()), "ts",
                                    data_repository['wt_ts_timestamp'])
        pj_junit_object.update_attr("onerror", onerror, "ts",
                                    data_repository['wt_ts_timestamp'])

        string_status = {"TRUE": "PASS", "FALSE": "FAIL", "ERROR": "ERROR",
                         "SKIP": "SKIP", "RAN": "RAN"}

        if str(testsuite_status).upper() in string_status.keys():
            data_repository['testsuite_{}_result'.format(suite_cntr)] = \
             string_status[str(testsuite_status).upper()]
        else:
            print_error("unexpected testsuite status, default to exception")
            data_repository['testsuite_%d_result' % suite_cntr] = "ERROR"

        ts_status_list, ts_impact_list = \
            common_execution_utils.compute_status(testsuite, ts_status_list,
                                                  ts_impact_list,
                                                  testsuite_status, testsuite_impact)
        if testsuite_impact.upper() == 'IMPACT':
            msg = "Status of the executed test suite impacts Project result"
        elif testsuite_impact.upper() == 'NOIMPACT':
            msg = "Status of the executed test suite does not impact project result"
        print_debug(msg)

        runmode, value, _ = common_execution_utils.get_runmode_from_xmlfile(testsuite)
        retry_type, retry_cond, retry_cond_value, retry_value,\
            retry_interval = common_execution_utils.get_retry_from_xmlfile(testsuite)
        if runmode is not None:
            # if runmode is 'ruf' & step_status is False, skip the repeated
            # execution of same TC step and move to next actual step
            if not project_error_value and runmode.upper() == "RUF" and\
                    testsuite_status is False:
                goto_testsuite = str(value)
            # if runmode is 'rup' & step_status is True, skip the repeated
            # execution of same TC step and move to next actual step
            elif runmode.upper() == "RUP" and testsuite_status is True:
                goto_testsuite = str(value)
        elif retry_type is not None:
            if testsuite.find("retry") is not None and\
              testsuite.find("retry").get("attempt") is not None:
                print_info("RETRY ATTEMPT: {0}"
                           .format(testsuite.find("retry").get("attempt")))
            if retry_type.upper() == 'IF':
                try:
                    if data_repository[retry_cond] == retry_cond_value:
                        condition_met = True
                        pNote("Wait for {0}sec before retrying".format(retry_interval))
                        pNote("The given condition '{0}' matches the expected"
                              "value '{1}'".format(data_repository[retry_cond],
                                                   retry_cond_value))
                        time.sleep(int(retry_interval))
                    else:
                        condition_met = False
                        print_warning("The condition value '{0}' does not match with the expected "
                                      "value '{1}'".format(data_repository[retry_cond],
                                                           retry_cond_value))
                except KeyError:
                    print_warning("The given condition '{0}' do not exists in "
                                  "the data repository".format(retry_cond_value))

                    condition_met = False
                if condition_met is False:
                    goto_testsuite = str(retry_value)
            else:
                if retry_type.upper() == 'IF NOT':
                    try:
                        if data_repository[retry_cond] != retry_cond_value:
                            condition_met = True
                            pNote("Wait for {0}sec before "
                                  "retrying".format(retry_interval))
                            pNote("The condition value '{0}' does not match "
                                  "with the expected value '{1}'".format(data_repository[retry_cond],
                                                                         retry_cond_value))
                            time.sleep(int(retry_interval))
                        else:
                            condition_met = False
                    except KeyError:
                        condition_met = False
                        print_warning("The given condition '{0}' is not there "
                                      "in the data repository".format(retry_cond_value))
                    if condition_met is False:
                        pNote("The given condition '{0}' matched with the "
                              "value '{1}'".format(data_repository[retry_cond],
                                                   retry_cond_value))
                        goto_testsuite = str(retry_value)
        else:
            if testsuite_status is False or testsuite_status == "ERROR" or\
                    testsuite_status == "EXCEPTION":
                goto_testsuite = onerror_driver.main(testsuite, project_error_action,
                                                     project_error_value)
            if goto_testsuite in ['ABORT', 'ABORT_AS_ERROR']:
                break
            # when 'onError:goto' value is less than the current ts num,
            # change the next iteration point to goto value
            elif goto_testsuite and int(goto_testsuite) < suite_cntr:
                suite_cntr = int(goto_testsuite)-1
                goto_testsuite = False
    # print the end of runmode execution as the steps skip when the condition
    # is met for RUF/RUP or when all the attempts finish
    if testsuite.find("runmode") is not None and \
       testsuite.find("runmode").get("attempt") is not None:
        if testsuite.find("runmode").get("attempt") == \
           testsuite.find("runmode").get("runmode_val"):
            print_info("\n----------------- End of Testsuite Runmode Execution"
                       " -----------------\n")
    project_status = Utils.testcase_Utils.compute_status_using_impact(ts_status_list,
                                                                      ts_impact_list)

    return project_status


def main(testsuite_list, project_repository, data_repository={}, auto_defects=False):
    """ Executes suites in a project sequentially """

    try:
        project_status = execute_sequential_testsuites(testsuite_list, project_repository,
                                                       data_repository, auto_defects)
    except Exception:
        project_status = False
        print_error('unexpected error {0}'.format(traceback.format_exc()))
    return project_status
