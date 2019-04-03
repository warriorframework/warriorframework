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

"""Module that contains methods for testcase results related operations """
#pylint: disable=wrong-import-position
#pylint: disable=pointless-string-statement
from WarriorCore.Classes import testcase_utils_class
TCOBJ = testcase_utils_class.TestcaseUtils()

""" ##################################################################################### """
""" The functions below this line are to be used by keyword developers in their keywords: """
""" ##################################################################################### """

def pSubStep(substep_txt=""):
    """Creates a substep tag in test case result xml file"""
    TCOBJ.p_substep(substep_txt)

def pNote(txt, print_type="info"):
    """Adds the provided txt as a note to the test case xml result file under the current tag
    and also prints the txt to the console.
    :Arguments:
        1. txt (string) = a text to be written to result file and printed to the console.
    :Returns:
        None
    """

    TCOBJ.p_note(txt, print_type)

def report_substep_status(status):
    """
    Reports the status of a substep to the test case xml result file based on the received status
    On receiving a True reports substep as Passed
    On receiving a False raises a warning
    On receiving a Skip reports substep execution as skipped

    :Arguments:
        1. status(bool) = status of the executed substep (True or False)
    :Returns:
        None
    """

    TCOBJ.report_substep_status(status)

def pSubKeyword(subkey_txt=""):

    """
    Adds the provided txt as a note to the test case xml result file under the
    current tag and also prints the txt to the console.
    :Arguments:
        1. txt (string) = a text to be written to result file and printed to
                          the console.
    :Returns:
        None
    """
    TCOBJ.p_subkeyword(subkey_txt)

def reportsubkeywordstatus(status, text="", level='Subkeyword'):
    """ Reports the status of a Keyword to the testcase xml result file baseid on
        the received status
    On receiving a True reports keyword as Passed
    On receiving a False reports keyword as Failure
    On receiving a Skip reports skips the keyword execution

    :Arguments:
        1. status = (bool) True or False
        2. text = (string) any useful description
        3. level = (string) Default: SubKeyword

    :Returns:
        None
    """

    TCOBJ.report_subkeyword_status(status, text, level)

""" ################################ WARNING ############################################ """
""""Functions below this line are used by the framework for reporting purposes
 DO NOT use these functions in your keywords."""
""" ##################################################################################### """

def pOpen(fileobject):
    """Open a file"""
    return TCOBJ.p_open(fileobject)

def pClose(fileobject):
    """close a file"""
    TCOBJ.p_close(fileobject)

# define the testcase root element
def pTestcase():
    """Creates a  root tag in the testcase result xml file"""
    TCOBJ.p_testcase()

def pKeyword(keyword_txt, driver_txt):
    """Creates a keyword tag as direct child to the <Testcase> tag """
    TCOBJ.p_keyword(keyword_txt, driver_txt)

def pDriver(driver_txt):
    """create a driver tag in testcase result xml file"""
    TCOBJ.p_driver(driver_txt)

def pStep(step_txt=""):
    """create a step tag in testcase result xml file"""
    TCOBJ.p_step(step_txt)

def update_step_num(step_num):
    """ adds step_num attribute to the step tag in
    test case result xml file"""

    TCOBJ.update_step_num(step_num)

def update_arguments(args):
    """ adds step_num attribute to the step tag in
            test case result xml file"""
    TCOBJ.update_arguments(args)

def update_kw_resultfile(kw_resultfile):
    """ adds result file attribute to the keyword tag in
    test case result xml file"""

    TCOBJ.update_kw_resultfile(kw_resultfile)

def pNote_level(txt, ptype="info", level=None, ptc=True):
    """Create Note at the provided level"""
    TCOBJ.p_note_level(txt, ptype, level, ptc)


def pCustomTag(name, txt):
    """Adds a note to the testcase xml result file under the current tag
    :Arguments:
        1. txt = (string) a text description of the step
        2. print_type(string) = type of print - info/debug/error/exception/warn/None

    :Returns:
        None

    """
    TCOBJ.p_custom_tag(name, txt)

def pReportRequirements(requirement_id):
    """Report the requirement-id to the xml result file """
    TCOBJ.p_report_requirements(requirement_id)

def get_wdesc_string(function_object):
    """ Gets the WDesc string from the function object
    """
    return TCOBJ.get_wdesc_string(function_object)

