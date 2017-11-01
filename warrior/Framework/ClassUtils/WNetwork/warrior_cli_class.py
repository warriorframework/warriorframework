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
import time
import subprocess
import getpass
import Tools
from Framework import Utils
from Framework.Utils.print_Utils import print_info, print_debug,\
 print_warning, print_exception, print_error
from Framework.Utils.testcase_Utils import pNote
from WarriorCore.Classes.war_cli_class import WarriorCliClass
from Framework.Utils.cli_Utils import cmdprinter
from Framework.ClassUtils import database_utils_class
from Framework.ClassUtils.WNetwork.loging import ThreadedLog
from Framework.Utils.list_Utils import get_list_by_separating_strings


""" Module for performing CLI operations """


class WarriorCli(object):
    """
    Class to handle CLI operations.
    """

    def __init__(self):
        """ Constructor """
        self.conn_obj = None

    def connect_ssh(self, ip, port="22", username="", password="",
                    logfile=None, timeout=60, prompt=".*(%|#|\$)",
                    conn_options="", custom_keystroke="", escape=""):
        """
        - Initiates SSH connection via a specific port. Creates log file.
        :Arguments:
            1. ip = destination ip
            2. port(string) = telnet port
            3. username(string) = username
            4. password(string) = password
            5. logfile(string) = logfile name
            6. timeout(int) = timeout duration
            7. prompt(string) = destination prompt
            8. conn_options(string) = extra arguments that will be used when
                                      sending the ssh/telnet command
            9. custom_keystroke(string) = keystroke(to be given after initial
                                          timeout)
            10. escape(string) = true/false(to set TERM as dump)
        :Returns:
            1. session_object(pexpect session object)
            2. conn_string(pre and post login message)
        """

        credentials = {}
        credentials['ip'] = ip
        credentials['port'] = port
        credentials['username'] = username
        credentials['password'] = password
        credentials['logfile'] = logfile
        credentials['timeout'] = timeout
        credentials['prompt'] = prompt
        credentials['conn_options'] = conn_options
        credentials['custom_keystroke'] = custom_keystroke
        credentials['escape'] = escape

        self.conn_obj = PexpectConnect(credentials)
        self.conn_obj.connect_ssh()

        return self.conn_obj.target_host, self.conn_obj.conn_string

    def connect_telnet(self, ip, port="23", username="", password="",
                       logfile=None, timeout=60, prompt=".*(%|#|\$)",
                       conn_options="", custom_keystroke="", escape=""):
        """
        Initiates Telnet connection via a specific port. Creates log file.
        :Arguments:
            1. ip = destination ip
            2. port(string) = telnet port
            3. username(string) = username
            4. password(string) = password
            5. logfile(string) = logfile name
            6. timeout(int) = timeout duration
            7. prompt(string) = destination prompt
            8. conn_options(string) = extra arguments that will be used when
                                      sending the ssh/telnet command
            9. custom_keystroke(string) = keystroke(to be given after initial
                                          timeout)
            10. escape(string) = true/false(to set TERM as dump)
        :Returns:
            1. session_object(pexpect session object)
            2. conn_string(pre and post login message)
        """

        credentials = {}
        credentials['ip'] = ip
        credentials['port'] = port
        credentials['username'] = username
        credentials['password'] = password
        credentials['logfile'] = logfile
        credentials['timeout'] = timeout
        credentials['prompt'] = prompt
        credentials['conn_options'] = conn_options
        credentials['custom_keystroke'] = custom_keystroke
        credentials['escape'] = escape

        self.conn_obj = PexpectConnect(credentials)
        self.conn_obj.connect_telnet()

        return self.conn_obj.target_host, self.conn_obj.conn_string

    def disconnect(self):
        """
        Disconnects pexpect/paramiko session
        """

        if self.conn_obj and self.conn_obj.target_host:
            self.conn_obj.disconnect()

    def disconnect_telnet(self):
        """
        Disconnects pexpect telnet session
        """

        if self.conn_obj and self.conn_obj.target_host:
            self.conn_obj.disconnect_telnet()

    @cmdprinter
    def send_command(self, start_prompt, end_prompt, command,
                     timeout=60):
        """ Sends the command to ssh/telnet session
        :Arguments:
            1. start_prompt(string) = expected start prompt
            2. end_prompt(string) = expected end prompt
            3. command(string) = command to be executed
            4. timeout(int) = timeout to wait for the end prompt
            5. child = pexpect/paramiko object
            6. childType = pexpect/paramiko
        :Returns:
            1. status(boolean)
            2. response - command execution response
        """

        status = False
        response = ""

        if self.conn_obj and self.conn_obj.target_host:
            status, response = self.conn_obj.send_command(
                command=command, start_prompt=start_prompt,
                end_prompt=end_prompt, timeout=timeout)

        return status, response

    def send_commands_from_testdata(self, testdatafile, **args):
        """
        - Parses the testdata file and gets the command details
        for rows marked execute=yes and row=str_rownum.
        - Sends the obtained commands to the warrior_cli_class
          session object(obj_Session).
        - If the commands have verification attribute set,
        then verifies the verification text for presence/absence as defined
        in the respective found attribute in the testdatfile.

        :Arguments:
            1. testdatafile = the xml file where command details are available
            2. logfile = logfile of the pexpect session object.
            3. varconfigfile = xml file from which the values will be taken
                               for substitution
            4. var_sub(string) = the pattern [var_sub] in the testdata
                                 commands, start_prompt, end_prompt,
                                 verification search will substituted
                                 with this value.
            5. args = Optional filter to specify title/rownum
        :Returns:
            1. finalresult = boolean
        """
        responses_dict = {}
        varconfigfile = args.get('varconfigfile', None)
        datafile = args.get("datafile", None)
        var_sub = args.get('var_sub', None)
        title = args.get('title', None)
        row = args.get('row', None)
        if WarriorCliClass.cmdprint:
            if title:
                pNote("*************{}*************".format('Title: ' + title))
            if row:
                pNote("*************{}*************".format('Row: ' + row))
        system_name = args.get("system_name")
        session_name = args.get("session_name")
        if session_name is not None:
            system_name = system_name + "." + session_name
        testdata_dict = Utils.data_Utils.get_command_details_from_testdata(
            testdatafile, varconfigfile, var_sub=var_sub, title=title, row=row,
            system_name=system_name, datafile=datafile)
        finalresult = True if len(testdata_dict) > 0 else False
        for key, details_dict in testdata_dict.iteritems():
            response_dict = {}
            responses_dict[key] = ""
            command_list = details_dict["command_list"]
            stepdesc = "Send the following commands: "
            pNote(stepdesc)
            n = 0
            for commands in command_list:
                pNote("Command #{0}\t: {1}".format((n+1), commands))
                n = n + 1
            intsize = len(command_list)
            if intsize == 0:
                finalresult = False

            # Send Commands
            for i in range(0, intsize):
                print_info("")
                print_debug(">>>")
                command = details_dict["command_list"][i]
                pNote("Command #{0}\t: {1}".format(str(i+1), command))
                new_obj_session, td_sys, details_dict = \
                    self._get_obj_session(details_dict, system_name, index=i)
                if new_obj_session:
                    result, response = new_obj_session._send_cmd_get_status(
                        details_dict, index=i, system_name=td_sys)
                    result, response = new_obj_session._send_command_retrials(
                        details_dict, index=i, result=result,
                        response=response, system_name=td_sys)
                    rspRes, response_dict = new_obj_session._get_response_dict(
                        details_dict, i, response, response_dict)
                    result = result and rspRes
                    print_debug("<<<")
                else:
                    finalresult = "ERROR"
                    pNote("COMMAND STATUS:{0}".format(finalresult))
                    print_debug("<<<")
                    continue

                if result == "ERROR" or finalresult == "ERROR":
                    result = "ERROR"
                    finalresult = "ERROR"
                finalresult = finalresult and result
            responses_dict[key] = response_dict
        return finalresult, responses_dict

    @cmdprinter
    def _send_cmd(self, **kwargs):
        """method to send command based on the type of object """

        result = False
        response = ""
        if self.conn_obj and self.conn_obj.target_host:
            command = kwargs.get('command')
            startprompt = kwargs.get('startprompt', ".*")
            endprompt = kwargs.get('endprompt', None)
            cmd_timeout = kwargs.get('cmd_timeout', None)
            result, response = self.conn_obj.send_command(command, startprompt,
                                                          endprompt,
                                                          cmd_timeout)
        return result, response

    @staticmethod
    def _get_response_dict(details_dict, index, response, response_dict):
        """Get the response dict for a command. """
        def print_warn_msg(keyvars, numpats):
            """ print a warning message if the number of vars to be stored with
            the patterns does not match with the number of patterns
            """
            warn_msg = ("The number of response reference keys to store is {0}"
                        " than \nthe response reference patterns.\nThe number "
                        "of response reference keys({1}) is {2}\nwhich is {0} "
                        "than number of response reference patterns {3}")
            lessormore = "less" if len(keyvars) < numpats else "more"
            print_warning(warn_msg.format(lessormore, ", ".join(keyvars),
                                          len(keyvars), numpats))
        resp_ref = details_dict["resp_ref_list"][index]
        resp_req = details_dict["resp_req_list"][index]
        resp_pat_req = details_dict["resp_pat_req_list"][index]
        resp_keys = details_dict["resp_key_list"][index]
        inorder = details_dict["inorder_resp_ref_list"][index]
        status = True
        if inorder is not None and inorder.lower().startswith("n"):
            inorder = False
        else:
            inorder = True

        resp_req = {None: 'y', '': 'y',
                    'no': 'n', 'n': 'n'}.get(str(resp_req).lower(), 'y')
        resp_ref = {None: index+1, '': index+1}.get(resp_ref, str(resp_ref))
        if not resp_req == "n":
            save_msg1 = "User has requested saving response"
            save_msg2 = "Response pattern required by user is : {0}"
            save_msg3 = ("Portion of response saved to the data repository "
                         "with key: {0}, value: {1}")
            save_msg4 = "Cannot found response pattern: {0} in response"
            if resp_pat_req is not None:
                # if the requested pattern not found return empty string
                reobj = re.search(resp_pat_req, response)
                if reobj is None:
                    pNote(save_msg4.format(resp_pat_req))
                response = reobj.group(0) if reobj is not None else ""
                response_dict[resp_ref] = response
                pNote(save_msg1+'.')
                pNote(save_msg2.format(resp_pat_req))
                pNote(save_msg3.format(resp_ref, response))
            elif resp_keys is not None:
                keys = resp_ref.split(',')
                # get the patterns from pattern entries in testdata file
                patterns = [k.get("resp_pattern_req") for k in resp_keys]
                # warn if number of patterns does not match number of resp_ref keys
                if len(keys) != len(patterns):
                    print_warn_msg(keys, len(patterns))
                if inorder:
                    pNote(save_msg1+' inorder.')
                    # since inorder pattern matching selected, join all the
                    # patterns in order to create a single big pattern
                    cpatterns = ["({})".format(pat) for pat in patterns]
                    pattern = ".*".join(cpatterns)
                    if pattern.endswith(".*(.*)"):
                        # remove .* pattern from above
                        pattern = pattern[:-6]+pattern[-4:]
                    reobj = re.search(pattern, response, re.DOTALL)
                    if reobj:
                        grps = reobj.groups()
                        # update response_dict with resp_ref keys and
                        # their corresponding matched patterns
                        response_dict.update(dict(zip(keys, grps)))
                        pNote(save_msg2.format(pattern))
                        # print to console the key and the corresponding match stored
                        [pNote(save_msg3.format(key, grp)) for (key, grp) in zip(keys, grps)]
                    else:
                        print_error("inorder search of patterns in response "
                                    "failed")
                        print_error("Expected: '{}'".format(pattern))
                        print_error("But Found: '{}'".format(response))
                        status = False
                else:
                    pNote(save_msg1+' separately.')
                    for key, pattern in zip(keys, patterns):
                        reobj = re.search(pattern, response)
                        presponse = reobj.group(0) if reobj is not None else ""
                        response_dict[key] = presponse
                        pNote(save_msg2.format(pattern))
                        pNote(save_msg3.format(key, presponse))
        else:
            response_dict[resp_ref] = ""
        return status, response_dict

    @staticmethod
    def start_threads(started_thread_for_system, thread_instance_list,
                      same_system, unique_log_verify_list, system_name):
        """This function iterates over unique_log_verify_list which consists of
         unique values gotten from monitor attributes and verify_on attributes

        If a system_name has a * against it, it indicates that the system is
        the same as the one on which the testcase is running. Thread would not
        be started for that system.

        :Returns:
        started_thread_for_system (list[str]) = Stores the system names for
        which threads were succesfully created

        thread_instance_list (list[str]) = stores the instances of thread
        created for corresponding system in the started_thread_for_system list,

        same_system (list[str]) = stores the system name which was the same as
        the system on which the TC is running without the trailing *,
        """
        started_thread_for_system = []
        thread_instance_list = []
        same_system = []
        for i in range(0, len(unique_log_verify_list)):
            if unique_log_verify_list[i] == system_name:
                temp_list = unique_log_verify_list[i].split(".")
                if len(temp_list) > 1:
                    unique_log_verify_list[i] = \
                     Utils.data_Utils.get_session_id(temp_list[0],
                                                     temp_list[1])
                else:
                    unique_log_verify_list[i] = \
                     Utils.data_Utils.get_session_id(temp_list[0])
                same_system.append(unique_log_verify_list[i])
            else:
                if unique_log_verify_list[i]:
                    temp_list = unique_log_verify_list[i].split(".")
                    if len(temp_list) > 1:
                        unique_log_verify_list[i] = \
                         Utils.data_Utils.get_session_id(temp_list[0],
                                                         temp_list[1])
                    else:
                        unique_log_verify_list[i] = \
                         Utils.data_Utils.get_session_id(temp_list[0])
                    datarep_obj = \
                        Utils.data_Utils.get_object_from_datarepository(
                            unique_log_verify_list[i])
                    if datarep_obj is False:
                        print_info("{0} does not exist in data repository"
                                   .format(unique_log_verify_list[i]))
                    else:
                        try:
                            new_thread = ThreadedLog()
                            new_thread.start_thread(datarep_obj)
                            print_info("Collecting response from: "
                                       "{0}".format(unique_log_verify_list[i]))
                            started_thread_for_system.append(
                                unique_log_verify_list[i])
                            thread_instance_list.append(new_thread)
                        except:
                            print_info("Unable to collect response from: "
                                       "{0}".format(unique_log_verify_list[i]))
        return started_thread_for_system, thread_instance_list, same_system

    @staticmethod
    def get_response_dict(started_thread_for_system, thread_instance_list,
                          same_system, response):
        """
        This function iterates over thread_instance_list and gets the data that
        the threads have stored in its data variable. Updates remote_resp_dict
        with the system name and the corresponding data collected.

        The system names in same_system also get stored in the remote_resp_dict
        but their value is the same as the response that was obtained through
        the _send_cmd function

        :Returns:

        remote_resp_dict (dict) with collected logs as value to the
        system_name key
        """
        remote_resp_dict = {}
        for i in range(0, len(same_system)):
            remote_resp_dict[same_system[i]] = response

        for i in range(0, len(started_thread_for_system)):
            data = thread_instance_list[i].data
            thread_instance_list[i].stop_thread()
            pNote("\n\n++++++++++++++++++++++++ RESPONSE FROM SYSTEM: {0} "
                  "++++++++++++++++++++\n\n".format(
                      started_thread_for_system[i]))
            pNote(data)
            pNote("\n\n++++++++++++++++++++++++ END OF DATA FROM SYSTEM: {0} "
                  "++++++++++++++++++++\n\n".format(
                      started_thread_for_system[i]))
            remote_resp_dict[started_thread_for_system[i]] = data

        if len(started_thread_for_system) > 0:
            print_info("Waiting for maximum of 30 seconds to stop collecting "
                       "logs from verify_on system(s)")

        for i in range(0, len(started_thread_for_system)):
            thread_instance_list[i].join_thread(timeout=30, retry=3)
            if thread_instance_list[i].thread_status() is True:
                print_error("Unable to stop collecting logs from {0}."
                            "Please check below message for all "
                            "exception trace that occurred: "
                            "\n{1}".format(started_thread_for_system[i],
                                           thread_instance_list[i].
                                           stop_thread_err_msg))
        return remote_resp_dict

    @staticmethod
    def get_unique_log_and_verify_list(log_list, verify_on_list, system_name):
        """This function loops through the log_list and the verify_on_list and
        returns a unique list containing unique sustem names fromboth the lists
        """
        final_list = []
        if log_list is not None and log_list != "" and log_list is not False:
            comma_sep_log_names = log_list.split(",")
            for i in range(0, len(comma_sep_log_names)):
                comma_sep_log_names[i] = comma_sep_log_names[i].strip()
        else:
            comma_sep_log_names = []

        comma_sep_verify_names = []
        if verify_on_list is not None and verify_on_list != "" and \
           verify_on_list is not False:
            for i in range(0, len(verify_on_list)):
                if verify_on_list[i] is not None and verify_on_list[i] != "" \
                 and verify_on_list[i] is not False:
                    temp_list = verify_on_list[i].split(",")
                    for j in range(0, len(temp_list)):
                        comma_sep_verify_names.append(temp_list[j].strip())
                else:
                    comma_sep_verify_names.append([])
        else:
            comma_sep_verify_names = []

        for i in range(0, len(comma_sep_log_names)):
            if comma_sep_log_names[i] not in final_list:
                final_list.append(comma_sep_log_names[i])

        for i in range(0, len(comma_sep_verify_names)):
            if comma_sep_verify_names[i] == "":
                comma_sep_verify_names[i] = system_name
            if comma_sep_verify_names[i] not in final_list:
                final_list.append(comma_sep_verify_names[i])
        return final_list

    @cmdprinter
    def _send_cmd_get_status(self, details_dict, index, system_name=None):
        """Sends a command, verifies the response and returns
        status of the command """
        command = details_dict["command_list"][index]
        startprompt = details_dict["startprompt_list"][index]
        endprompt = details_dict["endprompt_list"][index]
        verify_list = details_dict["verify_list"][index]
        cmd_timeout = details_dict["timeout_list"][index]
        verify_text_list = details_dict["verify_text_list"][index]
        verify_context_list = details_dict["verify_context_list"][index]
        sleeptime = details_dict["sleeptime_list"][index]
        resp_ref = details_dict["resp_ref_list"][index]
        resp_req = details_dict["resp_req_list"][index]
        resp_pat_req = details_dict["resp_pat_req_list"][index]
        verify_on_list = details_dict["verify_on_list"][index]
        log_list = details_dict["log_list"][index]
        inorder_search = details_dict["inorder_search_list"][index]
        varconfigfile = details_dict["vc_file_list"][index]
        operator = details_dict["operator_list"][index]
        cond_value = details_dict["cond_value_list"][index]
        cond_type = details_dict["cond_type_list"][index]
        unique_log_verify_list = self.get_unique_log_and_verify_list(
            log_list, verify_on_list, system_name)

        startprompt = {None: ".*", "": ".*"}.get(startprompt, str(startprompt))
        resp_req = {None: 'y', '': 'y',
                    'no': 'n', 'n': 'n'}.get(str(resp_req).lower(), 'y')
        resp_ref = {None: index+1, '': index+1}.get(resp_ref, str(resp_ref))
        resp_pat_req = {None: ""}.get(resp_pat_req, str(resp_pat_req))
        sleeptime = {None: 0, "": 0, "none": 0, False: 0, "false": 0}.get(
            str(sleeptime).lower(), str(sleeptime))
        sleeptime = int(sleeptime)

        if inorder_search is not None and \
           inorder_search.lower().startswith("y"):
            inorder_search = True
        else:
            inorder_search = False

        pNote("Startprompt\t: {0}".format(startprompt))
        pNote("Endprompt\t: {0}".format(endprompt))
        pNote("Sleeptime\t: {0}".format(sleeptime))
        pNote("Response required: {0}".format(resp_req))
        pNote("Response reference: {0}".format(resp_ref))
        pNote("Response pattern required: {0}".format(resp_pat_req))

        if not command:
            pNote("Received a boolean False or None type instead of a string "
                  "command, Command not provided or Variable substitution for "
                  "the command could have gone wrong", "error")
            pNote("Skipping execution of this command, result will be marked "
                  "as error", "debug")
            result = 'ERROR'
            response = ''
        else:
            started_thread_for_system, thread_instance_list, same_system = \
                self.start_threads([], [], [], unique_log_verify_list,
                                   system_name)

            result, response = self._send_cmd(startprompt=startprompt,
                                              endprompt=endprompt,
                                              command=command,
                                              cmd_timeout=cmd_timeout)

        if sleeptime > 0:
            pNote("Sleep time of '{0} seconds' requested post command "
                  "execution".format(sleeptime))
            time.sleep(sleeptime)

        try:
            remote_resp_dict = self.get_response_dict(
                started_thread_for_system, thread_instance_list, same_system,
                response)
        except NameError:
            remote_resp_dict = self.get_response_dict([], [], [], response)

        verify_on_list_as_list = get_list_by_separating_strings(
            verify_on_list, ",", system_name)
        if result and result is not 'ERROR':
            if verify_text_list is not None and verify_list is not None:
                verify_group = (operator, cond_value, cond_type)
                if inorder_search is True and len(verify_text_list) > 1:
                    result = Utils.data_Utils.verify_resp_inorder(
                        verify_text_list, verify_context_list, command,
                        response, varconfigfile, verify_on_list_as_list,
                        verify_list, remote_resp_dict, verify_group)
                else:
                    result = Utils.data_Utils.verify_resp_across_sys(
                        verify_text_list, verify_context_list, command,
                        response, varconfigfile, verify_on_list_as_list,
                        verify_list, remote_resp_dict, endprompt, verify_group)
        command_status = {True: "PASS", False: "FAIL", "ERROR": "ERROR"}.get(
            result)
        pNote("COMMAND STATUS:{0}".format(command_status))

        return result, response

    def _get_obj_session(self, details_dict, kw_system_name, index):
        """If system name is provided in testdata file
        get the session of that system name and use it or
        use the current obj_session"""

        value = False
        kw_system_nameonly, _ = Utils.data_Utils.split_system_subsystem(
            kw_system_name)
        td_sys = details_dict["sys_list"][index]
        # To get the session name if it is provided as part of sys tag in td
        td_sys_split = td_sys.split('.') if isinstance(td_sys, str) else []
        if len(td_sys_split) == 2:
            td_sys = td_sys_split[0]
            session = td_sys_split[1]
        else:
            session = details_dict["session_list"][index]

        td_sys = td_sys.strip() if isinstance(td_sys, str) else td_sys
        td_sys = {None: False, False: False, "": False}.get(td_sys, td_sys)
        session = session.strip() if isinstance(session, str) else session
        session = {None: None, False: None, "": None}.get(session, session)
        if td_sys:
            system_name = kw_system_nameonly + td_sys if \
             td_sys.startswith("[") and td_sys.endswith("]") else td_sys
            session_id = Utils.data_Utils.get_session_id(system_name, session)
            obj_session = Utils.data_Utils.get_object_from_datarepository(
                session_id)
            if not obj_session:
                pNote("Could not find a valid connection for system_name={}, "
                      "session_name={}".format(system_name, session), "error")
                value = False
            else:
                value = obj_session
        else:
            # print obj_session
            value = self
            system_name = kw_system_name

        pNote("System name\t: {0}".format(system_name))

        if details_dict["sys_list"][index] is not None:
            kw_system_name = details_dict["sys_list"][index]

        return value, kw_system_name, details_dict

    @cmdprinter
    def _send_command_retrials(self, details_dict, index, **kwargs):
        """ Sends a command to a session, if a user provided pattern
        is found in the command response then tries to resend the command
        multiple times.
        retry_timer = time interval between subsequent retries
        retry_onmatch = the pattern to be matched in the response
                        in order to retry the command.
        retry_count = no of times to retry.
        """
        retry = details_dict["retry_list"][index]
        retry = {None: 'n', '': 'n', 'none': 'n'}.get(str(retry).lower(),
                                                      retry)
        result = kwargs.get('result')
        response = kwargs.get('response')
        if retry == 'y' and (result is False or result == 'ERROR'):
            retry_timer = details_dict["retry_timer_list"][index]
            retry_onmatch = details_dict["retry_onmatch_list"][index]
            retry_count = details_dict["retry_count_list"][index]
            retry_timer = {None: 60, "": 60, "none": 60}.get(
                str(retry_timer).lower(), retry_timer)
            retry_count = {None: 5, "": 5, "none": 5}.get(
                str(retry_count).lower(), retry_count)
            print_info("")
            pNote("Retry was requested for the command")
            pNote("Command re-trials will begin since the most recent "
                  "command status was FAIL or ERROR")
            pNote("Retry count\t: {0}".format(retry_count))
            pNote("Retry timer\t: {0}".format(retry_timer))
            retry_onmatch = {None: False, "": False}.get(retry_onmatch,
                                                         str(retry_onmatch))
            print_onmatch = {False: ""}.get(retry_onmatch, str(retry_onmatch))
            pNote("Retry onmatch: {0}".format(print_onmatch))
            count = 0
            while count < int(retry_count):
                if result is False or result == 'ERROR':
                    match_status = self._get_match_status(retry_onmatch,
                                                          response)
                    if match_status:
                        count = count + 1
                        print_info("")
                        pNote("RETRIAL ATTEMPT:{0}".format(count))
                        pNote("Wait for {0}sec (retry_timer) before sending"
                              " the command again".format(retry_timer))
                        time.sleep(int(retry_timer))
                        result, response = self._send_cmd_get_status(
                            details_dict, index,
                            system_name=kwargs.get("system_name"))
                        command_status = {True: "PASS", False: "FAIL",
                                          "ERROR": "ERROR"}.get(result)
                        pNote("RETRIAL ATTEMPT:{0} STATUS:{1}".format(
                            count, command_status))
                    else:
                        break
                elif result is True:
                    break
        return result, response

    @staticmethod
    def _get_match_status(retry_onmatch, response):
        """ Searchs retry_onmatch value in response """
        status = True
        if retry_onmatch:
            pNote("Command will be executed again if "
                  "the pattern {0} is present in the "
                  "response of the previous execution of the command"
                  .format(retry_onmatch))
            match_object = re.search(retry_onmatch, response)
            if match_object:
                pNote("Found the pattern '{0}' "
                      "in the response of the previous execution "
                      "of the command".format(retry_onmatch))
            else:
                pNote("Did not find the pattern '{0}' "
                      "in the response of the previous execution "
                      "of the command".format(retry_onmatch))
                status = False
        return status

    def isalive(self):
        """
        Returns whether the paramiko/pexpect session is alive or not
        :Returns:
            True if alive else False
        """

        if self.conn_obj:
            target_host = self.conn_obj.target_host
        else:
            target_host = False

        if target_host:
            # for paramiko
            if self.conn_obj.conn_type == "SSH_NESTED":
                if target_host.get_transport():
                    status = target_host.get_transport().is_active()
                else:
                    status = False
            # for pexpect
            else:
                status = target_host.isalive()
        else:
            status = False

        return status

    def read_nonblocking(self, size=1024, timeout=None, *args, **kwargs):
        """
        Reads characters(size) from pexpect/paramiko session
        :Arguments:
            1. size = maximum number of bytes to read
        :Returns:
            1. read_string = Characters read from the pexpect/paramiko session
        """

        try:
            if self.conn_obj and self.conn_obj.target_host:
                if self.conn_obj.conn_type == "SSH_NESTED":
                    read_string = self.conn_obj.channel.recv(size)
                else:
                    read_string = self.conn_obj.target_host.\
                     read_nonblocking(size, timeout)
            else:
                read_string = ""
        except Exception:
            read_string = ""

        return read_string

    @property
    def timeout(self):
        """ Get session timeout(mins) value of pexpect/paramiko session  """

        timeout = None
        if self.conn_obj and self.conn_obj.target_host:
            if self.conn_obj.conn_type in ["SSH", "TELNET"]:
                timeout = self.conn_obj.target_host.timeout
            # elif self.conn_obj.conn_type == "SSH_NESTED":
            #    timeout = self.conn_obj.timeout
            #    # paramiko timeout value will be in seconds,
            #    # convert it to mins
            #    if timeout:
            #        timeout = timeout/60

        return timeout

    @timeout.setter
    def timeout(self, value):
        """ Set session timeout value(mins) for pexpect/paramiko session """

        if self.conn_obj and self.conn_obj.target_host:
            if self.conn_obj.conn_type in ["SSH", "TELNET"]:
                self.conn_obj.target_host.timeout = value
                # elif self.conn_obj.conn_type == "SSH_NESTED":
                #    # paramiko accepts timeout value in seconds
                #    self.conn_obj.timeout = value * 60

    @staticmethod
    def pexpect_spawn_with_env(pexpect_obj, command, timeout, escape=False,
                               env=None):

        """ spawn a pexpect object with environment variable """
        if env is None:
            env = {}
        if str(escape).lower() == "yes" or str(escape).lower() == "true":
            child = pexpect_obj.spawn(command, timeout=int(timeout), env=env)
        else:
            child = pexpect_obj.spawn(command, timeout=int(timeout))
        return child

    @staticmethod
    def _send_cmd_by_type(session_object, command):
        """Determine the command type and
        send accordingly """

        if command.startswith("wctrl:"):
            command = command.split("wctrl:")[1]
            session_object.sendcontrol(command)
        else:
            session_object.sendline(command)

    @staticmethod
    def smart_analyze(prompt, testdatafile=None):
        """
            retrieve the correspond smart testdata file for smart cmd
            from either Tools/connection or testcase testdata file
            :param prompt:
                The string that will be analyzed in order to find the
                device system
            :param testdatafile:
                optional arg to provide a pre-defined device system in the
                test datafile
            :return:
                the smart datafile that contains the smart cmd to be sent
        """
        system_name = None

        if testdatafile is not None:
            # when the testdatafile is a dictionary - this happens only when
            # the testdatafile is taken from database server
            if isinstance(testdatafile, dict):
                db_td_obj = database_utils_class.\
                 create_database_connection('dataservers',
                                            testdatafile.get('td_system'))
                root = db_td_obj.get_tdblock_as_xmlobj(testdatafile)
                db_td_obj.close_connection()
            else:
                root = Utils.xml_Utils.getRoot(testdatafile)
            system_name = Utils.data_Utils._get_global_var(root, "system_name")

        con_settings_dir = Tools.__path__[0] + os.sep + 'connection' + os.sep
        con_settings = con_settings_dir + "connect_settings.xml"

        if system_name is not None:
            sys_elem = Utils.xml_Utils.getElementWithTagAttribValueMatch(
                con_settings, "system", "name", system_name.text)
            if sys_elem is None or sys_elem.find("testdata") is None:
                return None
        else:
            system_list = Utils.xml_Utils.getElementListWithSpecificXpath(
                con_settings, "system[search_string]")
            for sys_elem in system_list:
                if sys_elem.find("search_string").text in prompt and \
                 sys_elem.find("testdata") is not None:
                    return con_settings_dir + sys_elem.find("testdata").text
            return None

        return con_settings_dir + sys_elem.find("testdata").text

    def send_smart_cmd(self, connect_testdata, session_object, tag_value,
                       call_system_name, pre_tag):
        """
            The beacons of Gondor are lit
            send out the smart command
            :param connect_testdata:
                the smart testdata file that contains the smart cmd
            :param session_object:
                use this pexpect object to send out command
            :param tag_value:
                specify the testdata block of commands that get sent out
            :param call_system_name:
                in order to get passed the substitutions, a system name must
                be provided
            :param pre_tag:
                Distinguish if it is a connect smart action or disconnect
                smart action
        """
        if Utils.xml_Utils.getElementWithTagAttribValueMatch(
           connect_testdata, "testdata", "title", tag_value) is not None:
            print_info("**********The following command are sent as part of "
                       "the smart analysis**********")
            main_log = session_object.logfile
            if pre_tag:
                smart_log = main_log.name.replace(".log", "pre_.log")
            else:
                smart_log = main_log.name.replace(".log", "post_.log")
            session_object.logfile = open(smart_log, "a")
            self.send_commands_from_testdata(connect_testdata, session_object,
                                             title=tag_value,
                                             system_name=call_system_name)
            session_object.logfile = main_log
            print_info("**********smart analysis finished**********")
        else:
            print_error()

    def smart_action(self, datafile, call_system_name, raw_prompt,
                     session_object, tag_value, connect_testdata=None):
        """
            entry function for sending smart command
            :param datafile:
                the testcase datafile
            :param call_system_name:
                in order to get passed the substitutions, a system name must
                be provided
            :param raw_prompt:
                The string that will be analyzed in order to find the device
                system
            :param session_object:
                use this pexpect object to send out command
            :param tag_value:
                specify the testdata block of commands that get sent out
            :param connect_testdata:
                the smart testdata file that contains the smart cmd,
                optional in here
            :return:
                the smart testdata file that contains the smart cmd
        """
        testdata, _ = Utils.data_Utils.get_td_vc(datafile, call_system_name,
                                                 None, None)
        pre_tag = False
        if connect_testdata is None:
            connect_testdata = self.smart_analyze(raw_prompt, testdata)
            pre_tag = True

        if connect_testdata is not None:
            self.send_smart_cmd(connect_testdata, session_object, tag_value,
                                call_system_name, pre_tag)
            return connect_testdata
        return None

    @staticmethod
    def get_connection_port(conn_type, inpdict):
        """Gets the port for ssh or telnet connections
        1. ssh :
            - looks if ssh_port is present in  inpdict.
            - if not checks for conn_port
            - if both not present returns None
        """
        if inpdict:
            conn_string = "{0}_port".format(conn_type)
            if conn_string in inpdict and inpdict[conn_string] is not False\
               and inpdict[conn_string] is not None:
                inpdict["port"] = inpdict["{0}_port".format(conn_type)]
            elif "conn_port" in inpdict and inpdict["conn_port"] is not False\
                 and inpdict["conn_port"] is not None:
                inpdict["port"] = inpdict["conn_port"]

        return inpdict

    @staticmethod
    def sendPing(hostname, count, fname):
        """Sends a ping command
        :Arguments:
            1. count(string) = no of pings to be sent
            2. src_iface(string) = source interface from whihc ping messages
                                    are to be sent.
            3. destip(string) = the destination ip address to ping.
            4. fname = logfile to log ping response.
        :Returns:
            status = boolean
        """
        status = False
        command = "ping -c " + count + " " + hostname + " >>" + fname
        print_debug("sendPing, cmd = '%s'" % command)

        response = os.system(command)
        if response == 0:
            print_debug("hostname : '%s' is up " % hostname)
            status = True
        print_debug("hostname : '%s' is down " % hostname)
        return status

    @staticmethod
    def sendSourcePing(count, src_iface, destip, fname):
        """Sends a source based ping command
        i.e. if multiple interfaces are configured and available,
        sends pings from the src_iface provided
        :Arguments:
            1. count(string) = no of pings to be sent
            2. src_iface(string) = source interface from whihc ping messages
                                    are to be sent.
            3. destip(string) = the destination ip address to ping.
            4. fname = logfile to log ping response.
        :Returns:
            status = boolean
        """
        status = False
        command = "ping -c " + count + " -I " + src_iface + " " + \
            destip + " >>" + fname
        print_debug("command, cmd = '%s'" % command)

        response = os.system(command)
        if response == 0:
            print_debug("hostname : '%s' is up " % destip)
            status = True
        print_debug("hostname : '%s' is down " % destip)
        return status


