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

"""This is the library called iron claw which checks the
correctness of the xml schema for testcase, testuite, project xml files
of warrior framework """

import os
import time
import  Tools
import  ProductDrivers
import re
import WarriorCore.Classes.kw_driver_class as kw_driver_class
import WarriorCore.Classes.execution_files_class as execution_files_class
from Framework.Utils.print_Utils import print_info, print_debug, print_error,\
                                        print_exception, print_warning
from Framework.Utils import xml_Utils, file_Utils, testcase_Utils
from WarriorCore import testsuite_utils
try:
    from lxml.etree import parse, XMLSchema, XMLSyntaxError
except Exception as exception:
    print_exception(exception)


class IronClaw(object):
    """ IronClaw Class"""

    def __init__(self):
        """ Contructor """

        self.xsd_dir = Tools.__path__[0] + os.sep + 'xsd' + os.sep

    @staticmethod
    def xml_to_xsd_validation(file_xml, file_xsd):
        """ Verify that the XML compliance with XSD
        Arguments:
            1. file_xml: Input xml file
            2. file_xsd: xsd file which needs to be validated against xml
        Return:
            No return value
        """
        try:
            print_info("Validating:{0}".format(file_xml))
            print_info("xsd_file:{0}".format(file_xsd))
            xml_doc = parse(file_xml)
            xsd_doc = parse(file_xsd)
            xmlschema = XMLSchema(xsd_doc)
            xmlschema.assert_(xml_doc)
            return True

        except XMLSyntaxError as err:
            print_error("PARSING ERROR:{0}".format(err))
            return False

        except AssertionError, err:
            print_error("Incorrect XML schema: {0}".format(err))
            return False

    def testcase_prerun(self, tc_filepath, check_files_dict=None):
        """Executes prerun of a testcase file """
        print('\n')
        print_info('='*40)
        print_debug("Validating Test case xml")
        print_info('='*40)

        testcase_xsd_fullpath = self.xsd_dir + os.sep + 'warrior_testcase.xsd'
        #print_info("Test case_xsd_location: {0}".format(testcase_xsd_fullpath))

        tc_status = self.xml_to_xsd_validation(tc_filepath, testcase_xsd_fullpath)

        if tc_status:
            data_file_valid = self.check_tc_input_datafile(tc_filepath, check_files_dict)
            tc_status &= data_file_valid
            steps_field_valid = self.check_steps(tc_filepath)
            tc_status &= steps_field_valid
        else:
            print_error("Incorrect xml format")
        time.sleep(5)
        status = testcase_Utils.convertLogic(tc_status)
        print_info('TC STATUS: {0}ED'.format(status))

        return tc_status

    def testsuite_prerun(self, testsuite_filepath, root, check_files_dict=None):
        """Executes prerun of a testsuite file """
        print('\n')
        print_info('*'*40)
        print_debug("Validating Test suite xml")
        print_info('*'*40)

        testsuite_xsd_fullpath = self.xsd_dir + os.sep + 'warrior_suite.xsd'
        testsuite_status = self.xml_to_xsd_validation(testsuite_filepath, testsuite_xsd_fullpath)
        if testsuite_status:
            data_file_valid, check_files_dict = self.check_testsuite_input_datafile(\
                testsuite_filepath, check_files_dict)
            testsuite_status &= data_file_valid
            for testcase in root.iter('Testcase'):
                tc_path_rel = testsuite_utils.get_path_from_xmlfile(testcase)
                tc_path = file_Utils.getAbsPath(tc_path_rel,
                                                os.path.dirname(testsuite_filepath))
                time.sleep(5)
                if os.path.isfile(tc_path):
                    print('\n')
                    print_info('tc_path: {0}, Testcase file exists...'.format(tc_path))
                    tc_status = self.testcase_prerun(tc_path, check_files_dict)
                else:
                    print('\n')
                    tc_status = False
                    print_error('tc_path: {0}, Testcase file does not exist'.format(tc_path))
                    print_info('TC STATUS: {0}'.format('FAILED'))
                testsuite_status &= tc_status

        else:
            print_error("Incorrect xml format")

        time.sleep(5)
        print('\n')
        status = testcase_Utils.convertLogic(testsuite_status)
        print_info('SUITE STATUS: {0}ED'.format(status))

        return testsuite_status

    def project_prerun(self, project_filepath, root):
        """Executes prerun of a project file """

        print('\n')
        print_info('+'*40)
        print_debug("Validating Project xml")
        print_info('+'*40)
        project_xsd_fullpath = self.xsd_dir + os.sep + 'warrior_project.xsd'
        project_status = self.xml_to_xsd_validation(project_filepath, project_xsd_fullpath)
        if project_status:
            check_files_dict = self.check_proj_results_logsdir(project_filepath)
            for testsuite in root.iter('Testsuite'):
                testsuite_path_rel = testsuite_utils.get_path_from_xmlfile(testsuite)
                testsuite_path = file_Utils.getAbsPath(testsuite_path_rel,
                                                       os.path.dirname(project_filepath))

                if os.path.isfile(testsuite_path):
                    print('\n')
                    print_info("Testsuite_path: {0}, Testsuite"\
                               "file exists...".format(testsuite_path))
                    ts_root = xml_Utils.getRoot(testsuite_path)
                    tsuite_status = self.testsuite_prerun(testsuite_path, ts_root, check_files_dict)
                else:
                    print('\n')
                    tsuite_status = False
                    print_error('testsuite_path: {0},\
                                Testsuite file does not exist'.format(testsuite_path))
                    print_info('SUITE STATUS: {0}'.format('FAILED'))
                project_status &= tsuite_status

        else:
            print_error("Incorrect xml format")

        time.sleep(5)
        print('\n')
        status = testcase_Utils.convertLogic(project_status)
        print_info('PROJECT STATUS: {0}ED'.format(status))

        return project_status

    def check_steps(self, testcase_filepath):
        """validate the drivers and steps exist in the Warrior path,
        if there is no such module or
        if there is no any valid actions it will return false"""

        steps_list = testcase_Utils.get_steps_list(testcase_filepath)
        matching_list = []
        for step in steps_list:
            module_name = step.attrib["Driver"]

            try:
                driver_path = ProductDrivers.__path__[0] + os.sep + module_name + ".py"
                if not os.path.isfile(driver_path):
                    print_error("Driver file {0} does not exist".format(driver_path))
                    continue
                module_list = get_action_dirlist(driver_path)
                if len(module_list) == 0:
                    print_error("No Actions package/Module exist"\
                    "for the driver {0} ".format(driver_path))
                    continue
                package_list = self.import_modules(module_list)
                if len(package_list) > 0:
                    result = self.search_for_match(package_list, step.attrib["Keyword"],
                                                   step.attrib["Driver"])
                    if result is not None:
                        matching_list += result
            except IOError:
                print_error("No such package: {0}".format(module_name))
        #print len(matching_list), len(steps_list)
        if len(matching_list) == len(steps_list) != 0:
            return True
        else:
            return False

    @classmethod
    def import_modules(cls, module_list):
        """Import the actions modules for a driver """
        package_list = []
        try:
            for module_string in module_list:
                if module_string is not '':
                    package_list.append(__import__(
                        "%s"%module_string, fromlist=["Actions"]))
        except ImportError:
            print_error("No such module '{0}'".format(module_string))
        return package_list

    @classmethod
    def search_for_match(cls, package_list, keyword, driver_name):
        """Searches for method or keyword that matches
        the keyword and returns a matching list
        Returns None of no match/duplicates found """

        drv_obj = kw_driver_class.ModuleOperations(package_list, keyword)

        search_result_list = drv_obj.matching_method_list + drv_obj.matching_function_list
        if len(search_result_list) == 1:
            print_info("Found one matching method/function for "\
                       "keyword '{0}'".format(keyword))
        elif len(search_result_list) == 0:
            print_info("There is no matching keyword: '{0}' "\
            "for the Driver: '{1}'".format(keyword,
                                           driver_name))
            search_result_list = None
        elif len(search_result_list) > 1:
            print_info("More than one method/function of same name: '{0}' "\
            "exists for the Driver: '{1}'".format(keyword,
                                                  driver_name))
            search_result_list = None

        return search_result_list

    @classmethod
    def check_tc_input_datafile(cls, testcase_filepath, check_files_dict):
        """ Verify that the input data file exists in the path provided.
            If path not provided verify the default data file

        Arguments:
              1. testcase_filepath: testcase path will be parsed as input for checking
                 Input data
              2. check_files_dict: a dict element to check the status of files
                 whether it has been verified already or not

        Return:
              1. result(bool): if the Datafiles exist, returns True: else False
        """
        if check_files_dict is None:
            check_files_dict = {}
            check_files_dict['check_datafile'] = None
            check_files_dict['check_resultsdir'] = None
            check_files_dict['check_logsdir'] = None

        result = []
        if check_files_dict['check_datafile'] is not True:
            result, check_files_dict = cls.__check_input_datafile(testcase_filepath,
                                                                  'Testcase', check_files_dict)

        if check_files_dict['check_resultsdir'] is not True:
            cls.__check_dir_exists(testcase_filepath, 'Resultsdir')
        if check_files_dict['check_logsdir'] is not True:
            cls.__check_dir_exists(testcase_filepath, 'Logsdir')

        if False in result:
            return False
        else:
            return True

    @classmethod
    def check_testsuite_input_datafile(cls, testsuite_filepath, check_files_dict):
        """ Verify that the input data file exists in the path provided.

        Arguments:
              1. testsuite_filepath: testsuite path will be parsed as input for checking
                 Input data
              2. check_files_dict: a dict element to check the status of files
                 whether it has been verified already or not

        Return:
              1. result(bool): if the Datafiles exist, returns True: else False
              2. check_files_dict: a dict element to check the status of files
                 whether it has been verified already or not
        """

        if check_files_dict is None:
            check_files_dict = {}
            check_files_dict['check_datafile'] = None
            check_files_dict['check_resultsdir'] = None
            check_files_dict['check_logsdir'] = None

        result, check_files_dict = cls.__check_input_datafile(testsuite_filepath,
                                                              'Testsuite', check_files_dict)

        if check_files_dict['check_resultsdir'] is not True:
            cls.__check_dir_exists(testsuite_filepath, 'Resultsdir')

        if check_files_dict['check_logsdir'] is not True:
            cls.__check_dir_exists(testsuite_filepath, 'Logsdir')

        check_files_dict['check_resultsdir'] = True
        check_files_dict['check_logsdir'] = True
        if False in result:
            return False, check_files_dict
        else:
            return True, check_files_dict

    @classmethod
    def check_proj_results_logsdir(cls, project_filepath):
        """ Verify that the result and logs directory exists in the path provided.

        Arguments:
              1. project_filepath: project path will be parsed as input for checking
                         Input data

        Return:
              1. check_files_dict: a dict element to check the status of files
                 whether it has been verified already or not
        """

        check_files_dict = {}
        cls.__check_dir_exists(project_filepath, 'Resultsdir')
        cls.__check_dir_exists(project_filepath, 'Logsdir')

        check_files_dict['check_resultsdir'] = True
        check_files_dict['check_logsdir'] = True
        return check_files_dict

    @classmethod
    def __check_dir_exists(cls, filepath, dirtag):
        """ Verify that the directory exists in the path provided.

        Arguments:
              1. filepath: file path will be parsed as input for checking
                 directories
              2. dirtag: directory tag that used to get directory path
        """

        dirt = xml_Utils.getChildTextbyParentTag(filepath, 'Details', dirtag)
        directory = file_Utils.getAbsPath(dirt, os.path.dirname(filepath))

        if directory is not False and directory is not None:
            print_info("{0} path {1}".format(dirtag, directory))
            if not os.path.exists(directory):
                print_warning("Directory does not exist in location {0}."\
                "\nWarrior framework will try to create the directory, if creation "\
                "fails then default warriorspace will be used to collect logs/results"\
                .format(directory))
        else:
            if dirtag is 'Resultsdir':
                print_info("Default directory in Warriorspace will be used to collect results")
            else:
                print_info("Default directory in Warriorspace will be used to collect logs")

    @classmethod
    def __check_input_datafile(cls, filepath, testname, check_files_dict):
        """ Verify that the input data file exists in the path provided.
            If path not provided verify the default data file

        Arguments:
              1. filepath: filepath will be parsed as input for checking
                 Input data
              3. testname: to mention whether it is Testcase/Testsuite datafile
              2. check_files_dict: a dict element to check the status of files
                 whether it has been verified already or not

        Return:
              1. result(bool): if the Datafiles exist, returns True: else False
              2. check_files_dict: a dict element to check the status of files
                 whether it has been verified already or not
        """

        result = []

        input_data_file = xml_Utils.getChildTextbyParentTag(filepath, 'Details',
                                                            'InputDataFile')
        if input_data_file is not False and input_data_file is not None:
            if testname is 'Testsuite':
                check_files_dict['check_datafile'] = True
            input_data_file = str(input_data_file).strip()
            if str(input_data_file).upper() == 'NO_DATA':
                print_info('No_Data option selected for this testcase')
                result.append(True)

            elif 'NO_DATA' not in str(input_data_file).upper():

                data_file_path = file_Utils.getAbsPath(input_data_file,
                                                       os.path.dirname(filepath))
                print_info("{0} input data_file_path: {1}".format(testname, data_file_path))
                if os.path.exists(data_file_path):
                    print_info("{0} Input datafile is present "\
                                "in location {1}".format(testname, data_file_path))
                    result.append(True)
                else:
                    print_error("{0} Input datafile is NOT "\
                                 "present in location {1}".format(testname, data_file_path))
                    result.append(False)

        elif input_data_file is None or input_data_file is False:
            if testname is 'Testcase':
                print_info("InputDataFile is not provided,"\
                           "checking if default InputDataFile exists....")
                default_datafilepath = execution_files_class.get_default_xml_datafile(\
                    filepath)
                print_debug("default_datafile_path: {0}".format(default_datafilepath))
                if os.path.exists(default_datafilepath):
                    print_info("Default input datafile for the Testcase is available")
                    result.append(True)
                else:
                    print_error("Default input datafile for the Testcase is NOT available")
                    result.append(False)
            else:
                check_files_dict['check_datafile'] = False

        return result, check_files_dict


def get_action_dirlist(driverpath):
    """ Get the list of action directories """
    actions_package_list = []
    try:
        if os.path.isfile(driverpath):
            lines = []
            with open(driverpath, 'r') as fobj:
                lines = fobj.readlines()
            lines_as_string = ''.join(lines)
            search_string = re.compile(r'package_list.*=.*\]', re.DOTALL|re.MULTILINE)
            match = re.search(search_string, lines_as_string)

            if match:
                match_string = match.group()
                actions_package_list = match_string.split('[')[1].split(']')[0].split(',')

            return actions_package_list
        else:
            print("file {0} does not exist".format(driverpath))
            return actions_package_list
    except Exception as exception:
        print_exception(exception)
    return actions_package_list
