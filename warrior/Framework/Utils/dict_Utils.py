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

import json

from Framework.Utils.testcase_Utils import pNote


def convert_string_to_dict(element, key_value_pair_sep=";", key_value_sep="="):
    """ This function converts a string into a dict.

        input = "foo=foo1; bar=bar1; ; =foobar; barfoo="
        return value = {'foo': 'foo1', 'bar': 'bar1'}

    If the dict is empty at the end of the function, None is returned
    """

    if isinstance(element, dict):
        return element

    final_dict = {}
    if element is not None and element is not False and element != "":
        try:
            str_converted_to_json = json.loads(element)
            return str_converted_to_json
        except ValueError:
            pass
        element = element.split(key_value_pair_sep)
        for i in range(0, len(element)):
            element[i] = element[i].strip()
            if element[i] is not None and element[i] is not False \
                    and element[i] != "":
                # element[i] will be split into 2 based on the key_value_sep
                # element[i] will be split on the first occurance of delimiter
                element[i] = element[i].split(key_value_sep, 1)
                for j in range(0, len(element[i])):
                    element[i][j] = element[i][j].strip()
                if len(element[i]) < 2:
                    if element[i][0] != "" and element[i][0] is not None \
                            and element[i][0] is not False:
                        pNote("{0} does not have a corresponding value. "
                              "Hence, discarded.".format(element[i][0]),
                              "error")
                    else:
                        pNote("Key Value undefined for data "
                              "number {0}!".format(i+1), "error")
                else:
                    if element[i][0] != "" and element[i][0] is not None \
                            and element[i][0] is not False:
                        if element[i][1] != "" and element[i][1] is not None\
                                and element[i][1] is not False:
                            final_dict[element[i][0]] = element[i][1]
                        else:
                            pNote("{0} does not have a corresponding value. "
                                  "Hence, discarded.".format(element[i][0]),
                                  "error")
                    else:
                        if element[i][1] != "" and element[i][1] is not None \
                                and element[i][1] is not False:
                            pNote("{0} does not have a corresponding key. "
                                  "Hence, discarded.".format(element[i][1]),
                                  "error")
                        else:
                            pNote("Key Value undefined for data number "
                                  "{0}!".format(i+1), "error")
            else:
                pNote("Key Value undefined for data number {0}!".format(i+1),
                      "error")
    else:
        final_dict = None

    if final_dict == {}:
        final_dict = None

    return final_dict

def get_dict_to_update(var, val):
    """
    The function creates a dictionary with Variable and value.
    If Variable has "." separated keys then the value is updated at
    appropriate level of the nested dictionary.
    :param var: Dictionary Key or Key separated with "." for nested dict keys.
    :param val: Value for the Key.

    :return: Dictionary
    """
    dic = {}
    if '.' in var:
        [key, value] = var.split('.', 1)
        dic[key] = get_dict_to_update(value, val)
    else:
        dic[var] = val
    return dic

def verify_key_already_exists_and_update(orig_dict, new_dict):
    """
    This function updates new_dict in orig_dict.
    :param orig_dict: Dictionary to be updated
    :param new_dict: Dictionary to update

    :return: updated dictionary
    """
    for key, value in new_dict.items():
        if key not in orig_dict:
            orig_dict[key] = value
        else:
            verify_key_already_exists_and_update(orig_dict[key], value)
    return orig_dict
