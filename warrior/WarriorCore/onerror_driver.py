#!/usr/bin/python
"""
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
"""

import Framework.Utils as Utils
from Framework.Utils.print_Utils import print_info, print_warning, print_debug
from WarriorCore.Classes.war_cli_class import WarriorCliClass

"""
onerror driver handles all the failures in Warrior framework
at levels like step/step conditions/testcase/testsuite/project.
Returns the actions that should e taken corresponding to the failure 
"""


def main(node, def_on_error_action, def_on_error_value, exec_type=False, skip_recovery=True):
    """Takes a xml element (steps/step codntion / testcase/ tesuite)
    as input and return the action to be performed for failure
    conditions """

    if WarriorCliClass.mock:
        # If it is in trialmode and has error, always run next step
        return False

    error_handle = {}
    action, value = getErrorHandlingParameters(node, def_on_error_action,
                                               def_on_error_value, exec_type)

    function = {'NEXT': next, 'GOTO': goto, 'ABORT': abort,
                'ABORT_AS_ERROR': abortAsError, "GOTO_RETURN": gotoReturn}.get(action.upper())

    error_handle = function(action, value, error_handle, skip_recovery=skip_recovery)
    result = get_failure_results(error_handle)
    return result


def get_failure_results(error_repository):
    """ Returns the appropriate values based on the onError actions for failing steps.

    Arguments:
    1. error_repository    = (dict) dictionary containing the onError action, values
    """
    if error_repository['action'] is 'NEXT':
        return False
    elif error_repository['action'] is 'GOTO' or error_repository['action'] is 'GOTO_RETURN':
        return error_repository['value']
    elif error_repository['action'] in ['ABORT', 'ABORT_AS_ERROR']:
        return error_repository['action']
    else:
        return False


def getErrorHandlingParameters(node, def_on_error_action, def_on_error_value, exec_type):
    """Takes a xml element at input and returns the values for on_error action , value
    If no value is available in the node then returns the default values """

    if exec_type:
        exec_node = node.find('Execute')
        def_on_error_action = 'NEXT'
        def_on_error_value = ''
        ex_rule_param = exec_node.find('Rule').attrib
        action = ex_rule_param['Else']
        if ex_rule_param['Else'].upper() == 'GOTO':
            value = ex_rule_param['Elsevalue']
        else:
            value = ''

    else:
        action = Utils.xml_Utils.get_attributevalue_from_directchildnode(node, 'onError', 'action')
        value = Utils.xml_Utils.get_attributevalue_from_directchildnode(node, 'onError', 'value')

    if action is None or action is False or action == '':
        action = def_on_error_action

    elif action is not None and action is not False:
        supported_values = ['next', 'goto', 'abort', 'abort_as_error', "goto_return"]
        action = str(action).strip()
        if action.lower() not in supported_values:
            print_warning(
                "unsupported option '{0}' provided for onError action, supported values are {1}".format(
                    action, supported_values))
            print_info("Hence using default_onError action")
            action = def_on_error_action

    if value is None or value is False:
        if action == "goto_return":
            print_warning("No step numbers given to go to for goto_return")
            print_info("Hence using default_onError action")
            action = def_on_error_action
        else:
            value = def_on_error_value
    else:
        if action == "goto_return":
            value = [x.strip() for x in value.split(",")]

    return action, value


def next(action, value, error_handle, skip_recovery=True):
    """returns 'NEXT' for on_error action = next """

    print_info("failure action= next")
    error_handle['action'] = 'NEXT'
    return error_handle


def goto(action, value, error_handle, skip_recovery=True):
    """returns goto_step_num for on_error action = goto """
    if skip_recovery:
        print_info("failed: failure action= goto  %s" % value)
        error_handle['action'] = 'GOTO'
        error_handle['value'] = value
    else:
        print_warning("Recovery Step cannot have goto as its onError mechanism")
        print_info("Setting on Error to default: NEXT")
        error_handle = next(action, value, error_handle, skip_recovery=skip_recovery)
    return error_handle


def abort(action, value, error_handle, skip_recovery=True):
    """returns ABORT for on_error action = abort """

    print_info("failed: failure action= Abort")
    error_handle['action'] = 'ABORT'
    return error_handle


def abortAsError(action, value, error_handle, skip_recovery=True):
    """returns ABORT_AS_ERROR for on_error action = abort_as_error """

    print_info("failed: failure action= abort_as_error")
    error_handle['action'] = 'ABORT_AS_ERROR'
    return error_handle


def gotoReturn(action, value, error_handle, skip_recovery=True):
    """returns ABORT_AS_ERROR for on_error action = abort_as_error """

    if skip_recovery:
        print_info("failed: failure action= goto_return")
        error_handle['action'] = 'GOTO_RETURN'
        error_handle['value'] = value
    else:
        print_warning("Recovery Step cannot have goto_return as its onError mechanism")
        print_info("Setting on Error to default: NEXT")
        error_handle = next(action, value, error_handle, skip_recovery=skip_recovery)
    return error_handle
