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

from __future__ import division
import os
import re
import ast
import copy
import operator as op
from collections import OrderedDict

from Framework.Utils import xml_Utils, string_Utils, testcase_Utils, config_Utils, file_Utils
from Framework.Utils.testcase_Utils import pNote
from Framework.Utils.print_Utils import (print_info, print_warning, print_error,
                                         print_debug, print_exception)
from Framework.ClassUtils.testdata_class import TestData, TestDataIterations
from Framework.Utils.xml_Utils import get_attributevalue_from_directchildnode as av_fromdc
from Framework.Utils.string_Utils import sub_from_varconfigfile
from Framework.ClassUtils import database_utils_class
from WarriorCore.Classes.argument_datatype_class import ArgumentDatatype
from WarriorCore.Classes.warmock_class import mocked
from WarriorCore.Classes.testcase_utils_class import TestcaseUtils

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
                          ("resp_pat_key_list", "resp_pat_key"),
                          ("resp_key_list", "resp_keys"),
                          ("inorder_resp_ref_list", "inorder_resp_ref"),
                          ("log_list", "monitor"),
                          ("verify_on_list", "verify_on"),
                          ("inorder_search_list", "inorder"),
                          ("verify_map_list", ""),
                          ("operator_list", "operator"),
                          ("cond_value_list", "cond_value"),
                          ("cond_type_list", "cond_type"),
                          ("repeat_list", "repeat"),
                          ("sleeptime_before_match_list", "sleep_before_match"),
                          ("return_on_fail_list", "return_on_fail"),
                          ("logmsg_list", "log")])

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
    startdir = os.path.dirname(datafile)
    element = _get_system_or_subsystem(datafile, system_name, tag=system)
    if element is not None:
        value = element.get(cnode, None)
        if value is None:
            value = get_cred_value_from_elem(element, cnode, startdir)
        value = sub_from_env_var(value)
        value = sub_from_data_repo(value)

    return value


def get_cred_value_from_elem(element, tag, startdir=''):
    """given an credential element find the credential
    value desired
    """
    chelem = element.find(tag)
    if chelem is None:
        return xml_Utils.get_text_from_direct_child(element, tag)
    if 'wtype' in chelem.attrib:
        value = get_actual_cred_value(chelem.tag, chelem.text,
                                      chelem.attrib['wtype'], startdir)
    else:
        value = chelem.text
    return value


def get_actual_cred_value(tag, value, etype, startdir=''):
    """get the credential value after converting to the
    desired type and if file type get absolute path relative
    to the startdir
    """
    try:
        adt = ArgumentDatatype(tag, value)
        adt.datatype = adt.get_type_func(etype)
        if adt.datatype is file:
            val = file_Utils.getAbsPath(value, startdir)
        else:
            val = adt.convert_string_to_datatype()
    except KeyError:
        val = value
    return val


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
    startdir = os.path.dirname(datafile)
    # Find the parent system
    element = _get_system_or_subsystem(datafile, system_name, tag=tag_name,
                                       attr=attr_name)
    value = False
    if element is not None and element is not False:
        output_dict = {}
        if len(myInfo) == 0:
            for child in element:
                val = child.text
                if 'wtype' in child.attrib:
                    val = get_actual_cred_value(child.tag, child.text,
                                                child.attrib['wtype'], startdir)
                output_dict[child.tag] = val

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
                            if 'wtype' in child.attrib:
                                cred_value[child.tag] = get_actual_cred_value(
                                    child.tag, child.text, child.attrib['wtype'], startdir)
                    else:
                        cred_value = get_cred_value_from_elem(element, x, startdir)
                output_dict[x] = cred_value
        value = output_dict
    updated_dict = sub_from_env_var(value)
    updated_dict = sub_from_data_repo(updated_dict)
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
    if element is not None and element is not False:
        tag_list = []
        value_list = []
        for child in child_list:
            cnode = element.find(child)
            if cnode is not None and cnode is not False:
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
    """ Gets the value for the object with the provided name from data repository.
    object_key contains .(dot) will be treated as nested key """
    try:
        data_repository = config_Utils.data_repository
        keys = object_key.split('.')
        obj = data_repository[keys[0]]
        for key in keys[1:]:
            obj = obj[key]
    except KeyError:
        obj = False
        if verbose:
            print_warning('{0} is not found in data repository'.format(object_key))
    return obj


