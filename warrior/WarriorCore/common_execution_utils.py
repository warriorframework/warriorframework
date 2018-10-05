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

import copy
import glob
import os

from Framework.Utils.print_Utils import print_warning, print_info
import Framework.Utils as Utils

""" Module that contains common utilities required for execution """


def append_step_list(step_list, step, value, go_next, mode, tag):
    """from step_list, append the number of times a step needs to be repeated
    if runmode or retry is present

    :Arguments:
        step_list = Ordered list of steps to be executed
        step = Current step
        value =  attempts in runmode/retry
        go_next = value of the real next step
        mode = runmode or retry
        tag = In runmode it is value, in retry it is count

    :Return:
        step_list = New step list formed by appending the replicated steps
    """
    for i in range(0, value):
        copy_step = copy.deepcopy(step)
        copy_step.find(mode).set(tag, go_next)
        copy_step.find(mode).set("attempt", i + 1)
        copy_step.find(mode).set(mode+"_val", value)
        step_list.append(copy_step)
    return step_list


def get_step_list(filepath, step_tag, sub_step_tag):
    """
    Takes the location of Testcase/Suite/Project file as input
    Returns a list of all the step/testcase/testsuite elements
    present in the file.

    :Arguments:
        1. filepath     = full path of the Testcase/suite/project xml file
        2. step_tag     = xml tag for group of step in the file
        3. sub_step_tag = xml tag for each step in the file
    """
    step_list_with_rmt_retry = []
    root = Utils.xml_Utils.getRoot(filepath)
    steps = root.find(step_tag)
    if steps is None:
        print_warning("The file: '{0}' has no {1} to be executed"
                      .format(filepath, step_tag))
    step_list = steps.findall(sub_step_tag)
    if root.tag == 'Project' or root.tag == 'TestSuite':
        step_list = []
        orig_step_list = steps.findall(sub_step_tag)
        for orig_step in orig_step_list:
            orig_step_path = orig_step.find('path').text
            if '*' not in orig_step_path:
                step_list.append(orig_step)
            # When the file path has asterisk(*), get the Warrior XML testcase/testsuite
            # files matching the given pattern
            else:
                orig_step_abspath = Utils.file_Utils.getAbsPath(
                    orig_step_path, os.path.dirname(filepath))
                print_info("Provided {0} path: '{1}' has asterisk(*) in "
                           "it. All the Warrior XML files matching "
                           "the given pattern will be executed."
                           .format(sub_step_tag, orig_step_abspath))
                # Get all the files matching the pattern and sort them by name
                all_files = sorted(glob.glob(orig_step_abspath))
                # Get XML files
                xml_files = [fl for fl in all_files if fl.endswith('.xml')]
                step_files = []
                # Get Warrior testcase/testsuite XML files
                for xml_file in xml_files:
                    root = Utils.xml_Utils.getRoot(xml_file)
                    if root.tag.upper() == sub_step_tag.upper():
                        step_files.append(xml_file)
                # Copy the XML object and set the filepath as path value for
                # all the files matching the pattern
                if step_files:
                    for step_file in step_files:
                        new_step = copy.deepcopy(orig_step)
                        new_step.find('path').text = step_file
                        step_list.append(new_step)
                        print_info("{0}: '{1}' added to the execution "
                                   "list ".format(sub_step_tag, step_file))
                else:
                    print_warning("Asterisk(*) pattern match failed for '{}' due "
                                  "to at least one of the following reasons:\n"
                                  "1. No files matched the given pattern\n"
                                  "2. Invalid testcase path is given\n"
                                  "3. No testcase XMLs are available\n"
                                  "Given path will be used for the Warrior "
                                  "execution.".format(orig_step_abspath))
                    step_list.append(orig_step)
    # iterate all steps to get the runmode and retry details
    for _, step in enumerate(step_list):
        runmode, value, _ = get_runmode_from_xmlfile(step)
        retry_type, _, _, retry_value, _ = get_retry_from_xmlfile(step)
        if runmode is not None and value > 0:
            go_next = len(step_list_with_rmt_retry) + value + 1
            step_list_with_rmt_retry = append_step_list(step_list_with_rmt_retry, step,
                                                        value, go_next, mode="runmode",
                                                        tag="value")
        if retry_type is not None and retry_value > 0:
            go_next = len(step_list_with_rmt_retry) + retry_value + 1
            if runmode is not None:
                get_runmode = step.find('runmode')
                step.remove(get_runmode)
            step_list_with_rmt_retry = append_step_list(step_list_with_rmt_retry, step,
                                                        retry_value, go_next, mode="retry",
                                                        tag="count")
        if retry_type is None and runmode is None:
            step_list_with_rmt_retry.append(step)
    return step_list_with_rmt_retry


