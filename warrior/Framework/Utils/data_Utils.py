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

import os
import re
import sys
from collections import OrderedDict
from ast import literal_eval
from Framework.Utils import xml_Utils, string_Utils, testcase_Utils,\
config_Utils, file_Utils
from Framework.Utils.testcase_Utils import pNote
from Framework.Utils.print_Utils import print_info, print_warning,\
print_error, print_debug, print_exception
from Framework.ClassUtils.testdata_class import TestData, TestDataIterations
from Framework.Utils.xml_Utils import get_attributevalue_from_directchildnode as av_fromdc
from Framework.Utils.string_Utils import sub_from_varconfigfile
from Framework.ClassUtils import database_utils_class

cmd_params = OrderedDict([("command_list", "send"),
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
                          ("log_list", "monitor"),
                          ("verify_on_list", "verify_on"),
                          ("inorder_search_list", "inorder"),
                          ("verify_map_list", ""),
                          ("operator_list", "operator"),
                          ("cond_value_list", "cond_value"),
                          ("cond_type_list", "cond_type"),
                          ("repeat_list", "repeat")])


def get_nc_request_rpc_string(config_datafile, xmlns, request_type, xmlns_tag):
    """
    Get the Request of netconf as a list
    """

    configuration = ""
    status = True
    try:
        data = xml_Utils.get_element_by_attribute(config_datafile,
                                                  request_type,
                                                  xmlns_tag, xmlns)
        if data:
            configuration = xml_Utils.convert_dom_to_string(data)
        else:
            testcase_Utils.pNote("XMLNS={0} is not found in config "
                                 "file ={1}".format(xmlns, config_datafile),
                                 "error")
            status = "error"

    except IOError as err:
        testcase_Utils.pNote("File does not exist: {0}".format(err),
                             "error")
        status = "error"

    except Exception as exception:
        print_exception(exception)
        status = "error"
    return status, configuration


def getSystemData(datafile, system_name, cnode, system='system'):
    """
    Returns the value for tag or attrib of a system or susbsystem

    If an attribute and a tag of the same name is present then
    returns the value of the attribute.

    Incase of attribute the value is the attribute value.
    Incase of a tag the value is the text of the tag.

    :Arguments:
        1. datafile(string) = absolute path of the system datafile
        2. system_name (string) = This can be name of the\
            system or a subsystem. In case of subsystem only\
            single subsystem is supported.
        3. cnode(string) = attributes or tag whose value is to be\
        obtained.

    :Returns:system='system'
        1. False if the system/subsystem cannot be found in the datafile.
        2. If an attribute or tag is not present its value=boolean False
        3. If a tag is present but has no text its value=None
    """
    value = False
    element = _get_system_or_subsystem(datafile, system_name, tag=system)
    if element is not None:
        value = element.get(cnode, None)
        if value is None:
            value = xml_Utils.get_text_from_direct_child(element, cnode)
        value = sub_from_env_var(value)

    return value


def get_credentials(datafile, system_name, myInfo=[], tag_name="system",
                    attr_name="name", **kwargs):
    """
    Takes an list(myInfo) of attribute or tag names as input and returns a
    dictionary having values for each of the requested attribute or tag name.

    If an empty list provided as myInfo returns a dictionary having
    all the attribute and tags with their values

    If an attribute and a tag of the same name is present then
    returns the value of the attribute.

    Incase of attribute the value is the attribute value.
    Incase of a tag the value is the text of the tag.

    If the tag has child elements, the value will be a dictionary with
    all its child tags as keys & their texts as values.

    :Arguments:
        1. datafile(string) = absolute path of the system datafile
        2. system_name (string) = This can be name of the\
            system or a subsystem. In case of subsystem only\
            single subsystem is supported.
        3. List of attributes or tags whose values are to be\
        obtained.

    :Returns:
        1. Dictionary of attributes/tags and their values
        2. False if the system/subsystem cannot be found in the datafile.
        3. If an attribute or tag is not present its value=boolean False
        4. If a tag is present but has no text its value=None
    """
    # Find the parent system
    element = _get_system_or_subsystem(datafile, system_name, tag=tag_name,
                                       attr=attr_name)
    value = False
    if element is not None and element is not False:
        output_dict = {}
        if len(myInfo) == 0:
            for child in element:
                output_dict[child.tag] = child.text
            attrib_dict = element.attrib
            output_dict.update(attrib_dict)
        else:
            for x in myInfo:
                # get the value of 'element' attribute 'x'
                cred_value = element.get(x, None)
                if cred_value is None:
                    # if 'x' is in the 'element', get its child elements as list
                    child_list = []
                    if element.find(x) is not None:
                        child_list = xml_Utils.get_child_node_list(element.find(x))
                    # If child list is not empty, get the child tags &
                    # its values as dictionary
                    if child_list:
                        cred_value = {}
                        for child in child_list:
                            cred_value[child.tag] = child.text
                    else:
                        cred_value = xml_Utils.get_text_from_direct_child(element,
                                                                          x)
                output_dict[x] = cred_value
        value = output_dict
    updated_dict = sub_from_env_var(value)
    return updated_dict


def _get_system_or_subsystem(datafile, system_name, tag="system", attr='name'):
    """Get a system or subsystem node
    returns None if system or subsystem could not be found"""
    element = None
    system_name, subsystem_name = split_system_subsystem(system_name)

    system_node = xml_Utils.getElementWithTagAttribValueMatch(datafile, tag,
                                                              attr, system_name)
    msg1 = 'system={0} is not found in datafile={1}'.format(system_name,
                                                            datafile)
    msg2 = 'The subsystem={0} is not found under ' \
           'the system={1} in datafile={2}'.format(subsystem_name, system_name,
                                                   datafile)

    if system_node is not False and system_node is not None:
        if subsystem_name is None:
            element = system_node
        else:
            subsystem = xml_Utils.getElementWithTagAttribValueMatch(system_node,
                                                                    'subsystem',
                                                                    attr,
                                                                    subsystem_name)
            if subsystem is not False and subsystem is not None:
                element = subsystem
            else:
                msg = msg2
    else:
        msg = msg1
    if element is None or element is False:
        pNote(msg, "warn")
    return element

def get_session_id(system_name, session_name=None):
    """Returns the session-id based on the provided system_name
    :Arguments:
        1. system_name (string) = This can be name of the\
        system or a subsystem. In case of subsystem only\
        single subsystem is supported.

        2. session_name (string) = Name of the session to\
        the system or to the session.
    :Returns:
        1. For system returns system_name + session_name
        2. For subsystems returns\
        system_name + subsystem_name + session_name
    """
    system_name, subsystem_name = split_system_subsystem(system_name)

    if subsystem_name is None:
        session_id = system_name
    else:
        session_id = system_name + subsystem_name
    if session_name is not None:
        session_id = session_id + session_name
    return session_id


def get_var_configfile(datafile, system_name):
    """Gets the var config file for the system with
    provided system_name in the datafile """

    status = _check_tag_or_attr_exists(datafile, system_name,
                                       "var_config_file", "system")
    var_tag = "var_config_file" if status is True else "variable_config"
    var_config_file = get_filepath_from_system(datafile, system_name, var_tag)[0]
    return var_config_file