@mocked
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
        db_td_obj = database_utils_class.create_database_connection(
            'dataservers', testdatafile.get('td_system'))
        root = db_td_obj.get_tdblock_as_xmlobj(testdatafile)

        # if testdata block in the datafile has separate db system
        # for 'testdata-global' values
        if testdatafile.get('global_system') is not None:
            print_info("Resolving testdata-global block from DB system - "
                       "'{}'".format(testdatafile.get('global_system')))
            db_tdglobal_obj = database_utils_class.create_database_connection(
                'dataservers', testdatafile.get('global_system'))
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
        db_var_obj = database_utils_class.create_database_connection(
            'dataservers', varconfigfile.get('var_system'))
        varconfigfile = db_var_obj.get_varblock_as_xmlobj(varconfigfile)
        db_var_obj.close_connection()

    for testdata in root.findall("testdata"):
        # use only test data blocks that are marked to execute
        exec_flag = get_exec_flag(testdata, title, row)
        exec_text = testdata.get("execute").strip()
        execute_req = string_Utils.conv_str_to_bool(exec_text)
        if execute_req and exec_flag:
            testdata_key = "{0}{1}".format(testdata.get('title', ""), _get_row(testdata))
            details_dict = _get_cmd_details(testdata, global_obj, system_name,
                                            varconfigfile, var_sub=var_sub)
            start_pat = _get_pattern_list(testdata, global_obj)
            end_pat = _get_pattern_list(testdata, global_obj, pattern="end")
            details_dict = sub_from_env_var(details_dict, start_pat, end_pat)

            print_info("var_sub:{0}".format(var_sub))
            td_obj = TestData()
            details_dict = td_obj.varsub_varconfig_substitutions(
                details_dict, vc_file=None, var_sub=var_sub, start_pat=start_pat, end_pat=end_pat)

            details_dict = td_obj.wdf_substitutions(details_dict, datafile,
                                                    kw_system_name=system_name)
            details_dict = sub_from_env_var(details_dict)
            details_dict = sub_from_data_repo(details_dict)

            td_iter_obj = TestDataIterations()
            details_dict, cmd_loc_list = td_iter_obj.resolve_iteration_patterns(details_dict)

            # List substitution happens after iteration because
            # list sub cannot recognize the + sign in iteration
            cmd_list_substituted, verify_text_substituted = td_obj.list_substitution_precheck(
                varconfigfile, details_dict, start_pat, end_pat)
            td_obj.list_substitution(details_dict, varconfigfile, cmd_list_substituted,
                                     verify_text_substituted, start_pat, end_pat)

            # Update 'cmd_loc_list' based on list substitution, this is
            # required for per_td_block iteration
            ref_cmd_loc_list = copy.deepcopy(cmd_loc_list)
            for i in range(len(cmd_loc_list)-1):
                for j in range(ref_cmd_loc_list[i], ref_cmd_loc_list[i+1]):
                    if cmd_list_substituted[j]:
                        pos = i+1
                        for _ in range(len(cmd_loc_list[i+1:])):
                            cmd_loc_list[pos] = cmd_loc_list[pos] + cmd_list_substituted[j] - 1
                            pos += 1

            iter_type = testdata.get('iter_type', None)
            # Type-2 iteration - per_td_block
            if iter_type == "per_td_block":
                details_dict, cmd_loc_list = td_iter_obj.repeat_per_td_block(details_dict,
                                                                             cmd_loc_list)
                details_dict = td_iter_obj.arrange_per_td_block(details_dict, cmd_loc_list)

            details_dict = td_obj.varsub_varconfig_substitutions(
                details_dict, vc_file=varconfigfile, var_sub=None, start_pat=start_pat,
                end_pat=end_pat)
            testdata_dict[testdata_key] = details_dict
        else:
            not_found += 1

    if not_found == len(root.findall("testdata")):
        print_warning('There are no rows with execute=yes and title={0}, row={1}'
                      ' in testdata {2} '.format(title, row, testdatafile))
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


def _get_key_elements(testdata, global_obj, keys):
    """given keys in a comma separated key names, get the elements
    corresponding to each key in the testdata or global testdata block
    :RETURN:
    list of xml elements corresponding to the keys in testdata or global
    testdata block. if the element is not found in testdata or global_obj,
    the same key name in string would be appended
    """
    elem_list = []
    if keys is None:
        return None
    keylist = [key.strip() for key in keys.split(',')]
    for key in keylist:
        # get the key_elem from test case corresponding to key from
        # the testdata or global section. Return None if it is not
        # found in both testdata and global section
        if testdata.find(key) is not None:
            elem_list.append(testdata.find(key))
            continue
        key_found = False
        if global_obj is not None:
            global_key_elem = global_obj.find("keys")
            global_keys = xml_Utils.get_child_node_list(global_key_elem)
            # return the first matched entry in global section with tag=key
            for glob_key in global_keys:
                if glob_key.tag == key:
                    elem_list.append(glob_key)
                    key_found = True
                    break
        if not key_found:
            print_error("There is no pattern element for key '{}',"
                        " please check".format(key))
            elem_list.append(key)
    return elem_list


