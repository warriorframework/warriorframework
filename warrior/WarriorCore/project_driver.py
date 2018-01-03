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
import shutil
import copy
import traceback
import glob
import Framework.Utils as Utils
from Framework.Utils.print_Utils import print_info, print_error, print_warning
from WarriorCore.Classes import execution_files_class, junit_class
from WarriorCore import common_execution_utils, sequential_testsuite_driver, \
 parallel_testsuite_driver



"""This the project driver that executes a collections of
Warrior testsuites """

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
    if def_on_error_value is None or def_on_error_value is False:
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
    # project_resultfile = open(project_resultfile, 'a+')
    # Utils.config_Utils.junit_file(project_resultfile)

    project_repository['title'] = project_title
    project_repository['operating_system'] = operating_system
    project_repository['project_name'] = project_name
    project_repository['def_on_error_action'] = def_on_error_action
    project_repository['def_on_error_value'] = def_on_error_value
    project_repository['project_execution_dir'] = project_execution_dir
    project_repository['project_resultfile'] = project_junit
    project_repository['wp_results_execdir'] = wp_results_execdir
    project_repository['wp_logs_execdir'] = wp_logs_execdir
    project_repository['project_filepath'] = project_filepath

    # copying testsuite xml file to execution directory of this testsuite
    shutil.copy2(project_filepath, project_execution_dir)

    return project_repository


def get_testsuite_list(project_filepath):
    """Takes the location of any Project.xml file as input
    Returns a list of all the Testsuite elements present in the Project"""

    testsuite_list_new = []
    root = Utils.xml_Utils.getRoot(project_filepath)
    testsuites = root.find('Testsuites')
    if testsuites is None:
        print_info('Testsuite is empty: tag <Testsuites> not "\
                   "found in the input file ')
    else:
        testsuite_list = testsuites.findall('Testsuite') # Use suites
        newlist = []  # Expanded list goes here.
        for a_single_suite in testsuite_list:
            sfilename = a_single_suite.find('path').text   # find the path.
            dirname = os.path.dirname(project_filepath)+os.sep
            if sfilename.find('*') < 0:  # Check if needs expansion
                newlist.append(a_single_suite)  #Nope ? ... keep it.
            else:
                files = glob.glob(dirname+sfilename)  # Expane
                for myfilename in files:
                    na_single_suite = copy.deepcopy(a_single_suite)  #Copy
                    na_single_suite.find('path').text = myfilename.replace(dirname, '')
                    newlist.append(na_single_suite)  # new node
        for a_single_suite in newlist: # tell the user what you did
            print_info("Added suite [{0}] ".format(a_single_suite.find('path').text))
        for a_single_suite in newlist:
            runmode, value, _ = common_execution_utils.\
                get_runmode_from_xmlfile(a_single_suite)
            retry_type, _, _, retry_value, _ = common_execution_utils.\
                get_retry_from_xmlfile(a_single_suite)
            if runmode is not None and value > 0:
                # more than one suite in suite list, insert new suite
                go_next = len(testsuite_list_new) + value + 1
                for i in range(0, value):
                    copy_ts = copy.deepcopy(a_single_suite)
                    copy_ts.find("runmode").set("value", go_next)
                    copy_ts.find("runmode").set("attempt", i+1)
                    testsuite_list_new.append(copy_ts)
            if retry_type is not None and retry_value > 0:
                if len(testsuite_list) > 1:
                    go_next = len(testsuite_list_new) + retry_value + 1
                    if runmode is not None:
                        get_runmode = a_single_suite.find('runmode')
                        a_single_suite.remove(get_runmode)
                    for i in range(0, retry_value):
                        copy_ts = copy.deepcopy(a_single_suite)
                        copy_ts.find("retry").set("count", go_next)
                        copy_ts.find("retry").set("attempt", i+1)
                        testsuite_list_new.append(copy_ts)
            if retry_type is None and runmode is None:
                testsuite_list_new.append(a_single_suite)
        return testsuite_list_new