def get_child_tag_value_list(datafile, system_name, child_list=[], *args):
    """Parse the datafile for the system and get the tag list ,
    value list of all the children provided in the child_list"""

    element = xml_Utils.getElementWithTagAttribValueMatch(datafile, 'system',
                                                          'name', system_name)
    if (element is not None and element is not False):
        tag_list = []
        value_list = []
        for child in child_list:
            cnode = element.find(child)
            if (cnode is not None and cnode is not False):
                for child in cnode:
                    tag_list.append(child.tag)
                    value_list.append(child.text)
        return tag_list, value_list
    return False


def update_datarepository(input_dict):
    """Updates the data repository with the provided
    dictionary"""
    data_repository = config_Utils.data_repository
    data_repository.update(input_dict)


def get_object_from_datarepository(object_key, verbose=True):
    """Gets the value for the object with the provided name from datarepositoy """
    try:
        data_repository = config_Utils.data_repository
        obj = data_repository[object_key]
    except KeyError:
        obj = False
        if verbose:
            print_warning('{0} is not found in data repository'.format(object_key))
    return obj


def get_command_details_from_testdata(testdatafile, varconfigfile=None, **attr):
    """Gets the command_list, startprompt_list, endprompt_list,
    verify_list from testdata """
    testdata_dict = {}
    var_sub = attr.get('var_sub', None)
    title = attr.get('title', None)
    row = attr.get('row', None)
    system_name = attr.get('system_name', None)
    datafile = attr.get("datafile", None)
    print_debug("title:{0} row:{1}".format(title, row))
    not_found = 0

    # when the testdatafile is a dictionary - this happens only when
    # the testdatafile is taken from database server
    if isinstance(testdatafile, dict):
        print_info("Resolving testdata details from DB system - "
                   "'{}'".format(testdatafile.get('td_system')))
        db_td_obj = database_utils_class.\
         create_database_connection('dataservers', testdatafile.get('td_system'))
        root = db_td_obj.get_tdblock_as_xmlobj(testdatafile)

        # if testdata block in the datafile has separate db system
        # for 'testdata-global' values
        if testdatafile.get('global_system') is not None:
            print_info("Resolving testdata-global block from DB system - "
                       "'{}'".format(testdatafile.get('global_system')))
            db_tdglobal_obj = database_utils_class.\
             create_database_connection('dataservers',
                                        testdatafile.get('global_system'))
            global_obj = db_tdglobal_obj.get_globalblock_as_xmlobj(testdatafile)
            db_tdglobal_obj.close_connection()
        else:
            global_obj = root.find("global")

        db_td_obj.close_connection()
    else:
        root = xml_Utils.getRoot(testdatafile)
        global_obj = root.find("global")

    # when the varconfigfile is a dictionary - this happens only when
    # the varconfigfile is taken from database server
    if isinstance(varconfigfile, dict):
        print_info("Resolving varconfig details from DB system - "
                   "'{}'".format(varconfigfile.get('var_system')))
        db_var_obj = database_utils_class.\
         create_database_connection('dataservers', varconfigfile.get('var_system'))
        varconfigfile = db_var_obj.get_varblock_as_xmlobj(varconfigfile)
        db_var_obj.close_connection()

    for testdata in root.findall("testdata"):
        # use only test data blocks that are marked to execute
        exec_flag = get_exec_flag(testdata, title, row)
        if testdata.get("execute") == "yes" and exec_flag:
            testdata_key="{0}{1}".format(testdata.get('title',""), \
                                         _get_row(testdata))
            details_dict = _get_cmd_details(testdata, global_obj, system_name,
                                            varconfigfile, var_sub=var_sub)
            start_pat =  _get_pattern_list(testdata, global_obj)
            end_pat =  _get_pattern_list(testdata, global_obj, pattern="end")
            details_dict = sub_from_env_var(details_dict, start_pat, end_pat)

            print_info("var_sub:{0}".format(var_sub))
            td_obj = TestData()
            details_dict = td_obj.varsub_varconfig_substitutions\
            (details_dict, vc_file=None, var_sub=var_sub, start_pat=start_pat, end_pat=end_pat)

            details_dict = td_obj.wdf_substitutions(details_dict, datafile, kw_system_name=system_name)
            details_dict = sub_from_env_var(details_dict)

            td_iter_obj = TestDataIterations()
            details_dict, cmd_loc_list = td_iter_obj.resolve_iteration_patterns\
            (details_dict)
            iter_type = testdata.get('iter_type', None)
            # Type-2 iteration - per_td_block
            if iter_type == "per_td_block":
                details_dict, cmd_loc_list = td_iter_obj.repeat_per_td_block\
                (details_dict, cmd_loc_list)
                details_dict = td_iter_obj.arrange_per_td_block\
                (details_dict, cmd_loc_list)

            # List substitution happens after iteration because list sub cannot recognize the + sign in iteration
            cmd_list_substituted, verify_text_substituted = td_obj.list_substitution_precheck(varconfigfile, details_dict, start_pat, end_pat)
            td_obj.list_substitution(details_dict, varconfigfile, cmd_list_substituted, verify_text_substituted, start_pat, end_pat)

            details_dict = td_obj.varsub_varconfig_substitutions\
            (details_dict, vc_file=varconfigfile, var_sub=None, start_pat=start_pat, end_pat=end_pat)
            testdata_dict[testdata_key]=details_dict
            found = 1

        else:
            not_found += 1

    if not_found == len(root.findall("testdata")):
        print_warning('There are no rows with execute=yes ' \
                      'and title={0}, row={1} in testdata {2} '.format(title,
                                                                       row,
                                                                       testdatafile))
    return testdata_dict


def _get_mapping_details(global_obj, vfylist):
    """
        get cmd-verify text mapping detail from xml (global_obj) and vfylist
        return a parsed verify list and the mapping list
    """
    map_list = []
    g_verify = global_obj.find("verifications") if global_obj is not None \
        else None
    for index, element in enumerate(vfylist):
        if element is not None:
            sub_vfylist = element.split(',')
            sub_map_list = []
            for sub_element in sub_vfylist:
                if ':m' in sub_element.lower():
                    sub_map_list.append("2")
                else:
                    # Check if the verify list has combo value, if yes,
                    # expand the mapping list as well
                    combo_value = av_fromdc(g_verify, sub_element,
                        "combo") if g_verify is not None else False
                    if combo_value:
                        for i in combo_value.split(","):
                            if ':m' in i.lower():
                                sub_map_list.append("2")
                            else:
                                sub_map_list.append("1")
                    else:
                        sub_map_list.append("1")

            map_list.append(sub_map_list)
            vfylist[index] = vfylist[index].replace(':M', '')
            vfylist[index] = vfylist[index].replace(':m', '')
        else:
            map_list.append(None)
    return (vfylist, map_list)


