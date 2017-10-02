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

import cookielib
import json
import os
import re
import sys

from Framework.ClassUtils.configuration_element_class import \
    ConfigurationElement
from Framework.Utils import file_Utils
from Framework.Utils.dict_Utils import convert_string_to_dict
from Framework.Utils.file_Utils import get_extension_from_path
from Framework.Utils.string_Utils import get_list_from_varconfigfile, \
    sub_from_varconfigfile, sub_from_varsub, sub_from_wdf
from Framework.Utils.testcase_Utils import pNote

from Framework.ClassUtils.testdata_class import TestDataIterations, TestData


def remove_invalid_req_args(credentials_dict, invalid_args):
    """
    This function iterates through the invalid_args list and removes the
    elements in that list from credentials_dict and adds those to a new
    dictionary

    Returns:
        credentials_dict: Input dictionary after popping the elements in
        invalid_args
        invalid_args_dict: All popped elements.

    """
    invalid_args_dict = {}
    for arg in invalid_args:
        invalid_args_dict[arg] = credentials_dict[arg]
        credentials_dict.pop(arg)

    return credentials_dict, invalid_args_dict


def check_ext_get_abspath(relative_path, start_directory, list_extn=[".json", ".xml", ".txt"]):
    """
    This is wrapper function that gets and verifies extention of a file path
    and then calls get_abs_path_from_start_dir and returns the absolute path.
    start_directory must be an absolute path
    """
    return file_Utils.check_extension_get_absolute_path(relative_path, start_directory, list_extn)


def get_abs_path_from_start_dir(relative_path, start_directory, extension=".json"):
    """When provided with a start directory and a relative path, this function
    returns the absolute path. Else returns the relative path
    start_directory must be an absolute path
    """
    return file_Utils.getAbsPath(relative_path, start_directory)

def resolve_credentials_for_rest(credentials, element, datafile=None, system_name=None, variable_config="variable_config", var_sub="var_sub"):
    if element == "expected_response":
        credentials[element] = resolve_exp_resp_string_as_list(credentials[element])
    if element == "allow_redirects":
        credentials[element] = resolve_value_of_redirects(credentials[element])
    if element == "data":
        credentials[element] = resolve_value_of_data(credentials[element], datafile)
    if element == "timeout":
        credentials[element] = resolve_value_of_timeout(credentials[element])
    if element == "json":
        credentials[element] = resolve_value_of_json(credentials[element], datafile, system_name, credentials[variable_config], credentials[var_sub])
    if element == "cookies":
        credentials[element] = resolve_value_of_cookies(credentials[element])
    if element == "files":
        credentials[element] = resolve_value_of_files(credentials[element])
    if element == "verify":
        credentials[element] = resolve_value_of_verify(credentials[element])
    if element == "stream":
        credentials[element] = resolve_value_of_stream(credentials[element])
    if element == "cert":
        credentials[element] = resolve_value_of_cert(credentials[element])
    if element == "proxies" or element == "headers" or element == "params":
        credentials[element] = convert_string_to_dict(credentials[element])
    return credentials


def resolve_exp_resp_string_as_list(element):
    """ User given comma separated data is converted into a list.
    If no data is given, then an empty list is formed.
    """
    if element is not None and element is not False:
        if element == "":
            element = []
        else:
            temp_list = element.split(",")
            for i in range(0, len(temp_list)):
                temp_list[i] = temp_list[i].strip()
            element = temp_list
    return element


def resolve_value_of_redirects(element):
    """ If allow_redirects is specifically set not no (case ignored), then and
    only then allow_redirects is set to False. Else is set to true.
    """
    pattern = re.compile('no', re.IGNORECASE)
    if element is not None and element is not False and not pattern.match(element):
        element = True
    else:
        element = False
    return element