@mocked
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
            sys_list = details_dict["sys_list"]
            vfylist = details_dict["verify_list"]
            resultant_list = _get_verification_details(testdata, global_obj,
                                                       vfylist, attrib,
                                                       system_name, sys_list)
        elif param == "verify_map_list":
            vfylist = details_dict["verify_list"]
            vfylist, maplist = _get_mapping_details(global_obj, vfylist)
            resultant_list = maplist
        elif param == "resp_key_list":
            keyslist = _get_cmdparams_list(testdata, global_obj, attrib)
            resultant_list = [_get_key_elements(testdata, global_obj, keys) for keys in keyslist]
        else:
            resultant_list = _get_cmdparams_list(testdata, global_obj, attrib)
            if param == "sys_list":
                # substitute sys tag value from var_config file
                resultant_list = string_Utils.sub_from_varconfig(varconfigfile,
                                                                 resultant_list)
                details_dict["vc_file_list"] = []
                vc_file_list = _get_vc_details(resultant_list, system_name,
                                               varconfigfile)
                details_dict["vc_file_list"].extend(vc_file_list)
        details_dict[param].extend(resultant_list)
    return details_dict


def _get_global_var(global_obj, key):
    """locate element in a etree object (in this case, child of global tag in testdata file)
    """
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
            value = default_value if value is None or value == "" else value
        else:
            if cmd_attrib in testdata.attrib and cmd_attrib == "monitor":
                value = testdata.attrib[cmd_attrib]
        resultant_list.append(value)
    return resultant_list


def _get_verification_details(testdata, global_obj, verify_list, cmd_attrib,
                              system_name=None, sys_list=None):
    """From the testdata file takes a testdata node and
    a list of nodes with verification present as input

    :Return:
        1. a list of verifcation_text or verification_context
    """
    g_verify = global_obj.find("verifications") if global_obj is not None \
        else None
    resultant_list = []
    for index, verify in enumerate(verify_list):
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
                if value is None or value == "":
                    value = 'yes' if cmd_attrib == "found" else value
                    if cmd_attrib == "verify_on" and sys_list is not None and \
                       sys_list[index] is not None:
                        value = sys_list[index]
                    else:
                        value = system_name
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
        if system and system != system_name:
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
        if process_row == row and testdata.get('title', None) is None:
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
                           endprompt="", verify_group=None, log="true"):
    """ New method to verify response of a command
    sent on one system with the response recieved from
    another system """

    msg = ("Verification required for command: '{0}' ".format(command))
    if log != "false":
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
                tmp_status = verify_cmd_response([match_list[i]], [context_list[i]], command,
                                                 data, verify_on_list[i][j], varconfigfile,
                                                 endprompt, verify_group, log)
                status = status and tmp_status
            except KeyError:
                print_error("Response could not be collected for {0}, hence, "
                            "it cannot be verified".format(verify_on_list[i][j]))
                status = "ERROR"
                # print "\n---------- END OF VERIFICATION ----------\n"
    return status


def get_no_impact_logic(context_str):
    """Get the silent tag from context
    return silence value and context value"""
    value = {
        'YES:NOIMPACT': (True, 'YES'),
        'YES': (False, 'YES'),
        'Y:NOIMPACT': (True, 'YES'),
        'Y': (False, 'YES'),
        'NO:NOIMPACT': (True, 'No'),
        'NO': (False, 'No'),
        'N:NOIMPACT': (True, 'No'),
        'N': (False, 'No'),
    }.get(context_str.upper(), False)

    return value


def convert2type(value, data_type='str'):
    """Convert value to data_type and return value in that data_type
    Currently supported are str/int/float only
    """
    type_funcs = {'str': str, 'int': int, 'float': float}
    convert = type_funcs[data_type]
    cvalue = value
    try:
        cvalue = convert(value)
    except ValueError:
        print_error("'{}' should be of type {}, please correct".format(value, data_type))
    except Exception as exception:
        print_exception(exception)
    return cvalue

