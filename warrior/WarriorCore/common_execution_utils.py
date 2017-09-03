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

"""Module that contains common utilities required for execution """
import copy

from Framework.Utils.print_Utils import print_warning
import Framework.Utils as Utils

def copy_step(step_list, step, value, go_next, mode, tag):
    """From a Step_list, append the number of times the step needs to be repeated based on
    Runmode or retry
    Arguments:
        step_list = Ordered list of steps to be executed
        step = Current step
        value = The value associated with attempts in runmode/retry
        go_next = The value of goto
        mode = Runmode or Retry
        tag = In runmode it is attempt, in retry it is count

    Return:
        step_list = New step list appended with the logic of runmode and retry
    """
    for i in range(0, value):
        copy_step = copy.deepcopy(step)
        copy_step.find(mode).set(tag, go_next)
        copy_step.find(mode).set("attempt", i + 1)
        step_list.append(copy_step)
    return step_list

def get_step_list(filepath, step_tag, sub_step_tag):
    """
    Takes the location of Testcase /Suite/Project xml file as input
    finds a list of all the step elements present in the file
    Parse the step object,
    1. Retrieve the runmode and it corresponding value.
    Based on runmode and value append the list.
    2. Retrieve the retry and it corresponding value.
    Based on runmode and value append the list.

    :Arguments:
        1. filepath    = full path of the Testcase/suite/project xml file
        2. step_tag = xml tag for group of step in the file
        3. sub_step_tag = xml tag for each step in the file

    """

    step_list_with_rmt_retry = []
    root = Utils.xml_Utils.getRoot(filepath)
    step_tag = root.find(step_tag)
    if step_tag is None:
        print_warning("The file: '{}' has no steps "
                      "to be executed".format(filepath))
    else:
        step_list = step_tag.findall(sub_step_tag)
        # iterate all steps to get the runmode and retry details
        for index, step in enumerate(step_list):
            runmode, value = get_runmode_from_xmlfile(step)
            retry_type, _, _, retry_value, _ = get_retry_from_xmlfile(step)
            if runmode is not None and value > 0:
                if len(step_list) > 1:
                    go_next = len(step_list_with_rmt_retry) + value + 1
                    step_list_with_rmt_retry = copy_step(step_list_with_rmt_retry, step, value,
                                                         go_next, mode = "runmode", tag = "value")
                # only one step in step list, append new step
                else:
                    go_next = len(step_list_with_rmt_retry) + value + 1
                    step_list_with_rmt_retry = copy_step(step_list_with_rmt_retry, step, value,
                                                         go_next, mode = "runmode", tag = "value")
            if retry_type is not None and value > 0:
                if len(step_list) > 1:
                    go_next = len(step_list_with_rmt_retry) + value + 1
                    if runmode is not None:
                        get_runmode = step.find('runmode')
                        step.remove(get_runmode)
                    step_list_with_rmt_retry = copy_step(step_list_with_rmt_retry, step, value,
                                                         go_next, mode = "retry_type", tag = "count")
                else:
                    go_next = len(step_list_with_rmt_retry) + value + 1
                    if runmode is not None:
                        get_runmode = step.find('runmode')
                        step.remove(get_runmode)
                    step_list_with_rmt_retry = copy_step(step_list_with_rmt_retry, step, value,
                                                         go_next, mode = "retry_type", tag = "count")
            if retry_type is None and runmode is None:
                step_list_with_rmt_retry.append(step)
    return step_list_with_rmt_retry

def get_runmode_from_xmlfile(element):
    """Get 'runmode:type' & 'runmode:value' of a step/testcase from the
    testcase.xml/testsuite.xml file. Supported values - 'ruf, rup, rmt',
    these values can not be combined with other values"""
    rt_type = None
    rt_value = 1
    runmode = element.find("runmode")
    if runmode is not None:
        rt_type = runmode.get("type").strip().upper()
        rt_value = runmode.get("value")
        rt_type = None if rt_type == "" or rt_type == "STANDARD" else rt_type
        if rt_value is not None and rt_type is not None:

            if rt_type not in ['RUF', 'RUP', 'RMT']:
                print_warning("Unsupported value '{0}' provided for 'runmode:"
                              "type' tag. Supported values : 'ruf, rup & rmt' "
                              "and these values can not be combined with other"
                              " values".format(rt_type))
                return (None, 1)

            try:
                rt_value = int(rt_value)
                if rt_value < 1:
                    rt_value = 1
                    print_warning("Value provided for 'runmode:value' tag "
                                  "'{0}' is less than '1', using default value"
                                  " 1 for execution".format(rt_value))
            except ValueError:
                print_warning("Unsupported value '{0}' provided for 'runmode:"
                              "value' tag, please provide an integer, using "
                              "default value '1' for execution".
                              format(rt_value))
                rt_value = 1
    return (rt_type, rt_value)

def get_retry_from_xmlfile(element):
    """Get 'retry' tag and its values from the testcase step.
       This value can be combined with runmode values
       such as ['rmt', 'rup','ruf']"""
    retry_type = None
    retry_cond = None
    retry_cond_value = None
    retry_value = 5
    retry_interval = 5
    retry_tag = element.find('retry')
    if retry_tag is not None and retry_tag.get('type') is not None:
        retry_type = retry_tag.get('type').strip().lower()
        retry_cond = retry_tag.get('Condition')
        retry_cond_value = retry_tag.get('Condvalue')
        retry_value = retry_tag.get('count')
        retry_interval = retry_tag.get('interval')
        if not retry_type in ['if', 'if not']:
            print_warning("Unsupported value '{0}' provided for 'retry:"\
                          "type' tag. Supported values : 'if, if not' "\
                          .format(retry_type))
            return (None, None, None, 5, 5)
        if (retry_cond is None) or (retry_cond_value is None):
            print_warning("Atleast one of the value provided "
                          "for 'retry_cond/retry_cond_value' is None.")
            return (None, None, None, 5, 5)
        retry_interval = str(retry_interval)
        retry_value = str(retry_value)
        if retry_interval.isdigit() is False:
            retry_interval = 5
            print_warning("The value provided for "\
                          "retry:retry_interval is not valid, "\
                          "using default value 5 for execution")
        retry_interval = int(retry_interval)
        if retry_value.isdigit() is False:
            retry_value = 5
            print_warning("The value provided for "\
                          "retry:retry_value is not valid, "\
                          "using default value 5 for execution")
        retry_value = int(retry_value)
    return (retry_type, retry_cond, retry_cond_value, retry_value, retry_interval)