def resolve_value_of_timeout(element):
    """ The value given by the User, either in the datafile or in the TC, for
    the "timeout" parameter is assessed here. The User can either give a single
    value or comma separated value.

    Requests docs for timeout:
     ** :param timeout: (optional) How long to wait for the server to send data
        before giving up, as a float, or a :ref:`(connect timeout, read
        timeout) <timeouts>` tuple.
    :type timeout: float or tuple **

    If a single value is given, then that value is used for both connect timeout
    and read timeout

    If more than two comma separated values are given, only the first two
    are considered.

    If the input is invalid (i.e. it is neither an integer, nor a float), then
    this function throws out an error, but keeps the user specified values,
    so that the Error can be caught when the keyword actually executes.

    """
    if element is not None:
        if element == "" or not element:
            element = None
        else:
            temp_list = element.split(",")
            for i in range(0, len(temp_list)):
                temp_list[i] = temp_list[i].strip()
            if len(temp_list) == 1:
                try:
                    element = float(temp_list[0])
                except ValueError:
                    pNote("{0} is not an integer or a float."
                                .format(temp_list[0]), "error")
                    element = None
            elif len(temp_list) > 1:
                try:
                    temp_list[0] = float(temp_list[0])
                except ValueError:
                    pNote("{0} is not an integer or a float."
                          .format(temp_list[0]), "error")
                try:
                    temp_list[1] = float(temp_list[1])
                except ValueError:
                    pNote("{0} is not an integer or a float."
                          .format(temp_list[1]), "error")
                element = (temp_list[0], temp_list[1])

    return element


def resolve_value_of_json(element, datafile=None, system_name=None, variable_config=None, var_sub=None):
    """ Input string or file is converted to a json object. If an exception
    occurs, 'Error' is returned.

    """
    final_list = []
    if element is not None and element is not False and element != "":
        element = check_ext_get_abspath(element, os.path.dirname(datafile))
        if os.path.exists(element):
            json_file = open(element, 'r')
            element = json_file.read()
        if variable_config is not None and variable_config is not False:

            if var_sub is not None:
                element = sub_from_varsub(element, var_sub)

            if datafile is not None:
                element = sub_from_wdf(datafile, [element], kw_system_name=system_name)
                element = element[0]

            tdi_obj = TestDataIterations()
            td_obj = TestData()
            pattern = tdi_obj.get_iteration_pattern(element)
            if pattern != "":
                list_values = tdi_obj._expand_iter_pattern(element, pattern, variable_config)
            else:
                list_values = ([element], True)
            if list_values[1]:
                for value in list_values[0]:
                    ce_obj = ConfigurationElement(variable_config)
                    ce_obj.parse_data(variable_config)
                    list_check = td_obj.list_check(ce_obj, value)
                    if list_check == "Error":
                        pNote("{0} has list substitutions that are unequal "
                              "in length.".format(value), "error")
                        final_list.append("Error")
                    elif not list_check:
                        substituted_var = sub_from_varconfigfile(value, variable_config)
                        if not substituted_var:
                            final_list.append("Error")
                        else:
                            final_list.append(substituted_var)
                    else:
                        new_list = get_list_from_varconfigfile(value, variable_config)
                        for key in new_list:
                            if new_list[key]:
                                list_substituted_list = td_obj.string_sub(value, new_list)
                                for i in range(0, len(list_substituted_list)):
                                    final_list.append(sub_from_varconfigfile(list_substituted_list[i], variable_config))
        else:
            final_list.append(element)

        for i in range(0, len(final_list)):
            if final_list[i] != "Error":
                try:
                    final_list[i] = json.loads(final_list[i])
                except ValueError:
                    pNote("{0} is neither a valid JSON file path nor is it in a"
                          " valid json format.".format(final_list[i]), "error")
                    final_list[i] = "Error"

    if not final_list:
        final_list.append(None)

    return final_list