def _get_cmd_details(testdata, global_obj, system_name,
                     varconfigfile, var_sub=None):
    """Get the command details from testdata file
    as a details dictionary"""
    details_dict = {}
    verifyparams = ["verify_text_list", "verify_context_list", "operator_list",
                    "cond_value_list", "cond_type_list"]

    # Initialize all lists
    for param, attrib in cmd_params.items():
        details_dict[param] = []
        if param == "verify_list":
            vfylist = _get_cmdparams_list(testdata, global_obj, "verify")
            vfylist, maplist = _get_mapping_details(global_obj, vfylist)
            vfylist = string_Utils.sub_from_varconfig(None, vfylist, var_sub)
            vfylist = string_Utils.sub_from_varconfig(varconfigfile, vfylist)
            resultant_list = vfylist
        elif param in verifyparams:
            vfylist = details_dict["verify_list"]
            resultant_list = _get_verification_details(testdata, global_obj,
                                                       vfylist, attrib)
        elif param == "verify_on_list":
            vfylist = details_dict["verify_list"]
            resultant_list = _get_verification_details(testdata, global_obj,
                                                       vfylist, attrib,
                                                       system_name)
        elif param == "verify_map_list":
            vfylist = details_dict["verify_list"]
            vfylist, maplist = _get_mapping_details(global_obj, vfylist)
            resultant_list = maplist
        else:
            resultant_list = _get_cmdparams_list(testdata, global_obj, attrib)
            if param == "sys_list":
                details_dict["vc_file_list"] = []
                vc_file_list = _get_vc_details(resultant_list, system_name,
                                               varconfigfile)
                details_dict["vc_file_list"].extend(vc_file_list)
        details_dict[param].extend(resultant_list)
    return details_dict


def _get_global_var(global_obj, key):
    return global_obj.find(key) if global_obj is not None else None


def _get_cmdparams_list(testdata, global_obj, cmd_attrib):
    """Get the list of values for a
    command parameter by reading testdata
    If user has not provided a specific value for
    command attribute returns the global values
    assigned in the testdata """

    global_cmd_params = global_obj.find("command_params") if global_obj is \
        not None else None
    global_exempt_list = ["send", "monitor"]
    resultant_list = []
    value_list = xml_Utils.getNodeListbyAttribute(testdata, "command",
                                                  cmd_attrib)
    for value in value_list:
        default_value = global_cmd_params.get(
            cmd_attrib) if global_cmd_params is not None else None
        if not cmd_attrib in global_exempt_list:
            value = default_value if value is None or value is "" else value
        else:
            if cmd_attrib in testdata.attrib and cmd_attrib == "monitor":
                value = testdata.attrib[cmd_attrib]
        resultant_list.append(value)
    return resultant_list


def _get_verification_details(testdata, global_obj, verify_list, cmd_attrib, system_name=None):
    """From the testdata file takes a testdata node and
    a list of nodes with verification present as input

    :Return:
        1. a list of verifcation_text or verification_context
    """
    g_verify = global_obj.find("verifications") if global_obj is not None \
        else None
    resultant_list = []
    for verify in verify_list:
        if verify is None or verify == "":
            value = None
            resultant_list.append(value)
        elif verify is not None:
            resultant_sublist = []
            verify_sublist = verify.split(",")
            new_verify_sublist = []
            for element in verify_sublist:
                # Get the attribute value(name:'combo') of the element in
                # the "global/verifications" section
                combo_value = av_fromdc(g_verify, element,
                              "combo") if g_verify is not None else False
                # Add combo value if exists else add verify tag in new list
                if combo_value:
                    new_verify_sublist.extend(combo_value.split(","))
                else:
                    new_verify_sublist.append(element)
            for element in new_verify_sublist:
                element = element.strip()
                value = xml_Utils.get_attributevalue_from_directchildnode(
                    testdata, element, cmd_attrib)
                default_value = av_fromdc(g_verify, element,
                                          cmd_attrib) if g_verify is not None else False
                if value is False:
                    value = default_value
                    if value is False:
                        print_warning(
                            "could not find specific or global value  " \
                            "for verification node={0}".format(element))
                if value is None or value is "":
                    value = 'yes' if cmd_attrib == "found" else value
                    value = system_name if cmd_attrib == "verify_on" else value
                value = value if not value else str(value).strip()
                resultant_sublist.append(value)
            resultant_list.append(resultant_sublist)
    return resultant_list

def _get_vc_details(sys_list, system_name, varconfigfile):
    """ To get the variable_config files specific to
    the systems in the sys_list from the datafile """
    vc_file_list = []
    data_file = config_Utils.datafile
    for system in sys_list:
        if system and system!=system_name:
            # Get system name when sys tag has both system & session name
            system = system.split(".")[0]
            if system.startswith("[") and system.endswith("]"):
                system = system_name.split("[")[0] + system
            vc_file = get_var_configfile(data_file, system)
            # when the vc_file is a dictionary - this happens only when
            # the vc_file is taken from database server
            if isinstance(vc_file, dict):
                print_info("Resolving varconfig details from DB system - "
                           "'{}'".format(vc_file.get('var_system')))
                db_var_obj = database_utils_class.\
                    create_database_connection('dataservers',
                                               vc_file.get('var_system'))
                vc_file = db_var_obj.get_varblock_as_xmlobj(vc_file)
                db_var_obj.close_connection()
        else:
            vc_file = varconfigfile

        vc_file_list.append(vc_file)
    return vc_file_list


def _get_pattern_list(testdata, global_obj, pattern="start"):
    """
        Get the pattern attribute from either the current testdata block
        or from the global section
    """

    global_var_pattern = global_obj.find("variable_pattern") if global_obj is \
        not None else None
    if pattern == "start":
        resultant = "${"
    else:
        resultant = "}"

    if testdata.get(pattern+"_pattern") is not None:
        resultant = testdata.get(pattern+"_pattern")
    elif global_var_pattern is not None and global_var_pattern.\
            get(pattern+"_pattern") is not None:
        resultant = global_var_pattern.get(pattern+"_pattern")

    return resultant


def get_exec_flag(testdata, title, row):
    """Get exec flag value """
    exec_flag = False
    # Get row or rownum or row_num from testdatafile.

    process_row = _get_row(testdata)

    if title and row:
        if testdata.get('title', None) == title and process_row == row:
            exec_flag = True
    elif title:
        if testdata.get('title', None) == title and process_row is None:
            exec_flag = True
        elif testdata.get('title', None) == title and process_row == 'none':
            exec_flag = True
        elif testdata.get('title', None) == title and process_row == '':
            exec_flag = True
    elif row:
        if process_row == row and testdata.get('title', None) == None:
            exec_flag = True
        elif process_row == row and testdata.get('title', None) == 'none':
            exec_flag = True
        elif process_row == row and testdata.get('title', None) == '':
            exec_flag = True
    else:
        exec_flag = True

    return exec_flag


def _get_row(testdata):
    """Get row or rownum or row_num from in testdatafile"""

    keys = ["row", "row_num", "rownum"]
    value = ""
    for key in keys:
        td_row = testdata.get(key, None)
        if td_row is None:
            continue
        else:
            value = td_row
            break
    return value


def get_verify_text_context_as_list(testdata, verify_list):
    """From the testdata file takes a testdat node and
    a list of nodes with verification present as input

    :Return:
        1. a list of verifcation_text
        2. a list of verification context """

    verify_text_list = []
    verify_context_list = []

    for verify in verify_list:
        if verify is None:
            verify_text = None
            verify_context = None
            verify_text_list.append(verify_text)
            verify_context_list.append(verify_context)

        elif verify is not None:
            verify_text_sublist = []
            verify_context_sublist = []
            verify_sublist = verify.split(",")
            for element in verify_sublist:
                verify_text = xml_Utils.\
                    get_attributevalue_from_directchildnode(testdata, element,
                                                            "search")
                verify_context = xml_Utils.\
                    get_attributevalue_from_directchildnode(testdata,
                                                            element, "found")
                if verify_text is False:
                    print_error(
                        "could not find childnode:{0} under testdata:"
                        "{1}".format(element, testdata))
                if verify_context is None:
                    verify_context = "yes"
                verify_text_sublist.append(verify_text)
                verify_context_sublist.append(verify_context)

            verify_text_list.append(verify_text_sublist)
            verify_context_list.append(verify_context_sublist)

    return verify_text_list, verify_context_list


