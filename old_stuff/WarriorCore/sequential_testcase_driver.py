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

"""This is sequential testcase driver which is used to execute
the testcases of a suite in sequential order"""

import os
import time
import traceback
import testcase_driver
import onerror_driver
import Framework.Utils as Utils
from Framework.Utils.testcase_Utils import pNote
from Framework.Utils.print_Utils import print_info, print_error, print_debug, print_warning
from WarriorCore import testsuite_utils, common_execution_utils
import exec_type_driver

def update_suite_attribs(junit_resultfile, errors, skipped,
                         tests, failures, time='0'):
    """Update suite attributes """
    testsuite_utils.pSuite_update_suite_attributes(junit_resultfile, str(errors),
                                                         str(skipped), str(tests), str(failures),
                                                         time)


def execute_sequential_testcases(testcase_list, suite_repository,
                                 data_repository, from_project, auto_defects,
                                 iter_ts_sys, tc_parallel, queue):
    """Executes the testsuite (provided as a xml file)
            - Takes a testsuite xml file as input and sends
            each testcase to Basedriver for execution.
            - Computes the testsuite status based on the testcase_status
            and the impact value of the testcase
            - Handles testcase failures as per the default/specific
            onError action/value
            - Calls the function to report the testsuite status

    Arguments:
    1. testsuite_filepath   = (string) the full path of the testsuite xml file.
    2. Warrior      = (module loader) module loader object to call the Warrior
    3. execution_dir  = (string) the full path of the directory under which
    the testsuite execution directory will be created
    (results for the testsuite will be stored in the  testsuite execution
    directory.)
    """
    goto_tc = False

    junit_resultfile = suite_repository['junit_resultfile']
    suite_name = suite_repository['suite_name']
    testsuite_filepath = suite_repository['testsuite_filepath']
    suite_error_action = suite_repository['def_on_error_action']
    suite_error_value = suite_repository['def_on_error_value']
    testsuite_dir = os.path.dirname(testsuite_filepath)

    errors = 0
    skipped = 0
    failures = 0
    tests = 0
    tc_duration = 0
    tc_status_list = []
    tc_impact_list = []
    impact_dict = {"IMPACT": "Impact", "NOIMPACT": "No Impact"}
    tc_duration_list = []
    tc_junit_list = []

    while tests < len(testcase_list):
        testcase = testcase_list[tests]
        tests += 1

        tc_rel_path = testsuite_utils.get_path_from_xmlfile(testcase)
        if tc_rel_path is not None:
            tc_path = Utils.file_Utils.getAbsPath(tc_rel_path, testsuite_dir)
        else:
            # if tc_rel_path is None, what are we doing here?
            tc_path = str(tc_rel_path)
        print('\n')
        print_debug("<<<< Starting execution of Test case: {0}>>>>".
                    format(tc_path))
        action, tc_status = exec_type_driver.main(testcase)
        tc_runtype = testsuite_utils.get_runtype_from_xmlfile(testcase)
        tc_impact = Utils.testcase_Utils.get_impact_from_xmlfile(testcase)
        tc_context = Utils.testcase_Utils.get_context_from_xmlfile(testcase)
        suite_step_data_file = testsuite_utils.get_data_file_at_suite_step(
                                                testcase, suite_repository)
        tc_onError_action = Utils.xml_Utils.get_attributevalue_from_directchildnode(
                                            testcase, 'onError', 'action')
        tc_onError_action = tc_onError_action if tc_onError_action else suite_error_action
        if suite_step_data_file is not None:
            data_file = Utils.file_Utils.getAbsPath(suite_step_data_file,
                                                    testsuite_dir)
            data_repository[tc_path] = data_file
        data_repository['wt_tc_impact'] = tc_impact
        if testcase.find("runmode") is not None and testcase.find("runmode").get("attempt") is not None:
            print_info("testcase attempt: {0}".format(
                                testcase.find("runmode").get("attempt")))
        if testcase.find("retry") is not None and testcase.find("retry").get("attempt") is not None:
            print_info("testcase attempt: {0}".format(
                                testcase.find("retry").get("attempt")))

        if Utils.file_Utils.fileExists(tc_path):
            tc_name = Utils.file_Utils.getFileName(tc_path)
            testsuite_utils.pSuite_testcase(junit_resultfile, suite_name,
                                            tc_name, time='0')

            if not goto_tc and action is True:
                try:
                    tc_result = testcase_driver.main(tc_path,
                                                     data_repository,
                                                     tc_context,
                                                     runtype=tc_runtype,
                                                     auto_defects=auto_defects,
                                                     suite=suite_name,
                                                     tc_onError_action=tc_onError_action,
                                                     iter_ts_sys=iter_ts_sys)

                    tc_status = tc_result[0]
                    tc_duration = tc_result[1]
                except Exception:
                    print_error('unexpected error {0}'.format(
                                                    traceback.format_exc()))
                    tc_status, tc_duration = False, False
                    tc_impact = Utils.testcase_Utils.get_impact_from_xmlfile(
                                                                    testcase)

            elif goto_tc and goto_tc == str(tests) and action is True:

                try:
                    tc_result= testcase_driver.main(tc_path,
                                                    data_repository,
                                                    tc_context,
                                                    runtype=tc_runtype,
                                                    auto_defects=auto_defects,
                                                    suite=suite_name,
                                                    tc_onError_action=tc_onError_action,
                                                    iter_ts_sys=iter_ts_sys)
                    tc_status = tc_result[0]
                    tc_duration = tc_result[1]
                    goto_tc = False

                except Exception:
                    print_error('unexpected error {0}'.format(
                                                    traceback.format_exc()))
                    tc_status, tc_duration = False, False
                    tc_impact = Utils.testcase_Utils.get_impact_from_xmlfile(
                                                                    testcase)

            else:
                print_info('skipped testcase %s ' % tc_name)
                skipped += 1
                testsuite_utils.pSuite_testcase_skip(junit_resultfile)
                testsuite_utils.pSuite_update_suite_attributes(
                                junit_resultfile, str(errors), str(skipped),
                                str(tests), str(failures), time='0')
                data_repository['wt_junit_object'].update_count(
                                "skipped", "1", "ts",
                                data_repository['wt_ts_timestamp'])
                data_repository['wt_junit_object'].update_count(
                                "tests", "1", "ts",
                                data_repository['wt_ts_timestamp'])
                data_repository['wt_junit_object'].update_count(
                                "tests", "1", "pj", "not applicable")
                tmp_timestamp = str(Utils.datetime_utils.get_current_timestamp())
                time.sleep(2)
                data_repository['wt_junit_object'].create_testcase(
                                location="from testsuite",
                                timestamp=tmp_timestamp,
                                ts_timestamp=data_repository['wt_ts_timestamp'],
                                classname=data_repository['wt_suite_name'],
                                name=os.path.splitext(tc_name)[0])
                data_repository['wt_junit_object'].add_testcase_message(
                                                    tmp_timestamp, "skipped")
                data_repository['wt_junit_object'].update_attr(
                                "status", "SKIPPED", "tc", tmp_timestamp)
                data_repository['testcase_%d_result' % tests] = "SKIP"
                title = Utils.xml_Utils.getChildTextbyParentTag(
                                        tc_path, 'Details', 'Title')
                title = title.strip() if title else "None"
                data_repository['wt_junit_object'].update_attr(
                                "title", title, "tc", tmp_timestamp)
                data_repository['wt_junit_object'].update_attr(
                                "impact", impact_dict.get(tc_impact.upper()),
                                "tc", tmp_timestamp)
                data_repository['wt_junit_object'].update_attr(
                                "onerror", "N/A", "tc", tmp_timestamp)
                data_repository['wt_junit_object'].output_junit(
                                data_repository['wt_results_execdir'],
                                print_summary=False)
                continue

        else:
            errors += 1
            msg = print_error("Test case does not exist in the provided path: "
                              "{0}".format(tc_path))
            testsuite_utils.pSuite_testcase(junit_resultfile, suite_name,
                                            tc_path, time='0')
            testsuite_utils.pSuite_testcase_error(junit_resultfile, msg, '0')
            tc_status = "ERROR"
            if goto_tc and goto_tc == str(tests):
                goto_tc = False
            elif goto_tc and goto_tc != str(tests):
                data_repository['testcase_%d_result' % tests] = "ERROR"
                continue

        goto_tc_num = onerror_driver.main(testcase, suite_error_action,
                                          suite_error_value)
        if goto_tc_num is False:
            onerror = "Next"
        elif goto_tc_num == "ABORT":
            onerror = "Abort"
        else:
            onerror = "Goto:" + str(goto_tc_num)
        data_repository['wt_junit_object'].update_attr(
                        "impact", impact_dict.get(tc_impact.upper()), "tc",
                        data_repository['wt_tc_timestamp'])
        data_repository['wt_junit_object'].update_attr(
                        "onerror", onerror, "tc",
                        data_repository['wt_tc_timestamp'])

        tc_status_list.append(tc_status)
        tc_duration_list.append(tc_duration)

        string_status = {"TRUE": "PASS", "FALSE": "FAIL", "ERROR": "ERROR",
                         "SKIP": "SKIP"}

        if str(tc_status).upper() in string_status.keys():
            data_repository['testcase_%d_result' % tests] = string_status[
                                                    str(tc_status).upper()]
        else:
            print_error("unexpected testcase status, default to exception")
            data_repository['testcase_%d_result' % tests] = "ERROR"

        tc_impact_list.append(tc_impact)
        if tc_impact.upper() == 'IMPACT':
            msg = "Status of the executed test case impacts Testsuite result"
        elif tc_impact.upper() == 'NOIMPACT':
            msg = "Status of the executed test case does not impact "
            "Teststuie result"
        print_debug(msg)

        runmode, value = common_execution_utils.get_runmode_from_xmlfile(
                                                                testcase)
        retry_type, retry_cond, retry_cond_value, retry_value, retry_interval = common_execution_utils.get_retry_from_xmlfile(testcase)
        if runmode is not None:
            if tc_status is True:
                testsuite_utils.update_tc_duration(str(tc_duration))
                # if runmode is 'rup' & tc_status is True, skip the repeated
                # execution of same testcase and move to next actual testcase
                if runmode == "rup":
                    goto_tc = str(value)
            elif tc_status == 'ERROR' or tc_status == 'EXCEPTION':
                errors += 1
                testsuite_utils.pSuite_testcase_error(
                            junit_resultfile,
                            'Encountered error/exception during TC execution',
                            str(tc_duration))
                goto_tc = onerror_driver.main(testcase, suite_error_action,
                                              suite_error_value)
                if goto_tc in ['ABORT', 'ABORT_AS_ERROR']:
                    update_suite_attribs(junit_resultfile, str(errors),
                                         str(skipped), str(tests),
                                         str(failures), time='0')
                    break
                # when 'onError:goto' value is less than the current tc num,
                # change the next iteration point to goto value
                elif goto_tc and int(goto_tc) < tests:
                    tests = int(goto_tc)-1
                    goto_tc = False
            elif tc_status is False:
                failures += 1
                testsuite_utils.pSuite_testcase_failure(junit_resultfile,
                                                        time=str(tc_duration))
                goto_tc = onerror_driver.main(testcase, suite_error_action,
                                              suite_error_value)
                if goto_tc in ['ABORT', 'ABORT_AS_ERROR']:
                    update_suite_attribs(junit_resultfile, str(errors),
                                         str(skipped), str(tests),
                                         str(failures), time='0')
                    break
                # when 'onError:goto' value is less than the current tc num,
                # change the next iteration point to goto value
                elif goto_tc and int(goto_tc) < tests:
                    tests = int(goto_tc)-1
                    goto_tc = False
                # if runmode is 'ruf' & tc_status is False, skip the repeated
                # execution of same testcase and move to next actual testcase
                if not goto_tc and runmode == "ruf":
                    goto_tc = str(value)
        elif retry_type is not None:
            if retry_type.upper() == 'IF':
                try:
                    if data_repository[retry_cond] == retry_cond_value:
                        condition_met = True
                        pNote("Wait for {0}sec before retrying".format(
                                                        retry_interval))
                        pNote("The given condition '{0}' matches the expected "
                              "value '{1}'".format(data_repository[retry_cond],
                                                   retry_cond_value))
                        time.sleep(int(retry_interval))
                    else:
                        condition_met = False
                        print_warning("The condition value '{0}' does not "
                                      "match with the expected value "
                                      "'{1}'".format(
                                        data_repository[retry_cond],
                                        retry_cond_value))
                except KeyError:
                    print_warning("The given condition '{0}' is not there in "
                                  "the data repository".format(
                                                    retry_cond_value))
                    condition_met = False
                if condition_met is False:
                    goto_tc = str(retry_value)
            else:
                if retry_type.upper() == 'IF NOT':
                    try:
                        if data_repository[retry_cond] != retry_cond_value:
                            condition_met = True
                            pNote("Wait for {0}sec before retrying".format(
                                                            retry_interval))
                            pNote("The condition value '{0}' does not match "
                                  "with the expected value "
                                  "'{1}'".format(data_repository[retry_cond],
                                                 retry_cond_value))
                            time.sleep(int(retry_interval))
                        else:
                            condition_met = False
                            print_warning("The given condition '{0}' matches "
                                          "the expected value "
                                          "'{1}'".format(
                                                data_repository[retry_cond],
                                                retry_cond_value))
                    except KeyError:
                        condition_met = False
                        print_warning("The given condition '{0}' is not there "
                                      "in the data repository".format(
                                                            retry_cond_value))
                    if condition_met is False:
                        pNote("The given condition '{0}' matched with the "
                              "value '{1}'".format(data_repository[retry_cond],
                                                   retry_cond_value))
                        goto_tc = str(retry_value)
