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
"""The test case driver is the driver responsible for execution of a testcase
It in turn calls the custom_sequential/custom_parallel/iterative_sequential/
iterative_parallel drivers according to the  data_type and run_type of the testcase"""

import sys
import os
import time
import shutil
import copy
from WarriorCore.defects_driver import DefectsDriver
from WarriorCore import custom_sequential_kw_driver, custom_parallel_kw_driver
from WarriorCore import iterative_sequential_kw_driver, iterative_parallel_kw_driver,\
common_execution_utils, framework_detail
from WarriorCore.Classes import execution_files_class, junit_class, hybrid_driver_class
import Framework.Utils as Utils
from Framework.Utils.testcase_Utils import convertLogic
from Framework.Utils.print_Utils import print_notype, print_info,print_warning, print_error, print_debug, print_exception
import Framework.Utils.email_utils as email

def get_testcase_details(testcase_filepath, data_repository, jiraproj):
    """Gets all the details of the Testcase
    (like title, resultsfolder, logsfolder, datafile, default on_error
    action/value etc) from its xml file,for details that are not provided
    by user assigns default values.
    """

    name = Utils.xml_Utils.getChildTextbyParentTag (testcase_filepath, 'Details', 'Name')
    title = Utils.xml_Utils.getChildTextbyParentTag (testcase_filepath, 'Details', 'Title')
    category = Utils.xml_Utils.getChildTextbyParentTag (testcase_filepath, 'Details', 'Category')
    def_on_error_action = Utils.testcase_Utils.get_defonerror_fromxml_file(testcase_filepath)
    def_on_error_value = Utils.xml_Utils.getChildAttributebyParentTag (testcase_filepath, 'Details', 'default_onError', 'value')
    filename = os.path.basename (testcase_filepath)
    filedir = os.path.dirname(testcase_filepath)
    nameonly = Utils.file_Utils.getNameOnly (filename)
    operating_system = sys.platform

    if name is None or name is False:
        name = nameonly
    else:
        name = name.strip()
        if name != nameonly:
            print_warning("<Name> tag in xml file should match the filename")
            name = nameonly

    if title is None or title is False:
        print_warning("title is missing, please provide a title for the testcase")
        title = "None"
    else:
        title = str(title).strip()
    
    if def_on_error_value is None or def_on_error_value is False:
        def_on_error_value = None

    if not data_repository.has_key('wt_results_execdir'):
        if data_repository.has_key('ow_resultdir'):
            data_repository['wt_results_execdir'] = data_repository['ow_resultdir']
        else:
            data_repository['wt_results_execdir'] = None


    if not data_repository.has_key('wt_logs_execdir'):
        if data_repository.has_key('ow_logdir'):
            data_repository['wt_logs_execdir'] = data_repository['ow_logdir']
        else:
            data_repository['wt_logs_execdir'] = None

    res_startdir = data_repository['wt_results_execdir']
    logs_startdir = data_repository['wt_logs_execdir']
    
    efile_obj = execution_files_class.ExecFilesClass(testcase_filepath, "tc", res_startdir, logs_startdir)
    resultfile = efile_obj.resultfile
    resultsdir = efile_obj.resultsdir
    logfile = efile_obj.logfile
    logsdir = efile_obj.logsdir
    defectsdir = efile_obj.get_defect_files()




    """Data files can be passed on to a test by four methods, below are the 
       four methods and its priority in order. 
       By this feature we allow the user to run the same testcases, with
       different data files with out actually changing the testcase.
    """ 

    ##First priority for data files given through CLI##
    if data_repository.has_key('ow_datafile'):
        datafile = data_repository['ow_datafile']
        data_type = efile_obj.check_get_datatype(datafile)
    ##Second priority for data files given in the Test suite step##
    elif data_repository.has_key(testcase_filepath):
        datafile = data_repository[testcase_filepath]
        data_type = efile_obj.check_get_datatype(datafile)
    ##Third priority for data files given in the Test Suite globally##
    elif data_repository.has_key('suite_data_file'):
        datafile = data_repository['suite_data_file']
        data_type = efile_obj.check_get_datatype(datafile)
    ##Fourth priority for data files given in the Testcase file##
    else:
        datafile, data_type = efile_obj.get_data_files()

    # tc_execution_dir = Utils.file_Utils.createDir_addtimestamp(execution_dir, nameonly)
    # datafile, data_type = get_testcase_datafile(testcase_filepath)
    # resultfile, resultsdir = get_testcase_resultfile(testcase_filepath, tc_execution_dir, nameonly)
    # logfile, logsdir = get_testcase_logfile(testcase_filepath, tc_execution_dir, nameonly)
    # defectsdir = get_testcase_defectsdir(testcase_filepath, tc_execution_dir, nameonly)
    kw_results_dir = Utils.file_Utils.createDir(resultsdir, 'Keyword_Results')
    console_logfile = Utils.file_Utils.getCustomLogFile(filename, logsdir, 'consoleLogs')

    Utils.config_Utils.debug_file(console_logfile)
    #objLogFile = Utils.testcase_Utils.pOpen(logfile)

    to_strip_list = [name, title, category, datafile, data_type, logsdir, resultsdir, defectsdir]
    stripped_list = Utils.string_Utils.strip_white_spaces(to_strip_list)
    
    name = stripped_list[0]
    title = stripped_list[1]
    category = stripped_list[2]
    datafile = stripped_list[3]
    data_type = stripped_list[4]
    logsdir = stripped_list[5]
    resultsdir = stripped_list[6]
    defectsdir = stripped_list[7]

    # Add variables to data_repository
    data_repository['wt_name'] = name
    data_repository['wt_testcase_filepath'] = testcase_filepath
    data_repository['wt_title'] = title
    data_repository['wt_filename'] = filename
    data_repository['wt_filedir'] = filedir
    data_repository['wt_datafile'] = datafile
    data_repository['wt_data_type'] = data_type.upper()
    data_repository['wt_resultsdir'] = resultsdir
    data_repository['wt_resultfile'] = resultfile
    data_repository['wt_logsdir'] = logsdir
    data_repository['wt_kw_results_dir'] = kw_results_dir
    data_repository['wt_defectsdir'] = defectsdir
    #data_repository['wt_logfile'] = objLogFile
    data_repository['wt_operating_system'] = operating_system.upper()
    data_repository['wt_def_on_error_action'] = def_on_error_action.upper()
    data_repository['wt_def_on_error_value'] = def_on_error_value
   
    # For custom jira project name
    if not data_repository.has_key('jiraproj'):
        data_repository['jiraproj'] = jiraproj
    
    # write resultfile, logsdir, datafile, filename, logfile to config file
    Utils.config_Utils.set_resultfile(resultfile)
    Utils.config_Utils.set_datafile(datafile)
    Utils.config_Utils.set_logsdir(logsdir)
    Utils.config_Utils.set_filename(filename)
    Utils.config_Utils.set_logfile(logfile)
    Utils.config_Utils.set_testcase_path(filedir)
 
    # write TC details to result file
    Utils.testcase_Utils.pTestcase()
    Utils.testcase_Utils.pCustomTag("Title", title)
    Utils.testcase_Utils.pCustomTag("TC_Location", testcase_filepath)
    Utils.testcase_Utils.pCustomTag("Datafile", datafile)
    Utils.testcase_Utils.pCustomTag("Logsdir", logsdir)
    Utils.testcase_Utils.pCustomTag("Defectsdir", defectsdir)
    Utils.testcase_Utils.pCustomTag("Resultfile", resultfile)
    Utils.testcase_Utils.pCustomTag("Operating_System", operating_system)

    
    # copying testcase xml file to execution directory of this testcase
    exec_dir =  os.path.dirname(data_repository['wt_resultsdir'])
    shutil.copy2(testcase_filepath, exec_dir)

    return data_repository



