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

import datetime
import xml.etree.ElementTree as ET
from Framework.Utils import xml_Utils, config_Utils
from Framework.Utils.print_Utils import print_info, print_error, print_warning

ROOT = None
CURRENT_POINTER = None
CURRENT_TESTSUITE_POINTER = None
CURRENT_PROPERTIES_POINTER = None
CURRENT_TESTCASE_POINTER = None

G_TESTSUITE = {}
G_TESTSUITE_LOOP = 0

G_PROPERTIES = {}
G_PROPERTIES_LOOP = 0

G_PROPERTY = {}
G_PROPERTY_LOOP = 0

G_TESTCASE = {}
G_TESTCASE_LOOP = 0


def printOutput():
    """ Prints the dump of the xml object to the file specified.
    This function can be used for debugging purpose and its called at the end of
    the functional calls.

    Arguments:
        resultfile = Result File

    Returns:
        None
    """
    global ROOT

    resultfile = config_Utils.junit_resultfile
    tree = ET.ElementTree(ROOT)
    # tree.write(resultfile)


def pSuite_root(resultfile):
    """ Get the root element and assign it to current pointer"""
    global ROOT
    global CURRENT_POINTER

    ROOT = ET.Element("testsuites")
    CURRENT_POINTER = ROOT
    printOutput()


def pSuite_testsuite(resultfile, name, errors, skipped, tests, failures, time, timestamp):
    """ set the attributes of test suite """
    global ROOT
    global CURRENT_POINTER
    global CURRENT_TESTSUITE_POINTER
    global CURRENT_PROPERTIES_POINTER
    global G_TESTSUITE
    global G_TESTSUITE_LOOP
    global G_PROPERTIES
    global G_PROPERTIES_LOOP

    G_TESTSUITE_LOOP = G_TESTSUITE_LOOP+1
    G_TESTSUITE[G_TESTSUITE_LOOP] = ET.SubElement(CURRENT_POINTER, "testsuite")

    G_TESTSUITE[G_TESTSUITE_LOOP].set('name', name)
    G_TESTSUITE[G_TESTSUITE_LOOP].set('errors', errors)
    G_TESTSUITE[G_TESTSUITE_LOOP].set('skipped', skipped)
    G_TESTSUITE[G_TESTSUITE_LOOP].set('tests', tests)
    G_TESTSUITE[G_TESTSUITE_LOOP].set('failures', failures)
    G_TESTSUITE[G_TESTSUITE_LOOP].set('time', time)
    # print "setting time to", time
    G_TESTSUITE[G_TESTSUITE_LOOP].set('timestamp', timestamp)
    CURRENT_TESTSUITE_POINTER = G_TESTSUITE[G_TESTSUITE_LOOP]

    G_PROPERTIES_LOOP = G_PROPERTIES_LOOP+1
    G_PROPERTIES[G_PROPERTIES_LOOP] = ET.SubElement(CURRENT_TESTSUITE_POINTER, "properties")
    G_PROPERTIES[G_PROPERTIES_LOOP].text = ""
    CURRENT_PROPERTIES_POINTER = G_PROPERTIES[G_PROPERTIES_LOOP]
    printOutput()


def pSuite_property(resultfile, name, value):
    """ set the properties of test suite """
    global CURRENT_PROPERTIES_POINTER
    global G_PROPERTIES
    global G_PROPERTIES_LOOP

    global G_PROPERTY
    global G_PROPERTY_LOOP

    G_PROPERTY_LOOP = G_PROPERTY_LOOP+1
    G_PROPERTY[G_PROPERTY_LOOP] = ET.SubElement(CURRENT_PROPERTIES_POINTER, "property")
    G_PROPERTY[G_PROPERTY_LOOP].set('name', name)
    G_PROPERTY[G_PROPERTY_LOOP].set('value', value)
    printOutput()