# suite_status = testsuite_utils.compute_testsuite_status(suite_status,
# tc_status, tc_impact)
        update_suite_attribs(junit_resultfile, str(errors),
                             str(skipped), str(tests), str(failures),
                             time='0')
        tc_junit_list.append(data_repository['wt_junit_object'])

    suite_status = Utils.testcase_Utils.compute_status_using_impact(
                                        tc_status_list, tc_impact_list)

    if tc_parallel:
        tc_impact = data_repository['wt_tc_impact']
        if tc_impact.upper() == 'IMPACT':
            msg = "Status of the executed test case impacts Testsuite result"
        elif tc_impact.upper() == 'NOIMPACT':
            msg = "Status of the executed test case does not impact Teststuie result"
        print_debug(msg)
        tc_name = Utils.file_Utils.getFileName(tc_path)
        # put result into multiprocessing queue and later retrieve in
        # corresponding driver
        queue.put((tc_status_list, tc_name, tc_impact_list, tc_duration_list,
                   tc_junit_list))
    return suite_status

def main(testcase_list, suite_repository,
         data_repository, from_project, auto_defects, iter_ts_sys=None, tc_parallel=False, queue=False):
    """Executes testcases in a testsuite sequentially """
    try:
        testsuite_status = execute_sequential_testcases(testcase_list, suite_repository,
                                                        data_repository,
                                                        from_project, auto_defects, iter_ts_sys, tc_parallel, queue)
    except Exception:
        testsuite_status = False
        print_error('unexpected error {0}'.format(traceback.format_exc()))
    return testsuite_status