def report_testcase_requirements(testcase_filepath):
    """Reports the requirements of the testcase to the result file """

    req_id_list = Utils.testcase_Utils.get_requirement_id_list(testcase_filepath)
    if req_id_list is not None:
        for req_id in req_id_list:
            Utils.testcase_Utils.pReportRequirements(req_id)

def junit_requirements(testcase_filepath, tc_junit_object, timestamp):
    req_id_list = Utils.testcase_Utils.get_requirement_id_list(testcase_filepath)
    if req_id_list is not None:
        for req_id in req_id_list:
            tc_junit_object.add_requirement(req_id, timestamp)

    
def get_steps_list(testcase_filepath):
    """Takes the location of any Testcase xml file as input
    Returns a list of all the step elements present in the Testcase

    :Arguments:
        1. testcase_filepath    = full path of the Testcase xml file
    """
    step_list = []
    root = Utils.xml_Utils.getRoot(testcase_filepath)   
    Steps = root.find('Steps')
    if Steps is None:
        print_info('Testcase has no commands: tag <Steps> not found in the input file ')
    else:
        step_list = []
        new_step_list = Steps.findall('step')
        #execute step multiple times
        for index, step in enumerate(new_step_list):
            runmode, value = common_execution_utils.get_runmode_from_xmlfile(step)
            retry_type, _, _, retry_value, _ = common_execution_utils.get_retry_from_xmlfile(step)
            if runmode is not None and value > 0:
                #more than one step in step list, insert new step
                if len(new_step_list) > 1:
                    go_next = len(step_list) + value + 1
                    for i in range(0, value):
                        copy_step = copy.deepcopy(step)
                        copy_step.find("runmode").set("value", go_next)
                        copy_step.find("runmode").set("attempt", i+1)
                        step_list.append(copy_step)
                #only one step in step list, append new step
                else:
                    for i in range(0, value):
                        copy_step = copy.deepcopy(step)
                        copy_step.find("runmode").set("attempt", i+1)
                        step_list.append(copy_step)
            if retry_type is not None and retry_value > 0:
                if len(new_step_list) > 1:
                    go_next = len(step_list) + retry_value + 1
                    if runmode is not None:
                        get_runmode = step.find('runmode')
                        step.remove(get_runmode)
                    for i in range(0, retry_value):
                        copy_step = copy.deepcopy(step)
                        copy_step.find("retry").set("count", go_next)
                        copy_step.find("retry").set("attempt", i+1)
                        step_list.append(copy_step)
                else:
                    if runmode is not None:
                        get_runmode = step.find('runmode')
                        step.remove(get_runmode)
                    for i in range(0, retry_value):
                        copy_step = copy.deepcopy(step)
                        copy_step.find("retry").set("attempt", i+1)
                        step_list.append(copy_step)
            if retry_type is None and runmode is None:
                step_list.append(step)
        return step_list

