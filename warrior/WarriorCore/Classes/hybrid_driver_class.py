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
Hybrid driver to handle hybrid mode test case execution:
------------
Description:
------------

When Testcase data type is selected as Hybrid, user can select certain steps
to be run in Iterative fashion and certain steps to be run in custom fashion.

During execution of a Hybrid mode testcase the steps will be executed in an
iterative fashion over the systems in the warrior system datafile. If user
provides a value for system name as argument in the step then the step will
be executed on the specified system and not on the current iterating system
(similar to custom mode execution)

The steps in a Hybrid mode testcase can have one of the three iteration_types
1. One per testcase
2. Standard (Default)
3. End of testcase.

Expected behavior for each iteration type while executing the steps in an
iterative fashion on the available systems:

Once per testcase:
------------------
Steps that have iteration type as once_per_testcase will be executed only
during the first iteration. User can have multiple once_per_testcase steps in
a testcase.

Any step in a testcase can be a once_per_testcase step, i.e. it is not
necessary to have only the first set of steps to be once_per_testcase.

Standard:
--------
Steps that have iteration type as standard will be executed on each iteration.

End of testcase:
---------------
Steps that have iteration type as end_of_testcase will be executed only during
the last iteration. User can have multiple end_of_testcase steps in a testcase
but all of them will be executed only during the last iteration.

Any step in a testcase can be end_of_testcase step, i.e. it is not necessary
to have only the last set of steps to be end_of_testcase.