def pConvertLogical(text):
    """map NO=false, YES=True and return the bool to the calling function"""
    return TCOBJ.p_convert_logical(text)

def convertLogic(text):
    """Converts
    True -> PASS
    False -> FAIL
    ERROR -> ERROR
    EXCEPTION -> ERROR
    """
    return TCOBJ.convert_logic(text)

def reportStatus(status, text="", level='Keyword'):
    """ Reports the status of a Keyword to the testcase xml result file base don the received status
    On receiving a True reports keyword as Passed
    On receiving a False reports keyword as Failure
    On receiving a Skip reports skips the keyword execution

    :Arguments:
        1. status = (bool) True or False
        2. text = (string) any useful description
        3. level = (string) only supported value currently is Keyword
    :Returns:
        None
    """

    TCOBJ.report_status(status, text, level)

def reportWarning(status, text="", level='subStep'):
    """ Reports the status of a substep to the testcase xml result file base don the received status
    On receiving a True reports substep as Passed
    On receiving a False raises a warning
    On receiving a Skip reports skips the substep execution

    :Arguments:
        1. status = (bool) True or False
        2. text = (string) any useful description
        3. level = (string) only supported value currently is subStep

    :Returns:
        None
    """
    TCOBJ.report_warning(status, text, level)


#  same as reportStatus: changed function name to be more meaningful
def reportKeywordStatus(status, kw_name):
    """ Reports the status of a Keyword to the testcase xml result file base don the received status
    On receiving a True reports keyword as Passed
    On receiving a False reports keyword as Failure
    On receiving a Skip reports skips the keyword execution

    :Arguments:
        1. status = (bool) True or False

    :Returns:
        None
    """

    TCOBJ.report_keyword_status(status, kw_name)

def pTestResult(text, resultfile):
    """report test case reult in result xml file"""
    TCOBJ.p_test_result(text, resultfile)

def append_result_files(dst_resultfile, kw_resultfile_list, dst_root='Testcase'):
    """append kw/system result xml files into testcase result xml file"""
    TCOBJ.append_result_files(dst_resultfile, kw_resultfile_list, dst_root)

def compute_status_using_impact(input_status_list, input_impact_list, status=True):
    """Computes the status from the list of input status and input impact """

    return TCOBJ.compute_status_using_impact(input_status_list, input_impact_list, status)

def compute_status_without_impact(input_status_list, status=True):
    """Computes the system status from the list of step status adn impact"""

    return TCOBJ.compute_status_without_impact(input_status_list, status)

def compute_system_resultfile(kw_resultfile_list, resultsdir, system_name):
    """Generates a system resultfile from the list of keyword result files """

    return TCOBJ.compute_system_resultfile(kw_resultfile_list, resultsdir, system_name)

def add_defects_to_resultfile(resultfile, defect_id):
    """Adds defects if any to the testcase result file """

    TCOBJ.add_defects_to_resultfile(resultfile, defect_id)

def get_impact_from_xmlfile(element):
    """Gets the impact value of a step/testcase/suite from the
    testcase.xml/testsuite.xml/project.xml file """

    return TCOBJ.get_impact_from_xmlfile(element)


def get_context_from_xmlfile(element):
    """Gets the context value of a step/testcase/suite from the
    testcase.xml/testsuite.xml/project.xml file """

    return TCOBJ.get_context_from_xmlfile(element)

def get_description_from_xmlfile(element):
    """Gets the description value of a step/testcase/suite from the
    testcase.xml/testsuite.xml/project.xml file """

    return TCOBJ.get_description_from_xmlfile(element)

def get_defonerror_fromxml_file(filepath):
    """Gets the default on error value of a step/testcase/suite from the
    testcase.xml/testsuite.xml/project.xml file """

    return TCOBJ.get_defonerror_fromxml_file(filepath)

def get_setup_on_error(filepath):
    """Gets the default setup on error value from the
    wrapper file """
    return TCOBJ.get_setup_on_error(filepath)

def get_requirement_id_list(testcase_filepath):
    """gets the list of requirements for the testcase """

    return TCOBJ.get_requirement_id_list(testcase_filepath)

def get_steps_list(testcase_filepath):
    """Takes the location of any Testcase xml file as input
    Returns a list of all the step elements present in the Testcase

    :Arguments:
        1. testcase_filepath    = full path of the Testcase xml file
    """

    return TCOBJ.get_steps_list(testcase_filepath)