def compute_testcase_status(step_status, tc_status):
    """Compute the status of the testcase based on the step_status and the impact value of the step

    Arguments:
    1. step_status    = (bool) status of the executed step
    2. tc_status      = (bool) status of the testcase
    3. data_repository= (dict) data_repository of the testcase
    """

    if step_status is None:
        return tc_status
    else:
        return tc_status and step_status

def report_testcase_result(tc_status, data_repository):
    """Report the testcase result to the result file

    :Arguments:
        1. tc_status (bool) = status of the executed testcase
        2. data_repository (dict) = data_repository of the executed  testcase
    """
    print_info("\n**** Testcase Result ***")
    print_info("TESTCASE:{0}  STATUS:{1}".format(data_repository['wt_name'], convertLogic(tc_status)))
    print("\n")
    Utils.testcase_Utils.pTestResult(tc_status, data_repository['wt_resultfile'])
    root = Utils.xml_Utils.getRoot(data_repository['wt_resultfile'])
    fail_count = 0
    for value in root.findall('Keyword'):
        kw_status = value.find('KeywordStatus').text
        if kw_status != "PASS":
            fail_count += 1
            kw_name = value.find('Name').text
            get_step_value = value.attrib.values()
            step_num = ','.join(get_step_value)
            if fail_count == 1:
                print_info("++++++++++++++++++++++++ Summary of Failed Keywords ++++++++++++++++++++++++")
                print_info("{0:15} {1:45} {2:10}".format('StepNumber', 'KeywordName', 'Status'))
                print_info("{0:15} {1:45} {2:10}".format(str(step_num), str(kw_name), str(kw_status)))
            elif fail_count > 1:
                print_info("{0:15} {1:45} {2:10}".format(str(step_num), str(kw_name), str(kw_status)))
    print_info("=================== END OF TESTCASE ===========================")