def resolve_value_of_cookies(element):
    """ This function evaluates user input for cookies. If a file path is given,
     then a cookiejar object is created and the contents of the file are loaded
     into the object. This object is then returned.

    Else, a dictionary would be created out of the string given
    input = "foo=foo1; bar=bar1; ; =foobar; barfoo="
    return value = {'foo': 'foo1', 'bar': 'bar1'}

    If the dictionary is empty at the end of the function, None is retuened.
    """
    if element is not None and element is not False and element != "":
        abs_path = file_Utils.getAbsPath(element, sys.path[0])
        if os.path.exists(abs_path):
            element = cookielib.LWPCookieJar(element)
            try:
                element.load()
            except cookielib.LoadError:
                pNote("Cookies could not be loaded from {}.".format(element),
                      "error")
                element = None
            except Exception as e:
                pNote("An Error Occurred: {0}".format(e), "error")
        else:
            element = convert_string_to_dict(element)
    else:
        element = None

    return element


def get_all_file_paths(element):
    """ This function evaluates the value of the files tag and returned
    validated data.

        input: string

        path/to/file1.txt, path/to/file2.txt

        output: dict

        {
        file1.txt: open file1.txt (in binary mode),
        file2.txt: open file2.txt (in binary mode),
        }

    """
    final_dict = {}
    if element is not None and element is not False and element != "":
        abs_path = file_Utils.getAbsPath(element, sys.path[0])
        if os.path.exists(abs_path):
            final_dict[os.path.basename(os.path.normpath(element))] = \
                open(element, 'rb')
        else:
            pNote("{0} doesn't exist!".format(element), "error")
    else:
        if element == "":
            pNote("File path cannot be empty!", "error")
        else:
            pNote("File path cannot be {0}!".format(element), "error")
    return final_dict


def dict_with_file_paths(element):
    """ This function evaluates the value of the files tag and returned
    validated data.

        input: string

        file_group_name=path/to/file2.txt; path/to/file3.txt

        output: dict

        {
        file_group_name_1: open file2.txt (in binary mode),
        file_group_name_2: open file3.txt (in binary mode),
        }

    """
    final_dict = {}
    temp_list = []
    if element is not None and element is not False and element != "":
        element = element.split("=")
        for i in range(0, len(element)):
            element[i] = element[i].strip()
        if len(element) < 2:
            pNote("File paths cannot be empty!", "error")
        else:
            if element[0] == "":
                pNote("File group name cannot be empty!", "error")
            elif element[0] is None or element[0] is False:
                pNote("File group name cannot be {0}!".format(element[0]),
                      "error")
            else:
                if element[1] == "":
                    pNote("File paths cannot be empty!", "error")
                elif element[1] is None or element[1] is False:
                    pNote("File paths cannot be {0}!".format(element[0]),
                          "error")
                else:
                    element[1] = element[1].split(";")
                    for i in range(0, len(element[1])):
                        element[1][i] = element[1][i].strip()
                        if element[1][i] is not None and element[1][i] is not \
                                False and element[1][i] != "":
                            abs_path = file_Utils.getAbsPath(element[1][i], sys.path[0])
                            if os.path.exists(abs_path):
                                temp_list.append(open(element[1][i], 'rb'))
                            else:
                                pNote("{0} doesn't exist!".format(element[1][i])
                                      , "error")
                        else:
                            if element[1][i] == "":
                                pNote("File path cannot be empty!", "error")
                            else:
                                pNote("File path cannot be {0}!"
                                      .format(element[1][i]), "error")
        if temp_list != []:
            for i in range(0, len(temp_list)):
                final_dict[element[0] + "_" + str(i+1)] = temp_list[i]
    else:
        if element == "":
            pNote("File group name and corresponding file paths cannot "
                  "be empty!", "error")
        else:
            pNote("File group name and corresponding file paths cannot"
                  " be {0}!".format(element), "error")
    return final_dict