@mocked
def verify_cmd_response(match_list, context_list, command, response,
                        verify_on_system, varconfigfile=None, endprompt="",
                        verify_group=None, log="true"):
    """Verifies the response with the provided
    match and context list
    """
    err_msg = ("Incorrect or no value provided for verification search/found, "
               "check the verification data provided for the command. Command "
               "result will be marked as ERROR")

    if varconfigfile and varconfigfile is not None:
        match_list = string_Utils.sub_from_varconfig(varconfigfile, match_list)
    verify_status = True

    for i in range(0, len(match_list)):
        pattern_match = False
        nogroup = False
        if context_list[i] and match_list[i]:
            noiimpact, found = get_no_impact_logic(context_list[i])
            found = string_Utils.conv_str_to_bool(found)
            if response:
                match_object = re.search(match_list[i], response)
            else:
                match_object = False
            if match_object:
                match = match_object.group()
                msg = "Found '{0}' in response to '{1}' on {2} & "\
                    "'Found' tag is set to '{3}', so the {4}"
                pattern_match = True
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
                msg = "Did not find '{0}' in response to '{1}' on {2} & "\
                    "'Found' tag is set to '{3}' so the {4}"
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
            if log != "false":
                if pattern_match is True and found is True:
                    print_info(msg .format(match_list[i], command, verify_on_system,
                                           "Yes", "verification Passed"))
                elif pattern_match is True and found is False:
                    print_debug(msg .format(match_list[i], command, verify_on_system,
                                            "No", "verification Failed"))
                elif pattern_match is False and found is True:
                    print_debug(msg .format(match_list[i], command, verify_on_system,
                                            "Yes", "verification Failed"))
                elif pattern_match is False and found is False:
                    print_info(msg .format(match_list[i], command, verify_on_system,
                                           "No", "verification Passed"))
        elif context_list[i] and match_list[i] == "":
            noiimpact, found = get_no_impact_logic(context_list[i])
            found = string_Utils.conv_str_to_bool(found)
            escapes = ''.join([chr(char) for char in range(1, 32)])
            response = re.sub(endprompt, "", response).strip()
            response = response.translate(None, escapes)
            if found:
                # found = context
                result = True if response == "" else False
            else:
                result = False if response == "" else True

            verification_text = "verification "
            verification_text += "success" if result else "failed"
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
    """
        Verify the value of the key in data repository matches
        with expected value
        the comparison will compare expected to key with comparison value
        eg. expected=5, value of key=3, comparison='ge' mean 5 >= 3
    """
    def validate():
        """Verify the value of the key in data repository matches
        with expected value
        """
        result = "TRUE"
        err_msg = ""
        exp = expected
        if data_type not in type_funcs:
            err_msg += ("type {} not supported, only one of {} supported\n".
                        format(data_type, '/'.join(type_funcs.keys())))
            result = "ERROR"
        else:
            convert = type_funcs[data_type]
            try:
                exp = convert(expected)
            except ValueError:
                err_msg += "expected {} should be of type {}\n".format(expected, data_type)
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
        'le': lambda x, y: x <= y,
        're.match': lambda x, y: re.match(y, x),
        're.search': lambda x, y: re.search(y, x)
    }
    if comparison == 're.match' or comparison == 're.search':
        data_type = 'str'
    result, err_msg, exp = validate()
    value = get_object_from_datarepository(key)
    key_err_msg = "In the given key '{0}', '{1}' is not present in data repository"
    if value:
        try:
            if result == "ERROR" or result == "EXCEPTION":
                print_error(err_msg)
            elif not comp_funcs[comparison](value, exp):
                result = "FALSE"
                if type(value) != type(exp):
                    print_warning("The expected value '{0}' is of {1} and data_repository value "
                                  "'{2}' is of {3}".format(exp, type(exp), value, type(value)))
                else:
                    print_warning("The key, value pair '{0}:{1}' present in the "
                                  "data_repository doesn't satisfy the expected value: '{2}' & "
                                  "condition: '{3}'".format(key, value, expected, comparison))
            else:
                print_info("The key, value pair '{0}:{1}' present in the  "
                           "data_repository satisfies the expected type & condition "
                           "'{2}:{3}'".format(key, value, data_type, comparison))
        except Exception as e:
            err_msg += "Got unknown exception {}\n".format(e)
            result = "EXCEPTION"
    else:
        # when the value is not in data_repo(value is False)
        result = "ERROR"
        print_error(key_err_msg.format(key, key.split('.')[0]))

    return result, value