class ParamikoConnect(object):
    """ Class to handle SSH operations using Paramiko module """
    def __init__(self, credentials={}):
        """ Constructor

        :Arguments
            1. credentials:
                1. ip = target_system ip
                2. port = target_system ssh port
                3. username(string) = target_system username
                4. password(string) = target_system password
                5. logfile = logfile name
                6. timeout = wait for response in target_system
                7. via_ip = intermediate_system ip
                8. via_port = intermediate_system ssh port
                9. via_username(string) = intermediate_system username
                10. via_password(string) = intermediate_system password
                11. via_timeout = wait for response in intermediate_system
                12. conn_type = session type(ssh/ssh_nested/telnet)
         """

        self.paramiko = None
        self.__import_paramiko()
        self.conn_string = ""
        self.response = ""
        self.target_host = None
        self.channel = None
        self.conn_type = credentials.get('conn_type')
        if self.conn_type:
            self.conn_type = self.conn_type.upper()
        self.ip = credentials.get('ip')
        self.port = credentials.get('port')
        if self.port is not None:
            self.port = int(self.port)
        self.username = credentials.get('username', '')
        self.password = credentials.get('password', '')
        self.logfile = credentials.get('logfile')
        self.timeout = credentials.get('timeout', 60)

        if self.conn_type == "SSH_NESTED":
            self.via_ip = credentials.get('via_ip')
            self.via_port = credentials.get('via_port')
            if self.via_port is not None:
                self.via_port = int(self.via_port)
            self.via_username = credentials.get('via_username', '')
            self.via_password = credentials.get('via_password', '')
            self.via_timeout = credentials.get('via_timeout', 60)

    def __import_paramiko(self):
        """Import the paramiko module """

        try:
            import paramiko
        except ImportError:
            print_info("{0}: paramiko module is not "
                       "installed".format(os.path.abspath(__file__)))
            print_info("Warrior Framework uses paramiko module for "
                       "cli(via nested SSH) related operations")
        else:
            self.paramiko = paramiko

    def connect_ssh(self):
        """
        Initiates SSH connection to target system using paramiko module.
        For nested SSH connections, session will be established
        via intermediate system.
        """

        if self.paramiko is None:
            print_error("Paramiko is not installed, please install it")
            return

        self.port = self.port if self.port else "22"
        try:
            # for nested SSH session
            if self.conn_type == "SSH_NESTED":
                pNote("Nested SSH connection is requested, first connecting to"
                      " intermediate system - {}".format(self.via_ip))
                self.via_host = self.paramiko.SSHClient()
                self.via_host.set_missing_host_key_policy(
                    self.paramiko.AutoAddPolicy())
                self.via_host.connect(self.via_ip, port=self.via_port,
                                      username=self.via_username,
                                      password=self.via_password,
                                      timeout=self.via_timeout)

                self.via_transport = self.via_host.get_transport()

                dest_addr = (self.ip, self.port)
                local_addr = ('127.0.0.1', 22)

                self.via_channel = self.via_transport.open_channel(
                    "direct-tcpip", dest_addr, local_addr)
                pNote("Connection to intermediate system - {} "
                      "is successful".format(self.via_ip))
            else:
                self.via_channel = None

            self.target_host = self.paramiko.SSHClient()
            self.target_host.set_missing_host_key_policy(
                self.paramiko.AutoAddPolicy())

            self.target_host.connect(self.ip, port=self.port,
                                     username=self.username,
                                     password=self.password,
                                     timeout=self.timeout,
                                     sock=self.via_channel)

            if self.logfile is not None:
                # paramiko logging level is DEBUG(default)
                self.paramiko.util.log_to_file(self.logfile)
            # self.conn_string = self.target_host.get_transport().get_banner()
            # Use invoke_shell option to get conn_string value
            self.channel = self.target_host.invoke_shell()
            self.conn_string = self.channel.recv(9999).decode("utf-8")
        except Exception as exception:
            self.target_host = None
            print_exception(exception)

    def disconnect(self):
        """ Disconnects nested paramiko session """
        self.channel.close()
        self.target_host.close()
        # for nested ssh session
        if self.conn_type == "NESTED_SSH":
            self.via_host.close()

    def send_command(self, command, get_pty=False, *args, **kwargs):
        """ Execute the command on the remote host

        :Arguments:
            1.command = command to be executed
            2.get_pty = request a pseudo-terminal

        """

        response = ""
        status = False

        try:
            start_time = Utils.datetime_utils.get_current_timestamp()
            pNote("[{0}] Sending Command: {1}".format(start_time, command))

            stdin, stdout, stderr = self.target_host.\
                exec_command(command, get_pty=get_pty)

            end_time = Utils.datetime_utils.get_current_timestamp()
            stdin.close()

            # If a linux command fails, corresponding response will be in
            # stderr, stdout.channel.recv_exit_status() will give non-zero
            # value but stderr value is also a valid response in Warrior
            # execution.we can't fail the command execution based on
            # recv_exit_status value.
            if stdout:
                response = response + stdout.read()
            if stderr:
                response = response + stderr.read()

            pNote("[{0}] Command execution completed".format(end_time))
            pNote("Response:\n{0}\n".format(response))
            status = True
        except Exception as exception:
            print_exception(exception)

        return status, response


