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
"""This the project driver that executes a collections of
Warrior testsuites """

import sys
import os
import shutil
import time

import WarriorCore.testsuite_driver as testsuite_driver
import WarriorCore.onerror_driver as onerror_driver
import traceback
import exec_type_driver
import Framework.Utils as Utils
from Framework.Utils.print_Utils import print_info, print_error, print_debug, print_warning
from WarriorCore.Classes import execution_files_class, junit_class
from WarriorCore import testsuite_utils

def get_project_details(project_filepath, res_startdir, logs_startdir, data_repository):
    """Gets all details of the Project from its xml file"""

    project_repository = {}
    project_name = Utils.xml_Utils.getChildTextbyParentTag(project_filepath, 'Details', 'Name')
    project_title = Utils.xml_Utils.getChildTextbyParentTag(project_filepath, 'Details', 'Title')
    def_on_error_action = Utils.testcase_Utils.get_defonerror_fromxml_file(project_filepath)
    def_on_error_value = Utils.xml_Utils.getChildAttributebyParentTag(project_filepath,
                                                                      'Details',
                                                                      'default_onError',
                                                                      'value')
    filename = os.path.basename(project_filepath)
    nameonly = Utils.file_Utils.getNameOnly(filename)
    operating_system = sys.platform

    if project_name is None or project_name is False:
        project_name = nameonly
    else:
        project_name = project_name.strip()
        if project_name != nameonly:
            print_warning("<Name> tag in xml file should match the filename")
            project_name = nameonly

    if project_title is None or project_title is False:
        print_warning("title is missing, please provide a title for the project")
    else:
        project_title = str(project_title).strip()

    if def_on_error_value  is None or def_on_error_value is False:
        def_on_error_value = None

    if data_repository.has_key('ow_resultdir'):
        res_startdir = data_repository['ow_resultdir']
    if data_repository.has_key('ow_logdir'):
        logs_startdir = data_repository['ow_logdir']

    efile_obj = execution_files_class.ExecFilesClass(project_filepath,
                                                     "proj",
                                                     res_startdir,
                                                     logs_startdir)
    project_resultfile = efile_obj.resultfile
    project_junit = Utils.file_Utils.getNameOnly(project_resultfile) + "_prjunit.xml"
    project_execution_dir = os.path.dirname(project_resultfile)
    wp_results_execdir = efile_obj.results_execdir
    wp_logs_execdir = efile_obj.logs_execdir
    #project_resultfile = open(project_resultfile, 'a+')
    #Utils.config_Utils.junit_file(project_resultfile)

    project_repository['title'] = project_title
    project_repository['operating_system'] = operating_system
    project_repository['project_name'] = project_name
    project_repository['def_on_error_action'] = def_on_error_action
    project_repository['def_on_error_value'] = def_on_error_value
    project_repository['project_execution_dir'] = project_execution_dir
    project_repository['project_resultfile'] = project_junit
    project_repository['wp_results_execdir'] = wp_results_execdir
    project_repository['wp_logs_execdir'] = wp_logs_execdir

    # copying testsuite xml file to execution directory of this testsuite
    shutil.copy2(project_filepath, project_execution_dir)

    return project_repository


def get_testsuite_list(project_filepath):
    """Takes the location of any Project.xml file as input
    Returns a list of all the Testsuite elements present in the Project"""

    testsuite_list = []
    root = Utils.xml_Utils.getRoot(project_filepath)
    testsuites = root.find('Testsuites')
    if testsuites is None:
        print_info('Testsuite is empty: tag <Testsuites> not found in the input file ')
    else:
        testsuite_list = testsuites.findall('Testsuite')
        return testsuite_list