def just_a_tuple(element):
    """ This function evaluates the value of the files tag and returned
    validated data.

        input: string

        (path/to/file4.txt;content_type), (path/to/file1.txt;content_type)

        output: dict

        {
        file4.txt: (file4.txt, open file4.txt (in binary mode), content_type)
        file1.txt: (file1.txt, open file1.txt (in binary mode), content_type)
        }

    """
    final_dict = {}
    temp_list = []
    element = element.strip(")")
    element = element.strip("(")
    if element is not None and element is not False and element != "":
        element = element.split(";")
        for i in range(0, len(element)):
            element[i] = element[i].strip()
        if element[0] is not None and element[0] is not False \
                and element[0] != "":
            abs_path = file_Utils.getAbsPath(element[0], sys.path[0])
            if os.path.exists(abs_path):
                temp_list.append(os.path.basename(os.path.normpath(element[0])))
                temp_list.append(open(abs_path, 'rb'))
                if len(element) > 1:
                    if element[1] is not None and element[1] is not False \
                            and element[1] != "":
                        temp_list.append(element[1])
            else:
                pNote("{0} doesn't exist!".format(element[0]), "error")
        else:
            if element == "":
                pNote("File path cannot be empty!", "error")
            else:
                pNote("File path cannot be {0}!".format(element[0]), "error")
        if temp_list != []:
            if len(temp_list) > 2:
                final_dict[temp_list[0]] = (temp_list[0], temp_list[1],
                                            temp_list[2])
            else:
                final_dict[temp_list[0]] = (temp_list[0], temp_list[1])
    else:
        if element == "":
            pNote("File path cannot be empty!", "error")
        else:
            pNote("File path cannot be {0}!".format(element), "error")
    return final_dict


def dict_in_tuple(element):
    """ This function evaluates the value of the files tag and returned
    validated data.

        input: string

        (path/to/file5.txt;content_type;(header1=value;header2=value2)),
        (path/to/file1.txt;content_type;(header3=value3;header4=value4))

        output: dict

        {
        file5.txt: (file5.txt, open file5.txt (in binary mode), content_type,
        { header1: value, header2: value2 }),
        file1.txt: (file1.txt, open file5.txt (in binary mode), content_type,
        { header3: value3, header4: value4 })
        }

    """
    final_dict = {}
    temp_list = []
    element = element.strip("))")
    element = element.strip("(")
    if element is not None and element is not False and element != "":
        element = element.split(";(")
        if element[0] is None or element[0] is False:
            pNote("File path cannot be {0}!".format(element), "error")
        elif element[0] == "":
            pNote("File path cannot be empty!", "error")
        else:
            element[0] = element[0].split(";")
            for j in range(0, len(element[0])):
                element[0][j] = element[0][j].strip()
            if element[0][0] is None or element[0][0] is False:
                pNote("File path cannot be {0}!".format(element), "error")
            elif element[0][0] == "":
                pNote("File path cannot be empty!", "error")
            else:
                abs_path = file_Utils.getAbsPath(element[0][0], sys.path[0])
                if os.path.exists(abs_path):
                    temp_list.append(os.path.basename(os.path.normpath(element[0][0])))
                    temp_list.append(open(abs_path, 'rb'))
                else:
                    pNote("{0} doesn't exist!".format(element[0]), "error")
            if len(element[0]) > 1:
                if element[0][1] is not None and element[0][1] is not False \
                        and element[0][1] != "":
                    temp_list.append(element[0][1])
                    if len(element) > 1:
                        if element[1] is not None and element[1] is not False \
                                and element[1] != "":
                            temp_list.append(convert_string_to_dict(element[1]))
            else:
                if len(element) > 1:
                    if element[1] is not None and element[1] is not False \
                            and element[1] != "":
                        temp_list.append("")
                        temp_list.append(convert_string_to_dict(element[1]))
        if temp_list != []:
            if len(temp_list) < 3:
                final_dict[temp_list[0]] = (temp_list[0], temp_list[1])
            elif len(temp_list) > 3:
                final_dict[temp_list[0]] = (temp_list[0], temp_list[1],
                                            temp_list[2], temp_list[3])
            elif len(temp_list) > 2:
                final_dict[temp_list[0]] = (temp_list[0], temp_list[1],
                                            temp_list[2])
    else:
        if element == "":
            pNote("File path cannot be empty!", "error")
        else:
            pNote("File path cannot be {0}!".format(element), "error")
    return final_dict