def get_runmode_from_xmlfile(element):
    """Get 'runmode:type' & 'runmode:value' of a step/testcase from the
    testcase.xml/testsuite.xml file. Supported values - 'ruf, rup, rmt',
    these values can not be combined with other values

    Argument : The Step xml object.

    Return:
    rtype : The runmode type RUP/RUF/RMT/NONE
    rt_value : Maximum attempts value for runmode rerun
    runmode_timer : The waittime between each runmode rerun attempts
    """
    rt_type = None
    rt_value = 1
    runmode_timer = None
    runmode = element.find("runmode")
    if runmode is not None:
        rt_type = runmode.get("type").strip().upper()
        rt_value = runmode.get("value")
        runmode_timer = runmode.get("runmode_timer")
        rt_type = None if rt_type == "" or rt_type == "STANDARD" else rt_type
        if rt_value is not None and rt_type is not None:
            if runmode_timer is None or runmode_timer == "":
                runmode_timer = None
            else:
                try:
                    runmode_timer = float(runmode_timer)
                except ValueError:
                    print_warning("The value for Runmode interval is {0}, please provide seconds to"
                                  " wait in numerals".format(runmode_timer))
                    runmode_timer = None

            if rt_type not in ['RUF', 'RUP', 'RMT']:
                print_warning("Unsupported value '{0}' provided for 'runmode:"
                              "type' tag. Supported values : 'ruf, rup & rmt' "
                              "and these values can not be combined with other"
                              " values".format(rt_type))
                return (None, 1, None)
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

    return (rt_type, rt_value, runmode_timer)


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
        if retry_type not in ['if', 'if not']:
            print_warning("Unsupported value '{0}' provided for 'retry:"
                          "type' tag. Supported values : 'if, if not' "
                          .format(retry_type))
            return (None, None, None, 5, 5)
        if (retry_cond is None) or (retry_cond_value is None):
            print_warning("Atleast one of the value provided for 'retry_cond/retry_cond_value' "
                          "is None.")
            return (None, None, None, 5, 5)
        retry_interval = str(retry_interval)
        retry_value = str(retry_value)
        if retry_interval.isdigit() is False:
            retry_interval = 5
            print_warning("The value provided for "
                          "retry:retry_interval is not valid, "
                          "using default value 5 for execution")
        retry_interval = int(retry_interval)
        if retry_value.isdigit() is False:
            retry_value = 5
            print_warning("The value provided for "
                          "retry:retry_value is not valid, "
                          "using default value 5 for execution")
        retry_value = int(retry_value)
    return (retry_type, retry_cond, retry_cond_value, retry_value, retry_interval)


def compute_status(element, status_list, impact_list, status, impact):
    """
        This function computes the overall status in case/suite/project
        execution
    """
    runmode, _, _ = get_runmode_from_xmlfile(element)
    if runmode is None:
        status_list.append(status)
        impact_list.append(impact)
    else:
        if element.find('runmode').get('status') not in [None, '', 'last_instance', 'expected']:
            print_warning("Unsupported value for status. Please provide a valid value. "
                          "Using the Default value for execution")
            element.find('runmode').set('status', '')
        if runmode.upper() == "RMT":
            status_list.append(status)
            impact_list.append(impact)
        elif runmode.upper() == "RUP":
            if element.find('runmode').get('status') is None or \
                 element.find('runmode').get('status') == '':
                status_list.append(status)
                impact_list.append(impact)
            elif element.find('runmode').get('status') == 'last_instance' or \
                    element.find('runmode').get('status') == 'expected':
                if status is True or \
                    (element.find('runmode').get('attempt') ==
                     element.find('runmode').get('runmode_val')):
                    status_list.append(status)
                    impact_list.append(impact)
        elif runmode.upper() == "RUF":
            if element.find('runmode').get('status') is None or \
                 element.find('runmode').get('status') == "":
                status_list.append(status)
                impact_list.append(impact)
            elif element.find('runmode').get('status') == 'last_instance':
                if status is False or \
                    (element.find('runmode').get('attempt') ==
                     element.find('runmode').get('runmode_val')):
                    status_list.append(status)
                    impact_list.append(impact)
            elif element.find('runmode').get('status') == 'expected':
                if status is False:
                    status_list.append(True)
                    impact_list.append(impact)
                elif status is not False and \
                    (element.find('runmode').get('attempt') ==
                     element.find('runmode').get('runmode_val')):
                    status_list.append(False)
                    impact_list.append(impact)
    return status_list, impact_list


def compute_runmode_status(global_status_list, runmode, global_xml):
    """ Computes the status of runmode execution when runmode is provided in
       global level (Details section)
    """
    if global_xml.find('runmode').get('status') not in [None, '', 'last_instance', 'expected']:
        print_warning("Unsupported value for status. Please provide a valid value. "
                      "Using the Default value for execution")
        global_xml.find('runmode').set('status', '')
    if global_xml.find('runmode').get('status') is None or \
        global_xml.find('runmode').get('status') == "" or \
            runmode.upper() == "RMT":
        if "FALSE" in global_status_list or False in global_status_list:
            status_value = False
        elif "RAN" in global_status_list:
            status_value = "RAN"
        elif "ERROR" in global_status_list:
            status_value = "ERROR"
        else:
            status_value = True
    elif runmode.upper() == "RUP":
        if global_xml.find('runmode').get('status') == 'last_instance':
            status_value = global_status_list.pop()
        elif global_xml.find('runmode').get('status') == 'expected' and \
            (global_status_list[-1] is True or
             global_status_list[-1] == "TRUE"):
            status_value = True
        else:
            status_value = global_status_list.pop()
    elif runmode.upper() == "RUF":
        if global_xml.find('runmode').get('status') == 'last_instance':
            status_value = global_status_list.pop()
        elif global_xml.find('runmode').get('status') == 'expected' and \
            (global_status_list[-1] is False or
             global_status_list[-1] == "FALSE"):
            status_value = True
        else:
            status_value = global_status_list.pop()
    return status_value
