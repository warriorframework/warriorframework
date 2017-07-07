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

from Framework.Utils import xml_Utils
from Framework.Utils.print_Utils import print_warning


def get_robot_xml_files(input_list):
    """
    Get robot xml files from the list of files.
    :Arguments:
        1. input_list(list) - list of file names
    :Return:
        1. output_list(list) - list of robot xml files
    """

    output_list = []
    if input_list:
        for filename in input_list:
            try:
                root = xml_Utils.getRoot(filename)
                if root.tag == 'robot':
                    output_list.append(filename)
            except Exception:
                print_warning("{} is not a valid xml file".format(filename))

    return output_list


def get_results_from_robot_xml(xml_file):
    """
    Get the required values from the robot xml results file 
    """

    suite_node_list = xml_Utils.getElementListWithSpecificXpath(xml_file, './/suite[@source]')