def resolve_value_of_files(element):
    """ This function evaluates the value of the files tag and returned
    validated data.

    input: string

    path/to/file1.txt, file_group_name=path/to/file2.txt; path/to/file3.txt,
    (path/to/file4.txt;content_type),
    (path/to/file5.txt;content_type;(header1=value;header2=value2))

    output: dict

    {
    file1.txt: open file1.txt (in binary mode),
    file_group_name_1: open file2.txt (in binary mode),
    file_group_name_2: open file3.txt (in binary mode),
    file4.txt: (file4.txt, open file4.txt (in binary mode), content_type)
    file5.txt: (file5.txt, open file5.txt (in binary mode), content_type,
                { header1: value, header2: value2 })
    }

    """
    final_dict = {}
    if element is not None and element is not False and element != "":
        element = element.split(",")
        for i in range(0, len(element)):
            element[i] = element[i].strip()
            if not element[i].startswith("("):
                if "=" not in element[i]:
                    final_dict.update(get_all_file_paths(element[i]))
                else:
                    final_dict.update(dict_with_file_paths(element[i]))
            else:
                if element[i].endswith("))"):
                    final_dict.update(dict_in_tuple(element[i]))
                else:
                    final_dict.update(just_a_tuple(element[i]))
        element = final_dict
    else:
        element = None

    if element == {}:
        element = None

    return element


def resolve_value_of_verify(element):
    """This function verifies the validity of the parameter verify. If the value
    is 'yes', verify gets set to True. If 'no', it gets set to False.
    If it is a path to a file and if the file exists,
    it gets set to the filepath.
    Else None."""
    aff_pattern = re.compile('^yes$', re.IGNORECASE)
    neg_pattern = re.compile('^no$', re.IGNORECASE)
    if element is not None and element is not False and element != "":
        abs_path = file_Utils.getAbsPath(element, sys.path[0])
        if not os.path.exists(abs_path):
            if aff_pattern.match(element):
                element = True
            elif neg_pattern.match(element):
                element = False
            else:
                element = True
    else:
        element = True
    return element


def resolve_value_of_stream(element):
    """ This function verifies the value of the parameter stream.
    If set explicitly to 'no', it would be evaluated as False, else True.
    """
    if element is not None and element is not False and element != "":
        pattern = re.compile('^no$', re.IGNORECASE)
        if pattern.match(element):
            element = False
        else:
            element = True
    else:
        element = False
    return element


def resolve_value_of_cert(element):
    """ This function verifies the value of the parameter cert.
    cert takes in either a path to the certificate file or a tuple containing
    the cerificate file and if the key is not included in that file, then a
    file containing the key. Else None.
    """
    if element is not None and element is not False and element != "":
        element_list = element.split(",")
        for i in range(0, len(element_list)):
            element_list[i] = element_list[i].strip()
            if not os.path.exists(element_list[i]):
                pNote("{0} doesn't exist!".format(element_list[0]), "error")
                element = None
        if len(element_list) == 1:
            element = element_list[0]
        elif len(element_list) > 1:
            element = (element_list[0], element_list[1])
    else:
        element = None

    return element


def resolve_value_of_data(element, datafile):
    """ This function validates the user input for data.
    If the input is a file path, then a file object is returned.
    if the input is in bytes, then the input is retuned.
    else, dictionary is returned.
        input = "foo=foo1; bar=bar1; ; =foobar; barfoo="
        return value = {'foo': 'foo1', 'bar': 'bar1'}
    If the dict is empty at the end of the function, None is returned
    """
    if element is not None and element is not False and element != "":
        element = check_ext_get_abspath(element, os.path.dirname(datafile))
        if os.path.exists(element):
            final_dict = open(element, 'rb')
        elif isinstance(element, unicode):
            final_dict = element
        else:
            final_dict = convert_string_to_dict(element)
    else:
        final_dict = None
    return final_dict

def get_type_of_api_response(response):
    """
        Takes API response as input and returns the type of the response
        whether it is json or xml or text
        Arguments:
            response: It takes API response as input
        Returns:
            returns the type of the response
    """
    content_type = response.headers['Content-Type']
    if 'xml' in content_type:
        type_of_response = 'xml'
    elif 'json' in content_type:
        type_of_response = 'json'
    else:
        type_of_response = 'text'
    return type_of_response
