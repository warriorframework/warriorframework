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
import sys
import os
import time
import traceback
import shutil
import sequential_testcase_driver
import parallel_testcase_driver
import testcase_driver
from WarriorCore.Classes import execution_files_class, junit_class
from WarriorCore.Classes.iterative_testsuite_class import IterativeTestsuite
from WarriorCore import testsuite_utils, common_execution_utils
import Framework.Utils as Utils
from Framework.Utils.print_Utils import print_info, print_debug, print_warning, print_error
"""Test suite driver module to execute a collection of testcases """

#===============================================================================
# Import all the necessary packages, libraries
# Utils     = package containing all utility files
# Actions   = package containing all Actions files
#===============================================================================


def initialize_suite_fields(data_repository):
    """Initializing suite fields in data_repository so that it does not get
    carried over to next suites. The following suite fields has to be taken
    fresh for each test suite
    wt_suite_execution_dir - for putting the results
    suite_data_file - data file for this suite
    wt_suite_name - name of this suite
    suite_exectype - exectype for this suite
    """
    print_info("initializing suite fields in data_repository")
    suite_fields_to_initialize = ['wt_suite_execution_dir', 'suite_data_file',
                                  'wt_suite_name', 'suite_exectype']
    for suite_field in suite_fields_to_initialize:
        if suite_field in data_repository:
            del data_repository[suite_field]


def get_suite_details(testsuite_filepath, data_repository, from_project,
                      res_startdir, logs_startdir):
    """Gets all the details of the Testsuite from its xml file
    Details that are currently obtained are:
        1. Name,
        2. default_onError action,
        3. default_onError value

    Arguments:
        filepath    = full path of the Testsuite xml file

    """
    suite_repository = {}
    suite_name = Utils.xml_Utils.getChildTextbyParentTag(testsuite_filepath, 'Details', 'Name')
    suite_title = Utils.xml_Utils.getChildTextbyParentTag(testsuite_filepath, 'Details', 'Title')
    suite_exectype = testsuite_utils.get_exectype_from_xmlfile(testsuite_filepath)
    def_on_error_action = Utils.testcase_Utils.get_defonerror_fromxml_file(testsuite_filepath)
    def_on_error_value = Utils.xml_Utils.getChildAttributebyParentTag(testsuite_filepath,
                                                                      'Details',
                                                                      'default_onError', 'value')
    filename = os.path.basename(testsuite_filepath)
    nameonly = Utils.file_Utils.getNameOnly(filename)
    operating_system = sys.platform

    if suite_name is None or suite_name is False:
        suite_name = nameonly
    else:
        suite_name = suite_name.strip()
        if suite_name != nameonly:
            print_warning("<Name> tag in xml file should match the filename")
            suite_name = nameonly

    if suite_title is None or suite_title is False:
        print_warning("title is missing, please provide a title for the testsuite")
        suite_title = "None"
    else:
        suite_title = str(suite_title).strip()

    if def_on_error_value is None or def_on_error_value is False:
        def_on_error_value = None

    if 'ow_resultdir' in data_repository and not from_project:
        res_startdir = data_repository['ow_resultdir']
    if 'ow_logdir' in data_repository and not from_project:
        logs_startdir = data_repository['ow_logdir']

    efile_obj = execution_files_class.ExecFilesClass(testsuite_filepath, "ts",
                                                     res_startdir, logs_startdir)
    # First priority is given for data files specified via CLI
    # Default datafiles: Given in the test suite globally.
    # If no datafiles are specified at CLI or global level, error is thrown.
    # At Suite level execution, step-wise datafiles are not considered.
    if data_repository.has_key('ow_datafile'):
        data_file = data_repository['ow_datafile']
    else:
        data_file = efile_obj.get_data_files()[0]
    suite_resultfile = efile_obj.resultfile
    suite_execution_dir = os.path.dirname(suite_resultfile)
    junit_resultfile = (Utils.file_Utils.getNameOnly(suite_resultfile) +
                        "_tsjunit.xml")
    ws_results_execdir = efile_obj.results_execdir
    ws_logs_execdir = efile_obj.logs_execdir

    Utils.config_Utils.junit_file(junit_resultfile)

    suite_repository['suite_name'] = suite_name
    suite_repository['testsuite_filepath'] = testsuite_filepath
    suite_repository['operating_system'] = operating_system
    suite_repository['suite_title'] = suite_title
    suite_repository['suite_exectype'] = suite_exectype
    suite_repository['def_on_error_action'] = def_on_error_action
    suite_repository['def_on_error_value'] = def_on_error_value
    suite_repository['suite_execution_dir'] = suite_execution_dir
    suite_repository['suite_resultfile'] = suite_resultfile
    suite_repository['junit_resultfile'] = junit_resultfile
    suite_repository['ws_results_execdir'] = ws_results_execdir
    suite_repository['ws_logs_execdir'] = ws_logs_execdir
    if data_file is not False:
        suite_repository['data_file'] = data_file

    # copying testsuite xml file to execution directory of this testsuite
    shutil.copy2(testsuite_filepath, suite_execution_dir)

    return suite_repository