def get_system_list(datafile, node_req=False, iter_req=False):
    """Get the list of systems from the datafile
    :Arguments:
        1. datafile(string) - path of the input data file
        2. node_req(boolean) :
            If True, returns system_node_list(system xml objects) along
            with system_list(name of the systems)
        3. iter_req(boolean) :
             If True, picks systems only with 'iter' value other than 'no'
             If False, picks all systems from the data file
    :Returns:
        1. system_list(list) - name of the systems in the datafile
        2. system_node_list(list) - xml objects of the systems in the
                                    datafile(when node_req is True)
    """
    root = Utils.xml_Utils.getRoot(datafile)
    temp_systems = root.findall('system')
    systems = []
    system_list = []
    system_node_list = []
    # exclude the systems with iter value as no
    if iter_req is True:
        for system in temp_systems:
            iter_flag = system.get('iter')
            if iter_flag:
                if str(iter_flag).lower() != "no":
                    systems.append(system)
            else:
                systems.append(system)
    else:
        systems = temp_systems
    for system in systems:
        #check if the system has subsystem or not.
        subsystems = system.findall('subsystem')
        if subsystems != []:
            first_subsystem = True
            for subsystem in subsystems:
                #if the system has subsystem, find the default subsystem for the system and use it to execute the keyword.
                default = subsystem.get('default')
                if default == "yes":
                    subsystem_name = subsystem.get('name')
                    system_name = system.get('name') + '[' + subsystem_name + ']'
                    break
                #if none of the subsystems have default="yes" then the default subsystem will be the first subsystem under the system.
                elif first_subsystem == True:
                    subsystem_name = subsystem.get('name')
                    system_name = system.get('name') + '[' + subsystem_name + ']'
                    first_subsystem = False
        #if there is no subsystem use the system.
        else:
            system_name = system.get('name')
            system_node = system
        system_list.append(system_name)
        system_node_list.append(system_node)
    if node_req:
        return system_list, system_node_list
    else:
        return system_list

def print_testcase_details_to_console(testcase_filepath, data_repository):
    """Prints the testcase details to the console """
    framework_detail.warrior_framework_details() 
    print_info("\n===============================  TC-DETAILS  ==================================================")
    print_info("Title: %s" % data_repository['wt_title'])
    print_info("Results directory: %s" % data_repository['wt_resultsdir'])
    print_info("Logs directory: %s" % data_repository['wt_logsdir'])
    print_info("Defects directory: {0}".format(data_repository["wt_defectsdir"]))
    print_info("Datafile: %s" % data_repository['wt_datafile'])
    report_testcase_requirements(testcase_filepath)
    print_info("================================================================================================")
    time.sleep(2)

def create_defects(auto_defects, data_repository):
    """Creates the defects json files for the testcase executed
    If auto_defects = True create bugs in jira for the associated project provided in jira config file
    """
    defect_obj = DefectsDriver(data_repository)
    json_status = defect_obj.create_failing_kw_json()

    if json_status:
        if auto_defects:
            print_info("auto-create defects ")
            defects_json_list = defect_obj.get_defect_json_list()
            if len(defects_json_list) == 0:
                print_warning("No defect json files found in defects"\
                              "directory '{0}' of this testcase".format(data_repository['wt_defectsdir']))
            elif len(defects_json_list) > 0:
                connect = defect_obj.connect_warrior_jira()
                if connect is True:
                    defect_obj.create_jira_issues(defects_json_list)
        else:
            print_info("auto-create defects was Not requested")

def check_and_create_defects(tc_status, auto_defects, data_repository, tc_junit_object):
    """Check tc_status and create defects if tc_status is fail/error/exception
    update testcase junit with error/failures accordingly """

    if tc_status is True:
        pass    
    elif tc_status is False:
        create_defects(auto_defects, data_repository)
    elif tc_status == 'EXCEPTION' or tc_status == 'ERROR':
        create_defects(auto_defects, data_repository)