def execute_project(project_filepath, auto_defects, jiraproj, res_startdir, logs_startdir,
                    data_repository):
    """
    - Takes a list of testsuite locations input.
    - Iterates over the list and sends each testsuite
    location to testsuite_driver for execution.
    - Gets the status of the testsuite from the
    Warrior and computes the project_status based on the impact value
    of the testsuite.
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
    project_title = Utils.xml_Utils.getChildTextbyParentTag(project_filepath, 'Details', 'Title')
    project_repository = get_project_details(project_filepath, res_startdir, logs_startdir,
                                             data_repository)
    project_repository['project_title'] = project_title
    testsuite_list = get_testsuite_list(project_filepath)

    # project_resultfile = project_repository['project_resultfile']

    project_name = project_repository['project_name']
    wp_results_execdir = project_repository['wp_results_execdir']
    data_repository['wp_results_execdir'] = wp_results_execdir

    data_repository['jiraproj'] = jiraproj

    pj_junit_object = junit_class.Junit(filename=project_name, timestamp=project_start_time,
                                        name=project_name, display="True")

    pj_junit_object.update_attr("resultsdir",
                                project_repository['project_execution_dir'],
                                "pj", project_start_time)
    pj_junit_object.update_attr("title", project_repository['project_title'], "pj",
                                project_start_time)
    pj_junit_object.add_property("resultsdir", project_repository['project_execution_dir'], "pj",
                                 project_start_time)

    # adding the resultsdir as attribute, need to be removed after making it
    # a property
    pj_junit_object.add_project_location(project_filepath)
    if "jobid" in data_repository:
        pj_junit_object.add_jobid(data_repository["jobid"])
        del data_repository["jobid"]
    data_repository['wt_junit_object'] = pj_junit_object

    data_repository["war_parallel"] = False

    execution_type = Utils.xml_Utils.getChildAttributebyParentTag(project_filepath, 'Details',
                                                                  'type', 'exectype')

    # for backward compatibility(when exectype is not provided)
    if execution_type is False:
        execution_type = "sequential_suites"

    if execution_type.upper() == 'PARALLEL_SUITES':
        pj_junit_object.remove_html_obj()
        data_repository["war_parallel"] = True
        print_info("Executing suites in parallel")
        project_status = parallel_testsuite_driver.main(testsuite_list, project_repository,
                                                        data_repository, auto_defects,
                                                        ts_parallel=True)
    elif execution_type.upper() == 'SEQUENTIAL_SUITES':
        print_info("Executing suites sequentially")
        project_status = sequential_testsuite_driver.main(testsuite_list, project_repository,
                                                          data_repository, auto_defects)
    else:
        print_error("unexpected project_type received...aborting execution")
        project_status = False

    print_info("\n")
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
        pj_junit_xml = project_repository['wp_results_execdir'] +\
            os.sep + pj_junit_object.filename + "_junit.xml"
        data_repository.get("db_obj").add_html_result_to_mongodb(pj_junit_xml)

    return project_status, project_repository


def compute_project_status(project_status, testsuite_status, testsuite_impact):
    """Computes the status of the project based on the value of impact for the testsuite

    Arguments:
    1. project_status    = (bool) status of the project under execution
    1. testsuite_status  = (bool) status of the executed testsuite
    2. testsuite_impact  = (string) impact noimpact
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
                      'ERROR': 'ERROR', 'EXCEPTION': 'ERROR'}.\
        get(str(project_status).upper())

    print_info("Project:{0}  STATUS:{1}".format(project_repository['project_name'],
                                                project_status))
    return project_status


def main(project_filepath, data_repository={}, auto_defects=False, jiraproj=None,
         res_startdir=None, logs_startdir=None):
    """ Project driver"""
    try:
        project_status, project_repository = execute_project(project_filepath, auto_defects,
                                                             jiraproj, res_startdir, logs_startdir,
                                                             data_repository)
    except Exception:
        project_status, project_repository = False, None
        print_error('unexpected error {0}'.format(traceback.format_exc()))
    return project_status, project_repository