def execute_project(project_filepath, auto_defects, jiraproj, res_startdir, logs_startdir, data_repository):
    """
    - Takes a list of testsuite locations input.
    - Iterates over the list and sends each testsuite
    location to testsuite_driver for execution.
    - Gets the status of the testsuite from the
    Warrior and computes the project_status based on the impact value of the testsuite.
    - If the testsuite fails, handles the failure using
    the default or specific  onError action,value.
    - Finally reports the project status to the result file.

    Arguments:
    1. testsuite_list        = (list) list of testsuite locations
    2. testsuite_driver      = (module loader) module loader of the testsuite_driver
    3. project_repository    = (dict) dictionary containing all data of the project under execution
    """
    project_start_time = Utils.datetime_utils.get_current_timestamp()
    print_info("[{0}] Project execution starts".format(project_start_time))
    suite_cntr = 0
    project_status = True
    goto_testsuite = False
    ts_status_list = []
    ts_impact_list = []
    impact_dict = {"IMPACT":"Impact", "NOIMPACT":"No Impact"}
    project_dir = os.path.dirname(project_filepath)
    project_repository = get_project_details(project_filepath, res_startdir, logs_startdir, data_repository)
    testsuite_list = get_testsuite_list(project_filepath)

    project_resultfile = project_repository['project_resultfile']

    project_name = project_repository['project_name']
    wp_results_execdir = project_repository['wp_results_execdir']
    data_repository['wp_results_execdir'] = wp_results_execdir
    wp_logs_execdir = project_repository['wp_logs_execdir']

    project_error_action = project_repository['def_on_error_action']
    project_error_value = project_repository['def_on_error_value']

    pj_junit_object = junit_class.Junit(filename=project_name, timestamp=project_start_time, name=project_name)
    
    pj_junit_object.update_attr("resultsdir", project_repository['project_execution_dir'],
                                "pj", project_start_time)
    pj_junit_object.add_property("resultsdir", project_repository['project_execution_dir'],
                                "pj", project_start_time)

    # adding the resultsdir as attribute, need to be removed after making it a property
    pj_junit_object.add_project_location(project_filepath)
    if "jobid" in data_repository:
        pj_junit_object.add_jobid(data_repository["jobid"])
        del data_repository["jobid"]
    data_repository['wt_junit_object'] = pj_junit_object

    while suite_cntr < len(testsuite_list):
        testsuite = testsuite_list[suite_cntr]
        suite_junit_type = 'file'
        suite_cntr += 1
        
        testsuite_rel_path = testsuite_utils.get_path_from_xmlfile(testsuite)
        if testsuite_rel_path is not None:
            testsuite_path = Utils.file_Utils.getAbsPath(testsuite_rel_path, project_dir)
        else:
            testsuite_path = str(testsuite_rel_path)
        print '\n'
        print_debug("<<<< Starting execution of Test suite: {0}>>>>".format(testsuite_path))
        action, testsuite_status = exec_type_driver.main(testsuite)
        testsuite_impact = Utils.testcase_Utils.get_impact_from_xmlfile(testsuite)
        testsuite_name = Utils.file_Utils.getFileName(testsuite_path)
        testsuite_nameonly = Utils.file_Utils.getNameOnly(testsuite_name)
        ts_onError_action = Utils.xml_Utils.get_attributevalue_from_directchildnode(testsuite, 'onError', 'action')
        ts_onError_action = ts_onError_action if ts_onError_action else project_error_action
        if Utils.file_Utils.fileExists(testsuite_path):
            if not goto_testsuite  and action is True:

                testsuite_result = testsuite_driver.main(testsuite_path,
                                                         data_repository=data_repository,
                                                         from_project=True,
                                                         auto_defects=auto_defects,
                                                         jiraproj=jiraproj,
                                                         res_startdir=wp_results_execdir,
                                                         logs_startdir=wp_logs_execdir,
                                                         ts_onError_action=ts_onError_action)
                testsuite_status = testsuite_result[0]
                testsuite_resultfile = testsuite_result[1]
                

            elif goto_testsuite and goto_testsuite == str(suite_cntr) and action is True:
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
                testsuite_resultfile = testsuite_result[1]

            else:
                msg = print_info('skipped testsuite: {0} '.format(testsuite_path))
                testsuite_resultfile = '<testsuite errors="0" failures="0" name="{0}" '\
                'skipped="0" tests="0" time="0" timestamp="{1}" > '\
                '<skipped message="{2}"/> </testsuite>'.format(testsuite_name,
                                                               project_start_time,
                                                               msg)
                tmp_timestamp = str(Utils.datetime_utils.get_current_timestamp())
                time.sleep(2)
                pj_junit_object.create_testsuite(
                    location=os.path.dirname(testsuite_path),
                    name=testsuite_nameonly, timestamp=tmp_timestamp,
                    **pj_junit_object.init_arg())
                pj_junit_object.update_attr("status", "SKIPPED", "ts", tmp_timestamp)
                pj_junit_object.update_attr("skipped", "1", "pj", tmp_timestamp)
                pj_junit_object.update_count("suites", "1", "pj", tmp_timestamp)
                data_repository['testsuite_%d_result'%suite_cntr] = "SKIP"
                # pj_junit_object.add_testcase_message(tmp_timestamp, "skipped")
                pj_junit_object.update_attr("impact", impact_dict.get(testsuite_impact.upper()),
                                            "ts", tmp_timestamp)
                pj_junit_object.update_attr("onerror", "N/A", "ts", tmp_timestamp)
                pj_junit_object.output_junit(wp_results_execdir,
                                             print_summary=False)
                continue

        else:
            
            msg = print_error("Test suite does not exist in "\
                              "provided path: {0}".format(testsuite_path))
            testsuite_status = 'ERROR'
            testsuite_resultfile = '<testsuite errors="0" failures="0" name="{0}" '\
            'skipped="0" tests="0" time="0" timestamp="{1}" > '\
            '<error message="{2}"/> </testsuite>'.format(testsuite_name, project_start_time, msg)
            suite_junit_type = 'string'
            if goto_testsuite and goto_testsuite == str(suite_cntr):
                goto_testsuite = False
            elif goto_testsuite and goto_testsuite != str(suite_cntr):
                data_repository['testsuite_%d_result'%suite_cntr] = "ERROR"
                continue

        goto_testsuite_num = onerror_driver.main(testsuite, project_error_action, project_error_value)
        if goto_testsuite_num == False:
            onerror = "Next"
        elif goto_testsuite_num == "ABORT":
            onerror = "Abort"
        else:
            onerror = "Goto:" + str(goto_testsuite_num)
        pj_junit_object.update_attr("impact", impact_dict.get(testsuite_impact.upper()),
                                    "ts", data_repository['wt_ts_timestamp'])
        pj_junit_object.update_attr("onerror", onerror, "ts", data_repository['wt_ts_timestamp'])

        string_status = {"TRUE":"PASS", "FALSE":"FAIL", "ERROR":"ERROR", "SKIP":"SKIP"}

        if str(testsuite_status).upper() in string_status.keys():
            data_repository['testsuite_%d_result'%suite_cntr] = string_status[str(testsuite_status).upper()]
        else:
            print_error("unexpected testsuite status, default to exception")
            data_repository['testsuite_%d_result'%suite_cntr] = "ERROR"
            
        ts_status_list.append(testsuite_status)
        ts_impact_list.append(testsuite_impact)
        if testsuite_impact.upper() == 'IMPACT': 
            msg = "Status of the executed test suite impacts Project result"
        elif testsuite_impact.upper() == 'NOIMPACT': 
            msg = "Status of the executed test suite does not impact project result"
        print_debug(msg)
