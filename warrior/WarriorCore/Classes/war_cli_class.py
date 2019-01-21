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

"""This is the class for handling and executing input args"""

import argparse
import xml.etree.ElementTree as ET
import datetime, time
import os
import Framework.Utils as Utils
from Framework.Utils.print_Utils import print_error, print_info
import WarriorCore.Classes.manual_defect_class as manual_defect_class

class WarriorCliClass(object):
    """Handle the command line input for warrior"""
    # Class variable for warmock functionality
    mock = False
    sim = False

    def __init__(self):
        """empty constructor"""
        return None

    @classmethod
    def gosleep(cls, target_time):
        """sleep until target_time,
        need to be modified so window doesn't freeze"""
        try:
            target_time = datetime.datetime.strptime(
                target_time, '%Y-%m-%d-%H-%M-%S')
            current_time = datetime.datetime.now().replace(microsecond=0)
            if target_time >= current_time:
                print_info('warrior will sleep until ' + str(target_time))
                print_info('please do not close this window')
                time.sleep((target_time-current_time).total_seconds())
                print_info('warrior is now awake')
            else:
                print_info('Please enter a future time')
                exit(1)
        except ValueError:
            print_error('Please enter a legit time in yyyy-mm-dd-hh-mm-ss format')
            exit(1)

    @classmethod
    def check_xml(cls, files):
        """return list of valid testcase xml files"""
        if isinstance(files, str):
            files = list(files)
        result = []
        for xmlfile in files:
            xmlfile_abspath = Utils.file_Utils.getAbsPath(xmlfile, os.curdir)
            if Utils.file_Utils.get_extension_from_path(xmlfile_abspath) == ".xml":
                if Utils.xml_Utils.getRoot(xmlfile_abspath).tag == 'Testcase':
                    result.append(xmlfile_abspath)
                else:
                    print_info(xmlfile_abspath + " is not a valid testcase xml")
            else:
                print_info(xmlfile_abspath + " is not a xml file")
        return result

    def check_tag(self, category_list, dirlist):
        """return list of valid testcase xml
        files with the correct category tag"""
        result = []
        cur_dir = os.path.abspath(os.getcwd())
        if dirlist is None:
            dirlist = [cur_dir]

        for folder in dirlist:
            os.chdir(cur_dir)
            folder = Utils.file_Utils.getAbsPath(folder, os.curdir)
            if os.path.isdir(folder):
                all_files = [Utils.file_Utils.getAbsPath(f, folder)
                             for f in os.listdir(folder)]
                is_xml_files = self.check_xml(all_files)
                for xmlfile in is_xml_files:
                    root = Utils.xml_Utils.getRoot(xmlfile)
                    detail = root.find('Details')
                    if detail is not None:
                        if detail.find('Category') is not None:
                            cat_text = detail.find('Category').text.strip()
                            cat_text = cat_text.split(",")
                            if len(set(category_list) & set(cat_text)) > 0:
                                result.append(xmlfile)
            else:
                print_error(str(folder) + "is not a directory")
        print_info("Number of matching testcases: {0}".format(len(result)))
        return result

    def examine_create_suite(self, namespace):
        """do the check for create testsuite"""
        tc_list = []

        if namespace.suite_dest is None:
            namespace.suite_dest = os.path.abspath(os.curdir)

        if Utils.file_Utils.dirExists(namespace.suite_dest):
            suite_dest = Utils.file_Utils.getAbsPath(namespace.suite_dest,
                                                     os.curdir)
            if namespace.cat is not None:
                tc_list += self.check_tag(namespace.cat, namespace.tcdir)
            else:
                if len(namespace.filepath) < 1:
                    print_error("Provide at least one test case xml file "\
                                "in the CLI command to create suite")
                    exit(1)
                tc_list += self.check_xml(namespace.filepath)
        else:
            print_error("Directory '{0}' does not exist".format(namespace.suite_dest))
            exit(1)
        if len(tc_list) == 0:
            print_error("No matching Testcases found (or) None of the provided xml "\
                        "files are valid testcases")
            exit(1)

        dest_suite_path = os.path.join(suite_dest, namespace.suitename)
        if not dest_suite_path.endswith('.xml'):
            dest_suite_path = dest_suite_path + '.xml'

        suite = CreateTestSuite(dest_suite_path, namespace.suitename, tc_list)
        suite.create_suite()
        return suite.output_file()

    def examine_cli_args(self, cli_args, namespace):
        """validate the cli_args and the needed files"""
        if len(namespace.filepath) < 1:
            print_error("Provide at least one test case xml file in the CLI command")
            exit(1)

        if sum(cli_args[:2]) < 2 and sum(cli_args[2:4]) < 2 and\
        not (any(cli_args[2:4]) and any(cli_args[4:])) and\
        not (any(cli_args[4:]) and cli_args[0]) and not all(cli_args[4:]):
            # Everything is legit in here
            kw_type = "sequential_keywords"
            if namespace.kwparallel:
                kw_type = "parallel_keywords"

            tc_type = "sequential_testcases"
            val = 0
            if namespace.tcparallel:
                tc_type = "parallel_testcases"
            elif namespace.RUF > 0:
                tc_type = "Run_Until_Fail"
                val = namespace.RUF
            elif namespace.RMT > 0:
                tc_type = "Run_Multiple"
                val = namespace.RMT

            tc_list = self.check_xml(namespace.filepath)
            if len(tc_list) > 0:
                suite_name = "custom_" + os.path.splitext(
                    os.path.split(namespace.filepath[0])[1])[0]
                suite_dir = os.path.join(
                    os.path.dirname(os.path.dirname(
                        os.path.abspath(namespace.filepath[0]))), "Suites")
                if Utils.file_Utils.dirExists(suite_dir):
                    suite_dest = os.path.join(suite_dir, suite_name + ".xml")
                else:
                    # if not, create the file in the same directory
                    suite_dest = os.path.join(os.path.dirname(
                        namespace.filepath[0]), suite_name + ".xml")
                suite = CreateTestSuite(suite_dest, suite_name, tc_list)
                suite.create_suite({"tc_type":tc_type, "kw_type":kw_type, "val":val})
                filepath = suite.output_file()
            else:
                print_error("None of the provided xml files are valid testcases")
                exit(1)
        else:
            print_error("**********\nWrong combination of CLI arguments,"\
                            " please choose only one testcase exec_type"\
                            " and one keyword exec_type, Warrior CLI commands"\
                            " does not support RMT and RUF with exec_type=parallel_keywords"\
                            "\n**********")
            exit(1)
        return filepath

    @staticmethod
    def manual_defects(path_type, paths, jiraproj=None):
        """Method to handle creating jira defects manually using cli command """
        defect_object = manual_defect_class.ManualDefectClass(path_type, jiraproj=jiraproj)
        defect_object.manual_defects(paths)

    @classmethod
    def parser(cls, arglist):
        """add rules about how to parse the inpurt args"""
        parser = argparse.ArgumentParser()

        # Display version and framework details
        parser.add_argument('--version', action='store_true', default=False,
                            help=':version: Help the user with Current Warrior version and other Warrior package details ')


        # schedule sleep
        parser.add_argument('-schedule', action='store', dest='target_time',
                            nargs='?', help=":schedule execution: Schedule Warrior "\
                            "execution to the specified time. "\
                            "Enter future time in yyyy-mm-dd-hh-mm-ss format")

        # create a testsuite xml file
        parser.add_argument('-cs', action="store_true", default=False,
                            dest="create", help=":create test suite: cli command to "
                            "create a Warrior testsuite xml, "\
                            "Use with -suitename(mandatory), list of testcase xml files "\
                            "(mandatory when -category is not used), "\
                            "-suitelocn(optional), -category(optional), -tcdir(optional)")

        # -runcat : execute testcases of particular category
        parser.add_argument('-runcat', nargs='*',
                            help=":run test cases of specific category: Enter list of test case "\
                            "category(ies) to be "\
                            "searched for (space seperated). "
                            "Additional arguments -tcdir(optional), "\
                             "-suitename(optional), -suitelocn(optional)   "\
                             "Format:- './Warrior -runcat [<category1> <category2>]"\
                             "-tcdir [<dir1> <dir2>] -suitename <suitename> "\
                             "-suitelocn <suite destination path> ")

        # arguments related to -createsuite and -runcat
        parser.add_argument('-suitename', nargs='?',
                            help=":suite name: Enter name of the suite to be created.\n"
                            "Used with -createsuite/-runcat. Format:- -suitename <testsuite name>")

        parser.add_argument('-suitelocn', action="store", nargs='?', dest="suite_dest",
                            help=":suite location: Enter location where the "\
                            "testsuite will be created, "\
                            "defaulted to current working directory. "\
                            "Used with -createsuite/-runcat. "\
                            "Format:- -suitelocn <dest directory to testsuite xml file>")

        parser.add_argument('-tcdir', nargs='*',
                            help=":testcase directories: Enter list of directories to search for "\
                            "testcase xml files (space seperated). "\
                            "Used with -creatsuite/-runcat. Format:- -tcdir [<dir1> <dir2>]")

        parser.add_argument('-cat', nargs='*',
                            help=":category: Enter list of test case category(ies) to be "\
                            "searched for (space seperated). "
                            "Used with -creatsuite. Format:- -category [<cat1> <cat2>]")


        # main functionality
        parser.add_argument('filepath', nargs='*',
                            help="Enter the testcase/testsuite/project xml files "\
                            "to be executed by Warrior. "\
                            "Multiple files of different type can be provided "\
                            "(separated by a space)")

        # Run Ironclaw tool
        parser.add_argument('-ironclaw', action='store_true', default=False,
                            help=":ironclaw: Run Warrior's IronClaw tool. "
                            "Validates the Warrior xml(testcase/testsuite/project) files")

        # CLI arguments
        parser.add_argument('-kwparallel', action='store_true', default=False,
                            help=":keyword parallel: Set keyword exec_type to parallel")

        parser.add_argument('-kwsequential', action='store_true', default=False,
                            help=":keyword sequential: Set keyword exec_type to sequential")

        parser.add_argument('-tcparallel', action='store_true', default=False,
                            help=":testcase parallel: Set testcase exec_type to parallel")

        parser.add_argument('-tcsequential', action='store_true', default=False,
                            help=":testcae sequential: Set testcase exec_type to sequential")

        parser.add_argument('-RMT', type=int, default=0,
                            help=" :run multiple times: Set testcase exec_type to run multiple times,"\
                            " Enter value for number of attempts after tag")

        parser.add_argument('-RUF', type=int, default=0,
                            help=" :run until fail:  set testcase exec_type to run until fails,"\
                            "Enter value for number of attempts after tag")

        # defects parsing
        parser.add_argument('-ad', action='store_true', default=False,
                            help=":autodefects:  "\
                            "Automatically creates bugs in jira for failing keywords. "\
                            "Takes -jiraproj as optional argument."\
                            "When used with -jiraproj creates jira bugs "\
                            "against the provided jira project from the "
                            "jira config file. "\
                            "If -jiraproj tag is not provided, creates jira bug against the "\
                            "default project from the jira config file."\
                            "Default project:- Is the first proj marked default='true', "\
                            "in the jira config file. If no projects are marked default='true' "\
                            "it is first project in the jira config file."\
                            "jira config file location = Tools/jira/jira_config.xml.")

        parser.add_argument('-ujd', action='store_true', default=False,
                            help=":upload jira defects: Manually upload "\
                            "defects/bugs to jira using "\
                            "cli command. Used with either -ddir or -djson. "\
                            "Takes -jiraproj as an optional argument")

        parser.add_argument('-ddir', action='store', nargs='*',
                            help=":defect directories: Used with -ujd, "\
                            "a list of all defects directories")

        parser.add_argument('-djson', action='store', nargs='*',
                            help=':defect json: Used with -ujd, a list of defect josn files')

        parser.add_argument('-jiraproj', action='store', nargs='?',
                            help=":jira project: Represents the name of "\
                            "jira project jira config file. "
                            "Used with -ad or -ujd. When provided with -ad or -jd jira bugs "\
                            "will be created against the "\
                            "provided project instead of default jira project."\
                            "jira config file location = Tools/jira/jira_config.xml.")

        parser.add_argument('-datafile', action='store', nargs='?',
                            help="overwrite the path of datafile in execution "\
                            "ignore the datafile specified in testcase.xml")
        #to accept -wrapperfile as command line argument
        parser.add_argument('-wrapperfile', action='store', nargs='?',
                            help="overwrite the path of wrapperfile in execution "\
                            "when specified in command line skips the wrapperfile "\
                            "in testcase.xml and suite.xml")
 
        parser.add_argument('-resultdir', action='store', nargs='?',
                            help="overwrite the path of result directory in execution "\
                            "ignore the result directory specified in testcase.xml")

        parser.add_argument('-logdir', action='store', nargs='?',
                            help="overwrite the path of log directory in execution "\
                            "ignore the log directory specified in testcase.xml")

        parser.add_argument('-outputdir', action='store', nargs='?',
                            help="overwrite the path of log directory and result directory "\
                            "in execution ignore the log directory specified in testcase.xml")

        parser.add_argument('-jobid', action='store', nargs='?',
                            help="create a property in test junit files which name is "\
                            "resultlocation and value is <job_url<url>> + <jobid>")

        parser.add_argument('-encrypt', action='store', nargs='*', dest="encrypt", help="encrypt data string")

        parser.add_argument('-decrypt', action='store', nargs='*', dest="decrypt", help="decrypt data string")

        # Run Testcases/Suites/Projects in default locations
        parser.add_argument('-wt', action='store', nargs='*', dest="tc_name",
                            help="Runs testcases available in default path, "\
                            "Warrior/Warriorspace/Testcases/. User need not give entire path. "\
                            "Format: ./Warrior -wt sample_test.xml."\
                            " Multiple file names can be provided "\
                            "(separated by a space)")

        parser.add_argument('-ws', action='store', nargs='*', dest="ts_name",
                            help="Runs testsuites available in default path, "\
                            "Warrior/Warriorspace/Suites/. User need not give entire path. "\
                            "Format: ./Warrior -ws sample_suite.xml."\
                            " Multiple file names can be provided "\
                            "(separated by a space)")

        parser.add_argument('-wp', action='store', nargs='*', dest="proj_name",
                            help="Runs project available in default path, "\
                            "Warrior/Warriorspace/Projects/. User need not give entire path. "\
                            "Format: ./Warrior -wp sample_suite.xml."\
                            " Multiple file names can be provided "\
                            "(separated by a space)")

        parser.add_argument('-secretkey', action='store', default=False,
                            help=":secretkey: It should be used along with the "
                                 "encrypt command to create a secret key"\
                            "...")

        # Update jira issue based on input ID and detail
        parser.add_argument('-jiraid', action='store', default=False,
                            help="The issue that will be updated based on current execution result")

        parser.add_argument('-dbsystem', action='store', nargs='?',
                            help=":dbsystem: Represents the name of database "\
                            "server in the database config file, both html " \
                            "and xml results will be stored in this " \
                            "database server, database config file " \
                            "location = Tools/database/database_config.xml.")

        #Running Warrior in Mock mode and Test mode
        parser.add_argument('-mock', action='store_true', default=False,
                            help=":mock mode: In this mode, connection to server "\
                            "will be mocked (won't actually connect) and keywords will run. "\
                            "User can verify input value from console output/result file")

        #Running Warrior in Mock mode and Test mode
        parser.add_argument('-sim', action='store_true', default=False,
                            help=":mock mode: In this mode, connection to server "\
                            "will be mocked (won't actually connect) and keywords will run. "\
                            "A response file can be specified in testdata file inside global tag."\
                            "Instead of actual server response, Warrior will use the response "\
                            "in the response file to do command verification"\
                            "or other CLI related operation."
                            "User can verify input value from console output/result file")

        parser.add_argument('-headless', action='store_true', default=False,
                            help="If headless mode is enabled, all selenium tests will run in xfvb "\
                            "which will not need a GUI")

        namespace = parser.parse_args(arglist)
        #see if the below line is requried
        if namespace.mock:
            WarriorCliClass.mock = True
        if namespace.sim:
            WarriorCliClass.sim = True
        return namespace