def verify_arith_exp(expression, expected, comparison='eq', repo_key='exp_op'):
    """ Verify the output of the arithmetic expression matches the expected(float comparison)
        Note : Binary floating-point arithmetic holds many surprises.
        Please refer to link, https://docs.python.org/2/tutorial/floatingpoint.html
        This Keyword inherits errors in Python float operations.
        :Arguments:
            1. expression: Arithmetic expression to be compared with expected.
                This can have env & data_repo values embedded in it.
                    Ex. expression: "10+${ENV.x}-${REPO.y}*10"
                Expression will be evaluated based on python operator precedence
                Supported operators: +, -, *, /, %, **, ^
            2. expected: Value to be compared with the expression output
                This can be a env or data_repo or any numeral value.
            3. comparison: Type of comparison(eq/ne/gt/ge/lt/le)
                eq - check if both are same(equal)
                ne - check if both are not same(not equal)
                gt - check if expression output is greater than expected
                ge - check if expression output is greater than or equal to expected
                lt - check if expression output is lesser than expected
                le - check if expression output is lesser than or equal to expected
            4. repo_key: Name of the key to be used to save the expression_output
               in the warrior data repository
                Ex. If repo_key is 'exp_op' & expression_output is 10.0
                    It will be stored in data_repo in the below format
                    data_repo = {
                                    ...
                                    verify_arith_exp: {'exp_op': 10.0},
                                    ...
                                }
                    This value can be retrieved from data_repo using
                    key : 'verify_arith_exp.exp_op'.
        :Returns:
            1. status(boolean)
    """
    status = True
    expression_ouput = None

    # Customize power(exponentiation) fun to not to support the values greater
    # than 1000 to avoid high CPU/Memory usage
    def power(a, b):
        """ Customized operator-power(op.pow) function """
        if any(abs(n) > 1000 for n in [a, b]):
            raise Exception("ValueError: Power operation is not supported on "
                            "values higher than 1000: '{0}, {1}'".format(a, b))
        return op.pow(a, b)

    # supported operators
    operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
                 ast.Div: op.truediv, ast.Mod: op.mod, ast.Pow: power,
                 ast.BitXor: op.xor}

    def eval_exp(parsed_exp):
        """ Evaluate arithmetic operations in an expression recursively """
        # number
        if isinstance(parsed_exp, ast.Num):
            return parsed_exp.n
        # binary operator
        elif isinstance(parsed_exp, ast.BinOp):
            return operators[type(parsed_exp.op)](eval_exp(parsed_exp.left),
                                                  eval_exp(parsed_exp.right))
        # Unary operator
        elif isinstance(parsed_exp, ast.UnaryOp):
            return operators[type(parsed_exp.op)](eval_exp(parsed_exp.operand))
        else:
            raise Exception("TypeError: Illegal expression")

    # Substitute env values in the expression & expected
    expression = sub_from_env_var(expression)
    expected = sub_from_env_var(expected)
    # Substitute data_repo values in the expression & expected
    expression = sub_from_data_repo(expression)
    expected = sub_from_data_repo(expected)

    try:
        expression_ouput = eval_exp(ast.parse(expression, mode='eval').body)
        expected = float(expected)
    except SyntaxError:
        print_error("Unable to evaluate the expression '{}' provided.\n"
                    "Possible reasons: \n1. Invalid arithmetic expression\n"
                    "2. Given env/data_repo values are not available".format(expression))

        status = "ERROR"
    except ValueError:
        print_error("Unable to convert expected value '{}' to float".format((expected)))
        status = "ERROR"
    except Exception as exception:
        print_exception(exception)
        status = "ERROR"

    comp_funcs = {
        'eq': lambda x, y: x == y,
        'ne': lambda x, y: x != y,
        'gt': lambda x, y: x > y,
        'ge': lambda x, y: x >= y,
        'lt': lambda x, y: x < y,
        'le': lambda x, y: x <= y
    }

    if comparison not in comp_funcs:
        print_error("Valid comparisons are {}".format('/'.join(comp_funcs.keys())))
        status = "ERROR"

    if status is True:
        comp_result = comp_funcs[comparison](expression_ouput, expected)
        if comp_result is True:
            print_info("Expression output satisfies the given condition: "
                       "'{0} {1} {2}'".format(expression_ouput, comparison, expected))
        else:
            status = False
            print_info("Expression output does not satisfy the given condition: "
                       "'{0} {1} {2}'".format(expression_ouput, comparison, expected))

    output_dict = get_object_from_datarepository('verify_arith_exp') \
        if get_object_from_datarepository('verify_arith_exp') else {}

    output_dict[repo_key] = expression_ouput
    print_info("Expression output: {0} is stored in a Key: {1} of Warrior "
               "data_repository".format(expression_ouput, 'verify_arith_exp.'+repo_key))
    update_datarepository({'verify_arith_exp': output_dict})

    return status


