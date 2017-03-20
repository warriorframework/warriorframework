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

#!/usr/bin/python

"""onerror driver handles all the failures in Warrior framework
at levels like step/step conditions/testcase/testsuite/project.
Returns the actions that should e taken corresponding to the failure """

from xml.etree import ElementTree as ET
import Framework.Utils as Utils
from Framework.Utils.print_Utils import print_info, print_warning, print_debug


def main(node, def_on_error_action, def_on_error_value, exec_type=False):
    """Takes a xml element (steps/step codntion / testcase/ tesuite)
    as input and return the action to be performed for failure
    conditions """

    error_handle = {}
    action, value = getErrorHandlingParameters(node, def_on_error_action,
                                               def_on_error_value, exec_type)

    function = {'NEXT': next, 'GOTO': goto, 'ABORT': abort,
                'ABORT_AS_ERROR': abortAsError,}.get(action.upper())

    error_handle = function(action, value, error_handle)
    result = get_failure_results(error_handle)
    return result

def get_failure_results(error_repository):
    """ Returns the appropriate values based on the onError actions for failing steps.

    Arguments:
    1. error_repository    = (dict) dictionary containing the onError action, values
    """
    if error_repository['action'] is 'NEXT':
        return False
    elif error_repository['action'] is 'GOTO':
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

    if action is None or action is False:
        action = def_on_error_action
    
    elif action is not None and action is not False:
        supported_values = ['next', 'goto', 'abort', 'abort_as_error']
        action = str(action).strip()
        if not action.lower() in supported_values:
            print_warning("unsupported option '{0}' provided for onError action, supported values are {1}".format(action, supported_values))
            print_info("Hence using default_onError action")
            action = def_on_error_action 
    
    if value is None or value is False:
        value = def_on_error_value

    return action, value

def next(action, value, error_handle):
    """returns 'NEXT' for on_error action = next """

    print_info("failure action= next")
    error_handle['action'] = 'NEXT'
    return error_handle

def goto(action, value, error_handle):
    """returns goto_step_num for on_error action = goto """

    print_info("failed: failure action= goto  %s" % value)
    error_handle['action'] = 'GOTO'
    error_handle['value'] = value
    return error_handle


def abort(action, value, error_handle):
    """returns ABORT for on_error action = abort """

    print_info("failed: failure action= Abort")
    error_handle['action'] = 'ABORT'
    return error_handle

def abortAsError(action, value, error_handle):
    """returns ABORT_AS_ERROR for on_error action = abort_as_error """

    print_info("failed: failure action= abort_as_error")
    error_handle['action'] = 'ABORT_AS_ERROR'
    return error_handle