For all the iteration types specified above if a system name in provided in as
argument in the step the step will be executed on the specified system
otherwise the step will be executed on the current iterating system.
"""

from Framework.Utils import data_Utils, xml_Utils, config_Utils, \
                        testcase_Utils, file_Utils
from Framework.Utils.testcase_Utils import pNote
from Framework.Utils.print_Utils import print_debug, print_info
from WarriorCore import step_driver, common_execution_utils
import WarriorCore.onerror_driver as onerror_driver
import WarriorCore.exec_type_driver as exec_type_driver


class HybridDriver(object):
    """
    Hybrid driver class
    """

    def __init__(self, step_list, data_repository, tc_status, system_name_list,
                 system_node_list):
        """
        Constructor
        """

        self.data_repository = data_repository

        # List of steps to be executed, these are the xml nodes of the steps
        # in the testcase
        # List of system names in the warrior data file
        # List of systems from the warrior data file as xml nodes
        # List of iteration type for each step
        # List of systems to be iterated upon from the warrior data file, this
        # is the list excluding the systems with iter=no
        # List of system names provide in the each step from the testcase xml
        # file.
        self.step_list = step_list
        self.system_name_list = system_name_list
        self.system_node_list = system_node_list
        self.iter_type_list = self._get_iteration_type_list(self.step_list)
        self.iter_sys_list = self._get_iteration_syslist(self.system_node_list,
                                                         self.system_name_list)
        self.kw_sys_list = self._get_kw_system_name_list(step_list)
        self.executed_or_not_list = self._get_executed_list(self.step_list)

        # The first sstem in the warrior datafile is taken as the defalt system
        self.default_system = self.system_name_list[0]

        # List of steps that should be executed at the end of the testcase
        # List of steps after removing end of testcase steps.
#
#         self.end_of_tc_list, self.end_of_tc_kw_syslist,\
#         self.end_of_tc_stepnum_list = self._get_exec_steps(self.step_list,
#                                            self.iter_type_list)

        # items required to compute status
        self.step_status_list = []
        self.kw_resultfile_list = []
        self.step_impact_list = []
        self.system_status_list = []
        self.system_resultfile_list = []

        self.default_error_action = self.data_repository['wt_def_on_error_action']
        self.default_error_value = self.data_repository['wt_def_on_error_value']
        self.stop_after_current_step = False
        self.system_executed = None
        self.iterating_system = None
        self.last_system = False
        self.execute_endoftc = False
        self.stop_after_current_iteration = False

    def execute_hybrid_mode(self):
        """
        Method that executes steps in a hybrid mode testcase
        """

    # Iterate over the list of systems in the data file and execute the steps

        for i in range(0, len(self.iter_sys_list)):
            # determine if it is the last system in the list of systems an set
            # the self.last_system flag accordingly.

            if i == len(self.iter_sys_list)-1:
                self.last_system = True
            else:
                self.last_system = False

            self.iterating_system = self.iter_sys_list[i]

            if self.stop_after_current_iteration:
                break

            # Call the _execute_step_list method to execute the list of steps,
            # Note that self.execute_endoftc flag is now False hence only
            # once_per_tc and standard steps will be executed
            self._execute_step_list()

            # if it is the last system, set self.execute_endoftc
            # flag and then call _execute_step_list so this time only the
            # end_of_tc steps will be executed.
            if self.last_system:
                self.execute_endoftc = True
                pNote(" ++++++ Now starting execution of step with "
                      "iter_type=end_of_tc ++++++")
                self._execute_step_list()

            # compute the system status
            self._compute_system_status(self.system_executed)

        # compute the testcase status form the satus of al the systems
        tc_status = self._compute_testcase_status()
        self.execute_endoftc = False
        self.stop_after_current_iteration = False
        self.stop_after_current_step = False
        self.last_system = False

        return tc_status

    def _compute_system_status(self, system_executed):
        """
        """
        system_status = testcase_Utils.compute_status_using_impact(
                                self.step_status_list, self.step_impact_list)
        system_resultfile = self.compute_system_resultfile(self.kw_resultfile_list,
                                                           self.data_repository['wt_resultsdir'],
                                                           system_executed)
        self.system_status_list.append(system_status)
        self.system_resultfile_list.append(system_resultfile)

        return

    def _compute_testcase_status(self):
        """
        """
        tc_status = testcase_Utils.compute_status_without_impact(
                                                    self.system_status_list)
        print_debug("Updating Testcase result file...")
        testcase_Utils.append_result_files(self.data_repository['wt_resultfile'],
                                           self.system_resultfile_list)
        return tc_status

    def _execute_step_list(self):
        """
        """

        goto_stepnum = False
        step_num = 0
        while step_num < len(self.step_list):

            index = step_num
            step = self.step_list[step_num]
            step_num += 1

            self.system_executed = self._get_system_executed(index)
            if self.stop_after_current_step:
                break

            # Decide whether or not to execute keyword
            # First decide if this step should be executed in this iteration
            if not goto_stepnum or goto_stepnum == str(step_num):
                # get Exectype information
                run_current_step, trigger_action = exec_type_driver.main(step)
                if not run_current_step:

                    if trigger_action.upper() in ['ABORT', 'ABORT_AS_ERROR']:
                        if any([self.iter_type_list[index] == "once_per_tc",
                               self.iter_type_list[index] == "end_of_tc"]):
                            pNote("step exectype check failed, fail action is set to {0} and"
                                  "step iter_type={1} hence aborting execution compeletely".\
                                  format(trigger_action.upper(), self.iter_type_list[index]), "debug")
                            self.stop_after_current_iteration = True
                            self.stop_after_current_step = True
                        else:
                            pNote("step exectype check failed, fail action is set to {0} and"
                                  "step iter_type={1} hence aborting execution for this system".\
                                  format(trigger_action.upper(), self.iter_type_list[index]), "debug")
                        goto_stepnum = False
                        break
                    elif trigger_action.upper() in ['SKIP', 'NEXT']:
                        result = self._update_skip_results(step, self.system_executed,
                                                   step_num)
                        self.kw_resultfile_list.append(result[1])
                        continue
                    # when 'onError:goto' value is less than the current step num,
                    # change the next iteration point to goto value
                    elif trigger_action and int(trigger_action) < step_num:
                        result = self._update_skip_results(step, self.system_executed,
                                                   step_num)
                        self.kw_resultfile_list.append(result[1])
                        step_num = int(trigger_action)-1
                        trigger_action = False

                    continue

            # when there is no goto
            if not goto_stepnum:
                result = self._execute_step(self.system_executed, step_num,
                                            index, goto_stepnum)

            # when goto is triggered and matches the current step number
            elif (goto_stepnum and goto_stepnum == str(step_num)):
                result = self._execute_step(self.system_executed, step_num,
                                            index, goto_stepnum)
                goto_stepnum = False

            # when goto is triggered and does not match current step... skip
            elif goto_stepnum and goto_stepnum != str(step_num):
                result = self._update_skip_results(step, self.system_executed,
                                                   step_num)
                self.kw_resultfile_list.append(result[1])
                continue

            step_status = result[0]
            kw_resultfile = result[1]
            step_impact = result[2]

            self._update_status_items(step_status, kw_resultfile, step_impact)
            goto_stepnum, step_num = self._compute_runmode_goto_operations(step, step_status,
                                                                           goto_stepnum, step_num)
            if (goto_stepnum == 'ABORT'):
                if any([self.iter_type_list[index] == "once_per_tc",
                       self.iter_type_list[index] == "end_of_tc"]):
                    pNote("step iter_type={0}, and onerror action=ABORT hence aborting execution"
                          "compeletely".format(self.iter_type_list[index]), "debug")
                    self.stop_after_current_iteration = True
                    self.stop_after_current_step = True
                goto_stepnum = False
                break

        return

    def _compute_runmode_goto_operations(self, step, step_status,
                                         goto_stepnum, step_num):
        """
        """
        runmode, value, _ = common_execution_utils.get_runmode_from_xmlfile(step)

        if runmode is not None:
            # if runmode is 'ruf' & step_status is False, skip the repeated
            # execution of same TC step and move to next actual step
            if all(runmode == "ruf", step_status is False):
                goto_stepnum = str(value)
            # if runmode is 'rup' & step_status is True, skip the repeated
            # execution of same TC step and move to next actual step
            elif runmode == "rup" and step_status is True:
                goto_stepnum = str(value)
            else:
                if any([step_status is False,
                       str(step_status).upper() == "ERROR",
                       str(step_status).upper() == "EXCEPTION"]):
                    goto_stepnum = onerror_driver.main(step, self.default_error_action,
                                                       self.default_error_value)
                    # if (goto_stepnum == 'ABORT'): break
        else:
            if any([step_status is False, str(step_status).upper() == "ERROR",
                   str(step_status).upper() == "EXCEPTION"]):
                goto_stepnum = onerror_driver.main(step, self.default_error_action,
                                                   self.default_error_value)
                if str(goto_stepnum).upper() == 'ABORT':
                    pass
                # when 'onError:goto' value is less than the current step num,
                # change the next iteration point to goto value
                elif goto_stepnum and int(goto_stepnum) < step_num:
                    step_num = int(goto_stepnum)-1
                    goto_stepnum = False
        return goto_stepnum, step_num

    def _update_status_items(self, step_status, kw_resultfile, step_impact):
        """
        """
        self.step_status_list.append(step_status)
        self.kw_resultfile_list.append(kw_resultfile)
        self.step_impact_list.append(step_impact)

    def _execute_step(self, system_executed, step_num, index, goto_stepnum):
        """
        """
        print_info("\n")
        result = (None, None, None, None)

        if not self.execute_endoftc:

            # once_per_tc
            if self.iter_type_list[index] == "once_per_tc":
                self._print_step_details(step_num, self.iter_type_list[index],
                                         system_executed)
                # if not already executed, execute now
                if self.executed_or_not_list[index] == "no":
                    result = step_driver.main(self.step_list[index], step_num,
                                              self.data_repository,
                                              system_executed)
                    self.executed_or_not_list[index] = "yes"
                # if already executed, skip now
                elif self.executed_or_not_list[index] == "yes":
                    pNote("step iter_type is 'once_per_testcase and has "
                          "already been executed, hence skipping'")
                    result = self._update_skip_results(self.step_list[index],
                                                       system_executed,
                                                       step_num)

            # if standard, execute it
            elif self.iter_type_list[index] == "standard":
                self._print_step_details(step_num, self.iter_type_list[index],
                                         system_executed)
                result = step_driver.main(self.step_list[index], step_num,
                                          self.data_repository,
                                          system_executed)

            # if end_of_tc, skip it
            elif all([self.iter_type_list[index] == "end_of_tc",
                     not goto_stepnum]):
                self._print_step_details(step_num, self.iter_type_list[index],
                                         system_executed)
                pNote("step iter_type={0} and will be executed at the end of "
                      "the testcase, hence skipping now".format(self.iter_type_list[index]))
                result = self._update_skip_results(self.step_list[index],
                                                   system_executed, step_num)

            elif self.iter_type_list[index] == "end_of_tc" and goto_stepnum:
                pNote("Goto step is of iter_type='end_of_tc', will execute all"
                      " end_of_tc_steps from here and complete execution")
                self._print_step_details(step_num, self.iter_type_list[index],
                                         system_executed)
                result = step_driver.main(self.step_list[index], step_num,
                                          self.data_repository,
                                          system_executed)
                self.execute_endoftc = True
                self.stop_after_current_iteration = True

        elif self.execute_endoftc:
            self._print_step_details(step_num, self.iter_type_list[index],
                                     system_executed)

            # if end_of_tc, execute it.
            if self.iter_type_list[index] == "end_of_tc":
                result = step_driver.main(self.step_list[index], step_num,
                                          self.data_repository,
                                          system_executed)
            # if iter_type=once_per_tc or standard skip it.
            else:
                pNote("Now executing only end_of_tc steps hence skipping "
                      "step={0} with iter_type={1}".format(step_num, self.iter_type_list[index]))
                result = self._update_skip_results(self.step_list[index],
                                                   system_executed, step_num)

        return result

    def _update_skip_results(self, step, system_name, step_num):
        """
        """
        keyword = step.get('Keyword')
        kw_resultfile = step_driver.get_keyword_resultfile(self.data_repository, system_name,
                                                           step_num, keyword)
        keyword_description = testcase_Utils.get_description_from_xmlfile(step)
        config_Utils.set_resultfile(kw_resultfile)
        testcase_Utils.pKeyword(keyword, step.get('Driver'))
        testcase_Utils.reportStatus('Skip')
        print_info("\n-----------------------------------------------------\n")
        self.data_repository['wt_junit_object'].update_count("skipped", "1", "tc",
                                                             self.data_repository['wt_tc_timestamp'])
        self.data_repository['wt_junit_object'].update_count("keywords", "1", "tc",
                                                             self.data_repository['wt_tc_timestamp'])
        self.data_repository['wt_junit_object'].add_keyword_result(self.
                                                                   data_repository['wt_tc_timestamp'],
                                                                   step_num, keyword, "SKIPPED",
                                                                   "skipped", "skipped", "skipped",
                                                                   "skipped", "skipped",
                                                                   keyword_description)
        self.data_repository['step_{}_result'.format(step_num)] = "SKIPPED"
        result = ("Skip", kw_resultfile, None, None)
        return result

    def _get_system_executed(self, index, sys_list=None):
        """
        """
        sys_list = self.kw_sys_list if sys_list is None else sys_list
        if sys_list[index] is not None:
            system_executed = sys_list[index]
        elif sys_list[index] is None and self.iterating_system is not None:
            system_executed = self.iterating_system
        elif sys_list[index] is None and self.iterating_system is None:
            system_executed = self.default_system

        return system_executed

    def _get_iteration_syslist(self, system_node_list, system_name_list):
        """
        Process the initial system_list and remove the systems
        that do not have iter=yes.
        """
        iteration_syslist = []
        for i in range(0, len(system_node_list)):
            system = system_node_list[i]
            iter_flag = system.get("iter", None)
            if iter_flag is None:
                iter_flag = xml_Utils.get_text_from_direct_child(system,
                                                                 "iter")
            iter_flag = data_Utils.sub_from_env_var(iter_flag)

            if str(iter_flag).lower() == "no":
                pass
            else:
                system_name = system_name_list[i]
                if not system_name:
                    pNote("No name provided for system/susbsystem in datafile",
                          "error")
                else:
                    iteration_syslist.append(system_name)

        return iteration_syslist

    def _get_executed_list(self, step_list):
        """
        """
        executed_or_not_list = []
        for _ in step_list:
            executed_or_not_list.append("no")
        return executed_or_not_list

    def _get_kw_system_name_list(self, step_list):
        """
        Get the iteration type of a step
        """
        kw_system_name_list = []

        for step in step_list:
            kw_system_name = None
            system_name_tag = step.find("Arguments/argument[@name='system_name']")
            if system_name_tag is not None or False:
                kw_system_name = system_name_tag.get("value")
            if kw_system_name is False or kw_system_name is None:
                kw_system_name = None
            else:
                kw_system_name = str(kw_system_name).strip()

            kw_system_name_list.append(kw_system_name)

        return kw_system_name_list

    def _get_exec_steps(self, step_list, iter_type_list):
        """
        """
        end_of_tc_list = []
        end_of_tc_kw_syslist = []
        end_of_tc_stepnum_list = []
        for i in range(0, len(step_list)):
            if str(iter_type_list[i]).lower() == "end_of_tc":
                end_of_tc_list.append(step_list[i])
                end_of_tc_kw_syslist.append(self.kw_sys_list[i])
                end_of_tc_stepnum_list.append(i+1)

        return end_of_tc_list, end_of_tc_kw_syslist, end_of_tc_stepnum_list

    def _get_iteration_type_list(self, step_list):
        """
        Get the iteration type of a step
        """
        iter_type_list = []

        for step in step_list:
            iteration_type = None
            iteration_type_tag = step.find("iteration_type")
            if iteration_type_tag is not None and \
               iteration_type_tag is not False:
                iteration_type = iteration_type_tag.get("type")
            if iteration_type is not None and iteration_type is not False:
                iteration_type = str(iteration_type).lower().strip()
            else:
                iteration_type = "standard"
            iter_type_list.append(iteration_type)
        return iter_type_list

    def compute_system_resultfile(self, kw_resultfile_list, resultsdir,
                                  system_name):
        """Takes a list of steps as input and executes them in sequential
        order by sending them to test case steps execution driver
        """
        system_results_dir = file_Utils.createDir(resultsdir, 'System_Results')
        system_resultfile = file_Utils.getCustomLogFile('system',
                                                        system_results_dir,
                                                        system_name, '.xml')
        testcase_Utils.append_result_files(system_resultfile,
                                           kw_resultfile_list,
                                           dst_root='System')
        return system_resultfile

    def _print_step_details(self, step_num, iter_type, system_executed):
        """
        Print step details to the console
        """
        pNote("Step_num: {0}".format(step_num))
        pNote("step iter_type: {0}".format(iter_type))
        pNote("system to be executed on: {0}".format(system_executed))
        return