def verify_resp_inorder(match_list, context_list, command, response,
                        varconfigfile=None, verify_on_list=None,
                        verify_list=None, remote_resp_dict=None,
                        verify_group=None):
    """ Method for in-order search.
    Verifies the 'search strings' in the system response
    and also verifies whether they are in order or not
    """

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
        for val in sorted(enumerate(index_list), key=lambda x: x[1]):
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
    for i in range(index-1, 0, -1):
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
    """verify the actual_value with the expected value
    """
    ver_args = {}
    if cond_type:
        pNote("cond_type is {}".format(cond_type))
        actual_value = convert2type(actual_value, cond_type)
        cond_value = convert2type(cond_value, cond_type)
        ver_args.update({"data_type": cond_type})
    if operator:
        ver_args.update({"comparison": operator})
    update_datarepository({"verify_cond": actual_value})
    result, _ = verify_data(cond_value, "verify_cond", **ver_args)
    status = True if result == "TRUE" else False
    return status


@mocked
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
                        msg = ("Found '{0}' in response to '{1}' on {2} and '{0}' is in the"
                               " correct order").format(match_list[i], command, system)
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
                        msg = ("Found '{0}' in response to '{1}' on {2} but '{0}' not in the"
                               " correct order").format(match_list[i], command, system)
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

    pNote("Search string(s) is/are found in the following order for the command '{0}':"
          " '{1}' on {2}".format(command, rcv_all_resp_string, system), "debug")

    if verify_order_list:
        verify_order_str = ",".join(verify_order_list)
        pNote("Following verification string(s) - {0} not in the expected "
              "order on {1}".format(verify_order_str, system), "debug")
    else:
        pNote("Search string(s) is/are found in the expected order on "
              "{0}".format(system), "debug")

    return status


def evaluate_tc_argument_value(element):
    """ Splits the value of the attribute value in the argument tag in the TC
    """
    temp_list = element.split("=")
    if len(temp_list) > 1:
        return temp_list[1]
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
    if element_value_in_argument.startswith("tag="):
        tag_name = evaluate_tc_argument_value(element_value_in_argument)
        if tag_name:
            system_name_list = xml_Utils.get_matching_firstlevel_children_from_root(
                datafile, "system")
            if system_name_list == [] or system_name_list is None or system_name_list is False:
                return element_value_in_argument
            for system in system_name_list:
                if system.attrib["name"] == system_name:
                    node_list = xml_Utils.get_matching_firstlevel_children_from_node(
                        system, tag_name)
                    if node_list == [] or node_list is None or node_list is False:
                        print_error("The tag value: {0} is not defined in the "
                                    "datafile:{1}".format(tag_name, datafile))
                        return False
                    tag_value = node_list[0].text
                    tag_value = sub_from_env_var(tag_value)
                    tag_value = sub_from_data_repo(tag_value)
                    return tag_value
            return element_value_in_argument
        print_error("The value for arg {0} is not defined in the case".
                    format(element_value_in_argument))
        return element_value_in_argument
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
            credentials[element] = resolve_argument_value_to_get_tag_value(
                datafile, system_name, kwargs[element])
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
                    print_warning("File '{0}' provided for tag '{1}' does not "
                                  "exist".format(abspath, tag))
                    abspath_lst.append(None)
            else:
                abspath_lst.append(None)
        else:
            abspath_lst.append(credentials[tag])

    return abspath_lst


def get_var_by_string_prefix(string):
    """Get value from Environment variable or data repo
    """
    if string.startswith("ENV."):
        return os.environ[string.split('.', 1)[1]]
    if string.startswith("REPO."):
        keys = string.split('.', 1)
        return get_object_from_datarepository(keys[1])