def execute_testcase(testcase_filepath, data_repository, tc_context,
                     runtype, tc_parallel, queue, auto_defects, suite, jiraproj,
                     tc_onError_action, iter_ts_sys):
    """ Executes the testcase (provided as a xml file)
            - Takes a testcase xml file as input and executes each command in the testcase.
            - Computes the testcase status based on the stepstatus and the impact value of the step
            - Handles step failures as per the default/specific onError action/value
            - Calls the function to report the testcase status

    :Arguments:
        1. testcase_filepath (string) = the full path of the testcase xml file
        2. execution_dir (string) = the full path of the directory under which the 
                                    testcase execution directory will be created
                                    (the results, logs for this testcase will be 
                                    stored in this testcase execution directory.)
    """

    tc_status = True
    tc_start_time = Utils.datetime_utils.get_current_timestamp()
    tc_timestamp = str(tc_start_time)
    print_info("[{0}] Testcase execution starts".format(tc_start_time))

    get_testcase_details(testcase_filepath, data_repository, jiraproj)

    # These lines are for creating testcase junit file
    from_ts = False
    if not 'wt_junit_object' in data_repository:
        # not from testsuite
        tc_junit_object = junit_class.Junit(filename=data_repository['wt_name'], timestamp=tc_timestamp,
                                            name="customProject_independant_testcase_execution", display="False")
        if "jobid" in data_repository:
            tc_junit_object.add_jobid(data_repository["jobid"])
            del data_repository["jobid"]
        tc_junit_object.create_testcase(location=data_repository['wt_filedir'], timestamp=tc_timestamp,
                                        ts_timestamp=tc_timestamp, name=data_repository['wt_name'],
                                        testcasefile_path=data_repository['wt_testcase_filepath'],
                                        display="False")
        junit_requirements(testcase_filepath, tc_junit_object, tc_timestamp)
        data_repository['wt_ts_timestamp'] = tc_timestamp
    else:
        tc_junit_object = data_repository['wt_junit_object']
        tc_junit_object.create_testcase(location="from testsuite", timestamp=tc_timestamp, ts_timestamp=data_repository['wt_ts_timestamp'], classname=data_repository['wt_suite_name'], name=data_repository['wt_name'], testcasefile_path=data_repository['wt_testcase_filepath'])
        from_ts = True
        junit_requirements(testcase_filepath, tc_junit_object, data_repository['wt_ts_timestamp'])
    data_repository['wt_tc_timestamp'] = tc_timestamp
    data_type = data_repository['wt_data_type']

    # Adding resultsdir, logsdir, title as attributes to testcase_tag in the junit result file
    # Need to remove these after making resultsdir, logsdir as part of properties tag in testcase
    tc_junit_object.add_property("resultsdir", os.path.dirname(data_repository['wt_resultsdir']),
                                "tc", tc_timestamp)
    tc_junit_object.add_property("logsdir", os.path.dirname(data_repository['wt_logsdir']),
                                "tc", tc_timestamp)
    tc_junit_object.update_attr("title", data_repository['wt_title'], "tc", tc_timestamp )
    data_repository['wt_junit_object'] = tc_junit_object

    data_repository['wt_junit_object'] = tc_junit_object
    print_testcase_details_to_console(testcase_filepath, data_repository)
    step_list = get_steps_list(testcase_filepath)

    if data_type.upper() == 'CUSTOM' and runtype.upper() == 'SEQUENTIAL_KEYWORDS':
        tc_status = execute_custom(data_type, runtype, custom_sequential_kw_driver, data_repository, step_list)

    elif data_type.upper() == 'CUSTOM' and runtype.upper() == 'PARALLEL_KEYWORDS':
        tc_status = execute_custom(data_type, runtype, custom_parallel_kw_driver, data_repository, step_list)

    elif data_type.upper() == 'ITERATIVE' and runtype.upper() == 'SEQUENTIAL_KEYWORDS':
        print_info("iterative sequential")
        system_list = get_system_list(data_repository['wt_datafile'],
                                      iter_req=True) \
            if iter_ts_sys is None else [iter_ts_sys]

        #print len(system_list)
        if len(system_list) == 0:
            print_warning("Datatype is iterative but no systems found in input datafile")
            print_warning("when Datatype is iterative the InputDataFile should have system(s) to iterate upon")
            tc_status = False
        elif len(system_list) > 0:
            tc_status = iterative_sequential_kw_driver.main(step_list, data_repository, tc_status, system_list)

    elif data_type.upper() == 'ITERATIVE' and runtype.upper() == 'PARALLEL_KEYWORDS':
        print_info("iterative parallel")
        system_list = get_system_list(data_repository['wt_datafile'],
                                      iter_req=True) \
            if iter_ts_sys is None else [iter_ts_sys]

        #print len(system_list)
        if len(system_list) == 0:
            print_warning("DataType is iterative but no systems found in input datafile")
            print_warning("when DataType id iterative the InputDataFile should have system(s) to iterate upon")
            tc_status = False
        elif len(system_list) > 0:
            tc_status = iterative_parallel_kw_driver.main(step_list, data_repository, tc_status, system_list)
            
    elif data_type.upper() == "HYBRID":
        print_info("Hybrid")
        system_list, system_node_list = get_system_list(data_repository['wt_datafile'], node_req=True)
        # call the hybrid driver here
        hyb_drv_obj = hybrid_driver_class.HybridDriver(step_list, data_repository, tc_status, system_list, system_node_list)
        tc_status = hyb_drv_obj.execute_hybrid_mode()
        
    else:
        print_warning("unsupported value provided for testcase data_type or testsuite runtype")
        tc_status = False

    if tc_context.upper() == 'NEGATIVE':
        if all([tc_status != 'EXCEPTION', tc_status != 'ERROR']):
            print_debug("Test case status is: '{0}', flip status as context is negative".format(tc_status))
            tc_status = not tc_status

    if tc_status == False and tc_onError_action and tc_onError_action.upper() == 'ABORT_AS_ERROR':
        print_info("Testcase status will be marked as ERROR as onError action is set to 'abort_as_error'")
        tc_status = "ERROR"

    check_and_create_defects(tc_status, auto_defects, data_repository, tc_junit_object)
    
    print("\n")
    tc_end_time = Utils.datetime_utils.get_current_timestamp()
    print_info("[{0}] Testcase execution completed".format(tc_end_time))
    tc_duration = Utils.datetime_utils.get_time_delta(tc_start_time)
    hms = Utils.datetime_utils.get_hms_for_seconds(tc_duration)
    print_info("Testcase duration= {0}".format(hms))

    tc_junit_object.update_count(tc_status, "1", "ts", data_repository['wt_ts_timestamp'])
    tc_junit_object.update_count("tests", "1", "ts", data_repository['wt_ts_timestamp'])
    tc_junit_object.update_count("tests", "1", "pj", "not appicable")
    tc_junit_object.update_attr("status", str(tc_status), "tc", tc_timestamp)
    tc_junit_object.update_attr("time", str(tc_duration), "tc", tc_timestamp)
    tc_junit_object.add_testcase_message(tc_timestamp, tc_status)

    # Adding resultsdir, logsdir, title as attributes to testcase_tag in the junit result file
    # Need to remove these after making resultsdir, logsdir as part of properties tag in testcase
    tc_junit_object.update_attr("resultsdir", os.path.dirname(data_repository['wt_resultsdir']),
                                "tc", tc_timestamp)
    tc_junit_object.update_attr("logsdir", os.path.dirname(data_repository['wt_logsdir']),
                                "tc", tc_timestamp)

    report_testcase_result(tc_status, data_repository)
    if not from_ts:
        tc_junit_object.update_count(tc_status, "1", "pj", "not appicable")
        tc_junit_object.update_count("suites", "1", "pj", "not appicable")
        tc_junit_object.update_attr("status", str(tc_status), "ts", data_repository['wt_ts_timestamp'])
        tc_junit_object.update_attr("status", str(tc_status), "pj", "not appicable")
        tc_junit_object.update_attr("time", str(tc_duration), "ts", data_repository['wt_ts_timestamp'])
        tc_junit_object.update_attr("time", str(tc_duration), "pj", "not appicable")

        tc_junit_object.output_junit(data_repository['wt_resultsdir'])

        # Save JUnit/HTML results of the Case in MongoDB server
        if data_repository.get("db_obj") is not False:
            tc_junit_xml =  data_repository['wt_resultsdir'] + os.sep +tc_junit_object.filename+"_junit.xml"
            data_repository.get("db_obj").add_html_result_to_mongodb(tc_junit_xml)
    else:
        # send an email on TC failure(no need to send an email here when
        # executing a single case).
        if str(tc_status).upper() in ["FALSE", "ERROR", "EXCEPTION"]:
            email_setting = None
            # for first TC failure
            if "any_failures" not in data_repository:
                email_params = email.get_email_params("first_failure")
                if all(value != "" for value in email_params[:3]):
                    email_setting = "first_failure"
                data_repository['any_failures'] = True
            # for further TC failures
            if email_setting is None:
                email_params = email.get_email_params("every_failure")
                if all(value != "" for value in email_params[:3]):
                    email_setting = "every_failure"

            if email_setting is not None:
                email.compose_send_email("Test Case: ", data_repository[
                 'wt_testcase_filepath'], data_repository['wt_logsdir'],
                 data_repository['wt_resultsdir'], tc_status, email_setting)

    if tc_parallel:
        tc_impact   =  data_repository['wt_tc_impact']
        if tc_impact.upper() == 'IMPACT': 
            msg = "Status of the executed test case impacts Testsuite result"
        elif tc_impact.upper() == 'NOIMPACT': 
            msg = "Status of the executed test case does not impact Teststuie result"
        print_debug(msg)
        tc_name = Utils.file_Utils.getFileName(testcase_filepath)
        # put result into multiprocessing queue and later retrieve in corresponding driver
        queue.put((tc_status, tc_name, tc_impact, tc_duration, tc_junit_object))

    # Save XML results of the Case in MongoDB server
    if data_repository.get("db_obj") is not False:
        data_repository.get("db_obj").add_xml_result_to_mongodb(data_repository['wt_resultfile'])

    # main need tc_status and data_repository values to unpack
    return tc_status, data_repository


