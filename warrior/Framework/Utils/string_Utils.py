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

"""This is the library to hold all api's related to string operations """

from Framework.ClassUtils.configuration_element_class import ConfigurationElement
from Framework.Utils.print_Utils import print_info, print_error, print_exception

import re
import difflib
from xml.etree import ElementTree

def strip_white_spaces(input_list):
    """Takes a list of string as input
    Removes the leading and trailing white spaces from each string in the list
    Returns an output list having the string elements with leading and trailing
    white spaces removed
    """

    output_list = []
    for element in input_list:
        if type(element) is str:
            element = element.strip()
        output_list.append(element)

    return output_list

def replace_from_varconfig(varconfigfile, details_dict, var_sub=None):
    """
    replace variables with values from variable config file
    """
    if varconfigfile is not None or var_sub is not None:
        details_dict["command_list"] = sub_from_varconfig(varconfigfile,
                                                          details_dict["command_list"],
                                                          var_sub)
        details_dict["startprompt_list"] = sub_from_varconfig(varconfigfile,
                                                              details_dict["startprompt_list"],
                                                              var_sub)
        details_dict["endprompt_list"] = sub_from_varconfig(varconfigfile,
                                                            details_dict["endprompt_list"],
                                                            var_sub)

    return details_dict

def return_quote(a, start_pat="${", end_pat="}"):
    """
        return the list of element that needs to be substituted in a string
    :param a:
    :return:
    """
    mode = 0
    start = 0
    count = 0
    result = []
    for index in range(len(a)):
        if mode == 0 and a[index:index+len(start_pat)] == start_pat:
            mode = 1
            start = index+len(start_pat)
            count += 1
        elif mode == 1 and a[index:index+len(start_pat)] == start_pat:
            count += 1
        elif mode == 1 and a[index:index+len(end_pat)] == end_pat:
            count -= 1
            if count == 0:
                result.append(a[start:index])
                mode = 0
    return result

def sub_from_varconfig(varconfigfile, string_list, var_sub=None, start_pat="${", end_pat="}"):
    """
    Replaces the string variables with their values taken from varconfig_file.
    :Arguments:
        1. varconfigfile - xml file or list of xml files from which the values will be taken
        for subtitution
        2. string_list - List of command strings, where the variables will be replaced by
        the config values
        3. var_sub(string) = the pattern [var_sub] in the testdata commands,
                                 start_prompt, end_prompt, verification search
                                 will substituted with this value.
    :Returns:
        1. List of command strings with replaced values or\
           False(boolean) - if any one of the variables does not exist in varconfig_file
    """
    newstring_list = []
    for i, string in enumerate(string_list):
        vc_file = varconfigfile[i] if isinstance(varconfigfile, list) else varconfigfile
        if string and var_sub is not None:
            string = sub_from_varsub(string, var_sub)
            if string and vc_file is not None:
                newstring = sub_from_varconfigfile(string, vc_file, start_pat, end_pat)
                newstring_list.append(newstring)
            else:
                newstring_list.append(string)
        else:
            if string and vc_file is not None:
                newstring = sub_from_varconfigfile(string, vc_file, start_pat, end_pat)
                newstring_list.append(newstring)
            else:
                newstring_list.append(string)

    return newstring_list


def sub_from_wdf(datafile, string_list, td_sys_list=None, kw_system_name=None):
    """
    substitute the patterns $wdf{} in the command/verify parameters
    with the values form the datafile
    """
    from Framework.Utils.data_Utils import getSystemData
    newstring_list = []
    for i in range(0, len(string_list)):
        string = string_list[i]
        td_sys = None if td_sys_list is None else td_sys_list[i]
        found = True
        while found:
            if string:
                match = re.search(r"(\$wdf\{)([^\}]*)(\})", string, re.IGNORECASE)
                if match is not None:
                    found = True
                    try:
                        wdf_match = match.group(0).strip("$wdf{")
                        wdf_match = wdf_match.strip("}")
                        system_or_subsystem = wdf_match.split(".")[0].strip()
                        if system_or_subsystem == "kw_system" or system_or_subsystem == "current_system":
                            system_or_subsystem = kw_system_name
                        elif system_or_subsystem == "target_system":
                            system_or_subsystem = td_sys if td_sys is not None else kw_system_name
                        tag_or_attr = wdf_match.split(".")[1].strip()
                        value = getSystemData(datafile, system_or_subsystem, tag_or_attr)
                        if not value:
                            print_error("Value for '{0}' not provided in the datafile={1}"\
                                        "under the system_or_subsystem = {2}".format(tag_or_attr,
                                                                                     datafile,
                                                                                     system_or_subsystem))
                    except Exception as err:
                        print_error("Incorrect format provided for substituting value"\
                                    "from warrior datafile in the test data file")
                        print_error("Correct format is $wdf{system_or_subsystemname.tag_or_attribute_name}")

                    else:
                        string = string.replace(match.group(0), value)
                else:
                    found = False
            else:
                found = False
        newstring_list.append(string)

    return newstring_list