def verify_resp_across_sys(match_list, context_list, command,
                           response, varconfigfile=None, verify_on_list=None,
                           verify_list=None, remote_resp_dict=None,
                           endprompt="", verify_group=None):
    """ New method to verify response of a command
    sent on one system with the response recieved from
    another system """

    msg = ("Verification required for command: '{0}' ".format(command))
    testcase_Utils.pNote(msg, "debug")

    status = True
    for i in range(0, len(verify_on_list)):
        for j in range(0, len(verify_on_list[i])):
            temp_list = verify_on_list[i][j].split(".")
            if len(temp_list) > 1:
                verify_on_list[i][j] = get_session_id(temp_list[0],
                                                      temp_list[1])
            else:
                verify_on_list[i][j] = get_session_id(temp_list[0])
            # print "\n---------- VERIFICATION --- Search Pattern: {0} ---
            # Pattern Context: {1} ----------\n".format(match_list[i],
            # context_list[i])
            try:
                data = remote_resp_dict[verify_on_list[i][j]]
                tmp_status = verify_cmd_response(
                                [match_list[i]], [context_list[i]], command,
                                data, verify_on_list[i][j], varconfigfile,
                                endprompt, verify_group)
                status = status and tmp_status
            except KeyError:
                print_error("Response could not be collected for {0}, hence, "
                            "it cannot be verified".format(
                                                verify_on_list[i][j]))
                status = "ERROR"
                # print "\n---------- END OF VERIFICATION ----------\n"
    return status


def get_no_impact_logic(context_str):
    """Get the silent tag from context
    return silence value and context value"""
    return {'YES:NOIMPACT': (True, 'YES'), 'NO:NOIMPACT': (True, 'No'), 'NO': (False, 'No'), 'YES': (False, 'YES')}.get(context_str.upper())


def convert2type(value, data_type='str'):
    """Convert value to data_type and return value in that data_type
    Currently supported are str/int/float only
    """
    type_funcs = {'str': str, 'int': int, 'float': float}
    convert = type_funcs[data_type]
    return convert(value)


def verify_cmd_response(match_list, context_list, command, response,
                        verify_on_system, varconfigfile=None, endprompt="",
                        verify_group=None):
    """Verifies the response with the provided
    match and context list
    """
    err_msg = "Incorrect or no value provided for verification search/found, "
    "check the verification data provided for the command. Command result will"
    " be marked as ERROR"

    if varconfigfile and varconfigfile is not None:
        match_list = string_Utils.sub_from_varconfig(varconfigfile, match_list)
    verify_status = True

    for i in range(0, len(match_list)):
        nogroup = False
        if context_list[i] and match_list[i]:
            noiimpact, found = get_no_impact_logic(context_list[i])
            found = testcase_Utils.pConvertLogical(found)
            if response:
                match_object = re.search(match_list[i], response)
            else:
                match_object = False
            if match_object:
                match = match_object.group()
                msg = "{0} '{1}' in  response to '{2}' on {4} :[{3}]:".format(
                        "Found ", match, command, "pattern matched",
                        verify_on_system)
                cond_value = verify_group[1][i]
                if cond_value:
                    grps = match_object.groups()
                    if len(grps) == 1:
                        actual_value = grps[0]
                        operator = verify_group[0][i]
                        cond_type = verify_group[2][i]
                        status = verify_relation(actual_value, cond_value,
                                                 operator, cond_type)
                        msg += "\n{0} comparison: {1} {2} {3} ".format(
                            cond_type or "str", actual_value, operator,
                            cond_value)
                        msg += "succeeded" if status else "failed"
                    else:
                        msg += ("pattern to compare should have exactly one "
                                "group to match with the condition value: "
                                "pattern failed")
                        nogroup = True
                        status = False
                else:
                    status = True
            else:
                match = match_list[i]
                msg = "{0} '{1}' in  response to '{2}' on {4} :[{3}]:".format(
                        "Did not find", match, command, "pattern match failed",
                        verify_on_system)
                status = False
            if found is status:
                result = False if not found and nogroup else True
            elif found is None:
                msg = err_msg
                result = "ERROR"
            else:
                if noiimpact:
                    result = True
                    testcase_Utils.pNote("Noimpact was requested on the below "
                                         "verification, hence the failure "
                                         "would not impact command status")
                else:
                    result = False
            testcase_Utils.pNote(msg, "debug")
        elif context_list[i] and match_list[i] == "":
            noiimpact, found = get_no_impact_logic(context_list[i])
            found = testcase_Utils.pConvertLogical(found)
            escapes = ''.join([chr(char) for char in range(1, 32)])
            response = re.sub(endprompt, "", response).strip()
            response = response.translate(None, escapes)
            if found:
                # found = context
                result = True if response == "" else False
            else:
                result = False if response == "" else True

            verification_text = "verification success" if result else "veri"
            "fication failed"
            msg = "Response " if found else "No response "
            msg += "found from command '{0}' on {2} :[{1}]:".format(
                            command, verification_text, verify_on_system)
            testcase_Utils.pNote(msg)
        else:
            testcase_Utils.pNote(err_msg, "error")
            result = "ERROR"
        if result == "ERROR" or verify_status == "ERROR":
            result = "ERROR"
            verify_status = "ERROR"
        verify_status = verify_status and result
    # print "\n---------- END OF VERIFICATION ----------\n"
    return verify_status


def verify_data(expected, key, data_type='str', comparison='eq'):
    """Verify the value of the key in data repository matches
    with expected value
    """
    def validate():
        result = "TRUE"
        err_msg = ""
        if data_type not in type_funcs:
            err_msg += "type {} not supported, only one of {} supported\n".\
                format(data_type, '/'.join(type_funcs.keys()))
            result = "ERROR"
        else:
            convert = type_funcs[data_type]
            try:
                exp = convert(expected)
            except ValueError:
                err_msg += "expected {} should be of type {}\n".format(
                                                        expected, data_type)
                result = "ERROR"
            except Exception as e:
                err_msg += "Got unknown exception {}, please check\n".format(e)
                result = "EXCEPTION"
        if comparison not in comp_funcs:
            err_msg += "valid comparisons are {}\n".\
                format('/'.join(comp_funcs.keys()))
            result = "ERROR"
        return result, err_msg, exp

    type_funcs = {'str': str, 'int': int, 'float': float}
    comp_funcs = {
        'eq': lambda x, y: x == y,
        'ne': lambda x, y: x != y,
        'gt': lambda x, y: x > y,
        'ge': lambda x, y: x >= y,
        'lt': lambda x, y: x < y,
        'le': lambda x, y: x <= y
    }
    result, err_msg, exp = validate()
    value = get_object_from_datarepository(key)
    if not value:
        err_msg += "key {} not present in data repository\n".format(key)
        result = "ERROR"
    if result != "TRUE":
        print_error(err_msg)
    elif not comp_funcs[comparison](value, exp):
        result = "FALSE"
    return result


