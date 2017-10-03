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
from WarriorCore.Classes.ironclaw_class import IronClaw
from Framework.Utils.print_Utils import print_info, print_error
from Framework.Utils import xml_Utils, file_Utils, testcase_Utils
from xml.etree import ElementTree


def iron_claw_warrior_xml_files(filepath):
    """Validate Warrior xml files (Testcase/Testsuite/Project) against
    their xsd schema files """
    try:
        root = xml_Utils.getRoot(filepath)
    except ElementTree.ParseError, err:
        print_error("PARSING ERROR:{0}".format(err))
        return False
    ironclaw_object = IronClaw()

    if root.tag == 'Testcase':
        result = ironclaw_object.testcase_prerun(filepath)
    if root.tag == 'TestSuite':
        result = ironclaw_object.testsuite_prerun(filepath, root)
    if root.tag == 'Project':
        result = ironclaw_object.project_prerun(filepath, root)

    return result

def main(parameter_list):
    """Check the validity of testcase/testuite/project xml files """
    valid = True
    print_info("="*10 + "PRE-RUN XML VALIDATION"+ "="*10 + "\n")
    if len(parameter_list) > 0:
        for parameter in parameter_list:
            # check if the input parameter is an xml file
            if file_Utils.get_extension_from_path(parameter) == '.xml':
                filepath = parameter
                abs_filepath = file_Utils.getAbsPath(filepath, os.curdir)
                res = iron_claw_warrior_xml_files(abs_filepath)
                result = testcase_Utils.convertLogic(res)
                valid &= res
                print_info("File '{0}' '{1}ED' Warrior prerun"\
                           "validation".format(abs_filepath, result))
            else:
                print_error("Provided file '{0}' is not an xml file".format(parameter))
    else:
        print_error("No input files provided to be validated")
        valid = False
    print '\n'
    print_info("Validation Completed:")
    if valid:
        print_info("Files are compatible with WARRIOR \n")

    else:
        print_error("Files failed Warrior Ironclaw validation\n")
    return valid


    