#         project_status = compute_project_status(project_status, testsuite_status,
#                                                 testsuite_impact)

        if testsuite_status is False or testsuite_status == "ERROR" \
        or testsuite_status == "EXCEPTION":
            goto_testsuite = onerror_driver.main(testsuite, project_error_action,
                                                 project_error_value)
            if goto_testsuite in ['ABORT', 'ABORT_AS_ERROR']:
                break
            # when 'onError:goto' value is less than the current ts num,
            # change the next iteration point to goto value
            elif goto_testsuite and int(goto_testsuite) < suite_cntr:
                suite_cntr = int(goto_testsuite)-1
                goto_testsuite = False

    project_status = Utils.testcase_Utils.compute_status_using_impact(ts_status_list,
                                                                      ts_impact_list)
    print ("\n")
    project_end_time = Utils.datetime_utils.get_current_timestamp()
    print_info("[{0}] Project execution completed".format(project_end_time))
    project_duration = Utils.datetime_utils.get_time_delta(project_start_time)
    hms = Utils.datetime_utils.get_hms_for_seconds(project_duration)
    print_info("Project duration= {0}".format(hms))

    project_status = report_project_result(project_status, project_repository)
    pj_junit_object.update_attr("status", str(project_status), "pj", project_start_time)
    pj_junit_object.update_attr("time", str(project_duration), "pj", project_start_time)

    pj_junit_object.output_junit(wp_results_execdir)

    # Save JUnit/HTML results of the Project in MongoDB server
    if data_repository.get("db_obj") is not False:
        pj_junit_xml =  project_repository['wp_results_execdir'] + os.sep + pj_junit_object.filename + "_junit.xml"
        data_repository.get("db_obj").add_html_result_to_mongodb(pj_junit_xml)

    return project_status, project_repository

def compute_project_status(project_status, testsuite_status, testsuite_impact):
    """Computes the status of the project based on the value of impact for the testsuite

    Arguments:
    1. project_status    = (bool) status of the project under execution
    1. testsuite_status  = (bool) status of the
                            executed testsuite
    2. testsuite_impact  = (string) impact
                                    noimpact
    """
    if testsuite_impact.upper() == 'IMPACT':
        project_status = project_status and testsuite_status
    elif testsuite_impact.upper() == 'NOIMPACT':
        print_info('result of this testsuite does not impact the testsuite status')
    return project_status

def report_project_result(project_status, project_repository):
    """Reports the result of the project executed
    Arguments:
        1. project_status        = (bool) status of the project executed
    """

    project_status = {'TRUE': 'PASS', 'FALSE': 'FAIL',
                      'ERROR': 'ERROR', 'EXCEPTION': 'ERROR'}.get(str(project_status).upper())

    print_info("Project:{0}  STATUS:{1}".format(project_repository['project_name'], project_status))
    return project_status

def main(project_filepath, data_repository={}, auto_defects=False, jiraproj=None,
         res_startdir=None, logs_startdir=None):
    """ Project driver"""
    try:
        project_status, project_repository = execute_project(project_filepath, auto_defects,
                                         jiraproj, res_startdir, logs_startdir, data_repository)
    except Exception:
        project_status = False
        print_error('unexpected error {0}'.format(traceback.format_exc()))
    return project_status, project_repository