def verify_resp_inorder(match_list, context_list, command, response,
                        varconfigfile=None, verify_on_list=None,
                        verify_list=None, remote_resp_dict=None,
                        verify_group=None):
    """ Method for in-order search.
    Verifies the 'search strings' in the system response
    and also verifies whether they are in order or not """

    msg = ("In-order verification requested for the command: "
           "'{0}' ".format(command))
    testcase_Utils.pNote(msg, "debug")

    if varconfigfile and varconfigfile is not None:
        match_list = string_Utils.sub_from_varconfig(varconfigfile, match_list)

    status = True
    if isinstance(verify_list, str):
        verify_list = verify_list.split(",")

    resp_details_dict = _get_resp_details(match_list, context_list,
                                          verify_on_list, verify_list,
                                          remote_resp_dict)

    for system in resp_details_dict:
        if resp_details_dict[system]:
            sys_status = verify_inorder_cmd_response(match_list, verify_list,
                                                     system, command,
                                                     resp_details_dict[system],
                                                     verify_group)
        else:
            pNote("Verification can not be done for the system : "
                  "{0}".format(system), "error")
            sys_status = "ERROR"

    status = "ERROR" if sys_status == "ERROR" else status and sys_status
    return status


def _get_resp_details(match_list, context_list, verify_on_list, verify_list,
                      remote_resp_dict):
    """ Get the response verification details """
    resp_details_dict = {}
    value = None
    for i in range(0, len(verify_list)):
        verify_dict = {i: {}}
        for j in range(0, len(verify_on_list[i])):
            temp_list = verify_on_list[i][j].split(".")
            if len(temp_list) > 1:
                verify_on_list[i][j] = get_session_id(temp_list[0],
                                                      temp_list[1])
            else:
                verify_on_list[i][j] = get_session_id(temp_list[0])

            if verify_on_list[i][j] not in resp_details_dict:
                resp_details_dict[verify_on_list[i][j]] = {}

            if verify_on_list[i][j] in remote_resp_dict:
                data = remote_resp_dict[verify_on_list[i][j]]
                if data:
                    match_object = re.search(match_list[i], data)
                else:
                    match_object = False
                if match_object:
                    match = True
                    start_index = match_object.start()
                    end_index = match_object.end()
                    values = match_object.groups()
                    value = values[0] if len(values) == 1 else None
                else:
                    match = False
                    start_index = None
                    end_index = None
                noimpact, found = get_no_impact_logic(context_list[i])
                found = testcase_Utils.pConvertLogical(found)
                verify_dict[i].update({'start_index': start_index})
                verify_dict[i].update({'end_index': end_index})
                verify_dict[i].update({'match': match})
                verify_dict[i].update({'value': value})
                verify_dict[i].update({'verify': verify_list[i]})
                verify_dict[i].update({'found': found})
                verify_dict[i].update({'noimpact': noimpact})

            resp_details_dict[verify_on_list[i][j]].update(verify_dict)

    resp_details_dict = _update_search_index(match_list, verify_list,
                                             remote_resp_dict,
                                             resp_details_dict)

    resp_details_dict = _get_resp_order(context_list, verify_list,
                                        resp_details_dict)

    return resp_details_dict


def _update_search_index(match_list, verify_list, remote_resp_dict,
                         resp_details_dict):
    """ To find if the search strings are in given order in the response.
    Update the exiting start & end index in case if it is found in order """

    for system in resp_details_dict:
        index = 0
        for i, tag in enumerate(verify_list):
            if resp_details_dict[system].has_key(i) and \
            resp_details_dict[system][i].get('verify') == tag and \
            resp_details_dict[system][i].get('match') is True:
                data = remote_resp_dict[system]
                match_object = re.search(match_list[i], data[index:])
                if match_object:
                    start_index = index + match_object.start()
                    end_index = index + match_object.end()
                    resp_details_dict[system][i]['start_index'] = start_index
                    resp_details_dict[system][i]['end_index'] = end_index
                    index = end_index

    return resp_details_dict


def _get_resp_order(context_list, verify_list, resp_details_dict):
    """ To get the received verification order of the search strings
    in the resp_details_dict and verify if the search_string's presence/order
    matches the expectation """

    for system in resp_details_dict:
        index_list = []
        for i in range(len(verify_list)):
            index_list.append(resp_details_dict[system][i]['start_index'])

        rcv_all_resp_order = []
        for val in sorted(enumerate(index_list), key=lambda x:x[1]):
            if val[1] is not None:
                rcv_all_resp_order.append(verify_list[val[0]])

        # verify if the search_string's presence/order matches the expectation
        for i in range(len(verify_list)):
            verify_order = False
            if resp_details_dict[system][i]['found'] is True:
                if resp_details_dict[system][i]['match'] is True:
                    index_status = _validate_index_value(i, index_list,
                                                         context_list)
                    if index_status is True:
                        verify_order = True
            elif resp_details_dict[system][i]['found'] is False:
                if resp_details_dict[system][i]['match'] is False:
                    verify_order = True
                elif resp_details_dict[system][i]['match'] is True:
                    index_status = _validate_index_value(i, index_list,
                                                         context_list)
                    if index_status is False:
                        verify_order = True

            resp_details_dict[system][i]['verify_order'] = verify_order

        resp_details_dict[system]['rcv_all_resp_order'] = rcv_all_resp_order

    return resp_details_dict

def _validate_index_value(index, index_list, context_list):
    """ Returns True if the value in the given index is in expected order """
    status = True

    new_index = 0
    for i in range(index-1,0,-1):
        _, found = get_no_impact_logic(context_list[i])
        found = testcase_Utils.pConvertLogical(found)
        if found is True:
            new_index = i
            break

    if index > 0:
        if not index_list[index] > index_list[new_index]:
            status = False

    return status


def verify_relation(actual_value, cond_value, operator, cond_type):
    ver_args = {}
    if cond_type:
        pNote("cond_type is {}".format(cond_type))
        actual_value = convert2type(actual_value, cond_type)
        cond_value = convert2type(cond_value, cond_type)
        ver_args.update({"data_type": cond_type})
    if operator:
        ver_args.update({"comparison": operator})
    update_datarepository({"verify_cond": actual_value})
    result = verify_data(cond_value, "verify_cond", **ver_args)
    status = True if result == "TRUE" else False
    return status