def report_suite_requirements(suite_repository, testsuite_filepath):
    """Reports the requirements of the testsuite to the result file """
    req_id_list = Utils.testcase_Utils.get_requirement_id_list(testsuite_filepath)
    ts_junit_object = suite_repository["wt_junit_object"]
    if req_id_list is not None:
        for req_id in req_id_list:
            ts_junit_object.add_requirement(req_id, suite_repository["wt_ts_timestamp"])


def report_testsuite_result(suite_repository, suite_status):
    """Reports the result of the testsuite executed
    Arguments:
    1. suite_repository    = (dict) dictionary caontaining all the data related to the testsuite
    2. suite_status        = (bool) status of the testsuite executed
    """
    suite_resultfile = suite_repository['junit_resultfile']

    print_info("\n ****** TestSuite Result ******")
    suite_status = {'TRUE': 'PASS', 'FALSE': 'FAIL', 'EXCEPTION': 'FAIL',
                    'ERROR': 'FAIL'}.get(str(suite_status).upper())
    print_info("Testsuite:{0}  STATUS:{1}".format(suite_repository['suite_name'], suite_status))
    testsuite_utils.pSuite_report_suite_result(suite_resultfile)
    print_info("\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ END OF TEST SUITE $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    return suite_status


def print_suite_details_to_console(suite_repository, testsuite_filepath, junit_resultfile):
    """Prints the testsuite details to console """

    print_info("\n\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$  TESTSUITE-DETAILS  $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n")

    print_info("Executing testsuite '{0}'".format(suite_repository['suite_name'].strip()))
    print_info("Title: {0}".format(suite_repository['suite_title'].strip()))
    print_info("Results directory: %s" % suite_repository['suite_execution_dir'])
    report_suite_requirements(suite_repository, testsuite_filepath)
    time.sleep(3)

#get the details of testwrapperfile, data_type, runtype from test suite xml
def get_testwrapper_file_details(testsuite_filepath, data_repository):
    """retuns testwrapperfile to use if specified, else returns False"""
    if data_repository.has_key('ow_testwrapperfile'):
        testwrapperfile = data_repository['ow_testwrapperfile']
    else:
        if Utils.xml_Utils.nodeExists(testsuite_filepath, "TestWrapperFile"):
            testwrapperfile = Utils.xml_Utils.getChildTextbyParentTag\
                (testsuite_filepath, 'Details', 'TestWrapperFile')
        else:
            return [False, False, False, 'abort']
    abs_cur_dir = os.path.dirname(testsuite_filepath)
    abs_testwrapperfile = Utils.file_Utils.getAbsPath(testwrapperfile, abs_cur_dir)
    Utils.xml_Utils.getRoot(abs_testwrapperfile)
    jfile_obj = execution_files_class.ExecFilesClass(abs_testwrapperfile, "ts", None, None)
    if not data_repository.get('suite_data_file', False):
        print_error("Input data file must be specified in test suite global details section")
        exit(0)
    j_data_type = jfile_obj.check_get_datatype(data_repository['suite_data_file'])
    j_runtype = jfile_obj.check_get_runtype()
    setup_on_error_action = Utils.testcase_Utils.get_setup_on_error(abs_testwrapperfile)
    return [abs_testwrapperfile, j_data_type, j_runtype, setup_on_error_action]

def execute_testsuite(testsuite_filepath, data_repository, from_project,
                      auto_defects, jiraproj, res_startdir, logs_startdir,
                      ts_onError_action, queue, ts_parallel):
    """Executes the testsuite (provided as a xml file)
            - Takes a testsuite xml file as input and
            sends each testcase to Basedriver for execution.
            - Computes the testsuite status based on the
            testcase_status and the impact value of the testcase
            - Handles testcase failures as per the default/specific onError action/value
            - Calls the function to report the testsuite status

    Arguments:
    1. testsuite_filepath   = (string) the full path of the testsuite xml file.
    2. Warrior          = (module loader) module loader object to call the Warrior
    3. execution_dir        = (string) the full path of the directory under which the testsuite
                              execution directory will be created (results for the testsuite will
                              be stored in the  testsuite execution directory.)
    """
    testsuite_status_list = []
    suite_start_time = Utils.datetime_utils.get_current_timestamp()
    print_info("[{0}] Testsuite execution starts".format(suite_start_time))
    initialize_suite_fields(data_repository)
    suite_repository = get_suite_details(testsuite_filepath, data_repository,
                                         from_project, res_startdir, logs_startdir)
    testcase_list = common_execution_utils.get_step_list(testsuite_filepath,
                                                         "Testcases", "Testcase")
    execution_type = suite_repository['suite_exectype'].upper()
    no_of_tests = str(len(testcase_list))

    junit_resultfile = suite_repository['junit_resultfile']
    suite_name = suite_repository['suite_name']
    suite_execution_dir = suite_repository['suite_execution_dir']

    data_repository['wt_suite_execution_dir'] = suite_execution_dir
    data_repository['wt_results_execdir'] = suite_repository['ws_results_execdir']
    data_repository['wt_logs_execdir'] = suite_repository['ws_logs_execdir']
    data_repository['wt_suite_name'] = suite_name

    suite_timestamp = testsuite_utils.get_suite_timestamp()
    data_repository['wt_ts_timestamp'] = suite_timestamp
    suite_repository['wt_ts_timestamp'] = suite_timestamp

    data_repository["suite_exectype"] = "iterative" if execution_type == "ITERATIVE_SEQUENTIAL" or \
    execution_type == "ITERATIVE_PARALLEL" else execution_type

    ts_junit_display = "True"
    pj_junit_display = "False"
    if "wt_junit_object" in data_repository:
        ts_junit_object = data_repository["wt_junit_object"]

    else:
        ts_junit_object = junit_class.Junit(filename=suite_name, timestamp=suite_timestamp,
                                            name="customProject_independant_testcase_execution",
                                            display=pj_junit_display)

        if "jobid" in data_repository:
            ts_junit_object.add_jobid(data_repository["jobid"])
            del data_repository["jobid"]
        data_repository["wt_junit_object"] = ts_junit_object
    suite_repository["wt_junit_object"] = ts_junit_object
    ts_junit_object.create_testsuite(location=os.path.dirname(testsuite_filepath),
                                     name=suite_name, timestamp=suite_timestamp,
                                     suite_location=suite_repository['testsuite_filepath'],
                                     title=suite_repository['suite_title'],
                                     display=ts_junit_display,
                                     **ts_junit_object.init_arg())

    # Adding resultsdir as attributes to testsuite_tag in the junit result file
    # Need to remove these after making resultsdir, logsdir as part of properties tag in testcase
    ts_junit_object.update_attr("resultsdir", suite_repository['suite_execution_dir'],
                                "ts", suite_timestamp)
    ts_junit_object.add_property("resultsdir", suite_repository['suite_execution_dir'],
                                 "ts", suite_timestamp)

    if suite_repository.has_key("data_file"):
        data_repository['suite_data_file'] = suite_repository['data_file']

    # jiraproj name
    data_repository['jiraproj'] = jiraproj

    # if not from_project:
    testsuite_utils.pSuite_root(junit_resultfile)

    testsuite_utils.pSuite_testsuite(junit_resultfile, suite_name,
                                     errors='0', skipped='0',
                                     tests=no_of_tests, failures='0',
                                     time='0', timestamp=suite_timestamp)
    testsuite_utils.pSuite_property(junit_resultfile, 'title', suite_repository['suite_title'])
    testsuite_utils.pSuite_property(junit_resultfile, 'location', testsuite_filepath)
    if "jobid" in data_repository:
        testsuite_utils.pSuite_property(junit_resultfile, 'resultlocation',
                                        data_repository["jobid"])
        # del data_repository["jobid"]

    print_suite_details_to_console(suite_repository, testsuite_filepath, junit_resultfile)

    # Prints the path of result summary file at the beginning of execution
    if data_repository['war_file_type'] == "Suite":
        filename = os.path.basename(testsuite_filepath)
        html_filepath = os.path.join(suite_repository['suite_execution_dir'],
                                     Utils.file_Utils.getNameOnly(filename))+'.html'
        print_info("HTML result file: {0}".format(html_filepath))
    if not from_project:
        data_repository["war_parallel"] = False

    root = Utils.xml_Utils.getRoot(testsuite_filepath)
    suite_global_xml = root.find('Details')
    runmode, value, _ = common_execution_utils.get_runmode_from_xmlfile(suite_global_xml)

    #get testwrapperfile details
    testwrapperfile, j_data_type, j_runtype, setup_on_error_action = \
        get_testwrapper_file_details(testsuite_filepath, data_repository)
    setup_tc_status, cleanup_tc_status = True, True
    #execute setup steps defined in testwrapper file if testwrapperfile is present
    if testwrapperfile:
        print_info("*****************TESTWRAPPER SETUP EXECUTION START*********************")
        data_repository['suite_testwrapper_file'] = testwrapperfile
        data_repository['wt_data_type'] = j_data_type
        setup_tc_status, data_repository = testcase_driver.execute_testcase(testwrapperfile,\
                                            data_repository, tc_context='POSITIVE',\
                                            runtype=j_runtype,\
                                            tc_parallel=None, queue=None,\
                                            auto_defects=auto_defects, suite=None,\
                                            jiraproj=None, tc_onError_action='ABORT_AS_ERROR',\
                                            iter_ts_sys=None, steps_tag='Setup')
        print_info("*****************TESTWRAPPER SETUP EXECUTION END**********************")
    if setup_on_error_action == 'next' or \
        (setup_on_error_action == 'abort' and setup_tc_status == True):
        if execution_type.upper() == 'PARALLEL_TESTCASES':
            ts_junit_object.remove_html_obj()
            data_repository["war_parallel"] = True
            print_info("Executing testcases in parallel")
            test_suite_status = parallel_testcase_driver.main(testcase_list, suite_repository,
                                                              data_repository, from_project,
                                                              tc_parallel=True,
                                                              auto_defects=auto_defects)

        elif execution_type.upper() == 'SEQUENTIAL_TESTCASES':
            if runmode is None:
                print_info("Executing testcases sequentially")
                test_suite_status = sequential_testcase_driver.main(testcase_list, suite_repository,
                                                                    data_repository, from_project,
                                                                    auto_defects=auto_defects)

            elif runmode.upper() == "RUF":
                print_info("Execution type: {0}, Attempts: {1}".format(runmode, value))
                i = 0
                while i < int(value):
                    i += 1
                    print_debug("\n\n<======= ATTEMPT: {0} ======>".format(i))
                    test_suite_status = sequential_testcase_driver.main(testcase_list,
                                                                        suite_repository,
                                                                        data_repository,
                                                                        from_project,
                                                                        auto_defects=auto_defects)
                    test_count = i * len(testcase_list)
                    testsuite_status_list.append(test_suite_status)
                    testsuite_utils.pSuite_update_suite_tests(str(test_count))
                    if str(test_suite_status).upper() == "FALSE" or\
                       str(test_suite_status).upper() == "ERROR":
                        break

            elif runmode.upper() == "RUP":
                print_info("Execution type: {0}, Attempts: {1}".format(runmode, value))
                i = 0
                while i < int(value):
                    i += 1
                    print_debug("\n\n<======= ATTEMPT: {0} ======>".format(i))
                    test_suite_status = sequential_testcase_driver.main(testcase_list,
                                                                        suite_repository,
                                                                        data_repository,
                                                                        from_project,
                                                                        auto_defects=auto_defects)
                    test_count = i * len(testcase_list)
                    testsuite_status_list.append(test_suite_status)
                    testsuite_utils.pSuite_update_suite_tests(str(test_count))
                    if str(test_suite_status).upper() == "TRUE":
                        break

            elif runmode.upper() == "RMT":
                print_info("Execution type: {0}, Attempts: {1}".format(runmode, value))
                i = 0
                while i < int(value):
                    i += 1
                    print_debug("\n\n<======= ATTEMPT: {0} ======>".format(i))
                    # We aren't actually summing each test result here...
                    test_suite_status = sequential_testcase_driver.main(testcase_list,
                                                                        suite_repository,
                                                                        data_repository,
                                                                        from_project,
                                                                        auto_defects=auto_defects)
                    testsuite_status_list.append(test_suite_status)
        # The below runmode part is not modified/removed to preserve backward compatibility
        elif execution_type.upper() == 'RUN_UNTIL_FAIL' and runmode is None:
            execution_value = Utils.xml_Utils.getChildAttributebyParentTag(testsuite_filepath,
                                                                           'Details',
                                                                           'type', 'Max_Attempts')
            execution_value = 1 if execution_value == "" else execution_value
            print_info("Execution type: {0}, Attempts: {1}".format(execution_type, execution_value))
            i = 0
            while i < int(execution_value):
                i += 1
                print_debug("\n\n<======= ATTEMPT: {0} ======>".format(i))
                test_suite_status = sequential_testcase_driver.main(testcase_list, suite_repository,
                                                                    data_repository, from_project,
                                                                    auto_defects=auto_defects)
                test_count = i * len(testcase_list)
                testsuite_utils.pSuite_update_suite_tests(str(test_count))
                if str(test_suite_status).upper() == "FALSE" or\
                   str(test_suite_status).upper() == "ERROR":
                    break

        elif execution_type.upper() == 'RUN_UNTIL_PASS' and runmode is None:
            execution_value = Utils.xml_Utils.getChildAttributebyParentTag(testsuite_filepath,
                                                                           'Details',
                                                                           'type', 'Max_Attempts')
            execution_value = 1 if execution_value == "" else execution_value
            print_info("Execution type: {0}, Attempts: {1}".format(execution_type, execution_value))
            i = 0
            while i < int(execution_value):
                i += 1
                print_debug("\n\n<======= ATTEMPT: {0} ======>".format(i))
                test_suite_status = sequential_testcase_driver.main(testcase_list, suite_repository,
                                                                    data_repository, from_project,
                                                                    auto_defects=auto_defects)
                test_count = i * len(testcase_list)
                testsuite_utils.pSuite_update_suite_tests(str(test_count))
                if str(test_suite_status).upper() == "TRUE":
                    break

        elif execution_type.upper() == 'RUN_MULTIPLE' and runmode is None:
            execution_value = Utils.xml_Utils.getChildAttributebyParentTag(testsuite_filepath,
                                                                           'Details', 'type',
                                                                           'Number_Attempts')
            execution_value = 1 if execution_value == "" else execution_value
            print_info("Execution type: {0}, Attempts: {1}".format(execution_type, execution_value))

            i = 0
            while i < int(execution_value):
                i += 1
                print_debug("\n\n<======= ATTEMPT: {0} ======>".format(i))
                # We aren't actually summing each test result here...
                test_suite_status = sequential_testcase_driver.main(testcase_list, suite_repository,
                                                                    data_repository, from_project,
                                                                    auto_defects=auto_defects)

        elif execution_type.upper() == "ITERATIVE_SEQUENTIAL":
            # if execution type is iterative sequential call WarriorCore.Classes.iterative_testsuite
            # class and execute the testcases in iterative sequential fashion on the systems
            print_info("Iterative sequential suite")

            iter_seq_ts_obj = IterativeTestsuite(testcase_list, suite_repository,
                                                 data_repository, from_project,
                                                 auto_defects)
            test_suite_status = iter_seq_ts_obj.execute_iterative_sequential()

        elif execution_type.upper() == "ITERATIVE_PARALLEL":
            # if execution type is iterative parallel call WarriorCore.Classes.iterative_testsuite
            # class and execute the testcases in iterative parallel fashion on the systems
            ts_junit_object.remove_html_obj()
            print_info("Iterative parallel suite")
            data_repository["war_parallel"] = True
            iter_seq_ts_obj = IterativeTestsuite(testcase_list, suite_repository,
                                                 data_repository, from_project, auto_defects)

            test_suite_status = iter_seq_ts_obj.execute_iterative_parallel()

        else:
            print_error("unexpected suite_type received...aborting execution")
            test_suite_status = False

        if runmode is not None:
            test_suite_status = common_execution_utils.compute_runmode_status(testsuite_status_list,
                                                                              runmode,
                                                                              suite_global_xml)
    else:
        print_error("Test cases in suite are not executed as setup failed to execute,"\
                    "setup status : {0}".format(setup_tc_status))
        print_error("Steps in cleanup will be executed on besteffort")
        test_suite_status = "ERROR"
    #execute cleanup steps defined in testwrapper file if testwrapperfile is present
    if testwrapperfile:
        print_info("*****************TESTWRAPPER CLEANUP EXECUTION START*********************")
        data_repository['wt_data_type'] = j_data_type
        cleanup_tc_status, data_repository = testcase_driver.execute_testcase(testwrapperfile,\
                                                          data_repository, tc_context='POSITIVE',\
                                                          runtype=j_runtype,\
                                                          tc_parallel=None, queue=None,\
                                                          auto_defects=auto_defects, suite=None,\
                                                          jiraproj=None, tc_onError_action=None,\
                                                          iter_ts_sys=None, steps_tag='Cleanup')
        print_info("*****************TESTWRAPPER CLEANUP EXECUTION END*********************")
    print_info("\n")
    suite_end_time = Utils.datetime_utils.get_current_timestamp()
    print_info("[{0}] Testsuite execution completed".format(suite_end_time))

    if test_suite_status == True and cleanup_tc_status == True:
        test_suite_status = True
    #set status to WARN if only cleanup fails
    elif test_suite_status == True and cleanup_tc_status != True:
        print_warning("setting test suite status to WARN as cleanup failed")
        test_suite_status = 'WARN'

    suite_duration = Utils.datetime_utils.get_time_delta(suite_start_time)
    hms = Utils.datetime_utils.get_hms_for_seconds(suite_duration)
    print_info("Testsuite duration= {0}".format(hms))
    testsuite_utils.update_suite_duration(str(suite_duration))
    if test_suite_status == False and ts_onError_action and\
        ts_onError_action.upper() == 'ABORT_AS_ERROR':
        print_info("Testsuite status will be marked as ERROR as onError action is set"
                   "to 'abort_as_error'")
        test_suite_status = "ERROR"
    testsuite_utils.report_testsuite_result(suite_repository, test_suite_status)

    ts_junit_object = data_repository['wt_junit_object']
    ts_junit_object.update_count(test_suite_status, "1", "pj")
    ts_junit_object.update_count("suites", "1", "pj", "not appicable")
    ts_junit_object.update_attr("status", str(test_suite_status), "ts", suite_timestamp)
    ts_junit_object.update_attr("time", str(suite_duration), "ts", suite_timestamp)

    if not from_project:
        ts_junit_object.update_attr("status", str(test_suite_status), "pj", "not applicable")
        ts_junit_object.update_attr("time", str(suite_duration), "pj", "not appicable")
        ts_junit_object.output_junit(data_repository['wt_results_execdir'])

        # Save JUnit/HTML results of the Suite in MongoDB server
        if data_repository.get("db_obj") is not False:
            ts_junit_xml = (data_repository['wt_results_execdir'] + os.sep +
                            ts_junit_object.filename+"_junit.xml")
            data_repository.get("db_obj").add_html_result_to_mongodb(ts_junit_xml)
    else:
        # Do not output JUnit result file for parallel suite execution
        if not ts_parallel and not data_repository['war_parallel']:
            # Create and replace existing Project junit file for each suite
            ts_junit_object.output_junit(data_repository['wp_results_execdir'],
                                         print_summary=False)

    if ts_parallel:
        ts_impact = data_repository['wt_ts_impact']
        if ts_impact.upper() == 'IMPACT':
            msg = "Status of the executed suite impacts project result"
        elif ts_impact.upper() == 'NOIMPACT':
            msg = "Status of the executed suite case does not impact project result"
        print_debug(msg)
        # put result into multiprocessing queue and later retrieve in corresponding driver
        queue.put((test_suite_status, ts_impact, suite_timestamp, ts_junit_object))

    return test_suite_status, suite_repository


def main(testsuite_filepath, data_repository={}, from_project=False, auto_defects=False,
         jiraproj=None, res_startdir=None, logs_startdir=None, ts_onError_action=None,
         queue=None, ts_parallel=False):
    """Executes a test suite """
    try:
        test_suite_status, suite_repository = execute_testsuite(testsuite_filepath,
                                                                data_repository, from_project,
                                                                auto_defects, jiraproj,
                                                                res_startdir, logs_startdir,
                                                                ts_onError_action, queue,
                                                                ts_parallel)

    except Exception:
        print_error('unexpected error {0}'.format(traceback.format_exc()))
        test_suite_status, suite_repository = False, None
    return test_suite_status, suite_repository
