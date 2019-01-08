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


# step driver module

import traceback
from WarriorCore.Classes.argument_datatype_class import ArgumentDatatype
import Framework.Utils as Utils
from Framework.Utils import file_Utils
from Framework.Utils.print_Utils import print_info, print_debug, print_error, print_exception
from WarriorCore.Classes.war_cli_class import WarriorCliClass


def get_arguments(step):
    """ For a step in the testcase xml file gets the list of all
    user supplied arguments and updates it to the args_repository

    Arguments:
    1. step = (xml element) an xml element with tag <step>
    """
    arg_datatype_object = ArgumentDatatype(None, None)
    args_repository = {}
    Arguments = step.find('Arguments')
    if Arguments is not None and Arguments is not False:
        for argument in Arguments.findall('argument'):
            arg_name = argument.get('name')
            if arg_name is not None:
                arg_value = argument.get('value')
                if arg_value is None or arg_value is False:
                    arg_value = argument.text
                if "${ENV." in arg_value:
                    arg_value = Utils.data_Utils.sub_from_env_var(arg_value)
                arg_datatype_object.arg_name = arg_name
                arg_datatype_object.arg_value = arg_value
                value = arg_datatype_object.convert_arg_to_datatype()
                args_repository[arg_name] = value
    return args_repository


def send_keyword_to_productdriver(driver_name, plugin_name, keyword,
                                  data_repository, args_repository):
    """send the keyword to corresponding product driver for execution"""
    step_num = data_repository["step_num"]
    # driver_call = 'ProductDrivers.{0}'.format(driver_name)
    try:
        if plugin_name is not None:
            import_name = ".".join(["plugins", plugin_name, "bin",
                                    plugin_name[:-7]+'_driver'])
        else:
            import_name = "ProductDrivers.{0}".format(driver_name)
        driver_call = __import__(import_name, fromlist=[driver_name])
    except Exception:
        trcback = print_exception(Exception)
        data_repository['step-%s_status' % step_num] = 'ERROR'
        data_repository['step-%s_exception' % step_num] = trcback
        Utils.testcase_Utils.pStep()
        return data_repository
    # return eval(driver_call).main(keyword, data_repository, args_repository)
    else:
        return driver_call.main(keyword, data_repository, args_repository)


def get_keyword_resultfile(data_repository, system_name, step_num, keyword):
    """Get the keyword result file """
    kw_results_dir = data_repository['wt_kw_results_dir']
    if system_name is None:
        prefix = "step-{0}".format(str(step_num))
    elif system_name is not None:
        prefix = "{0}_step-{1}".format(system_name, str(step_num))
    keyword_resultfile = Utils.file_Utils.getCustomLogFile(prefix, kw_results_dir,
                                                           keyword, '.xml')

    return keyword_resultfile


def get_step_console_log(filename, logsdir, console_name):
    """Assign seperate console logfile for each step in parallel execution """

    console_logfile = Utils.file_Utils.getCustomLogFile(
        filename, logsdir, console_name)
    print_info("\n************ This is parallel execution ************")
    print_info("\n... console logs for {0} will be logged in {1} ".format(
        console_name, console_logfile))
    Utils.config_Utils.debug_file(console_logfile)

    return console_logfile


