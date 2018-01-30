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

import xml.etree.ElementTree as ET
from Framework.Utils import file_Utils, xml_Utils, config_Utils
import datetime
from Framework.Utils.print_Utils import print_debug, print_info, print_error, print_warning

root = None
currentPointer = None
currentTestSuitePointer = None
currentPropertiesPointer = None
currentTestCasePointer= None

gTestSuite = {}
gTestSuiteLoop = 0

gProperties = {}
gPropertiesLoop = 0

gProperty = {}
gPropertyLoop = 0

gTestCase = {}
gTestCaseLoop = 0


def printOutput():
    """ Prints the dump of the xml object to the file specified.
    This function can be used for debugging purpose and its called at the end of the functional calls.
        
    Arguments:
        resultfile = Result File
        
    Returns:
        None
    """
    global root
    
    resultfile = config_Utils.junit_resultfile
    tree = ET.ElementTree(root)
    # tree.write(resultfile)


def pSuite_root(resultfile):
    global root
    global currentPointer
    
    root=ET.Element("testsuites")
    currentPointer = root
    printOutput()


def pSuite_testsuite(resultfile, name, errors, skipped, tests, failures, time, timestamp):   
    global root
    global currentPointer
    global currentTestSuitePointer
    global currentPropertiesPointer
    global gTestSuite
    global gTestSuiteLoop
    global gProperties
    global gPropertiesLoop
    
    gTestSuiteLoop = gTestSuiteLoop+1   
    gTestSuite[gTestSuiteLoop] = ET.SubElement(currentPointer,"testsuite")

    gTestSuite[gTestSuiteLoop].set('name',name)
    gTestSuite[gTestSuiteLoop].set('errors',errors)
    gTestSuite[gTestSuiteLoop].set('skipped',skipped)
    gTestSuite[gTestSuiteLoop].set('tests',tests)
    gTestSuite[gTestSuiteLoop].set('failures',failures)
    gTestSuite[gTestSuiteLoop].set('time',time)
    #print "setting time to", time
    gTestSuite[gTestSuiteLoop].set('timestamp',timestamp)
    currentTestSuitePointer = gTestSuite[gTestSuiteLoop]
    
    gPropertiesLoop = gPropertiesLoop+1
    gProperties[gPropertiesLoop] = ET.SubElement(currentTestSuitePointer,"properties")
    gProperties[gPropertiesLoop].text = ""
    currentPropertiesPointer = gProperties[gPropertiesLoop]
    printOutput()
    

def pSuite_property(resultfile, name, value):
    global currentPropertiesPointer
    global gProperties  
    global gPropertiesLoop
    
    global gProperty
    global gPropertyLoop
    
    gPropertyLoop  = gPropertyLoop+1    
    gProperty[gPropertyLoop] = ET.SubElement(currentPropertiesPointer,"property")   
    gProperty[gPropertyLoop].set('name',name)
    gProperty[gPropertyLoop].set('value',value) 
    printOutput()
    

def pSuite_testcase(resultfile, classname, name, time):
    global currentTestSuitePointer
    global currentTestCasePointer
    
    global gTestSuite
    global gTestSuiteLoop
    
    global gTestCase
    global gTestCaseLoop
    
    gTestCase[gTestCaseLoop] = ET.SubElement(currentTestSuitePointer,"testcase")    
    gTestCase[gTestCaseLoop].set('classname',classname)
    gTestCase[gTestCaseLoop].set('name',name)
    gTestCase[gTestCaseLoop].set('time',time)
    currentTestCasePointer = gTestCase[gTestCaseLoop]
    printOutput()


def pSuite_testcase_failure(resultfile, msg='test failure', time='0', testCaseText=''):
    global currentTestCasePointer
    global gTestCase
    global gTestCaseLoop
    
    testCaseStatus = ET.SubElement(currentTestCasePointer,"failure")
    testCaseStatus.set('message',msg)
    testCaseStatus.text = testCaseText
    update_tc_duration(time)
    


def pSuite_testcase_skip(resultfile):
    global currentTestCasePointer
    global gTestCase
    global gTestCaseLoop
    
    testCaseStatus = ET.SubElement(currentTestCasePointer,"skipped")    
    testCaseStatus.text = ""
    printOutput()
    
    #resultfile.write('<skipped/>\n')
    #resultfile.flush()