class PexpectConnect(object):
    """ Class to handle SSH operations using Pexpect module """

    def __init__(self, credentials={}):
        """ Constructor

        :Arguments
            1. credentials:
                1. ip = destination ip
                2. port = ssh/telnet port
                3. username(string) = username
                4. password(string) = password
                5. logfile(string) = logfile name
                6. timeout = timeout duration
                7. prompt(string) = destination prompt
                8. conn_options = connection options
                9. custom_keystroke = keystroke(to be given
                                      after initial timeout)
                10. escape(string) = true/false(to escape color codes by
                                     setting TERM as dump)
                11. conn_type = session type(ssh/telnet)
         """

        self.pexpect = None
        self.__import_pexpect()
        self.conn_string = ""
        self.response = ""
        self.target_host = None
        self.channel = None
        self.conn_type = credentials.get('conn_type')
        if self.conn_type:
            self.conn_type = self.conn_type.upper()
        self.ip = credentials.get('ip')
        self.port = credentials.get('port')
        self.username = credentials.get('username', '')
        self.password = credentials.get('password', '')
        self.logfile = credentials.get('logfile')
        self.timeout = credentials.get('timeout', 60)
        self.prompt = credentials.get('prompt', '.*(%|#|\$)')
        self.conn_options = credentials.get('conn_options', '')
        self.custom_keystroke = credentials.get('custom_keystroke', '')
        self.escape = credentials.get('escape', False)

    def __import_pexpect(self):
        """Import the pexpect module """

        try:
            import pexpect
        except ImportError:
            print_info("{0}: pexpect module is not "
                       "installed".format(os.path.abspath(__file__)))
            print_info("Warrior Framework uses pexpect module for "
                       "cli(SSH & telent) related operations")
        else:
            self.pexpect = pexpect

    def connect_ssh(self):
        """
        Initiates SSH connection via a specific port. Creates log file.
        """

        if self.pexpect is None:
            print_error("Pexpect is not installed, please install it")
            return

        self.target_host = None
        self.conn_string = ""
        self.port = self.port if self.port else "22"
        conn_options = "" if self.conn_options is False or \
            self.conn_options is None else self.conn_options
        custom_keystroke = "wctrl:M" if not self.custom_keystroke else \
            self.custom_keystroke
        # delete -o StrictHostKeyChecking=no and put them in conn_options
        if not conn_options or conn_options is None:
            conn_options = ""
        if not self.username:
            self.username = ""
            print_warning("Using '{0}' as username since it is not provided "
                          "in data file".format(getpass.getuser()))
        else:
            self.username += '@'
        command = 'ssh -p {0} {1}{2} {3}'.format(self.port, self.username,
                                                 self.ip, conn_options)
        # command = ('ssh -p '+ port + ' ' + username + '@' + ip)
        print_debug("connectSSH: cmd = %s" % command)
        if WarriorCliClass.cmdprint:
            pNote("connectSSH: :CMD: %s" % command)
            return None, ""
        child = WarriorCli.pexpect_spawn_with_env(self.pexpect, command,
                                                  self.timeout,
                                                  env={"TERM": "dumb"})

        child.logfile = sys.stdout

        if self.logfile is not None:
            try:
                fdobj = open(self.logfile, "a")
                if fdobj:
                    child.logfile = fdobj
            except Exception as exception:
                print_exception(exception)

        try:
            flag = True
            child.setecho(False)
            child.delaybeforesend = .5
            while True:
                result = child.expect(["(yes/no)", self.prompt,
                                       '.*(?i)password:.*',
                                       ".*(?i)(user(name)?:|login:) *$",
                                       self.pexpect.EOF, self.pexpect.TIMEOUT,
                                       '.*(?i)remote host identification has '
                                       'changed.*'])
                if result == 0:
                    child.sendline('yes')
                elif result == 1:
                    self.target_host = child
                    self.conn_string = self.conn_string + child.before + \
                        child.after
                    break
                elif result == 2:
                    child.sendline(self.password)
                    self.conn_string = self.conn_string + child.before + \
                        child.after
                elif result == 3:
                    child.sendline(self.username)
                elif result == 4:
                    pNote("Connection failed: {0}, with the system response: "
                          "{1}".format(command, child.before), "error")
                    break
                elif result == 5:
                    # Some terminal expect specific keystroke before showing
                    # login prompt
                    if flag is True:
                        pNote("Initial timeout occur, "
                              "sending custom_keystroke")
                        WarriorCli._send_cmd_by_type(child, custom_keystroke)
                        flag = False
                        continue
                    pNote("Connection timed out: {0}, expected prompt: {1} "
                          "is not found in the system response: {2}"
                          .format(command, self.prompt, child.before), "error")
                    break
                elif result == 6:
                    cmd = "ssh-keygen -R " + self.ip if self.port == '22' else\
                          "ssh-keygen -R " + "[" + self.ip + "]:" + self.port
                    print_debug("SSH Host Key is changed - Remove it from "
                                "known_hosts file : cmd = %s" % cmd)
                    subprocess.call(cmd, shell=True)
                    child = self.pexpect.spawn(command,
                                               timeout=int(self.timeout))
                    print_debug("ReconnectSSH: cmd = %s" % command)
        except Exception as exception:
            print_exception(exception)

    def connect_telnet(self):
        """
        Initiates Telnet connection via a specific port. Creates log file.
        """

        self.target_host = None
        self.conn_string = ""
        self.port = self.port if self.port else "23"
        conn_options = "" if self.conn_options is False or \
            self.conn_options is None else self.conn_options
        custom_keystroke = "wctrl:M" if not self.custom_keystroke else \
            self.custom_keystroke
        print_debug("timeout is: %s" % self.timeout)
        print_debug("port num is: %s" % self.port)
        command = ('telnet ' + self.ip + ' ' + self.port)
        if not conn_options or conn_options is None:
            conn_options = ""
        command = command + str(conn_options)
        print_debug("connectTelnet cmd = %s" % command)

        child = WarriorCli.pexpect_spawn_with_env(self.pexpect, command,
                                                  self.timeout,
                                                  env={"TERM": "dumb"})

        try:
            child.logfile = open(self.logfile, "a")
        except Exception:
            child.logfile = None

        try:
            flag = True
            child.setecho(False)
            child.delaybeforesend = .5
            while True:
                result = child.expect([self.prompt, '.*(?i)password:.*',
                                       ".*(?i)(user(name)?:|login:) *$",
                                       self.pexpect.EOF,
                                       self.pexpect.TIMEOUT])
                if result == 0:
                    self.target_host = child
                    self.conn_string = self.conn_string + child.before + \
                        child.after
                    break
                elif result == 1:
                    child.sendline(self.password)
                    self.conn_string = self.conn_string + child.before + \
                        child.after
                elif result == 2:
                    child.sendline(self.username)
                elif result == 3:
                    pNote("Connection failed: {0}, with the system response: "
                          "{1}".format(command, child.before), "error")
                    break
                elif result == 4:
                    # timed out tryonce with Enter has some terminal expects it
                    if flag is True:
                        pNote("Initial timeout occur, "
                              "sending custom_keystroke")
                        WarriorCli._send_cmd_by_type(child, custom_keystroke)
                        flag = False
                        continue
                    pNote("Connection timed out: {0}, expected prompt: {1} "
                          "is not found in the system response: {2}"
                          .format(command, self.prompt, child.before), "error")
                    break
        except Exception as exception:
            print_error(" ! could not connect to %s...check logs" % self.ip)
            print_exception(exception)

    def disconnect(self):
        """
        Disconnects a pexpect session
        """
        if self.target_host.isalive():
            if self.target_host.ignore_sighup:
                self.target_host.ignore_sighup = False
            self.target_host.close()

    def disconnect_telnet(self):
        """
        Disconnects a telnet session
        """
        if self.target_host.isalive():
            time.sleep(2)
            self.target_host.sendcontrol(']')
            time.sleep(2)
            self.target_host.expect('telnet> ')
            time.sleep(2)
            self.target_host.sendline('q')
            time.sleep(2)
            self.target_host.close()

    @cmdprinter
    def send_command(self, command, start_prompt, end_prompt,
                     timeout=60, *args, **kwargs):
        """
        Send an command to pexpect session object and returns
        the status of the command sent
        - Checks for the availability of the start_prompt.
        - if start prompt was available sends the command
        - if failure response is not None and failure response found in
        response then returns False.
        - else if failure response was not found
        and end prompt also not found returns False.
        - else if failure response was not found and end prompt found,
        then returns true.
        """
        tmout = {None: 60, "": 60, "none": 60}.get(timeout,
                                                   str(timeout).lower())
        self.target_host.timeout = int(tmout)
        pNote("Command timeout: {0}".format(self.target_host.timeout))
        response = ""
        msg = ""
        end_time = False
        status = False
        cmd_timedout = False
        # time_format = "%Y-%b-%d %H:%M:%S"
        try:
            boolprompt = self.target_host.expect(start_prompt)
        except Exception as exception:
            pNote("Could not find the start_prompt '{0}'!! exiting!!".
                  format(str(start_prompt)), "error")
            boolprompt = -1
        if boolprompt == 0:
            start_time = Utils.datetime_utils.get_current_timestamp()
            pNote("[{0}] Sending Command: {1}".format(start_time, command))
            WarriorCli._send_cmd_by_type(self.target_host, command)
            try:
                while True:
                    result = self.target_host.expect([end_prompt,
                                                      self.pexpect.EOF,
                                                      self.pexpect.TIMEOUT]) \
                                                      if end_prompt else -1
                    end_time = Utils.datetime_utils.get_current_timestamp()
                    if result == 0:
                        curr_time = Utils.datetime_utils.\
                            get_current_timestamp()
                        msg1 = "[{0}] Command completed successfully". \
                            format(end_time)
                        msg2 = "[{0}] Found end prompt '{1}' after command" \
                            "had timed out".format(curr_time, end_prompt)
                        status = {True: "ERROR", False: True}.get(cmd_timedout)
                        msg = {True: msg2, False: msg1}.get(cmd_timedout)
                        break
                    elif result == -1:
                        pNote("[{0}] end prompt not provided".format(end_time),
                              "error")
                        status = "ERROR"
                        break
                    elif result == 1:
                        msg = "[{0}] EOF encountered".format(end_time)
                        status = "ERROR"
                        break
                    elif result == 2:
                        tmsg1 = "[{0}] Command timed out, command will be " \
                            "marked as error".format(end_time)
                        tmsg2 = "Will wait 60 more seconds to get end " \
                            "prompt '{0}'".format(end_prompt)
                        tmsg3 = "Irrespective of whether end prompt is " \
                            "received or not command will be marked as error" \
                            " because command had timed out once."
                        if not cmd_timedout:
                            self.target_host.timeout = 1
                            pNote(tmsg1, "debug")
                            pNote(tmsg2, "debug")
                            pNote(tmsg3, "debug")
                            tstamp = Utils.datetime_utils.\
                                get_current_timestamp()
                        cmd_timedout = True
                        status = "ERROR"
                        tdelta = Utils.datetime_utils.get_time_delta(tstamp)
                        if int(tdelta) >= 60:
                            msg = "[{0}] Did not find end prompt '{1}' even " \
                                "after 60 seconds post command time out". \
                                format(Utils.datetime_utils.
                                       get_current_timestamp(),
                                       end_prompt)
                            break
                        else:
                            continue
            except Exception as exception:
                print_exception(exception)
            else:
                response = self.target_host.before
                response = str(response) + str(self.target_host.after)
                pNote("Response:\n{0}\n".format(response))
                pNote(msg, "debug")
                if status is True:
                    duration = Utils.datetime_utils.get_time_delta(start_time,
                                                                   end_time)
                    pNote("Command Duration: {0} sec".format(duration))
        return status, response