def execute_step(step, step_num, data_repository, system_name, kw_parallel, queue,
                 skip_invoked=True):
    """ Executes a step from the testcase xml file
        - Parses a step from the testcase xml file
        - Get the values of Driver, Keyword, impactsTcResult
        - If the step has arguments, get all the arguments and store them as key/value pairs in
          args_repository
        - Sends the Keyword, data_repository, args_repository to the respective Driver.
        - Reports the status of the keyword executed (obtained as return value from the respective
          Driver)

    Arguments:
    1. step            = (xml element) xml element with tag <step> containing the details of the
                         step to be executed like (Driver, Keyword, Arguments, Impact etc..)
    2. step_num        = (int) step number being executed
    3. data_repository = (dict) data_repository of the testcase
    """

    tc_junit_object = data_repository['wt_junit_object']
    driver = step.get('Driver')
    plugin = step.get('Plugin')
    keyword = step.get('Keyword')
    context = Utils.testcase_Utils.get_context_from_xmlfile(step)
    step_impact = Utils.testcase_Utils.get_impact_from_xmlfile(step)
    step_description = Utils.testcase_Utils.get_description_from_xmlfile(step)
    parallel = kw_parallel

    if parallel is True:
        step_console_log = get_step_console_log(data_repository['wt_filename'],
                                                data_repository['wt_logsdir'],
                                                'step-{0}_{1}_consoleLogs'.format(step_num,
                                                                                  keyword))

    data_repository['step_num'] = step_num
    data_repository['wt_driver'] = driver
    data_repository['wt_plugin'] = plugin
    data_repository['wt_keyword'] = keyword
    data_repository['wt_step_impact'] = step_impact
    data_repository['wt_step_context'] = context
    data_repository['wt_step_description'] = step_description

    kw_resultfile = get_keyword_resultfile(
        data_repository, system_name, step_num, keyword)
    Utils.config_Utils.set_resultfile(kw_resultfile)
    # print the start of runmode execution
    if step.find("runmode") is not None and \
       step.find("runmode").get("attempt") is not None:
        if step.find("runmode").get("attempt") == 1:
            print_info("\n----------------- Start of Step Runmode Execution -----------------\n")
        print_info("KEYWORD ATTEMPT: {0}".format(
            step.find("runmode").get("attempt")))
    # print keyword to result file
    Utils.testcase_Utils.pKeyword(keyword, driver)
    print_info("step number: {0}".format(step_num))
    print_info("Teststep Description: {0}".format(step_description))

    if step.find("retry") is not None and step.find("retry").get("attempt") is not None:
        print_info("KEYWORD ATTEMPT: {0}".format(
            step.find("retry").get("attempt")))
    kw_start_time = Utils.datetime_utils.get_current_timestamp()
    print_info("[{0}] Keyword execution starts".format(kw_start_time))
    # get argument list provided by user
    args_repository = get_arguments(step)
    if system_name is not None:
        args_repository['system_name'] = system_name
    Utils.testcase_Utils.update_arguments(args_repository)
    Utils.testcase_Utils.update_kw_resultfile(kw_resultfile)

    # Executing keyword
    send_keyword_to_productdriver(
        driver, plugin, keyword, data_repository, args_repository)
    keyword_status = data_repository['step-%s_status' % step_num]
    Utils.testcase_Utils.update_step_num(str(step_num))
    if context.upper() == 'NEGATIVE' and type(keyword_status) == bool:
        print_debug("Keyword status = {0}, Flip status as context is Negative".format(
            keyword_status))
        keyword_status = not keyword_status
    if WarriorCliClass.mock and (keyword_status is True or keyword_status is False):
        keyword_status = "RAN"

    # Getting onError action
    # Insert rules else statement here
    print_info("")
    print_info("*** Keyword status ***")
    step_goto_value = False
    step_onError_action = Utils.xml_Utils.get_attributevalue_from_directchildnode(
        step, 'onError', 'action')
    if step_onError_action is not False:
        if step_onError_action.upper() == 'GOTO':
            step_goto_value = Utils.xml_Utils.get_attributevalue_from_directchildnode(
                step, 'onError', 'value')
    testcase_error_action = data_repository['wt_def_on_error_action']
    step_onError_action = step_onError_action if step_onError_action else testcase_error_action
    if step_onError_action.upper() == "GOTO" and step_goto_value is False:
        step_goto_value = data_repository['wt_def_on_error_value']
    onerror = step_onError_action.upper()
    if step_goto_value is not False and step_goto_value is not None:
        onerror = onerror + " step " + step_goto_value
    if keyword_status is False and step_onError_action and \
            step_onError_action.upper() == 'ABORT_AS_ERROR' and skip_invoked:
        print_info("Keyword status will be marked as ERROR as onError action is set to"
                   "'abort_as_error'")
        keyword_status = "ERROR"
    Utils.testcase_Utils.reportKeywordStatus(keyword_status, keyword)
    print_info("step number: {0}".format(step_num))

    # Reporting status to data repo
    string_status = {"TRUE": "PASS", "FALSE": "FAIL",
                     "ERROR": "ERROR", "EXCEPTION": "EXCEPTION", "SKIP": "SKIP", "RAN":"RAN"}

    if str(keyword_status).upper() in string_status.keys():
        data_repository['step_%s_result' %
                        step_num] = string_status[str(keyword_status).upper()]
    else:
        print_error("unexpected step status, default to exception")
        data_repository['step_%s_result' % step_num] = "EXCEPTION"

    # Addressing impact
    if step_impact.upper() == 'IMPACT':
        msg = "Status of the executed step  impacts TC result"
        if str(keyword_status).upper() == 'SKIP':
            keyword_status = None
        # elif exec_type_onerror is False and str(keyword_status).upper() ==
        # 'SKIP':
    elif step_impact.upper() == 'NOIMPACT':
        msg = "Status of the executed step does not impact TC result"
    Utils.testcase_Utils.pNote_level(msg, "debug", "kw")
    if data_repository.has_key('step-%s_exception' % step_num):
        msg = "Exception message: " + \
            data_repository['step-%s_exception' % step_num]
        Utils.testcase_Utils.pNote_level(msg, "debug", "kw", ptc=False)

    print_info("")
    kw_end_time = Utils.datetime_utils.get_current_timestamp()
    kw_duration = Utils.datetime_utils.get_time_delta(kw_start_time)
    hms = Utils.datetime_utils.get_hms_for_seconds(kw_duration)
    print_info("Keyword duration= {0}".format(hms))
    print_info("[{0}] Keyword execution completed".format(kw_end_time))
    # condition to  print the end of runmode execution when all the attempts finish
    if step.find("runmode") is not None and \
       step.find("runmode").get("attempt") is not None:
        if step.find("runmode").get("attempt") == \
           step.find("runmode").get("runmode_val"):
            print_info("\n----------------- End of Step Runmode Execution -----------------\n")

    impact_dict = {"IMPACT": "Impact", "NOIMPACT": "No Impact"}
    tc_timestamp = data_repository['wt_tc_timestamp']
    impact = impact_dict.get(step_impact.upper())
    tc_resultsdir = data_repository['wt_resultsdir']
    tc_name = data_repository['wt_name']
    #to append keyword name with Setup/Cleanup in testcase report
    if data_repository['wt_step_type'] != 'step':
        keyword = data_repository['wt_step_type']+ "--" + keyword
    add_keyword_result(tc_junit_object, tc_timestamp, step_num, keyword,
                       keyword_status, kw_start_time, kw_duration,
                       kw_resultfile, impact, onerror, step_description,
                       info=str(args_repository), tc_name=tc_name,
                       tc_resultsdir=tc_resultsdir)

    if parallel is True:
        # put result into multiprocessing queue and later retrieve in
        # corresponding driver
        queue.put((keyword_status, kw_resultfile,
                   step_impact.upper(), tc_junit_object))
    elif not data_repository['war_parallel']:
        # Get the type of the file being executed by Warrior: Case/Suite/Project
        war_file_type = data_repository.get('war_file_type')
        if war_file_type == "Case":
            # Create and replace existing Case junit file for each step
            tc_junit_object.output_junit(data_repository['wt_resultsdir'],
                                         print_summary=False)
        elif war_file_type == "Suite":
            # Create and replace existing Suite junit file for each step
            tc_junit_object.output_junit(data_repository['wt_results_execdir'],
                                         print_summary=False)
        elif war_file_type == "Project":
            # Create and replace existing Project junit file for each step
            tc_junit_object.output_junit(data_repository['wp_results_execdir'],
                                         print_summary=False)
    return keyword_status, kw_resultfile, step_impact


def add_keyword_result(tc_junit_object, tc_timestamp, step_num, keyword,
                       keyword_status, kw_start_time, kw_duration,
                       kw_resultfile, impact, onerror, step_description,
                       info="", tc_name="", tc_resultsdir=""):
    """ Add keyword results into junit object """
    tc_junit_object.add_keyword_result(tc_timestamp, step_num, keyword,
                                       str(keyword_status), kw_start_time,
                                       kw_duration, kw_resultfile,
                                       impact, onerror, step_description, info=info,
                                       tc_name=tc_name, tc_resultsdir=tc_resultsdir)

    tc_junit_object.update_count(str(keyword_status), "1", "tc", tc_timestamp)
    tc_junit_object.update_count("keywords", "1", "tc", tc_timestamp)


def main(step, step_num, data_repository, system_name, kw_parallel=False, queue=None,
         skip_invoked=True):
    """Get a step, executes it and returns the result """
    try:
        step_status = execute_step(step, step_num, data_repository, system_name, kw_parallel,
                                   queue, skip_invoked=skip_invoked)
    except Exception:
        step_status = False, [], data_repository['wt_step_impact'], False
        print_error('unexpected error: {0}'.format(traceback.format_exc()))
    return step_status
