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
Module that has all tetdata related class and methods
"""
import re
from xml.etree import ElementTree
from collections import OrderedDict

from Framework.Utils import xml_Utils, string_Utils
from Framework.Utils.testcase_Utils import pNote
from Framework.Utils.print_Utils import print_error, print_exception,\
print_debug, print_warning
from Framework.ClassUtils.configuration_element_class import ConfigurationElement

# Always keep 'repeat_list' as a last key for CMD_PARAMS dictionary
CMD_PARAMS = OrderedDict([("command_list", "send"),
                          ("sys_list", "sys"),
                          ("session_list", "session"),
                          ("startprompt_list", "start"),
                          ("endprompt_list", "end"),
                          ("verify_list", "verify"),
                          ("verify_text_list", "search"),
                          ("verify_context_list", "found"),
                          ("timeout_list", "timeout"),
                          ("sleeptime_list", "sleep"),
                          ("retry_list", "retry"),
                          ("retry_timer_list", "retry_timer"),
                          ("retry_count_list", "retry_count"),
                          ("retry_onmatch_list", "retry_onmatch"),
                          ("resp_ref_list", "resp_ref"),
                          ("resp_req_list", "resp_req"),
                          ("resp_pat_req_list", "resp_pat_req"),
                          ("resp_pat_key_list", "resp_pat_key"),
                          ("resp_key_list", "resp_keys"),
                          ("inorder_resp_ref_list", "inorder_resp_ref"),
                          ("log_list", "monitor"),
                          ("verify_on_list", "verify_on"),
                          ("inorder_search_list", "inorder"),
                          ("vc_file_list", ""),
                          ("verify_map_list", ""),
                          ("operator_list", "operator"),
                          ("cond_value_list", "cond_value"),
                          ("cond_type_list", "cond_type"),
                          ("sleeptime_before_match_list", "sleep_before_match"),
                          ("return_on_fail_list", "return_on_fail"),
                          ("logmsg_list", "log"),
                          ("repeat_list", "repeat")])  # keep this in the last


VFY_PARAM_LIST = ["verify_text_list", "verify_context_list",
                  "verify_on_list", "verify_map_list"]

VERIFY_PARAMS = ["verify_context_list", "verify_on_list", "verify_map_list"]

VARSUB_PARAM_LIST = ["verify_text_list", "verify_context_list", "verify_on_list",
                     "verify_map_list", "operator_list", "cond_value_list",
                     "cond_type_list", "resp_key_list"]


class TestData(object):
    """
    Class to handle generic test data related operations
    """

    def __init__(self):
        """
        Constructor
        """
        pass

    @staticmethod
    def varsub_varconfig_substitutions(details_dict, vc_file, var_sub,
                                       start_pat="${", end_pat="}"):
        """
        Substitute the patterns [VAR_SUB] in command, command parameters,
        verification search, verification parameters with the value of
        VAR_SUB provided by user in the testcase.

        Substitute the value of the variables (provided as dotted notation
        inside the pattern ${} ) in command, command parameters,
        verification search, verification parameters with the value provided
        in the varaiable config file (vc_file).

        """
        vc_file_list = None if vc_file is None else details_dict["vc_file_list"]
        for param, _ in CMD_PARAMS.items():
            if param not in VARSUB_PARAM_LIST and param != "vc_file_list":
                # list in here is just a list of strings
                string_list = details_dict[param]
                new_string_list = string_Utils.sub_from_varconfig\
                    (vc_file_list, string_list, var_sub, start_pat, end_pat)
                details_dict[param] = new_string_list

            elif param in VARSUB_PARAM_LIST:
                # list in here is a list of sublists of strings
                string_list = details_dict[param]
                for i, sub_list in enumerate(string_list):
                    if sub_list is not None:
                        sub_vc_file_list = None if vc_file_list is None\
                         else [vc_file_list[i]]*len(sub_list)
                        new_sub_list = string_Utils.sub_from_varconfig(sub_vc_file_list, sub_list,
                                                                       var_sub, start_pat, end_pat)

                        string_list[i] = new_sub_list
                        details_dict[param] = string_list
        return details_dict

    def list_check(self, cfg_elem_obj, text):
        """
            check the text to see if there are multiple list substitutions
        :param cfg_elem_obj:
            the object that load and parse the varconfig file
            we can match text to list element
        :param text:
            the text being analyzed
        :return:
            return the particular list or None
        """
        dict_of_lists = cfg_elem_obj.get_list(text)
        if len(dict_of_lists.values()) > 1:
            if all(len(x) == len(dict_of_lists.values()[0]) for x in dict_of_lists.values()):
                return len(dict_of_lists.values()[0])
            else:
                # There are multiple lists with different length!
                return 'Error'
        elif len(dict_of_lists.values()) == 1 and dict_of_lists.values()[0]:
            return len(dict_of_lists.values()[0])

        return False

    def cmd_quote_check(self, cfg_elem_obj, details_dict):
        """
            check the command text to see if there is any different list substitution
        :param cfg_elem_obj:
            the object that load and parse the varconfig file
            we can match text in command text to list element
        :param details_dict:
        :return:
            list of boolean shows if the command has list substitution of not
        """
        cmd_list_substituted = [False] * len(details_dict["command_list"])

        for cmd_index in range(len(details_dict["command_list"])):
            # check if current cmd is invalid
            if details_dict["command_list"][cmd_index]:
                cmd = self.list_check(cfg_elem_obj, details_dict["command_list"][cmd_index])
                if cmd is not False and cmd != 'Error':
                    cmd_list_substituted[cmd_index] = cmd
                elif cmd == 'Error':
                    print_error("Multiple lists with different length found in command text")
                    details_dict["command_list"][cmd_index] = False
                    details_dict["verify_text_list"][cmd_index] = []
            elif details_dict["verify_text_list"][cmd_index]:
                print_error("Ignored verify text for current invalid cmd")
                details_dict["verify_text_list"][cmd_index] = []
        return cmd_list_substituted

    def verify_text_check(self, cfg_elem_obj, details_dict):
        """
            check the verify text to see if there is any different list substitution
        :param cfg_elem_obj:
            the object that load and parse the varconfig file
            we can match text in verify text to list element
        :param details_dict:
        :return:
            list of boolean shows if the verify text has list substitution of not
        """
        verify_text_substituted = [False] * len(details_dict["command_list"])

        for verify_index in range(len(details_dict["verify_text_list"])):
            # check if sublist in verify_text_list is invalid
            if details_dict["verify_text_list"][verify_index]:
                for verify_string in details_dict["verify_text_list"][verify_index]:
                    # check if verify_string is invalid
                    if verify_string:
                        verify_text = self.list_check(cfg_elem_obj, verify_string)
                        if verify_text is not False and verify_text != 'Error':
                            if not verify_text_substituted[verify_index]:
                                verify_text_substituted[verify_index] = [verify_text]
                            else:
                                verify_text_substituted[verify_index].append(verify_text)
                        elif verify_text == 'Error':
                            print_error("Multiple lists with different length found in verify text")
                            details_dict["command_list"][verify_index] = False
                            details_dict["verify_text_list"][verify_index] = []

        return verify_text_substituted

    def list_substitution_precheck(self, varconfigfile, details_dict, start_pat="${", end_pat="}"):
        """
            entry function for cmd and verify text substitution check
        :param cfg_elem_obj:
            the object that load and parse the varconfig file
        :param details_dict:
        :return:
            pair of list of boolean returned from cmd_quote_check and verify_text_check
        """
        if len(details_dict["command_list"]) != len(details_dict["verify_text_list"]):
            raise ValueError("command list and verify_text_list aren't the same length")

        cmd_list_substituted = [False]*len(details_dict["command_list"])
        verify_text_substituted = [False]*len(details_dict["command_list"])

        if varconfigfile is not None:
            # when varconfigfile is an XMl object(root element) - this happens
            # only when varconfigfile is taken from database server
            if isinstance(varconfigfile, ElementTree.Element) is True:
                cfg_elem_obj = ConfigurationElement("Varconfig_from_database",
                                                    start_pat, end_pat)
                cfg_elem_obj.parse_data(varconfigfile, elem_type="xml_object")
            else:
                cfg_elem_obj = ConfigurationElement(varconfigfile, start_pat, end_pat)
                cfg_elem_obj.parse_data(varconfigfile)
            cmd_list_substituted = self.cmd_quote_check(cfg_elem_obj, details_dict)
            if details_dict["verify_text_list"]:
                verify_text_substituted = self.verify_text_check(cfg_elem_obj, details_dict)
        return (cmd_list_substituted, verify_text_substituted)

    def string_sub(self, raw_str, dict_of_list, start_pat="${", end_pat="}"):
        """
            expand the raw_str into a list using the substitution value from dict_of_list
            :param raw_str:
                the source string that needs to be expanded
            :param dict_of_list:
                a dict with orignal list/range as key "1..4,5,6..7:0.5"
                parsed list as value [1,2,3,4,5,6,6.5,7]
            :return:
                a list with expanded raw_str
        """
        expanded_str = []
        for str_match, list_value in dict_of_list.items():
            if list_value:
                # There is a list that needs to expand
                if expanded_str == []:
                    for value in list_value:
                        expanded_str.append(raw_str.replace(start_pat+str_match+end_pat, str(value)))
                else:
                    for index, value in enumerate(list_value):
                        expanded_str[index] = expanded_str[index].\
                         replace(start_pat+str_match+end_pat, str(value))
            else:
                if str_match == 'Error':
                    return 'Error'

        return expanded_str

    def cmd_sub(self, details_dict, cmd_index, varconfigfile, start_pat="${", end_pat="}"):
        """
            expand the command_list with list/range value
        :param details_dict:
        :param cmd_index:
            current cmd that we are processing
        :param varconfigfile:
            reference to find value list
        :return:
            list of value indicating if the cmd has list substitution or not
        """
        if details_dict["repeat_list"][cmd_index] is not None:
            print_warning("repeat tag is not supported for the command with list "
                          "substitution - {}".format(details_dict["command_list"][cmd_index]))
            details_dict["repeat_list"][cmd_index] = None
        cmd_result = string_Utils.get_list_from_varconfigfile(details_dict["command_list"][cmd_index],
                                                              varconfigfile, start_pat, end_pat)
        expanded_cmd = self.string_sub(details_dict["command_list"][cmd_index], cmd_result,
                                       start_pat, end_pat)

        if expanded_cmd and expanded_cmd != 'Error':
            # Every cmd in here supposed to have at least 1 list sub
            # But just in case, check if there is no list sub
            details_dict["command_list"][cmd_index] = expanded_cmd
        elif str(expanded_cmd) == 'Error':
            details_dict["command_list"][cmd_index] = False
            details_dict["verify_text_list"][cmd_index] = False
            return []

        return cmd_result.values()

    def verify_sub(self, details_dict, cmd_index, varconfigfile, start_pat="${", end_pat="}"):
        """
            expand the verify_text_list with list/range value
        :param details_dict:
        :param cmd_index:
            current cmd that we are processing
        :param varconfigfile:
            reference to find value list
        :return:
            list of value indicating if the verify text list has list substitution or not
        """
        expanded_verify_list = []
        verify_text_match_list = []
        for verify_text_string in details_dict["verify_text_list"][cmd_index]:

            verify_text_result = string_Utils.get_list_from_varconfigfile(verify_text_string,
                                                                          varconfigfile, start_pat,
                                                                          end_pat)
            expanded_verify_text = []

            # add the value to the verify text list (1 cmd can have multiple verify text)
            verify_text_match_list.append(verify_text_result.values())

            expanded_verify_text = self.string_sub(verify_text_string, verify_text_result,
                                                   start_pat, end_pat)

            if expanded_verify_text and expanded_verify_text != 'Error':
                expanded_verify_list.append(expanded_verify_text)
            elif str(expanded_verify_text) == 'Error':
                details_dict["command_list"][cmd_index] = False
                details_dict["verify_text_list"][cmd_index] = False
                return []
            else:
                expanded_verify_list.append(verify_text_string)

        details_dict["verify_text_list"][cmd_index] = expanded_verify_list
        return verify_text_match_list

    def align_both(self, details_dict, cmd_index, cmd_match, verify_text_match_list):
        """
            In the case of both command list and verify text list get list substitution
            handle the following case:
            command and verify text share same substitution: 1-1 match the list value,
            so cmd 1 - verify 1, cmd2 - verify 2
            command and verify text have different substitution: 1-many match the list value,
            so cmd 1 - verify a, verify b, verify c
            command has list substitution but verify text doesn't: 1-1 match, cmd 1 - verify text
            also expand other lists to match # of cmd
        :param details_dict:
        :param cmd_index:
            current cmd that we are processing
        :param cmd_match:
            list for value indicating whether cmd text list has list substitution
            can be [list1, list2, list3] all lists have same length (checked before sub)
            or []
        :param verify_text_match_list:
            list for value indicating whether verify text list has list substitution
            can be [[list1_for_ver_text1, list2, list3], [False], [list1_for_ver_text3, list2...]]
            or []
        :return:
        """

        for sub_cmd_index, cmd in enumerate(details_dict["command_list"][cmd_index]):
            # for every expanded cmd...
            for param, _ in CMD_PARAMS.items():
                if param not in VFY_PARAM_LIST and param != "command_list":
                    # list in here is just a list of strings
                    # insert duplicated element after the current element
                    details_dict[param].insert(cmd_index+sub_cmd_index+1,
                                               details_dict[param][cmd_index])
                elif param in VFY_PARAM_LIST:
                    # list in here is a list of sublists of strings
                    # for example: verify_text_list = [[v1[1], v1[2], v1[3]], [v2], [v3[1], v3[2]]]
                    processed_list = []
                    for sub_verify_text_index, verify_text_match in enumerate(verify_text_match_list):
                        if param == "verify_text_list":
                            if verify_text_match == [False] or verify_text_match == ["Error"]:
                                # no verify text substitution for the current subtext
                                processed_list.append(details_dict[param][cmd_index][sub_verify_text_index])
                            elif len(verify_text_match[0]) == len(cmd_match[0]):
                                # cmd and verify text are replacing the same list
                                if details_dict["verify_map_list"][cmd_index][sub_verify_text_index] == "1":
                                    # 1-1 mapping
                                    processed_list.append(details_dict[param][cmd_index][sub_verify_text_index][sub_cmd_index])
                                elif details_dict["verify_map_list"][cmd_index][sub_verify_text_index] == "2":
                                    # 1-M mapping
                                    processed_list.extend(details_dict[param][cmd_index][sub_verify_text_index])
                            else:
                                # cmd and verify text have different length
                                processed_list.extend(details_dict[param][cmd_index][sub_verify_text_index])
                        else:
                            if verify_text_match == [False] or verify_text_match == ["Error"]:
                                processed_list.append(details_dict[param][cmd_index][sub_verify_text_index])
                            elif len(verify_text_match[0]) == len(cmd_match[0]):
                                # cmd and verify text are replacing the same list, use 1-1 connection
                                if details_dict["verify_map_list"][cmd_index][sub_verify_text_index] == "1":
                                    # 1-1 mapping
                                    processed_list.append(details_dict[param][cmd_index][sub_verify_text_index])
                                elif details_dict["verify_map_list"][cmd_index][sub_verify_text_index] == "2":
                                    # 1-M mapping
                                    processed_list.extend([details_dict[param][cmd_index][sub_verify_text_index]]*len(details_dict["verify_text_list"][cmd_index][sub_verify_text_index]))
                            else:
                                processed_list.extend([details_dict[param][cmd_index][sub_verify_text_index]]*len(details_dict["verify_text_list"][cmd_index][sub_verify_text_index]))

                    details_dict[param].insert(cmd_index+sub_cmd_index+1, processed_list)
            details_dict["command_list"].insert(cmd_index+sub_cmd_index+1, cmd)

    def align_cmd(self, details_dict, cmd_index, cmd_match):
        """
            In the case of only command list get list substitution
            handle the following case:
            command has list substitution but verify text doesn't:
            all expanded cmd have their own copy of verify text
            also expand other lists to match # of cmd
        :param details_dict:
        :param cmd_index:
            current cmd that we are processing
        :param cmd_match:
            list for value indicating whether cmd text list has list substitution
        :return:
        """
        for sub_cmd_index, cmd in enumerate(details_dict["command_list"][cmd_index]):
            # for every expanded cmd...
            for param, _ in CMD_PARAMS.items():
                if param != "command_list":
                    # list in here is just a list of strings
                    # insert duplicated element after the current element
                    details_dict[param].insert(cmd_index+sub_cmd_index+1,
                                               details_dict[param][cmd_index])
            details_dict["command_list"].insert(cmd_index+sub_cmd_index+1, cmd)

    def align_ver(self, details_dict, cmd_index, verify_text_match_list):
        """
            In the case of only verify text list get list substitution
            handle the following case:
            verify text has list substitution but cmd text doesn't:
            1 cmd maps to all of its verify texts
        :param details_dict:
        :param cmd_index:
            current cmd that we are processing
        :param verify_text_match_list:
            list for value indicating whether verify text list has list substitution
        :return:
        """
        # First handle the context list because they haven't expanded themselves during list substitution
        for param in ["verify_context_list", "verify_on_list", "verify_map_list"]:
            processed_list = []
            for sub_verify_text_index, verify_text_match in enumerate(verify_text_match_list):
                if verify_text_match and verify_text_match != [False] and verify_text_match != ["Error"]:
                    processed_list.extend([details_dict[param][cmd_index][sub_verify_text_index]]*len(details_dict["verify_text_list"][cmd_index][sub_verify_text_index]))
                else:
                    processed_list.append(details_dict[param][cmd_index][sub_verify_text_index])
            details_dict[param].insert(cmd_index+1, processed_list)

        # break up verify text list to corrent chunk
        processed_list = []
        for sub_verify_text_index, verify_text_match in enumerate(verify_text_match_list):
            if verify_text_match and verify_text_match != [False] and verify_text_match != ["Error"]:
                processed_list.extend(details_dict["verify_text_list"][cmd_index][sub_verify_text_index])
            else:
                processed_list.append(details_dict["verify_text_list"][cmd_index][sub_verify_text_index])
        details_dict["verify_text_list"].insert(cmd_index+1, processed_list)

    def list_substitution(self, details_dict, varconfigfile, cmd_list_substituted,
                          verify_text_substituted, start_pat="${", end_pat="}"):
        """
            entry function for different list substitution case
            also handle the deletion of original list after alignment
        :param details_dict:
        :param varconfigfile:
            reference for list of values
        :param cmd_list_substituted:
            list for value indicating whether cmd list has list substitution
        :param verify_text_substituted:
            list for value indicating whether verify text list has list substitution
        :return:
        """
        old_cmd_index = 0
        cmd_index = 0

        while cmd_index < len(details_dict["command_list"]):
            if cmd_list_substituted[old_cmd_index]:
                if verify_text_substituted[old_cmd_index]:
                    cmd_match = self.cmd_sub(details_dict, cmd_index, varconfigfile, start_pat,
                                             end_pat)
                    verify_text_match_list = self.verify_sub(details_dict, cmd_index, varconfigfile,
                                                             start_pat, end_pat)

                    self.align_both(details_dict, cmd_index, cmd_match, verify_text_match_list)

                    cmd_jump = len(details_dict["command_list"][cmd_index])
                    for param in CMD_PARAMS.keys():
                        del details_dict[param][cmd_index]

                    cmd_index += cmd_jump
                else:
                    cmd_match = self.cmd_sub(details_dict, cmd_index, varconfigfile, start_pat, end_pat)
                    cmd_jump = len(details_dict["command_list"][cmd_index])

                    self.align_cmd(details_dict, cmd_index, cmd_match)

                    for param in CMD_PARAMS.keys():
                        del details_dict[param][cmd_index]

                    cmd_index += cmd_jump
            else:
                if verify_text_substituted[old_cmd_index]:
                    verify_text_match_list = self.verify_sub(details_dict, cmd_index, varconfigfile,
                                                             start_pat, end_pat)

                    self.align_ver(details_dict, cmd_index, verify_text_match_list)

                    for param in VFY_PARAM_LIST:
                        del details_dict[param][cmd_index]

                else:
                    pass

                cmd_index += 1

            old_cmd_index += 1

    @staticmethod
    def wdf_substitutions(details_dict, datafile, kw_system_name):
        """
        Substitute the patterns $wdf{} in command, command parameters,
        verification search, verification parameters with the value of
         provided by user in the datafile.

        """
        for param, _ in CMD_PARAMS.items():
            if param not in VARSUB_PARAM_LIST and param!="vc_file_list":
                string_list = details_dict[param]
                td_sys_list = details_dict["sys_list"]
                new_string_list = string_Utils.sub_from_wdf(datafile, string_list,
                                                            td_sys_list, kw_system_name)
                details_dict[param] = new_string_list

            elif param in VARSUB_PARAM_LIST:
                string_list = details_dict[param]
                for i, sub_list in enumerate(string_list):
                    if sub_list is not None:
                        new_sub_list = string_Utils.sub_from_wdf(datafile, sub_list)
                        string_list[i] = new_sub_list
                        details_dict[param] = string_list
        return details_dict


class TestDataIterations(object):
    """
    Class to handle iterations in testdata
    """

    def __init__(self):
        """
        Constructor
        """
        pass

    def resolve_iteration_patterns(self, details_dict):
        """
        Takes a details dict as input
        and resolves the iteration patterns in each command
        and its parameters and in each verification search and its
        parameters

        :Return:
            Returns an updated details_dict and cmd_loc_list
            (cmd_loc_list - list of starting locations of
            each td command in the expanded cmd_list,
            last value of this list is the total number of
            commands in the in the expanded cmd_list)
        """
        cmd_list = details_dict["command_list"]
        vc_file_list = details_dict["vc_file_list"]
        repeat_list = details_dict["repeat_list"]
        res_status = True
        ### for each command in cmd_list resolve the iterations
        cmd_list_length = len(cmd_list)
        cmd_loc_list = [0]
        cmd_size = 1
        for i, cmd in enumerate(cmd_list):
            vc_file = vc_file_list[i]
            iteration_status = self.validate_iteration_patterns(cmd, details_dict, i)
            cmd_size = 1 if cmd_size < 1 else cmd_size
            # if iteration_status is False, mark command as False and
            # move on to the next command
            if not iteration_status:
                print_error("Iteration pattern validation failed for the "
                            "the command {0}".format(cmd))
                cmd_list[i] = False
                cmd_loc_list.append(i + cmd_size)
                continue

            # At this point it is safe to assume all validations with respect
            # to command iterations are done, and when iteration patterns are
            # expanded in the below steps they will be uniform.

            else:
                # find the iter pattern for the command
                cmd_iter_pattern = self.get_iteration_pattern(cmd)
                # iter_pattern="" it means no iter_pattern found for the cmd
                # move on to the next command
                # This also means that the command parameters do not have any
                # iteration patterns because the validation was already done.
                if cmd_iter_pattern != "":
                    # if cmd_iterpattern is not ""
                    # call the expand cmd_params method to resolve the
                    # iteration patterns in the command and get a updated
                    # details_dict get a updated details dict

                    if repeat_list[i] is not None:
                        print_warning("repeat tag is not supported for the"
                                      " command with iteration pattern - "
                                      "{}". format(cmd))
                    cmdresolved_details_dict = self.expand_cmd_params\
                        (cmd_iter_pattern, details_dict, i, vc_file)

                    details_dict = cmdresolved_details_dict

                new_details_dict = self.expand_vfy_params\
                    (details_dict, i, vc_file, cmd_iter_pattern)
                details_dict = new_details_dict
                cmd_list = details_dict["command_list"]

                res_result = self._check_list_lengths(details_dict)
                res_status = res_status and res_result

            new_cmd_list_length = len(cmd_list)
            if new_cmd_list_length > cmd_list_length:
                cmd_size = (new_cmd_list_length - cmd_list_length) + 1
                cmd_list_length = new_cmd_list_length
                cmd_loc_list.append(i + cmd_size)
            else:
                if cmd_size == 1:
                    cmd_loc_list.append(i + cmd_size)
                cmd_size -= 1

        if res_status:
            print_debug("resolving iteration patterns in the command, "
                        "command_parameters, verify search, verifcation "
                        "parameters was successful")

        else:
            print_debug("resolving iteration patterns in the command, "
                        "command_parameters, verify search, verifcation "
                        "parameters was failed")
        return details_dict, cmd_loc_list

    def validate_iteration_patterns(self, cmd, details_dict, index):
        """
        Validate iteration patterns provided in the
        1. command string
        2. command parameters
        3. verification search string of the command
        4. verification parameters (found, verify_on)

        """
        # get the iteration pattern of the command
        cmd_iter_pattern = self.get_iteration_pattern(cmd)
        cmd_status = self._validate_cmd_iterpattern(cmd, cmd_iter_pattern)
        param_status = self._validate_params_iterpattern\
            (cmd, details_dict, cmd_iter_pattern, index)
        vfy_search_status = self._validate_vfysearch_iterpattern(cmd, details_dict, index)
        vfyparams_status = self._validate_vfyparams_iterpattern(cmd, details_dict, index)
        status = cmd_status and param_status and vfy_search_status \
            and vfyparams_status
        return status

    def get_iteration_pattern(self, cmd):
        """
        Get the iteration pattern from a string
        """
        var_pat_list = self._get_varpat_list(cmd)
        iter_pattern_list = self._get_iterpattern_list(var_pat_list)
        iter_pattern = "" if len(iter_pattern_list) == 0\
            else iter_pattern_list[0]
        return iter_pattern

    def expand_cmd_params(self, cmd_iter_pattern, details_dict, index, vc_file):
        """
        Expand the iteration patterns in the command,
        command parameters and return a updated details dict
        """

        excl_list = ["command_list"]
        # First expand the iteration pattern in the actual command
        cmd_list = details_dict["command_list"]
        cmd = cmd_list[index]
        # Change the repeat_list value in this index as None since td 'repeat'
        # tag is not supported for the commands with iteration pattern
        details_dict["repeat_list"][index] = None
        error = False
        resolved_cmd_list, status = self._expand_iter_pattern\
        (cmd, cmd_iter_pattern, vc_file)
        if status and len(resolved_cmd_list) > 0:
            # if resolving the iteration patterns in the command
            # was successful then replace the command in the original
            # command list with the new commands in the resolved_cmd_list
            cmd_list[index:index+1] = resolved_cmd_list

            # remember the length of the resolved cmd list say n
            # for other command parameters if the iter pattern is provided
            # resolve the iteration pattern provided, else repeat the parameter
            # in its list by n times, so that each command that was resolved
            # has the corresponding parameter repeated.
            ref_length = len(resolved_cmd_list)
            for param, _ in CMD_PARAMS.items():
                if param not in excl_list:
                    param_list = details_dict[param]
                    param_value = param_list[index]
                    iter_pattern = self.get_iteration_pattern(param_value)\
                    if isinstance(param_value, str) else ""

                    if iter_pattern is not "":
                        res_list, status = self._expand_iter_pattern\
                        (param_value, iter_pattern, vc_file)
                        if status and len(res_list) > 0:
                            param_list[index:index+1] = res_list
                        else:
                            error = True
                    else:
                        res_list = []
                        for _ in range(0, ref_length):
                            if isinstance(param_value, list):
                                new_list = []
                                for element in param_value:
                                    new_list.append(element)
                                res_list.append(new_list)
                            else:
                                res_list.append(param_value)
                        param_list[index:index+1] = res_list
        else:
            error = True
        if error:
            # if there were any problems in resolving the iteration patterns
            # or if none of the nodes in the iterpattern are availabel in the
            # varconfig file, i.e. resolved_cmd_list=[]mark command as False,
            # do not care to resolve other cmd parameters. return details dict
            cmd_list[index] = False
        return details_dict

    def expand_vfy_params(self, details_dict, index, vc_file,
                          cmd_iter_pattern):
        """
        Expand the iter patterns in the verification search
        and found.
        """
        verify_text_list = details_dict["verify_text_list"]
        cur_verify_text_list = verify_text_list[index]

        if cur_verify_text_list:
            for i, verify_text in enumerate(cur_verify_text_list):
                error = False
                vfy_iter_pattern = self.get_iteration_pattern(verify_text)\
                    if isinstance(verify_text, str) else ""

                identical = True if vfy_iter_pattern == cmd_iter_pattern\
                    else False

                # If a verification search has an iter pattern, resolve it
                # and get a list of new search strings. Replace search string
                # in erify_text list with the new search_string list obtained.
                if vfy_iter_pattern is not "":
                    res_vfytext_list, status = self._expand_iter_pattern\
                        (verify_text, vfy_iter_pattern, vc_file)
                    if status and len(res_vfytext_list) > 0:
                        # if resolving the verify iter pattern was successful
                        if identical:
                            for cnt in range(0, len(res_vfytext_list)):
                                verify_text_list[index + cnt][i] = \
                                    res_vfytext_list[cnt]
                        else:
                            cur_verify_text_list[i:i+1] = res_vfytext_list

                        # After resolving the iter patterns in the search
                        # check if iter pattern is provided in corresponding
                        # found, if provided resolve iter pattern of found.
                        # NOte: At this point it is safe to assume that the iter
                        # patterns in search and found are same because the
                        # validation was performed earlier.
                        ref_length = len(res_vfytext_list)
                        for param in VERIFY_PARAMS:
                            verify_params_list = details_dict[param]
                            param_list = details_dict[param][index]
                            param_value = param_list[i]
                            iter_pattern = self.get_iteration_pattern\
                                (param_value) if isinstance(param_value, str) \
                                else ""

                            if iter_pattern is not "":
                                res_list, status = self._expand_iter_pattern\
                                    (param_value, iter_pattern, vc_file)
                                if status and len(res_list) > 0:
                                    if identical:
                                        for cnt in range(0, len(res_vfytext_list)):
                                            verify_params_list\
                                                [index + cnt][i] = res_list[cnt]
                                    else:
                                        param_list[i:i+1] = res_list
                                else:
                                    # If there were problems in resolving iter
                                    # patterns of the found, then set a flag to
                                    # mark the verification text as False
                                    error = True
                                    error_list = res_list
                            else:
                                # If iter pattern not provided in found, then
                                # repeat found value n times where n is no of
                                # times the search was repeated.
                                if not identical:
                                    res_list = []
                                    for _ in range(0, ref_length):
                                        res_list.append(param_value)
                                    param_list[i:i+1] = res_list
                    else:
                        # If there were errors in resolving the iter
                        # patterns of the search then set a flag to mark
                        # verification text as False.
                        error = True
                        error_list = res_vfytext_list

                    if error:
                        if identical:
                            for num in range(0, len(error_list)):
                                verify_text_list[index + num][i] = False

                        else:
                            # if there were any problems in resolving the iteration
                            # patterns or if none of nodes in iter pattern are
                            # available in varconfig file,i.e.resolved_cmd_list=[],
                            # mark verify search as False, dont care to resolve
                            # other verify parameters. return details dict
                            cur_verify_text_list[i] = False
        return details_dict

    def arrange_per_td_block(self, details_dict, cmd_loc_list):
        """
        Rearrange details_dict values as per cmd_loc_list

        Returns updated details_dict with expanded values
        arranged in per_td_block order
        """
        status = self._validate_cmd_loc_list(cmd_loc_list)
        cmd_lst_length = len(details_dict['command_list'])
        if status is False or cmd_lst_length != cmd_loc_list[-1]:
            return details_dict

        new_details_dict = {key: [] for key in details_dict.keys()}
        new_cmd_loc_list = cmd_loc_list[:-1]
        while len(details_dict['command_list']) >\
                len(new_details_dict['command_list']):
            for i, loc in enumerate(new_cmd_loc_list):
                if loc < cmd_loc_list[i+1]:
                    for val in details_dict:
                        new_details_dict[val].append(details_dict[val][loc])
                    new_cmd_loc_list[i] += 1
        return new_details_dict

    def repeat_per_td_block(self, details_dict, cmd_loc_list):
        """
        Find the max iteration count(td block) from cmd_loc_list.
        Expand all command values in details_dict for 'repeat_count'
        times if repeat tag is 'yes'.
        """
        # Get repeat_count(largest delta between two consecutive
        # values in cmd_loc_list) from cmd_loc_list
        repeat_count = max(abs(val1 - val2) for (val1, val2) in\
                           zip(cmd_loc_list[1:], cmd_loc_list[:-1]))
        repeat_list = details_dict['repeat_list']

        for index, repeat_val in enumerate(repeat_list):
            # Proceed only if repeat tag is 'y' and the command index is
            # available in cmd_loc_list
            if isinstance(repeat_val, str) and \
             repeat_val.lower().startswith('y') and index in cmd_loc_list:
                cmd_pos = cmd_loc_list.index(index) + 1
                # Update cmd positions by adding repeat_count-1 to
                # remaining values in cmd_loc_list
                cmd_loc_list[cmd_pos:] = [val+repeat_count-1 for val in
                                          cmd_loc_list[cmd_pos:]]
                for param, _ in CMD_PARAMS.items():
                    param_list = details_dict[param]
                    element = param_list[index]
                    if param == 'repeat_list':
                        element = None
                    param_list[index:index+1] = [element]*repeat_count

        return details_dict, cmd_loc_list


###################
# Private methods
###################

    def _validate_cmd_iterpattern(self, cmd, cmd_iter_pattern):
        """
        Validate the different iteration patterns appearing
        on the command
        """
        # A command can have multiple iteration strings in it.
        # When more that one iteration string is used in a command
        # all the strings should be same.
        # In short mix of different iteration strings within a
        # command is not supported.

        status = True
        var_pat_list = self._get_varpat_list(cmd)
        iter_pattern_list = self._get_iterpattern_list(var_pat_list)
        for pat in iter_pattern_list:
            result = True if pat == cmd_iter_pattern else False

            if not result:
                print_error("Command: {0}".format(cmd))
                print_error("Mix of different iteration patterns is "
                            "not supported within a command "
                            "[{0} != {1}]".format(pat, cmd_iter_pattern))
            status = status and result
        return status

    def _validate_params_iterpattern(self, cmd, details_dict,
                                     cmd_iter_pattern, index):
        """
        Validate the iteration patterns in command
        parameters, with the iteration pattern of the command
        """
        status = True
        excl_list = ["verify_text_list", "verify_context_list",
                     "verify_on_list", "vc_file_list"]

        # if the command does not have an iteration other command
        # parameters also should not have any iteration pattern
        # However the verification parameters can have an iterations
        # even if the command does not have iterations

        # if the cmd has an iteration pattern then
        # the other command parameters may or may not have iteration pattern
        # and if they do it should be same as the iteration pattern of cmd
        supported_patterns = [""] if cmd_iter_pattern == ""\
            else ["", cmd_iter_pattern]

        for param, attrib in CMD_PARAMS.items():
            if param not in excl_list:
                element = details_dict[param][index]

                element_iter_pattern = self.get_iteration_pattern(element) \
                    if isinstance(element, str) else ""

                result = True if element_iter_pattern in supported_patterns\
                    else False

                if not result:
                    err_msg1 = "Command '{0}' does not have iterations, "
                    "So iterations are not allowed in other command params "
                    ", please remove iterations from '{1}'".format(cmd, attrib)

                    err_msg2 = "Iteration patterns used in cmd parameters "
                    "should match the iteration pattern used in the cmd={0} "
                    "please check iterations in '{1}'".format(cmd, attrib)

                    err_msg = err_msg1 if cmd_iter_pattern == "" else err_msg2
                    pNote(err_msg, "error")
                status = result and status
        return status

    def _validate_vfysearch_iterpattern(self, cmd, details_dict, index):
        """
        Validate the iteration pattern provided in each verification search
        for the command
        """
        final_status = True
        verify_text_list = details_dict["verify_text_list"][index]
        if verify_text_list is not None:
            for i in range(0, len(verify_text_list)):
                status = True
                verify_text = verify_text_list[i]

                vfy_iter_pattern = self.get_iteration_pattern(verify_text) \
                    if isinstance(verify_text, str) else ""

                if vfy_iter_pattern is not "":
                    var_pat_list = self._get_varpat_list(verify_text)
                    iter_pattern_list = self._get_iterpattern_list(var_pat_list)
                    for pat in iter_pattern_list:
                        result = True if pat == vfy_iter_pattern else False
                        if not result:
                            print_error("Command: {0}".format(cmd))
                            print_error("Mix of different iteration patterns is "
                                        "not supported within a verification search "
                                        "[{0} != {1}]".format(pat, vfy_iter_pattern))
                        status = status and result
                final_status = status and final_status
        return final_status

    def _validate_vfyparams_iterpattern(self, cmd, details_dict, index):
        """
        Validate the iter patterns provided in the verification
        search and its parameters (found, verify_on)
        """
        status = True
        verify_text_list = details_dict["verify_text_list"][index]
        if verify_text_list is not None:
            for i in range(0, len(verify_text_list)):
                verify_text = verify_text_list[i]
                vfy_iter_pattern = self.get_iteration_pattern(verify_text) \
                    if isinstance(verify_text, str) else ""

                supported_patterns = [""] if vfy_iter_pattern is ""\
                    else ["", vfy_iter_pattern]

                for param in VERIFY_PARAMS:
                    param_list = details_dict[param][index]
                    param_value = param_list[i]

                    param_iter_pattern = self.get_iteration_pattern\
                        (param_value) if isinstance(param_value, str) \
                        else ""

                    result = True if param_iter_pattern in supported_patterns\
                        else False

                    if not result:
                        err_msg1 = "Verification search '{0}' for cmd={1} "
                        "does not have iterations, So iterations are not "
                        "allowed in other verification related params"\
                            .format(verify_text, cmd)

                        err_msg2 = "Iteration patterns used in verification "
                        "related parameters should match the iteration "
                        "pattern used in the verification search={0} please "
                        "check iterations in the verify sections of cmd={1}"\
                            .format(verify_text, cmd)

                        err_msg = err_msg1 if vfy_iter_pattern == "" \
                            else err_msg2
                        pNote(err_msg, "error")
                    status = result and status
        return status

    @staticmethod
    def _get_varpat_list(cmd):
        """
        Get the list of variable patterns for the given
        command
        """
        var_pat_list = []
        if isinstance(cmd, str):
            var_search = re.search(r".*(\${(.*)}).*", cmd)
            if var_search:
                var_pat_list = re.findall(r"\${([^}]*)}", cmd)
        return var_pat_list

    @staticmethod
    def _get_iterpattern_list(var_pat_list):
        """Get the iteration pattern list for each command"""
        iter_pattern = ""
        iter_pat_list = []
        for var_pat in var_pat_list:
            nested_string_list = var_pat.split(" ")
            # split the variable pattern on a space to extract
            # individual words from the pattern.
            # Resulting in a posiibility of nested variable patter
            # like network1.ne1.${network1.ne1.shel+.id}
            for nested_string in nested_string_list:
                # split the nested string on the ${ to resolved nested strings
                string_list = nested_string.split("${")
                for string in string_list:
                    # extract the string from beginning till the last +
                    plus_match = re.match(r".*(\+)", string)
                    if plus_match:
                        iter_pattern = plus_match.group(0)
                        iter_pattern = iter_pattern.strip("${")
                        iter_pat_list.append(iter_pattern)
        return iter_pat_list

    def _expand_iter_pattern(self, cmd, iter_pattern, vc_file):
        """
        Expand the iteration patterns in a command
        and returns a new list with the iteration
        patterns in the command replaced with actual values
        from the vc_file.
        If there were any problems in resolving the iteration patterns
        then status is set to False
        """
        resolved_cmd_list = []

        # get the list of
        # 1. parent names (i.e. the value of name attribute of the parents
        #    in the iter pattern
        # 2. parent list i.e. the xml node values of the parents provided
        #    in the iter pattern.
        # 3. iter list i.e. the the list of nodes to be iterated upon.
        name_list = self._get_parent_name_list(iter_pattern)
        parent_list = self._get_iter_parents(name_list, vc_file)
        iter_list = self._get_iter_list(iter_pattern)

        # If there are any problems in finding the parent nodes in the vc_file
        # set status = False
        status = False if len(parent_list) == 0 or len(name_list) == 0 \
            else True

        if status:
            # initialize the last parent name to the name of the first parent
            # in the parent list, iterate over the list and create a dotted
            # name notation like firstparent.secondparent.thirdparent.. etc.
            last_parent_name = name_list[0]
            for i in range(1, len(name_list)):
                last_parent_name = "{0}.{1}".format(last_parent_name, name_list[i])

            parent_name_list = [last_parent_name]
            parent_node_list = [parent_list[-1]]

            replacement_list, status = self._get_replacement_list\
                (iter_list, parent_node_list, parent_name_list)

            if status:
                for string in replacement_list:
                    new_cmd = cmd.replace(iter_pattern, string)
                    resolved_cmd_list.append(new_cmd)

        return resolved_cmd_list, status

    @staticmethod
    def _get_parent_name_list(cmd_iter_pattern):
        """
        Get the name list of parents from the
        cmd_iter_pattern.
        Note: Here no check is done to verify if node with
        the provided name exists in the vc_file. The check will
        be done while getting the parent_node_list.
        """
        parent_name_list = []
        name_list = cmd_iter_pattern.split(".")
        for name in name_list:
#             cur_parent_name = "" if len(parent_name_list) == 0\
#             else parent_name_list[-1]

            if name.endswith("+"):
                break
            else:
#                 parent_name = name if cur_parent_name == ""\
#                 else "{0}.{1}".format(cur_parent_name, name)
                parent_name_list.append(name)
        return parent_name_list

    def _get_iter_parents(self, parent_name_list, vc_file):
        """
        Get the parent node list from the
        cmd_iter_pattern
        Note: Here check is done to verify if the node
        with the provided name exists under the proper
        parent in the vc_file.
        If any of the child node does not exist then
        an empty list is returned.
        """
        parent_node_list = []

        # Get the root of vc_file if there are problems is getting the root
        # catch the exception and assign root=None
        try:
            root = xml_Utils.getRoot(vc_file)
        except Exception as exception:
            root = None
            print_exception(exception)

        # initialize parent as root
        parent = root
        # for each name in the parent_name list
        # find the element with same name under current parent in vc_file
        # if element could not be found assign parent_node_list =[]
        # if element could be found add it to the parent_node_list
        # and make this element as the parent for the next iteration
        for name in parent_name_list:
            if parent is not None and parent is not False:
                node = self._find_node_with_name(parent, name)
                if node is not None and node is not False:
                    parent = node
                    parent_node_list.append(parent)
                else:
                    print_error("Could not find node={0} under parent={1} "
                                "in file={2}".format(name, parent.tag, vc_file))
                    parent_node_list = []
                    break
            else:
                print_error("Error while parsing the variable config file="
                            "{0}".format(vc_file))
        return parent_node_list

    @staticmethod
    def _get_iter_list(cmd_iter_pattern):
        """
        Get the iter list from the cmd_iter_pattern
        """
        iter_list = []
        node_list = cmd_iter_pattern.split(".")
        for node in node_list:
            if node.endswith("+"):
                iter_list.append(node)
        return iter_list

    @staticmethod
    def _get_replacement_list(iter_list, pnode_list, pname_list):
        """
        Get the replacement list for a command
        based on its iteration pattern
        """

        # THis algorithm fixes the intial parent_node and parent_names as
        # Then for each iteration requested in the iter_list
        # finds all the child nodes under the initial parent
        # IN subsequent iterations the child node list becomes the parent_list
        # for the next element in the iter_list.
        status = True
        for i in range(0, len(iter_list)):
            child_tag = iter_list[i].strip("+")
            replacement_list = []
            new_pnode_list = []
            new_pname_list = []
            for i in range(0, len(pnode_list)):
                pnode = pnode_list[i]
                pname = pname_list[i]
                cnode_list = pnode.findall(child_tag)
                # If the user has requested iteration over all child nodes
                # of a particular node in the varconfig file, and while
                # parsing the varconfig file there are no child nodes
                # for that parent, then it is not a failure scenario.
                # It is understood that user wnats tot use all child nodes under
                # the specific node if available, so we do not mark iter pattern
                # resoltions as False but simply continue.
                result = False if len(cnode_list) == 0 else True
                if not result:
                    pNote("Could not find child={0} under parent={1} in "
                          "variable config file".format(child_tag, pname),
                          "error")
                    continue
                for cnode in cnode_list:
                    cname = cnode.get("name", None)
                    result = False if cname is None else True
                    if result:
                        name = "{0}.{1}".format(pname, cname)
                        new_pnode_list.append(cnode)
                        new_pname_list.append(name)
                        replacement_list.append(name)
                    else:
                        # If name attribute is not available in the var config
                        # file for any child modes, that means user has provided
                        # a child he wants to use, but format is incorrect
                        # in this case resolving cmd iterations will be marked
                        # as false because without the name value fetching the
                        # data for the child is impossible.
                        print_error("'name' attribute is essential to "
                                    "identify a node in the variable "
                                    "file, 'name' attribute is missing "
                                    "in some of the '{0}' nodes under {1}"
                                    .format(child_tag, pname))
                        status = False
                        continue
            pnode_list = new_pnode_list
            pname_list = new_pname_list
        return replacement_list, status

    @staticmethod
    def _find_node_with_name(parent, name):
        """
        Find the node with provided name under the given
        parent in an xml file
        """
        value = False
        for child in parent:
            child_name = child.get("name")
            if child_name == name:
                value = child
                break
        return value

    @staticmethod
    def _check_list_lengths(details_dict):
        """
        Verify whether cmd, cmd_params, verify_search, verify_params are
        of same length

        Verify whether each list in verify_search, verify_params are of
        same length
        """
        status = True
        cmd_list = details_dict["command_list"]
        cmd_length = len(cmd_list)
        for param, _ in CMD_PARAMS.items():
            param_list = details_dict[param]
            if len(param_list) == cmd_length:
                cmd_status = True
            else:
                cmd_status = False
                print_error("number of {0} did not match number of commands"
                            "={1}".format(param, cmd_length))

        verify_list = details_dict["verify_text_list"]
        for i, search_list in enumerate(verify_list):
            vfy_status = True
            for vfy_param in VERIFY_PARAMS:
                vfy_param_list = details_dict[vfy_param][i]
                if search_list and vfy_param_list:
                    if len(vfy_param_list) == len(search_list):
                        vfy_status = True
                    else:
                        vfy_status = False
                        print_error("length of {0} did not match the no of "
                                    "verification searches".format(vfy_param))
        status = status and cmd_status and vfy_status

        return status

    @staticmethod
    def _validate_cmd_loc_list(cmd_loc_list):
        """
        Validate cmd_loc_list.
        Returns False(bool) when
            1. length of cmd_loc_list is less than 2
            2. first element of cmd_loc_list is not zero
            3. cmd_loc_list values are not in ascending order
            4. cmd_loc_list has duplicate value(s)
        else return True(bool)
        """
        status = True
        if isinstance(cmd_loc_list, list):
            if len(cmd_loc_list) < 2 or cmd_loc_list[0] != 0:
                status = False
            else:
                for i in range(len(cmd_loc_list)-1):
                    if cmd_loc_list[i] > cmd_loc_list[i+1]:
                        status = False
        else:
            status = False
        return status