def verify_inorder_cmd_response(match_list, verify_list, system, command,
                                verify_dict, verify_group=None):
    """ Verifies search strings in the system response and matches the
    received response order with the expected order """
    status = True
    verify_order_list = []
    for i, tag in enumerate(verify_list):
        if i in verify_dict and verify_dict[i].get('verify') == tag:
            match = verify_dict[i].get('match', None)
            verify_order = verify_dict[i].get('verify_order', None)
            noimpact = verify_dict[i].get('noimpact', None)
            found = verify_dict[i].get('found', None)

            if match is True:
                actual_value = verify_dict[i].get("value")
                if verify_order is True:
                    verify_status = True
                    if found is True:
                        msg = ("Found '{0}' in response to '{1}' on {2} "
                               "and '{0}' is in the correct order").format(
                                                match_list[i], command, system)
                        if verify_group:
                            cond_value = verify_group[1][i]
                            operator = verify_group[0][i]
                            cond_type = verify_group[2][i]
                            if cond_value and actual_value:
                                verify_status = verify_relation(actual_value,
                                                                cond_value,
                                                                operator,
                                                                cond_type)
                                msg += "\n{0} comparison: {1} {2} {3} ".format(
                                    cond_type or "str", actual_value, operator,
                                    cond_value)
                                if verify_status:
                                    msg += "succeeded"
                                else:
                                    msg += "failed"
                            elif cond_value:
                                verify_status = False
                                msg += ("\npattern to compare should have "
                                        "exactly one group to match with the "
                                        "condition value: pattern failed")
                    else:
                        if verify_group[1][i] and not actual_value:
                            verify_status = False
                            msg += ("\npattern to compare should have exactly "
                                    "one group to match with the condition "
                                    "value: pattern failed")
                        else:
                            msg = ("Found '{0}' in response to '{1}' on {2} "
                                   "but '{0}' is not in the specified location"
                                   " as expected").format(match_list[i],
                                                          command, system)
                else:
                    verify_status = False
                    verify_order_list.append(tag)
                    if found is True:
                        msg = ("Found '{0}' in response to '{1}' on {2} but"
                               " '{0}' not in the correct order").format(
                                    match_list[i], command, system)
                    else:
                        if verify_group[1][i] and not actual_value:
                            msg = ("Found '{0}' in response to '{1}' on {2} in"
                                   " the correct order, but \npattern to "
                                   "compare should have exactly one group to "
                                   "match with the condition value: pattern "
                                   "failed").format(match_list[i], command,
                                                    system)
                        else:
                            msg = ("Found '{0}' in response to '{1}' on {2}, "
                                   "but '{0}' is not expected to be found in "
                                   "the location where it is found "
                                   "now").format(match_list[i], command,
                                                 system)
            else:
                msg = ("Did not find '{0}' in response to '{1}' on "
                       "{2}").format(match_list[i], command, system)
                verify_status = True if verify_order is True else False

            if noimpact is True:
                verify_status = True
                pNote("Noimpact was requested on the below verification, hence"
                      " the failure would not impact command status")
            pNote(msg, "debug")
        else:
            verify_status = "ERROR"
            pNote("Verification of '{0}' in response to '{1}' on {2} can "
                  "not be done".format(match_list[i], command, system),
                  "error")

        if verify_status == "ERROR":
            status = "ERROR"
        else:
            status = status and verify_status

    rcv_all_resp_order = verify_dict.get('rcv_all_resp_order', [])
    rcv_all_resp_string = ",".join(rcv_all_resp_order)

    pNote("Search string(s) is/are found in the following order for the "
          "command '{0}': '{1}' on {2}".format(
                    command, rcv_all_resp_string, system), "debug")

    if verify_order_list:
        verify_order_str = ",".join(verify_order_list)
        pNote("Following verification string(s) - {0} not in the expected "
              "order on {1}".format(verify_order_str, system), "debug")
    else:
        pNote("Search string(s) is/are found in the expected order on "
              "{0}".format(system), "debug")

    return status

def get_cse_script_args_string(datafile, system_name):
    """Form the argument string for the CSE script from the arguments
    provided in datafile"""
    args_string = False
    tag_value = get_child_tag_value_list(datafile, system_name, ['Arguments'])

    if tag_value is not False:
        tag_list = tag_value[0]
        value_list = tag_value[1]
        script_args_list = []
        x = len(tag_list)
        for x in range(0, x):
            attr = '-' + tag_list[x]
            value = value_list[x]
            script_args_list.append(attr)
            if value is None: value = ''
            script_args_list.append(value)
        args_string = ' '.join(script_args_list)

        return args_string


def evaluate_tc_argument_value(element):
    """ Splits the value of the attribute value in the argument tag in the TC
    """
    temp_list = element.split("=")
    if len(temp_list) > 1:
        return temp_list[1]
    else:
        return False


def resolve_argument_value_to_get_tag_value(datafile, system_name,
                                            element_value_in_argument):
    """ Here, the value of the attribute value in the argument tag is resolved.
    From now on value represents the value of the attribute value in the
    argument tag in the TC

    Conditions:
    value can be simple and direct. Eg. "http://httpbin.org". In this case,
    it is returned as is.

    value can start with tag, then everything after "=" is taken and a tag of
    that name is searched for under the provided system in the datafile. If tag
    of the same name is found, then the text of that tag is returned.

    If tag is not found, then a False is returned.

    If no system tag with the name as that of the system name is found then,
    then value is returned.

    """
    if element_value_in_argument.startswith("tag"):
        tag_name = evaluate_tc_argument_value(element_value_in_argument)
        if tag_name is not False:
            system_name_list = xml_Utils.get_matching_firstlevel_children_from_root(datafile, "system")
            if system_name_list == [] or system_name_list is None or system_name_list is False:
                return element_value_in_argument
            else:
                for system in system_name_list:
                    if system.attrib["name"] == system_name:
                        node_list = xml_Utils.get_matching_firstlevel_children_from_node(system, tag_name)
                        if node_list == [] or node_list is None or node_list is False:
                            return False
                        else:
                            return node_list[0].text
                return element_value_in_argument
        else:
            return element_value_in_argument
    else:
        return element_value_in_argument


def get_user_specified_tag_values_in_tc(datafile, system_name, **kwargs):
    """Get the details for rest call from the datafile.
    The required details are provided as a key,value pair for the **kwargs
    argument of example, if rest_url, rest_data are required then
    while call this funciton as
    get_user_specified_tag_values_in_tc(datafile, system_name, rest_url=value, rest_data=value)

    If the input value of one of them in None then use the value from the
    datafile else use the provided value
    """
    in_list = []
    for element in kwargs:
        in_list.append(element)
    credentials = get_credentials(datafile, system_name, in_list)

    for element in kwargs:
        if kwargs[element] is not None:
            credentials[element] = resolve_argument_value_to_get_tag_value(datafile, system_name, kwargs[element])
    return credentials


def get_netconf_data(datafile, config_name, **kwargs):
    """Get the details for netconf from the datafile.
    The required details are provided as a key,value pair for the **kwargs argument.
    of example, if rest_url, rest_data are required then while call this funciton as
    get_netconf_data(datafile, system_name, rest_url=value, rest_data=value)

    If the input value of one of them in None then use the value from the datafile
    else use the provided value
    """
    in_list = []
    for element in kwargs:
        in_list.append(element)
    print_info('Get Netconf Data(): {}, {}'.format(datafile, config_name))
    config_data = get_credentials(datafile, config_name, attr_name='name',
                                  tag_name='config')
    for element in kwargs:
        if kwargs[element] is not None:
            config_data[element] = kwargs[element]

    return config_data


def get_filepath_from_system(datafile, system_name, *args):
    """ This function takes variable number of tag names as input and
    returns a list of absolute paths for all the tag values.
    In case of non-string tag values, it will simply return those
    non-string values.
    """

    abspath_lst = []
    credentials = get_credentials(datafile, system_name, args)
    start_directory = os.path.dirname(datafile)

    for tag in args:
        if isinstance(credentials[tag], str) or credentials[tag] is False:
            abspath = file_Utils.getAbsPath(credentials[tag], start_directory)
            if abspath:
                if os.path.isfile(abspath):
                    abspath_lst.append(abspath)
                else:
                    print_warning( "File '{0}' provided for tag '{1}' does "
                                   "not exist".format(abspath, tag))
                    abspath_lst.append(None)
            else:
                abspath_lst.append(None)
        else:
            abspath_lst.append(credentials[tag])

    return abspath_lst


