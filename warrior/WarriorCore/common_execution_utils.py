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
from Framework.Utils.print_Utils import print_warning


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
        if not retry_type in ['if', 'if not']:
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
    elif runmode.upper() == "RMT":
            status_list.append(status)
            impact_list.append(impact)
    elif runmode.upper() == "RUP":
        if element.find('runmode').get('status') is None or \
           element.find('runmode').get('status') == "":
                status_list.append(status)
                impact_list.append(impact)
        elif element.find('runmode').get('status') == 'last_instance' or \
                element.find('runmode').get('status') == 'expected':
            if status is True or \
                (element.find('runmode').get('attempt') ==
                 element.find('runmode').get('runmode_value')):
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
                 element.find('runmode').get('runmode_value')):
                    status_list.append(status)
                    impact_list.append(impact)
        elif element.find('runmode').get('status') == 'expected':
            if status is False:
                status_list.append(True)
                impact_list.append(impact)
            elif status is not False and \
                (element.find('runmode').get('attempt') ==
                 element.find('runmode').get('runmode_value')):
                    status_list.append(False)
                    impact_list.append(impact)
    return status_list, impact_list