class CreateTestSuite(object):
    """create testsuite xml file"""
    def __init__(self, suite_path, filename, tc_list):
        """Constructor to intialize default values for creating a suite """
        self.suite_dest = suite_path
        self.suitename = filename
        self.tc_list = tc_list
        self.root = ET.Element('TestSuite')
        self.detail = self.create_element("Details", {}, "")
        self.requirement = self.create_element("Requirements", {}, "")
        self.testcases = self.create_element("Testcases", {}, "")

    @classmethod
    def create_element(cls, name="", attr=None, value=None):
        """create an xml element with a given name,
        a dict of attribute and the value inside"""
        if attr is None:
            attr = {}
        if value is None:
            value = ""
        elem = ET.Element(name)
        for key, val in attr.items():
            elem.set(str(key), val)
        elem.text = value
        return elem

    def create_suite(self, extra_arg=None):
        """ create the main structure of the result testsuite file"""
        tc_type = "sequential_testcases"
        kw_type = "sequential_keywords"
        val = 0
        if extra_arg is not None:
            if extra_arg.get("tc_type") is not None:
                tc_type = extra_arg.get("tc_type")
            if extra_arg.get("kw_type") is not None:
                kw_type = extra_arg.get("kw_type")
            if extra_arg.get("val") is not None:
                val = extra_arg.get("val")
        self.create_details(self.suitename, {"tc_type":tc_type, "val":val})
        self.create_requirements()
        self.create_testcases(self.tc_list, kw_type)

    def create_details(self, filename, extra_arg=None):
        """ create the details part of the result testsuite file"""
        detail = self.detail
        tc_type = extra_arg.get("tc_type")
        val = extra_arg.get("val")

        detail.append(self.create_element("Name", {}, filename))
        detail.append(self.create_element("Title", {}, filename))
        detail.append(self.create_element("Engineer", {}, ""))
        detail.append(self.create_element("Date", {},
                                          datetime.datetime.now().strftime("%m/%d/%Y")))
        detail.append(self.create_element("Time", {},
                                          datetime.datetime.now().strftime("%H:%M:%S")))
        if tc_type == "Run_Until_Fail":
            detail.append(self.create_element("type",
                                              {"Max_Attempts":str(val),
                                               "exectype":tc_type}, ""))
        elif tc_type == "Run_Multiple":
            detail.append(self.create_element("type",
                                              {"Number_Attempts":str(val),
                                               "exectype":tc_type}, ""))
        else:
            detail.append(self.create_element("type",
                                              {"exectype":tc_type}, ""))
        detail.append(self.create_element("default_onError",
                                          {"action":"next"}, ""))
        detail.append(self.create_element("Resultsdir", {}, ""))

        self.root.append(detail)

    def create_testcase(self, path, kw_type="sequential_keywords"):
        """create the testcase part for one test case
        of the result testsuite file"""

        testcase = ET.Element('Testcase')
        testcase.append(self.create_element("path", {}, path))
        testcase.append(self.create_element("context", {}, "positive"))
        testcase.append(self.create_element("runtype", {}, kw_type))
        testcase.append(self.create_element("onError", {"action":"next", "value":""}, ""))
        testcase.append(self.create_element("impact", {}, "impact"))
        return testcase

    def create_testcases(self, tc_path_list, kw_type):
        """ scan each testcase files and add it under the testcases element"""
        testcases = self.testcases
        for path in tc_path_list:
            testcases.append(self.create_testcase(path, kw_type))
        self.root.append(testcases)

    def create_requirements(self):
        """create a requirement tag, will add requirement in the future"""
        self.root.append(self.create_element("Requirements", {}, ""))

    def output_file(self):
        """output the xml file"""
        path = self.suite_dest
        #path = Utils.file_Utils.addTimeDate(self.suite_dest)
        filename = os.path.basename(path)
        self.root.find('Details').find('Name').text = Utils.file_Utils.getNameOnly(filename)
        ET.ElementTree(self.root).write(path)
        return [path]