def execute_custom(datatype, runtype, driver, data_repository, step_list):
    """
    Execute a custom testcase
    """
    print_info("{0} {1}".format(datatype, runtype))
    tc_status = False
    if data_repository.has_key("suite_exectype") and data_repository["suite_exectype"].upper() == "ITERATIVE":
        print_info("Testsuite execute type=iterative but the testcase datatype=custom. "\
                   "All testcases in a iterative testsuite should have datatype=iterative, "\
                   "Hence this testcase will be marked as failure.")
    elif runtype.upper() == 'SEQUENTIAL_KEYWORDS' or runtype.upper() == 'PARALLEL_KEYWORDS':
        tc_status = driver.main(step_list, data_repository, tc_status, system_name=None)
    else:
        print_error("Unsuppored runtype found, please check testcase file")
    return tc_status

def main(testcase_filepath, data_repository = {}, tc_context='POSITIVE',
         runtype='SEQUENTIAL_KEYWORDS', tc_parallel=False, auto_defects=False, suite=None,
         tc_onError_action=None, iter_ts_sys=None, queue=None, jiraproj=None):

    """ Executes a testcase """
    tc_start_time = Utils.datetime_utils.get_current_timestamp()
    if Utils.file_Utils.fileExists(testcase_filepath):
           
        try:
            tc_status, data_repository = execute_testcase(testcase_filepath, 
                                         data_repository, tc_context, runtype,
                                         tc_parallel, queue, auto_defects, suite,
                                         jiraproj, tc_onError_action, iter_ts_sys)
        except Exception as exception:
            print_exception(exception)
            tc_status = False

    else: 
        print_error("Testcase xml file does not exist in provided path: {0}".format(testcase_filepath))
        tc_status = False
        if tc_parallel:
            queue.put(('ERROR', str(testcase_filepath), 'IMPACT', '0'))
            
    tc_duration = Utils.datetime_utils.get_time_delta(tc_start_time)

    return tc_status, tc_duration, data_repository