def sub_from_env_var(raw_value, start_pattern="${", end_pattern="}"):
    """Takes a key value pair as input, if the value
    has a pattern matching ${ENV.env_variable_name}.
    Searches for the env_variable_name in the environment and replaces
    it and return the updated dictionary. If environment variable
    is not found then substitutes with None"""
    # Also take string now for free!
    error_msg1 = "Could not find any environment variable '{0}' corresponding"\
                 " to '{1}' provided in input data/testdata file. \n"\
                 "Will default to None"
    error_msg2 = "Unable to substitute environment variable '{0}' "\
                 "corresponding to '{1}' provided in input data/testdata file"
    if type(raw_value) == dict:
        for k in raw_value:
            value = raw_value[k]
            extracted_var = string_Utils.return_quote(str(value), start_pattern, end_pattern)
            extracted_var = [string for string in extracted_var if "ENV." in string]
            if len(extracted_var) > 0:
                for string in extracted_var:
                    try:
                        if isinstance(raw_value[k], str):
                            raw_value[k] = raw_value[k].replace(start_pattern+string+end_pattern,
                                           os.environ[string[4:]])
                        elif isinstance(raw_value[k], (list, dict)):
                            raw_value[k] = literal_eval(str(raw_value[k]).replace(
                                           start_pattern+string+end_pattern,os.environ[string[4:]]))
                        else:
                            print_error("Unsupported format - " + \
                                        error_msg2.format(string, value))
                    except KeyError:
                        print_error(error_msg1.format(string, value))
                        if isinstance(raw_value[k], str):
                            raw_value[k] = None
                        elif isinstance(raw_value[k], (list, dict)):
                            search_str = "'[^']*"+re.escape(start_pattern)+string+re.escape(end_pattern)+"[^']*'"
                            search_obj = re.search(search_str, str(raw_value[k]))
                            if search_obj:
                                raw_value[k] = literal_eval(str(raw_value[k]).replace(
                                               search_obj.group(), 'None'))
                    except SyntaxError:
                        print_error("Syntax Error - " + \
                                    error_msg2.format(string,value))
    elif type(raw_value) == str:
        extracted_var = string_Utils.return_quote(str(raw_value), start_pattern, end_pattern)
        extracted_var = [string for string in extracted_var if "ENV." in string]
        if len(extracted_var) > 0:
            for string in extracted_var:
                try:
                    raw_value = raw_value.replace(start_pattern+string+end_pattern, os.environ[string[4:]])
                except KeyError:
                    print_error(error_msg1.format(string, raw_value))
                    raw_value = None

    return raw_value


def process_subsystem_list(datafile, system_name, subsystem=None):
    """Takes a system_name and a list of subsystem names as input and process
    them by removing blank spaces for each element in the subsystem name list.
    Then remove all duplicate entries in the list. If any input subsystem_name
    in the list is 'all', a list of all subsystem exist under the provided
    system_name in the datafile will be return. If the system_name is not found
    in the datafile, subsystem_list will be set None."""
    system = xml_Utils.getElementWithTagAttribValueMatch(datafile, 'system',
                                                         'name', system_name)
    if system is not None and system is not False:
        if subsystem is not None and subsystem is not False:
            subsystem = subsystem.split(',')
            # Strip blank spaces in each element, duplicate entry can be remove:
            strip_subsystem_list = []
            for name in subsystem:
                name = name.strip()
                strip_subsystem_list.append(name)
            # Remove duplicate entry
            subsystem_list = []

            [subsystem_list.append(item) for item in strip_subsystem_list if
             item not in subsystem_list]
            # Look for any subsystem = 'all'
            all_subsys_flag = False
            for name in subsystem_list:
                if re.search(name.lower(), 'all'):
                    all_subsys_flag = True
                    break
            if all_subsys_flag is True:
                # Find all subsystem_names for the system in datafile:
                subsystem_list = xml_Utils.getNodeListbyAttribute(system,
                                                                  'subsystem',
                                                                  'name')
            else:  # when subsystem_list is empty, set it to None
                if len(subsystem_list) == 0: subsystem_list = None
        else:
            subsystem_list = None
    else:
        subsystem_list = None
    return subsystem_list


def resolve_system_subsystem_list(datafile, system_name):
    """
    Using the provided system_name which may include both system_name and
    subsystem_name. Ex: NE1[dip,cli]
    Call 'split_system_subsystem' to separate the system_name and subsystem(s)
    Then call 'process_subsystem_list' to compare the list of subsystem(s)
    from the input against actuals subsystem in the referenced datafile.
    Return a system_name, subsystem_list
    """
    system_name, subsystem = split_system_subsystem(system_name)
    subsystem_list = process_subsystem_list(datafile, system_name, subsystem)

    return system_name, subsystem_list


def split_system_subsystem(system_name):
    """Separate system_name and subsystem_name str from the input
       Ex: system_name=NE1[cli,dip,if1] will be separate into
           system_name=NE1
           subsystem_name str = 'cli, dip, if1'"""
    new_system_name = system_name.split('[')
    system_name = new_system_name[0]
    subsystem_name = None if len(new_system_name) == 1 else \
        new_system_name[1].split(']')[0]

    return system_name, subsystem_name


def get_td_vc(datafile, system_name, td_tag, vc_tag):
    """
    Get the testdata and varconfig file paths
    from the datafile using the
    testdata nd varconfig tag given as input
    """
    testdata_tag = td_tag if td_tag else "testdata"
    status = _check_tag_or_attr_exists(datafile, system_name,
                                       "var_config_file", "system")
    var_tag = "var_config_file" if status is True else "variable_config"
    varconfig_tag = vc_tag if vc_tag else var_tag

    abspaths = get_filepath_from_system(datafile, system_name,
                                        testdata_tag, varconfig_tag)

    testdata = abspaths[0]
    varconfigfile = abspaths[1]

    return testdata, varconfigfile

def get_nc_config_string(config_datafile, config_name, var_configfile=None):
    """
    Get the config of netconf as a list
    """

    configuration = ""
    configuration_list = []
    status = True
    try:
        data = xml_Utils.get_element_by_attribute(config_datafile, "config_data",
                                                  "name", config_name)
        if data:
            config_node = xml_Utils.get_child_with_matching_tag(data, "config")
            if config_node:
                configuration = xml_Utils.convert_dom_to_string(config_node)
                if var_configfile:
                    configuration = sub_from_varconfigfile(configuration,var_configfile)
                configuration_list.append(configuration)
            else:
                filepath_list = xml_Utils.get_child_with_matching_tags(data, "filepath")
                for filepath in filepath_list:
                    if filepath:
                        rel_path = filepath.firstChild.data
                        abs_filepath = file_Utils.getAbsPath(rel_path, os.path.dirname(config_datafile))
                        root = xml_Utils.get_document_root(abs_filepath)
                        config_node = xml_Utils.get_child_with_matching_tag(root, "config")
                        if config_node:
                            configuration = xml_Utils.convert_dom_to_string(config_node)
                            if var_configfile:
                                configuration = sub_from_varconfigfile(configuration,var_configfile)
                            configuration_list.append(configuration)
                        else:
                            testcase_Utils.pNote("no <config> found in file {0}".format(abs_filepath),"error")

                if not filepath_list:
                    testcase_Utils.pNote("neither <config> nor a file containing <config> "\
					                     "provided for the config_data = {0} in config file "\
										 "= {1}".format(config_name, config_datafile),"error")
                    status = "error"
        else:
            testcase_Utils.pNote("config_data={0} is not found in config "\
			                     "file ={1}".format(config_name, config_datafile),"error")
            status = "error"

    except IOError as err:
        testcase_Utils.pNote("File does not exist: {0}".format(err),"error")
        status = "error"

    except Exception as exception:
        print_exception(exception)
        status = "error"
    return status, configuration_list