def pSuite_testcase_error(resultfile, msg='test error', time='0', testCaseText=''):
    global currentTestCasePointer
    global gTestCase
    global gTestCaseLoop
    
    testCaseStatus = ET.SubElement(currentTestCasePointer,"error")
    testCaseStatus.set('message',msg)
    testCaseStatus.text = testCaseText
    update_tc_duration(time)


def update_tc_duration(time):
    """ """
    global root
    global currentTestCasePointer
    
    global gTestSuite
    global gTestSuiteLoop
    currentTestCasePointer.set('time',time)
    printOutput()
    
def update_suite_duration(time):
    """ """
    global root
    global currentTestSuitePointer
    
    global gTestSuite
    global gTestSuiteLoop
    
    currentTestSuitePointer.set('time',time)
    printOutput()   

def pSuite_update_suite_attributes(resultfile, errors, skipped, tests, failures, time='0'):
    global root
    global currentTestSuitePointer
    
    global gTestSuite
    global gTestSuiteLoop
    
    currentTestSuitePointer.set('errors',errors)
    currentTestSuitePointer.set('skipped',skipped)
    currentTestSuitePointer.set('tests',tests)
    currentTestSuitePointer.set('failures',failures)
    currentTestSuitePointer.set('time',time)
    printOutput()

def pSuite_update_suite_tests(tests):
    global root
    global currentTestSuitePointer
    
    global gTestSuite
    global gTestSuiteLoop
    
    currentTestSuitePointer.set('tests',tests)
    printOutput()

def pSuite_report_suite_result(resultfile): 
    tree = ET.ElementTree(root) 
    tree.write(resultfile)

def get_suite_timestamp():
    """Returns the date-time stamp for the start of testsuite execution in JUnit format """
    return datetime.datetime.now().strftime ("%Y-%m-%dT%H:%M:%S")


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
        suite_status =  suite_status and tc_status
        

    elif tc_impact.upper() == 'NOIMPACT': 
        print_info('result of this testcase does not impact the testsuite status')
    print suite_status
    return suite_status


def report_testsuite_result(suite_repository, suite_status) :
    """Reports the result of the testsuite executed
    Arguments:
    1. suite_repository    = (dict) dictionary caontaining all the data related to the testsuite
    2. suite_status        = (bool) status of the testsuite executed
    """
    suite_resultfile = suite_repository['junit_resultfile'] 
    print_info( "\n ****** TestSuite Result ******")
    suite_status = {'TRUE': 'PASS', 'FALSE': 'FAIL', 'EXCEPTION': 'ERROR', 'ERROR': 'ERROR'}.get(str(suite_status).upper())
    print_info("Testsuite:{0}  STATUS:{1}".format(suite_repository['suite_name'], suite_status))
    #pSuite_report_suite_result(suite_resultfile)
    print_info( "\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ END OF TEST SUITE $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
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
        runtype='sequential_keywords'
    elif runtype is not None and runtype is not False:
        runtype = runtype.strip()
        supported_values = ['sequential_keywords', 'parallel_keywords']
        if runtype.lower() not in supported_values:
            print_warning("unsupported value '{0}' provided for runtype, supported values are '{1}', case-insensitive".format(runtype, supported_values))
            print_info("Hence using default value for runtype which is 'sequential_keywords'")
            runtype = 'sequential_keywords'
    return runtype

def get_exectype_from_xmlfile(filepath):
    """Gets the exectype values for testcases from the testsuite.xml file """
    
    exectype = xml_Utils.getChildAttributebyParentTag(filepath, 'Details', 'type', 'exectype')
    if exectype is None or exectype is False:
        exectype='sequential_testcases'
    elif exectype is not None and exectype is not False:
        exectype = exectype.strip()
        supported_values = ['sequential_testcases', 'parallel_testcases', 'run_until_fail', 'run_multiple', 'run_until_pass', "iterative_sequential",
                            "iterative_parallel"]
        if exectype.lower() not in supported_values:
            print_warning("unsupported value '{0}' provided for exectype, supported values are '{1}', case-insensitive".format(exectype, supported_values))
            print_info("Hence using default value for exectype which is 'sequential_testcases'")
            exectype = 'sequential_testcases'
    return exectype