def subst_var_patterns_by_prefix(raw_value, start_pattern="${",
                                 end_pattern="}", prefix="ENV"):
    """Takes a key value pair or string (value) as input in raw_value,
        if the value has a pattern matching ${ENV.env_variable_name}.
    Searches for the env_variable_name in the environment and replaces
    it and return the updated dictionary. If environment variable
    is not found then substitutes with None.
        if the value has a pattern matching ${REPO.key}.
    Searches for the key in the data repository and replaces it and return
    the updated dictionary. If key is not found then None is substituted.
        if the value has a pattern matching ${REPO.k1.k2.k3}.
    Searches for the keys k1, k2, k3 in the data repository in nested order
    as provided and replaces it and return the updated dictionary. If
    keys is not found in the order or does not exist then None is substituted.
    source could be environment or datarepository for now.
    """
    error_msg1 = ("Could not find any %s variable {0!r} corresponding to {1!r}"
                  " provided in input data/testdata file.\nWill default to "
                  "None") % (prefix)
    error_msg2 = ("Unable to substitute %s variable {0!r} corresponding to "
                  "{1!r} provided in input data/testdata file.\nThe value "
                  "processed till now is {2!r} whose evaluation resulted in "
                  "{3!r} exception") % (prefix)
    if type(raw_value) == dict:
        for k in raw_value:
            value = raw_value[k]
            extracted_var = string_Utils.return_quote(str(value),
                                                      start_pattern,
                                                      end_pattern)
            extracted_var = [string for string in extracted_var
                             if prefix in string]
            if len(extracted_var) > 0:
                for string in extracted_var:
                    try:
                        if isinstance(raw_value[k], (str, unicode)):
                            raw_value[k] = raw_value[k].replace(
                                start_pattern+string+end_pattern,
                                get_var_by_string_prefix(string))
                        elif isinstance(raw_value[k], (list, dict)):
                            raw_value[k] = str(raw_value[k]).replace(
                                start_pattern+string+end_pattern, get_var_by_string_prefix(string))
                            raw_value[k] = ast.literal_eval(raw_value[k])
                        else:
                            print_error("Unsupported format - " +
                                        error_msg2.format(string, value))
                    except (KeyError, TypeError):
                        print_error(error_msg1.format(string, value))
                        if isinstance(raw_value[k], str):
                            raw_value[k] = None
                        elif isinstance(raw_value[k], (list, dict)):
                            search_str = ("'[^']*" + re.escape(start_pattern) +
                                          string + re.escape(end_pattern) +
                                          "[^']*'")
                            search_obj = re.search(search_str,
                                                   str(raw_value[k]))
                            if search_obj:
                                raw_value[k] = ast.literal_eval(
                                    str(raw_value[k]).replace(
                                        search_obj.group(), 'None'))
                    except SyntaxError:
                        tuc_obj = TestcaseUtils()
                        print_info("Cannot convert below value into correct format, removing "
                                   "non-printable characters, will attempt conversion again")
                        print_info("<<{}>>".format(raw_value[k]))
                        try:
                            raw_value[k] = tuc_obj.rem_nonprintable_ctrl_chars(raw_value[k])
                            raw_value[k] = ast.literal_eval(raw_value[k])
                        except Exception as exc:
                            print_error("Error - " + error_msg2.format(
                                        string, value, raw_value[k], exc))
    elif isinstance(raw_value, str):
        extracted_var = string_Utils.return_quote(str(raw_value),
                                                  start_pattern, end_pattern)
        extracted_var = [string for string in extracted_var
                         if prefix in string]
        if extracted_var != []:
            for string in extracted_var:
                try:
                    raw_value = raw_value.replace(start_pattern+string+end_pattern,
                                                  get_var_by_string_prefix(string))
                except KeyError:
                    print_error(error_msg1.format(string, raw_value))
                    raw_value = None

    return raw_value


def sub_from_env_var(raw_value, start_pattern="${", end_pattern="}"):
    """wrapper function for subst_var_patterns_by_prefix"""
    return subst_var_patterns_by_prefix(raw_value, start_pattern, end_pattern,
                                        "ENV")


def sub_from_data_repo(raw_value, start_pattern="${", end_pattern="}"):
    """wrapper function for subst_var_patterns_by_prefix"""
    return subst_var_patterns_by_prefix(raw_value, start_pattern, end_pattern,
                                        "REPO")