def sub_from_varsub(string, var_sub):
    """Replace the pattern [var_sub] in the string
    with the value of var_sub

    :Arguments:
        1. string(string) = input string which needs substitution
        3. var_sub(string) = value to replace the pattern [var_sub]
                             in the input string
    :Returns:
        1. updated string
    """
    match = re.search(r".*(\[(var_sub)\]).*", string, re.IGNORECASE)
    if match is not None:
        string = string.replace(match.group(1), var_sub)

    return string

def sub_from_varconfigfile(string, varconfigfile, start_pat="${", end_pat="}"):
    """ """
    try:
        # when varconfigfile is an XMl object(root element) - this happens
        # only when varconfigfile is taken from database server
        if isinstance(varconfigfile, ElementTree.Element) is True:
            cfg_elem_obj = ConfigurationElement("Varconfig_from_database",
                                                start_pat, end_pat)
            cfg_elem_obj.parse_data(varconfigfile, elem_type="xml_object")
        else:
            cfg_elem_obj = ConfigurationElement(varconfigfile, start_pat, end_pat)
            cfg_elem_obj.parse_data(varconfigfile)
        newstring = cfg_elem_obj.expand_variables(string)
    except TypeError as exception:
        print_info("At least one of the variables in command string is not found in  " + varconfigfile)
        #print_exception(exception)
        return False
    return newstring

def get_list_from_varconfigfile(string, varconfigfile, start_pat="${", end_pat="}"):
    """ """
    try:
        # when varconfigfile is an XMl object(root element) - this happens
        # only when varconfigfile is taken from database server
        if isinstance(varconfigfile, ElementTree.Element) is True:
            cfg_elem_obj = ConfigurationElement("Varconfig_from_database",
                                                start_pat, end_pat)
            cfg_elem_obj.parse_data(varconfigfile, elem_type="xml_object")
        else:
            cfg_elem_obj = ConfigurationElement(varconfigfile, start_pat, end_pat)
            cfg_elem_obj.parse_data(varconfigfile)
        newstring = cfg_elem_obj.get_list(string)
    except TypeError as exception:
        print_info("At least one of the variables in command string is not found in  " + varconfigfile)
        #print_exception(exception)
        return False
    return newstring


def text_compare(text1, text2, output_file):
    """
        Compares two strings and if they match returns True
        else writes the difference to the output_file.
    """
    if text1 == text2:
        return True
    diff = list(difflib.Differ().compare(text1.split(), text2.split()))
    te = open(output_file, 'w')
    for line in diff:
        te.write(line+"\n")
    te.close()
    return False

def compare_string_using_regex(response, list_of_regex_patterns):
    """
        Checks whether each regular expression is present in response
        and if all are present returns True else False
    """
    status = True
    for regex_pattern in list_of_regex_patterns:
        pattern = regex_pattern.strip("regex=")
        match = re.search(pattern, response)
        if not match:
            status = False
            print_error("The given {0} is not present in api response".format(regex_pattern))
    return status

def seek_next(pattern, data):
    """find the next pattern in the data and return its position
    """
    prev = 0
    search_object = re.search(pattern, data)
    while search_object:
        pos = search_object.start()
        yield prev+pos
        search_object = re.search(pattern, data[pos+1:])
        prev = pos
    else:
        raise StopIteration


def conv_str_to_bool(text, mapping_dict=None):
    """
    Map a text to a boolean value.
    The default text to bool mapping is provided in the
    default_map dict below, however text
    and mapping_dict as inputs to map as per needs.
    default_map = {'yes': True, 'y': True, 'no': False, 'n': False }
    """


    default_map = {'yes': True,
                   'y': True,
                   'no': False,
                   'n': False
                   }
    mapping = mapping_dict if mapping_dict else default_map
    result = mapping.get(text.lower(), False)

    return result