def pSuite_testcase(resultfile, classname, name, time):
    """ set the attributes of test case """
    global CURRENT_TESTSUITE_POINTER
    global CURRENT_TESTCASE_POINTER

    global G_TESTSUITE
    global G_TESTSUITE_LOOP

    global G_TESTCASE
    global G_TESTCASE_LOOP

    G_TESTCASE[G_TESTCASE_LOOP] = ET.SubElement(CURRENT_TESTSUITE_POINTER, "testcase")
    G_TESTCASE[G_TESTCASE_LOOP].set('classname', classname)
    G_TESTCASE[G_TESTCASE_LOOP].set('name', name)
    G_TESTCASE[G_TESTCASE_LOOP].set('time', time)
    CURRENT_TESTCASE_POINTER = G_TESTCASE[G_TESTCASE_LOOP]
    printOutput()


def pSuite_testcase_failure(resultfile, msg='test failure', time='0', testCaseText=''):
    """  Computes failed case status with message and update on case duration in
         test suite """
    global CURRENT_TESTCASE_POINTER
    global G_TESTCASE
    global G_TESTCASE_LOOP

    testCaseStatus = ET.SubElement(CURRENT_TESTCASE_POINTER, "failure")
    testCaseStatus.set('message', msg)
    testCaseStatus.text = testCaseText
    update_tc_duration(time)


def pSuite_testcase_skip(resultfile):
    """ Computes skipped case status in test suite """
    global CURRENT_TESTCASE_POINTER
    global G_TESTCASE
    global G_TESTCASE_LOOP

    testCaseStatus = ET.SubElement(CURRENT_TESTCASE_POINTER, "skipped")
    printOutput()

    # resultfile.write('<skipped/>\n')
    # resultfile.flush()


def pSuite_testcase_error(resultfile, msg='test error', time='0', testCaseText=''):
    """ Computes error case status with message and update on case duration in
        suite """
    global CURRENT_TESTCASE_POINTER
    global G_TESTCASE
    global G_TESTCASE_LOOP

    testCaseStatus = ET.SubElement(CURRENT_TESTCASE_POINTER, "error")
    testCaseStatus.set('message', msg)
    testCaseStatus.text = testCaseText
    update_tc_duration(time)


def update_tc_duration(time):
    """ Updates the case duration"""
    global ROOT
    global CURRENT_TESTCASE_POINTER

    global G_TESTSUITE
    global G_TESTSUITE_LOOP
    CURRENT_TESTCASE_POINTER.set('time', time)
    printOutput()


def update_suite_duration(time):
    """ Updates the suite duration """
    global ROOT
    global CURRENT_TESTSUITE_POINTER

    global G_TESTSUITE
    global G_TESTSUITE_LOOP

    CURRENT_TESTSUITE_POINTER.set('time', time)
    printOutput()


def pSuite_update_suite_attributes(resultfile, errors, skipped, tests, failures, time='0'):
    """ Updates the suite attributes """
    global ROOT
    global CURRENT_TESTSUITE_POINTER

    global G_TESTSUITE
    global G_TESTSUITE_LOOP

    CURRENT_TESTSUITE_POINTER.set('errors', errors)
    CURRENT_TESTSUITE_POINTER.set('skipped', skipped)
    CURRENT_TESTSUITE_POINTER.set('tests', tests)
    CURRENT_TESTSUITE_POINTER.set('failures', failures)
    CURRENT_TESTSUITE_POINTER.set('time', time)
    printOutput()


def pSuite_update_suite_tests(tests):
    """ Updates the suite tests"""
    global ROOT
    global CURRENT_TESTSUITE_POINTER

    global G_TESTSUITE
    global G_TESTSUITE_LOOP

    CURRENT_TESTSUITE_POINTER.set('tests', tests)
    printOutput()


def pSuite_report_suite_result(resultfile):
    """Reports the suite result to the suite result xml file """
    tree = ET.ElementTree(ROOT)
    tree.write(resultfile)


def get_suite_timestamp():
    """Returns the date-time stamp for the start of testsuite execution in JUnit format """
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def pSuite_report_suite_requirements(resultfile, requirement_id):
    """Reports the requirements of the suite to the suite result xml file """
    pSuite_property(resultfile, 'requirement', requirement_id)


