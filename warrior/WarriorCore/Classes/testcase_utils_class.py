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

"""
Module that contains methods for testcase results related operations

!!! Important!!!
DO NOT import any modules from warrior/Framework package that uses
warrior/Framework/Utils/print_Utils.py at module level into this module
as it will lead to cyclic imports.
"""

import xml.etree.ElementTree as ET
import inspect
import re

from Framework.Utils.print_Utils import  print_info, print_debug, print_warning,\
print_error, print_exception, print_sub, print_notype, print_without_logging

#import Framework.Utils.file_Utils as file_Utils
#import Framework.Utils.config_Utils as config_Utils
#import Framework.Utils.xml_Utils as xml_Utils

class TestcaseUtils(object):
    """testcase utils class"""
    def __init__(self):
        """
            set default value
        """
        #self.resultfile = config_Utils.resultfile
        self.root = None
        self.current_pointer = None
        self.gkeyword = {}
        self.gkeywordloop = 0
        self.gstep = {}
        self.gsteploop = 0
        self.gsubstep = {}
        self.gsubsteploop = 0
        self.grequirement = {}
        self.grequirementloop = 0
        self.gsubkey = {}
        self.gsubkeyloop = 0
        self.pnote = False

    def file_utils(self):
        """
        """
        import Framework.Utils.file_Utils as file_utils
        return file_utils
    def xml_utils(self):
        """
        """
        import Framework.Utils.xml_Utils as xml_utils
        return xml_utils

    def print_output(self):
        """ Prints the dump of the xml object to the file specified.
        This function can be used for debugging purpose and
        its called at the end of the functional calls.

        :Arguments:
            resultfile = Result File

        :Returns:
            None
        """

        try:
            import Framework.Utils.config_Utils as config_Utils
            resultfile = config_Utils.resultfile
            tree = ET.ElementTree(self.root)
            tree.write(resultfile)
        except UnicodeDecodeError as e:
            print_exception(e)
        except Exception as err:
            print_exception(err)

    @staticmethod
    def p_open(fileobject):
        """Open a file"""
        fobj = open(fileobject, 'a')
        return fobj
    @staticmethod
    def p_close(fileobject):
        """Close a file"""
        fileobject.close()

    # define the testcase self.root element
    def p_testcase(self):
        """Creates a  self.root tag in the testcase result xml file"""

        self.root = ET.Element("Testcase")
        self.current_pointer = self.root
        self.print_output()

    def p_keyword(self, keyword_txt, driver_txt):
        """Creates a keyword tag as direct child to the <Testcase> tag """

        self.p_testcase()
        self.gkeywordloop = self.gkeywordloop+1
        print_info("\n********************* Keyword: %s *********************\n" % keyword_txt)
        self.gkeyword[self.gkeywordloop] = ET.SubElement(self.root, "Keyword")
        self.current_pointer = self.gkeyword[self.gkeywordloop]
        name = ET.SubElement(self.gkeyword[self.gkeywordloop], "Name")
        name.text = keyword_txt
        self.p_driver(driver_txt)
        self.print_output()

    def p_subkeyword(self, keyword_txt):
        """ Creates a Keyword tag as the child node to the <SubStep> tag """
        self.gsubkeyloop = self.gsubkeyloop+1
        print_info("\n***************Sub-Keyword: %s "
                   "***************\n" % keyword_txt)
        self.gsubkey[self.gsubkeyloop] = ET.SubElement(\
                self.gstep[self.gsteploop], "Keyword")
        self.current_pointer = self.gsubkey[self.gsubkeyloop]
        self.gsubkey[self.gsubkeyloop].text = keyword_txt
        self.print_output()


    def p_driver(self, driver_txt):
        """Create a Driver tag"""
        ldriver = ET.SubElement(self.current_pointer, "Driver")
        ldriver.text = driver_txt
        self.print_output()

    def p_step(self, step_txt=""):
        """Create a step tag"""
        self.gsteploop = self.gsteploop+1
        self.gstep[self.gsteploop] = ET.SubElement(self.gkeyword[self.gkeywordloop], "Step")
        self.current_pointer = self.gstep[self.gsteploop]
        self.gstep[self.gsteploop].text = step_txt
        self.print_output()

    def update_kw_resultfile(self, kw_resultfile):
        """ adds step_num attribute to the step tag in
        test case result xml file"""
        rf = ET.SubElement(self.gkeyword[self.gkeywordloop], "Resultfile")
        rf.text = str(kw_resultfile)

    def update_step_num(self, step_num):
        """ adds step_num attribute to the step tag in
        test case result xml file"""
        self.gkeyword[self.gkeywordloop].set('step_num', str(step_num))
        self.gstep[self.gsteploop].set('step_num', str(step_num))

    def update_arguments(self, args):
        """Update the arguments supplied to the keyword """
        arguements = ET.SubElement(self.gkeyword[self.gkeywordloop], "Arguments")
        for arg in args:
            ET.SubElement(arguements, "argument", name=str(arg), value=str(args[arg]))

    def p_substep(self, substep_txt=""):
        """Create a substep tag"""
        self.gsubsteploop = self.gsubsteploop+1
        self.gsubstep[self.gsubsteploop] = ET.SubElement(self.gstep[\
                                                self.gsteploop], "SubStep")
        self.current_pointer = self.gsubstep[self.gsubsteploop]
        self.gsubstep[self.gsubsteploop].text = substep_txt
        print_info("\n<< Substep >>")
        print_info("Keyword Description: {0}".format(substep_txt))

        self.print_output()

    def get_write_locn(self, level):
        """Get the write locn, either kw/step/substep/None
        None = current level """
        write_locn = self.current_pointer
        try:
            if level == "KW":
                write_locn = self.gkeyword[self.gkeywordloop]
            elif level == "STEP":
                write_locn = self.gstep[self.gsteploop]
            elif level == "SUBSTEP":
                write_locn = self.gsubstep[self.gsteploop]
            elif level == "NONE":
                write_locn = self.current_pointer
        except KeyError:
            write_locn = self.current_pointer
        return write_locn

    def p_note_level(self, txt, print_type="info", level=None, ptc=True):
        """Create Note at the provided level"""
        write_locn = self.get_write_locn(str(level).upper())
        print_util_types = ["-D-", "", "-I-", "-E-", "-W-", "-N-",
                            "\033[1;31m-E-\033[0m", "\033[1;33m-W-\033[0m"]
        p_type = {'INFO': print_info,
                  'DEBUG': print_debug,
                  'WARN': print_warning,
                  'WARNING': print_warning,
                  'ERROR': print_error,
                  'EXCEPTION': print_exception,
                  'SUB': print_sub,
                  'NOTYPE': print_notype,
                  'NOLOG': print_without_logging}.get(str(print_type).upper(),
                                                      print_info)
        txt = self.rem_nonprintable_ctrl_chars(str(txt))
        if write_locn is None:
            write_locn = self.current_pointer
        if ptc and print_type not in print_util_types:
            p_type(txt)
        # self.current_pointer may be None,which is not a intended behavior
        # If print_type is nolog or -N-,the message will be logged in terminal
        # but not in result file
        if write_locn is not None and (print_type != '-N-' and print_type != 'nolog'):
            doc = ET.SubElement(write_locn, "Note")
            doc.text = txt
            self.print_output()
        # The below elif is bypasses the else below. As we may want to
        # print items (banners) before we have a handle to write
        elif print_type == "notype":
            pass

        elif print_type not in print_util_types and print_type != 'nolog':
            print_error("Unable to write to location in result file, the "
                        "message is logged in terminal but not in result file")


    def rem_nonprintable_ctrl_chars(self, txt):
        """Remove non_printable ascii control characters """
        #Removes the ascii escape chars
        try:
            txt = re.sub(r'[^\x20-\x7E|\x09-\x0A]','', txt)
            # remove non-ascii characters
            txt = repr(txt).decode('unicode_escape').encode('ascii','ignore')[1:-1]
        except Exception as exception:
            print_exception(exception)
        return txt

    def p_note(self, txt, print_type="info"):
        """Adds a note to the testcase xml result file under the current tag
        :Arguments:
            1. txt = (string) a text description of the step

        :Returns:
            None
        """
        self.pnote = True 
        self.p_note_level(txt, print_type)
        self.pnote = False

    def p_custom_tag(self, name, txt):
        """Adds a note to the testcase xml result file under the current tag
        :Arguments:
            1. txt = (string) a text description of the step

        :Returns:
            None
        """
        doc = ET.SubElement(self.current_pointer, str(name))
        doc.text = str(txt)
        self.print_output()

    def p_status(self, status, level):
        """Report the status"""
        if level.upper() == "SUBSTEP":
            levelobj = self.gsubstep[self.gsubsteploop]
        elif level.upper() == "STEP":
            levelobj = self.gstep[self.gsteploop]
        elif level.upper() == "KEYWORD":
            levelobj = self.gkeyword[self.gkeywordloop]
        elif level.upper() == "SUBKEYWORD":
            levelobj = self.gsubkey[self.gsubkeyloop]
        status_tag = ET.SubElement(levelobj, "%sStatus" % level)
        status_tag.text = status
        self.print_output()

    def p_ran(self, level, text=""):
        """Report a pass """
        print_info("{0} STATUS:RAN".format(text))
        #print_info("PASS: %s\n" % text)
        self.p_status("RAN", level)

    def p_pass(self, level, text=""):
        """Report a pass """
        print_info("{0} STATUS:PASS".format(text))
        #print_info("PASS: %s\n" % text)
        self.p_status("PASS", level)

    def p_fail(self, level, text=""):
        """Report a fail """
        print_info("{0} STATUS:FAIL".format(text))
        #print_info("FAIL: %s\n" % text)
        self.p_status("FAIL", level)

    def p_exception(self, level, text=""):
        """Report a exception """
        print_info("{0} STATUS:EXCEPTION".format(text))
        #print_info("EXCEPTION: %s\n" % text)
        self.p_status("EXCEPTION", level)

    def p_error(self, level, text=""):
        """Report a error """
        print_info("{0} STATUS:ERROR".format(text))
        #print_error("ERROR: %s\n" % text)
        self.p_status("ERROR", level)

    def p_warn(self, level, text=""):
        """Report a warning """
        print_info("{0} STATUS:WARNING".format(text))
        #print_warning("WARNING: %s\n" % text)
        self.p_status("WARNING", level)

    def p_skip(self, level, text=""):
        """Report a skip """
        print_info("{0} STATUS:SKIPPED".format(text))
        #print_info("SKIPPED: %s\n" % text)
        self.p_status("SKIPPED", level)

    def p_report_requirements(self, requirement_id):
        """Report the requirement-id to the xml result file """

        self.grequirementloop = self.grequirementloop + 1
        print_info("Requirement: %s " % requirement_id)
        self.grequirement[self.grequirementloop] = ET.SubElement(self.current_pointer,
                                                                 "Requirement")
        self.grequirement[self.grequirementloop].text = requirement_id
        self.print_output()

    @staticmethod
    def get_wdesc_string(function_object):
        """ Gets the WDesc string from the function object
        """
        source = inspect.getsource(function_object)
        search_wdesc_var = function_object.__name__
        #code_lines = source.split('WDesc')
        code_lines = re.split("(?i)WDESC", source)
        if len(code_lines) > 1:
            funcbody = code_lines[1]
            search_var = re.search('(\")([^\"]*)(\")', funcbody, re.DOTALL|re.MULTILINE)
            if search_var is not None:
                search_wdesc_var = search_var.group()
            elif search_var is None:
                search_wdesc_var = function_object.__name__
        return search_wdesc_var

    @staticmethod
    def p_convert_logical(text):
        """ map NO=false, YES=True and return the bool to the calling function"""
        return {'NO': False, 'YES': True}.get(text.upper())

    @staticmethod
    def convert_logic(text):
        """Converts
        True -> PASS
        False -> FAIL
        ERROR -> ERROR
        EXCEPTION -> ERROR
        """
        #added WARN status
        result = {True: 'PASS', False: 'FAIL',
            'ERROR': 'ERROR', 'EXCEPTION': 'ERROR', 'RAN': 'RAN', 'WARN': 'WARN'}.get(text)
        if result is None:
            print_error("junk or no value received, expecting TRUE/FALSE/ERROR/EXCEPTION")
            result = 'ERROR'
        return result

    def report_status(self, status, text="", level='Keyword'):
        """
        Reports the status to the testcase xml result file base on the received status
        On receiving a True reports keyword status as Passed
        On receiving a False reports keyword status as Failed
        On receiving a Skip reports keyword status as Skipped
        On receiving a Exception reports keyword status as Exception
        On receiving a Error reports Keyword status as Error
        On receiving a RAN reports Keyword status as RAN

        :Arguments:
            1. status = (bool) True or False
            2. text = (string) any useful description
            3. level = (string) only supported value currently is Keyword

        :Returns:
            None
        """

        status = {'TRUE': self.p_pass, 'FALSE': self.p_fail,
                  'SKIP': self.p_skip, 'EXCEPTION': self.p_exception,
                  'ERROR': self.p_error, 'RAN': self.p_ran}.get(str(status).upper())
        if status is None:
            print_error("unexpected or no value received, expecting TRUE/FALSE/SKIP")
            self.p_error(level, text)
        else:
            status(level, text)

    def report_warning(self, status, text="", level='subStep'):
        """
        Reports the status to the testcase xml result file based on the received status
        On receiving a True reports keyword status as Passed
        On receiving a False reports keyword status as Warning
        On receiving a Skip reports keyword status as Skipped
        On receiving a Exception reports keyword status as Exception
        On receiving a Error reports Keyword status as Error

        :Arguments:
            1. status = (bool) True or False
            2. text = (string) any useful description
            3. level = (string) only supported value currently is Keyword

        :Returns:
            None
        """
        from WarriorCore.Classes.war_cli_class import WarriorCliClass
        if WarriorCliClass.mock:
            if str(status).upper() == 'TRUE' or str(status).upper() == 'FALSE':
                status = 'RAN'
        status = {'TRUE': self.p_pass, 'FALSE': self.p_warn,
                  'SKIP': self.p_skip, 'EXCEPTION': self.p_exception,
                  'ERROR': self.p_error, 'RAN': self.p_ran}.get(str(status).upper())
        if status is None:
            print_error("unexpected or no value received, expecting TRUE/FALSE/SKIP")
            self.p_error(level, text)
        else:
            status(level, text)

    def report_substep_status(self, status):
        """ Same as reportWarning created to have a more meaningful name for the function...
        Reports the status of a substep to the testcase xml result file base don the received status
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
        print_info("\n<< Substep status >>")
        self.report_warning(status)

    def report_keyword_status(self, status, kw_name=''):
        """ Same as reportStatus: changed function name to be more meaningful
        Reports the status of a Keyword to the testcase xml result file base don the received status
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
        kw_text = "KEYWORD:{0}  ".format(kw_name)
        self.report_status(status, text=kw_text)

    def report_subkeyword_status(self, status, text, level='SubKeyword'):
        """Reports the status of a sub-keyword to the testcase xml result file
        based on the received status
        On receiving a True reports keyword as Passed
        On receiving a False reports keyword as Failure
        On receiving a Skip reports skips the keyword execution

        :Arguments:
            1. status = (bool) True or False
            2. text = (string) any useful description
            3. level = (string) default would be 'Subkeyword'
        :Returns:
            None
        """
        self.report_status(status, text, level)

    def p_test_result(self, text, resultfile):
        """Report test result"""
        result = self.convert_logic(text)
        self.root = self.xml_utils().getRoot(resultfile)
        tcstatus = ET.SubElement(self.root, "TCstatus")
        tcstatus.text = result
        tree = ET.ElementTree(self.root)
        tree.write(resultfile)

    def append_result_files(self, dst_resultfile, kw_resultfile_list, dst_root='Testcase', childtag='Keyword'):
        """Append kw/system result files into a testcase result file"""
        try:
            finstring = ''
            for kw_file in kw_resultfile_list:
                if kw_file is not None and kw_file is not False:
                    tree = self.xml_utils().get_tree_from_file(kw_file)
                    self.root = tree.getroot()
                    for child in self.root:
                        if child.tag == childtag:
                            finstring = finstring+self.xml_utils().convert_element_to_string(child)
            tc_string = ' '
            if self.file_utils().fileExists(dst_resultfile):
                tc_tree = ET.parse(dst_resultfile)
                tc_root = tc_tree.getroot()
                for tc_child in tc_root:
                    tc_string = tc_string+self.xml_utils().convert_element_to_string(tc_child)
            finalresult = '\n'.join(['<{0}>'.format(dst_root), tc_string + finstring,
                                     '</{0}>'.format(dst_root)])
            with open(dst_resultfile, 'w') as resultfile:
                resultfile.write(finalresult)
                resultfile.flush()
                resultfile.close()
        except Exception, err:
            print_info('unexpected error: {0}'.format(str(err)))

    @staticmethod
    def compute_status_using_impact(input_status_list, input_impact_list, status=True):
        """Computes the status from the list of input status and input impact """
        value = True
        result = []
        for i in range(0, len(input_status_list)):
            input_status = input_status_list[i]
            input_impact = input_impact_list[i]
            if str(input_impact).upper() == 'IMPACT' and input_status != None:
                if str(input_status).upper() == 'ERROR' or str(input_status).upper() == 'EXCEPTION':
                    value = 'ERROR'
                elif str(input_status).upper() == 'RAN':
                    value = 'RAN'
                elif input_status is False:
                    value = False
                elif input_status is True:
                    value = True
            result.append(value)
        if 'ERROR' in result:
            status = 'ERROR'
        elif False in result:
            status = False
        elif 'RAN' in result:
            status = 'RAN'
        else:
            status = True
        return status

    @staticmethod
    def compute_status_without_impact(input_status_list, status=True):
        """Computes the system status from the list of step status"""
        status = True
        for i in range(0, len(input_status_list)):
            input_status = input_status_list[i]
            if input_status is not None:
                if str(input_status).upper() == 'ERROR' or str(input_status).upper() == 'EXCEPTION':
                    #input_status_list[i] = False
                    status = 'ERROR'
                    break
                elif str(input_status).upper() == 'RAN':
                    status = 'RAN'
                elif input_status == False:
                    status = False
                    break
                elif input_status is True:
                    status = True
        return status

    def compute_system_resultfile(self, kw_resultfile_list, resultsdir, system_name):
        """Generates a system resultfile from the list of keyword result files """

        system_results_dir = self.file_utils().createDir(resultsdir, 'System_Results')
        system_resultfile = self.file_utils().getCustomLogFile('system', system_results_dir,
                                                        system_name, '.xml')
        self.append_result_files(system_resultfile, kw_resultfile_list, dst_root='System')
        return system_resultfile

    def add_defects_to_resultfile(self, resultfile, defect_id):
        """Adds defects if any to the testcase result file """
        self.root = self.xml_utils().getRoot(resultfile)
        defects = ET.SubElement(self.root, "Defect")
        defects.text = defect_id
        tree = ET.ElementTree(self.root)
        tree.write(resultfile)


    def get_impact_from_xmlfile(self, element):
        """Gets the impact value of a step/testcase/suite
        from the testcase.xml/testsuite.xml/project.xml file """

        impact = self.xml_utils().get_text_from_direct_child(element, 'impact')
        if impact is None or impact is False:
            impact = 'IMPACT'
        elif impact is not None and impact is not False:
            impact = str(impact).strip()
            supported_values = ['impact', 'noimpact']
            if impact.lower() not in supported_values:
                print_warning("unsupported value '{0}' provided for impact,"\
                              "supported values are '{1}',"\
                              "case-insensitive".format(impact, supported_values))
                print_info("Hence using default value for impact which is 'impact'")
                impact = 'IMPACT'
        return impact


    def get_context_from_xmlfile(self, element):
        """Gets the context value of a step/testcase/suite
        from the testcase.xml/testsuite.xml/project.xml file """

        context = self.xml_utils().get_text_from_direct_child(element, 'context')
        if context is None or context is False:
            context = 'POSITIVE'
        elif context is not None and context is not False:
            context = str(context).strip()
            supported_values = ['positive', 'negative']
            if context.lower() not in supported_values:
                print_warning("unsupported value '{0}' provided for context,"\
                              "supported values are '{1}',"\
                              "case-insensitive".format(context, supported_values))
                print_info("Hence using default value for context which is 'positive'")
                context = 'POSITIVE'
        return context

    def get_description_from_xmlfile(self, element):
        """Gets the description value of a step/testcase/suite
        from the testcase.xml/testsuite.xml/project.xml file """

        description = self.xml_utils().get_text_from_direct_child(element, 'Description')
        if not description:
            description = '*** Description not provided by user ***'
        else:
            description = str(description).strip()
        return description

    def get_defonerror_fromxml_file(self, filepath):
        """Gets the default on error value of a step/testcase/suite
        from the testcase.xml/testsuite.xml/project.xml file """

        def_on_error_action = self.xml_utils().getChildAttributebyParentTag(filepath, 'Details',\
                                                                     'default_onError', 'action')

        if def_on_error_action is None or def_on_error_action is False:
            def_on_error_action = 'NEXT'

        elif def_on_error_action is not None and def_on_error_action is not False:
            supported_values = ['next', 'goto', 'abort', 'abort_as_error']
            if not str(def_on_error_action).lower() in supported_values:
                print_warning("unsupported option '{0}' provided for default_onError"\
                              "action, supported values are {1}".format(def_on_error_action,
                                                                        supported_values))
                print_info("Hence using default value for default_onError action which is 'next'")
                def_on_error_action = 'NEXT'
        return def_on_error_action

    def get_setup_on_error(self, filepath):
        """Gets the setup on error value
        from the wrapperfile.xml file """

        setup_on_error_action = self.xml_utils().getChildAttributebyParentTag(filepath, 'Details',\
                                                                     'setup_onError', 'action')

        if setup_on_error_action is None or setup_on_error_action is False:
            setup_on_error_action = 'abort'

        elif setup_on_error_action is not None and setup_on_error_action is not False:
            supported_values = ['next', 'abort']
            if not str(setup_on_error_action).lower() in supported_values:
                print_warning("unsupported option '{0}' provided for setup_onError"\
                              "action, supported values are {1}".format(setup_on_error_action,
                                                                        supported_values))
                print_info("Hence using default value for setup_onError action which is 'abort'")
                setup_on_error_action = 'abort'
        return setup_on_error_action

    def get_requirement_id_list(self, testcase_filepath):
        """gets the list of requirements for the testcase """

        tc_root = self.xml_utils().getRoot(testcase_filepath)
        requirements = tc_root.find('Requirements')
        req_id_list = []
        if requirements is None or requirements is False:
            print_warning('Testcase does not have any requirements')
        else:
            requirement_list = requirements.findall('Requirement')
            if requirement_list is None:
                print_warning('Testcase does not have any requirement')
            else:
                for req in requirement_list:
                    req_id = req.text
                    if req_id is not None and req_id is not False:
                        req_id = req_id.strip()
                        req_id_list.append(req_id)

        if len(req_id_list) == 0:
            req_id_list = None

        return req_id_list

    def get_steps_list(self, testcase_filepath):
        """Takes the location of any Testcase xml file as input
        Returns a list of all the step elements present in the Testcase

        :Arguments:
            1. testcase_filepath    = full path of the Testcase xml file
        """

        step_list = []
        tc_root = self.xml_utils().getRoot(testcase_filepath)
        steps = tc_root.find('Steps')
        if steps is None:
            print_info('Testcase has no commands: tag <Steps> not found in the input file ')
        else:
            step_list = steps.findall('step')
            return step_list