def _check_tag_or_attr_exists(datafile, system_name, cnode, system='system'):
    """Check if the given tag/attribute(cnode) exists for the system_name in
     the datafile and returns True(bool) if exists else return False(bool)"""
    status = False
    element = _get_system_or_subsystem(datafile, system_name, tag=system)
    if element is not None and element is not False:
        if (element.get(cnode, None) is not None) or\
           (element.find(cnode) is not None):
            status = True
    return status


def get_default_ecf_and_et(arguments_dict, current_datafile, current_browser,
                           name_tuple=("element_config_file", "element_tag"),
                           def_name_tuple=("DEF_ecf", "DEF_et")):
    """
    Updates selenium argument sict with Default ECF and default element_tag
    """
    for j in range(0, len(name_tuple)):
        if name_tuple[j] in arguments_dict:
            if arguments_dict[name_tuple[j]] is None:
                if current_browser.find(name_tuple[j]) is not None:
                    arguments_dict[def_name_tuple[j]] = current_browser.find(name_tuple[j]).text
                else:
                    arguments_dict[def_name_tuple[j]] = current_browser.get(name_tuple[j], None)
            else:
                if arguments_dict[name_tuple[j]].startswith("tag") and "=" in arguments_dict[name_tuple[j]]:
                    temp_list = arguments_dict[name_tuple[j]].split("=")
                    temp_var = temp_list[1]
                    for i in range(2, len(temp_list)):
                        temp_var = temp_var + "=" + temp_list[i]
                    temp_var = temp_var.strip()
                    if "/" in temp_var:
                        root = xml_Utils.getRoot(current_datafile)
                        arguments_dict[def_name_tuple[j]] = root.find(temp_var).text
                    else:
                        if current_browser.find(temp_var) is not None:
                            arguments_dict[def_name_tuple[j]] = current_browser.find(temp_var).text
                        else:
                            arguments_dict[def_name_tuple[j]] = current_browser.get(temp_var, None)
                elif "=" in arguments_dict[name_tuple[j]]:
                    temp_list = arguments_dict[name_tuple[j]].split("=")
                    if temp_list[0] in arguments_dict:
                        temp_var = temp_list[1]
                        for k in range(2, len(temp_list)):
                            temp_var = temp_var + "=" + temp_list[k]
                        arguments_dict[def_name_tuple[j]] = temp_var
                    else:
                        arguments_dict[def_name_tuple[j]] = arguments_dict[name_tuple[j]]
                else:
                    arguments_dict[def_name_tuple[j]] = arguments_dict[name_tuple[j]]
        else:
            arguments_dict[def_name_tuple[j]] = None

    return arguments_dict

def get_all_system_or_subsystem(datafile, system_name=None):
    """
        return all the system elements or all the children of a system element with specific name
    """
    if system_name is None:
        return xml_Utils.getElementListWithSpecificXpath(datafile, "./system")
    else:
        return xml_Utils.getElementListWithSpecificXpath(datafile, "./system[@name='" + system_name + "']/*")

def group_systems_with_same_tag_value(root, tag, value):
    """
        Put systems with the same tag value pair in one list
        and all other system in another list
    """
    all_system_list = xml_Utils.getChildElementsListWithSpecificXpath(root, "./system")
    system_list = xml_Utils.getChildElementsListWithSpecificXpath(root, "./system/[" + tag + "='" + value + "']")
    other_system_list = [ele for ele in all_system_list if ele not in system_list]
    return system_list, other_system_list

def group_systems_with_unique_tag_value(root, tag):
    """
        Separate system into lists where each list only has system with unique tag value
    """
    all_system_list = xml_Utils.getChildElementsListWithSpecificXpath(root, "./system")
    return _helper_unique_group(all_system_list, tag)

def _helper_unique_group(all_system_list, tag):
    """
        helper function for group_systems_with_unique_tag_value
        Separate system into lists where each list only has system with unique tag value
    """
    system_list = []
    system_text_list = []
    other_system_list = []
    for ele in all_system_list:
        if ele.find(tag).text not in system_text_list:
            system_list.append(ele)
            system_text_list.append(ele.find(tag).text)
        else:
            other_system_list.append(ele)

    if other_system_list != []:
        other_system_list = _helper_unique_group(other_system_list, tag)

    other_system_list.insert(0, system_list)
    return other_system_list

def get_system_list(datafile, node_req=False):
    """Get the list of systems from the datafile
    if node_req = True returns 1. list of system names, 2. list of system nodes
    if node_rq = False returns on the list of system names
    """
    root = xml_Utils.getRoot(datafile)
    systems = root.findall('system')
    system_list = []
    system_node_list = []
    for system in systems:
        #check if the system has subsystem or not.
        subsystems = system.findall('subsystem')
        if subsystems != []:
            first_subsystem = True
            for subsystem in subsystems:
                #if the system has subsystem, find the default subsystem for the system and use it to execute the keyword.
                default = subsystem.get('default')
                if default == "yes":
                    subsystem_name = subsystem.get('name')
                    system_name = system.get('name') + '[' + subsystem_name + ']'
                    break
                #if none of the subsystems have default="yes" then the default subsystem will be the first subsystem under the system.
                elif first_subsystem == True:
                    subsystem_name = subsystem.get('name')
                    system_name = system.get('name') + '[' + subsystem_name + ']'
                    first_subsystem = False
        #if there is no subsystem use the system.
        else:
            system_name = system.get('name')
            system_node = system
        system_list.append(system_name)
        system_node_list.append(system_node)
    if node_req:
        return system_list, system_node_list
    else:
        return system_list



def get_iteration_syslist(system_node_list, system_name_list):
    """
    Takes a list of system nodes and system names and
    returns.
    1. List of system names with iter=yes
    2. List of system nodes with iter=yes
    """

    iteration_sysnamelist = []
    iteration_sysnodelist = []
    for i in range (0, len(system_node_list)):
        system = system_node_list[i]
        iter_flag = system.get("iter", None)
        if iter_flag is None:
            iter_flag = xml_Utils.get_text_from_direct_child(system, "iter")
        iter_flag = sub_from_env_var(iter_flag)

        if str(iter_flag).lower() == "no":
            pass
        else:
            system_name = system_name_list[i]
            if not system_name:
                pNote("No name provided for system/susbsystem in datafile", "error")
            else:
                iteration_sysnamelist.append(system_name)
                iteration_sysnodelist.append(system)

    return iteration_sysnamelist, iteration_sysnodelist

def generate_datafile(lists_of_systems, output_dir, filename):
    """
        take in a list of lists which contains systems
        generate one input data file per list
    """
    result = []
    for index, list_of_sys in enumerate(lists_of_systems):
        output_filename = filename + "_" + str(index) + ".xml"
        output_file = os.path.join(output_dir, output_filename)
        fd = file_Utils.open_file(output_file, "w+")
        if fd is not None:
            root = xml_Utils.create_element("root")
            for system in list_of_sys:
                root.append(system)
            fd.write(xml_Utils.convert_element_to_string(root))
            result.append(output_file)
    return result