def compute_testsuite_status(suite_status, tc_status, tc_impact):
    """Computes the status of the testsuite based on the impact value for the testcase

    Arguments:
    1. tc_status = (bool) status of the executed testcase
    2. tc_impact = (string) impact   = tc_status will be used to compute testsuite_status
                            noimpact = tc_status will not be used to compute testsuite_status
    """

    if tc_impact.upper() == 'IMPACT':
        suite_status = suite_status and tc_status

    elif tc_impact.upper() == 'NOIMPACT':
        print_info('result of this testcase does not impact the testsuite status')
    print_info(suite_status)
    return suite_status


def report_testsuite_result(suite_repository, suite_status):
    """Reports the result of the testsuite executed
    Arguments:
    1. suite_repository    = (dict) dictionary caontaining all the data related to the testsuite
    2. suite_status        = (bool) status of the testsuite executed
    """
    # suite_resultfile = suite_repository['junit_resultfile']
    print_info("\n ****** TestSuite Result ******")
    suite_status = {'TRUE': 'PASS', 'FALSE': 'FAIL', 'EXCEPTION': 'ERROR', 'ERROR': 'ERROR',
                    'RAN': 'RAN'}.get(str(suite_status).upper())
    print_info("Testsuite:{0}  STATUS:{1}".format(suite_repository['suite_name'], suite_status))
    # pSuite_report_suite_result(suite_resultfile)
    print_info("\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ END OF TEST SUITE $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    return suite_status


def get_path_from_xmlfile(element):
    """Gets the testcase/testsuite path  from the testsuite.xml/project.xml file """

    path = xml_Utils.get_text_from_direct_child(element, 'path')
    if path is None or path is False:
        print_error("path cannot be empty check input xml file")
        path = None
    elif path is not None and path is not False:
        path = path.strip()
    return path


def get_data_file_at_suite_step(element, suite_repository):
    """Gets the testcase/testsuite path  from the testsuite.xml/project.xml file """

    if suite_repository["suite_exectype"].upper() == "ITERATIVE_SEQUENTIAL" \
       or suite_repository["suite_exectype"].upper() == "ITERATIVE_PARALLEL":
        print_info("Suite exectype=iterative, so all testcases in the suite will use the suite datafile as their input datafile")
        data_file = suite_repository["data_file"]
    else:
        data_file = xml_Utils.get_text_from_direct_child(element, 'InputDataFile')
    if data_file is None or data_file is False:
        data_file = None
    elif data_file is not None and data_file is not False:
        data_file = str(data_file).strip()
    return data_file


def get_runtype_from_xmlfile(element):
    """Gets the runtype value of a testcase from the testsuite.xml file """

    runtype = xml_Utils.get_text_from_direct_child(element, 'runtype')
    if runtype is None or runtype is False:
        runtype = 'sequential_keywords'
    elif runtype is not None and runtype is not False:
        runtype = runtype.strip()
        supported_values = ['sequential_keywords', 'parallel_keywords']
        if runtype.lower() not in supported_values:
            print_warning("unsupported value '{0}' provided for runtype, supported values are '{1}', case-insensitive"
                          .format(runtype, supported_values))
            print_info("Hence using default value for runtype which is 'sequential_keywords'")
            runtype = 'sequential_keywords'
    return runtype


def get_exectype_from_xmlfile(filepath):
    """Gets the exectype values for testcases from the testsuite.xml file """

    exectype = xml_Utils.getChildAttributebyParentTag(filepath, 'Details', 'type', 'exectype')
    if exectype is None or exectype is False:
        exectype = 'sequential_testcases'
    elif exectype is not None and exectype is not False:
        exectype = exectype.strip()
        supported_values = ['sequential_testcases', 'parallel_testcases', 'run_until_fail', 'run_multiple', 'run_until_pass', "iterative_sequential",
                            "iterative_parallel"]
        if exectype.lower() not in supported_values:
            print_warning("unsupported value '{0}' provided for exectype, supported values are '{1}', case-insensitive".format(exectype, supported_values))
            print_info("Hence using default value for exectype which is 'sequential_testcases'")
            exectype = 'sequential_testcases'
    return exectype