def substitute_var_patterns(raw_value, start_pattern="${", end_pattern="}"):
    """substitute variable inside start and end pattern
    """

    prefixes = {'ENV': ('environment', lambda var: os.environ[var]),
                'REPO': ('data repository', get_object_from_datarepository)}
    error_msg = ("Could not find any {0} variable {1!r} corresponding to {2!r}"
                 " provided in input data/testdata file.\nWill default to None"
                 )
    if raw_value is None:
        return raw_value
    elif isinstance(raw_value, str):
        extracted_var = string_Utils.return_quote(raw_value, start_pattern,
                                                  end_pattern)
        for string in extracted_var:
            [prefix, var] = string.split('.', 1)
            if prefix in prefixes:
                try:
                    val = prefixes[prefix][1](var)
                except KeyError:
                    print_error(error_msg.format(prefixes[prefix][0], string,
                                                 raw_value))
            if val:
                raw_value = raw_value.replace(start_pattern+string+end_pattern,
                                              val)
        return raw_value
    elif isinstance(raw_value, list):
        return [substitute_var_patterns(val, start_pattern, end_pattern) for val in raw_value]
    elif isinstance(raw_value, dict):
        for key in raw_value:
            raw_value[key] = substitute_var_patterns(raw_value[key],
                                                     start_pattern,
                                                     end_pattern)
        return raw_value
    else:
        print_error("Unsupported format - raw_value should either be a string,"
                    " list or dictionary")
        print_error("raw_value: #{}# and its type is {}".format(
                                    raw_value, type(raw_value)))
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
                if subsystem_list == []:
                    subsystem_list = None
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
                    configuration = sub_from_varconfigfile(configuration, var_configfile)
                configuration_list.append(configuration)
            else:
                filepath_list = xml_Utils.get_child_with_matching_tags(data, "filepath")
                for filepath in filepath_list:
                    if filepath:
                        rel_path = filepath.firstChild.data
                        abs_filepath = file_Utils.getAbsPath(
                                        rel_path, os.path.dirname(config_datafile))
                        root = xml_Utils.get_document_root(abs_filepath)
                        config_node = xml_Utils.get_child_with_matching_tag(root, "config")
                        if config_node:
                            configuration = xml_Utils.convert_dom_to_string(config_node)
                            if var_configfile:
                                configuration = sub_from_varconfigfile(
                                                    configuration, var_configfile)
                            configuration_list.append(configuration)
                        else:
                            testcase_Utils.pNote("no <config> found in file {0}"
                                                 .format(abs_filepath), "error")

                if not filepath_list:
                    testcase_Utils.pNote("neither <config> nor a file containing <config> provided"
                                         " for the config_data = {0} in config file = {1}".format(
                                                            config_name, config_datafile), "error")
                    status = "error"
        else:
            testcase_Utils.pNote("config_data={0} is not found in config file "
                                 "={1}".format(config_name, config_datafile), "error")
            status = "error"

    except IOError as err:
        testcase_Utils.pNote("File does not exist: {0}".format(err), "error")
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
                if ((arguments_dict[name_tuple[j]].startswith("tag") and
                     "=" in arguments_dict[name_tuple[j]])):
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
    return xml_Utils.getElementListWithSpecificXpath(datafile, "./system[@name"
                                                     "='%s']/*" % (system_name))


def group_systems_with_same_tag_value(root, tag, value):
    """
        Put systems with the same tag value pair in one list
        and all other system in another list
    """
    all_system_list = xml_Utils.getChildElementsListWithSpecificXpath(root, "./system")
    system_list = xml_Utils.getChildElementsListWithSpecificXpath(root, "./system/[" + tag +
                                                                  "='" + value + "']")
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
        # check if the system has subsystem or not.
        subsystems = system.findall('subsystem')
        if subsystems != []:
            first_subsystem = True
            for subsystem in subsystems:
                # if the system has subsystem, find the default subsystem for the system and
                # use it to execute the keyword.
                default = subsystem.get('default')
                if default == "yes":
                    subsystem_name = subsystem.get('name')
                    system_name = system.get('name') + '[' + subsystem_name + ']'
                    break
                # if none of the subsystems have default="yes" then the default subsystem
                # will be the first subsystem under the system.
                elif first_subsystem is True:
                    subsystem_name = subsystem.get('name')
                    system_name = system.get('name') + '[' + subsystem_name + ']'
                    first_subsystem = False
        # if there is no subsystem use the system.
        else:
            system_name = system.get('name')
            system_node = system
        system_list.append(system_name)
        system_node_list.append(system_node)
    if node_req:
        return system_list, system_node_list
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
    for i in range(0, len(system_node_list)):
        system = system_node_list[i]
        iter_flag = system.get("iter", None)
        if iter_flag is None:
            iter_flag = xml_Utils.get_text_from_direct_child(system, "iter")
        iter_flag = sub_from_env_var(iter_flag)
        iter_flag = sub_from_data_repo(iter_flag)

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


def set_gnmi_cert_params(p_dic):
    """
    Set the data params for GNMI
    """
    ca_crt = p_dic['ca_crt']
    client_crt = p_dic['client_crt']
    client_key = p_dic['client_key']
    return ca_crt, client_crt, client_key
