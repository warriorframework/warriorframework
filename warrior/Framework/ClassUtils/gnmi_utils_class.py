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
gnmi Utils class
"""

import json, re
from Framework.Utils import testcase_Utils, data_Utils, config_Utils, cli_Utils, file_Utils
from Framework.ClassUtils.json_utils_class import JsonUtils as JU
from time import sleep


try:
    import pexpect
except:
    testcase_Utils.pNote("Need to have pexpect module.", "error")


class gnmi(object):
    """gnmi Utils Class"""

    def __init__(self):
        """___init___"""
        self.ju = JU()

    def scp_client_ca(self, cmd_string, passwd, external_system=None, external_system_session=None):
        """
        Perform scp/sftp operation
        :param cmd_string: scp/sftp command string
        :param passwd: remote system password
        :param external_system: external system mentioned in the data file
        :param external_system_session: external system session if any
        :return: True or False
        """
        status = False
        if external_system == None:
            child = pexpect.spawn(cmd_string)
        else:
            session_id = data_Utils.get_session_id(external_system, external_system_session)
            child = data_Utils.get_object_from_datarepository(session_id)
            child.sendline(cmd_string)
        while 1:
            try:
                u_index = child.expect(['password', 'Permission denied', pexpect.EOF,
                                        'want to continue connecting', '.*100%.*(%|#|\$)',
                                        'Connection reset by peer', pexpect.TIMEOUT], timeout=20)
                if u_index == 0:
                    child.sendline(passwd)
                    testcase_Utils.pNote(child.before+child.match.group(0))
                if u_index == 1:
                    status = False
                    testcase_Utils.pNote(child.before+child.match.group(0)+child.after)
                    break
                if u_index == 2:
                    testcase_Utils.pNote(child.before)
                    if "100%" in child.before:
                        status = True
                    break
                if u_index == 4:
                    testcase_Utils.pNote(child.before+child.match.group(0))
                    if "100%" in child.before+child.match.group(0):
                        status = True
                    break
                if u_index == 3:
                    testcase_Utils.pNote(child.before+child.match.group(0)+child.after)
                    child.sendline('yes')
                if u_index == 5:
                    testcase_Utils.pNote(child.before+child.match.group(0))
                    status = False
                    break
            except:
                testcase_Utils.pNote("File Copy Failed", "error")
                status = False
                break
        if status:
            testcase_Utils.pNote("Client certificate copied Successfully.")
        else:
            testcase_Utils.pNote("Client certificate copy Failed.", "error")
        return status

    def execute(self, binary, cmd_string, uname, passwd, prompt, external_system=None,
                external_system_session=None, stop_after=None, gnmi_obj=None, script="No"):
        """
        Execute gnmi command using gnmi binary
        :param cmd_string:
        :param uname:
        :param passwd:
        :param external_system:
        :param external_system_session:
        :param stop_after:
        :param gnmi_obj:
        :param script:
        :return:
        """
        status = False
        result = None
        execute = False
        child = None
        cmd = binary + cmd_string
        testcase_Utils.pNote("********** Command to be Executed ********** \n {0}".format(cmd))
        if external_system == None:
            child = pexpect.spawn(cmd)
            child.maxread = 50000
        else:
            session_id = data_Utils.get_session_id(external_system, external_system_session)
            child = data_Utils.get_object_from_datarepository(session_id)
            child.sendline(cmd)
        if script.lower() == "no":
            credentials = {"username.*": uname, "password.*": passwd}
            for response, value in credentials.iteritems():
                index = child.expect([response, ".*error.*", pexpect.EOF, pexpect.TIMEOUT],
                                     timeout=5)
                if index == 0:
                    child.sendline(value)
                    testcase_Utils.pNote(child.match.group(0) + value)
                    execute = True
                    status = True
                else:
                    execute = False
                    break
        if execute or script.lower() == "yes":
            if stop_after == None and "poll" not in cmd_string.lower() \
                                  and "stream" not in cmd_string.lower():
                j_index = child.expect([prompt, pexpect.EOF, pexpect.TIMEOUT], timeout=50)
                if j_index == 1 or j_index == 0:
                    if "client had error while displaying results" not in child.before and \
                            "could not create a gNMI client" not in child.before:
                        if j_index == 1:
                            sleep(5)
                            result = child.before
                            testcase_Utils.pNote(result)
                            #self.ju.pretty_print_json(result)
                        else:
                            result = child.after
                            testcase_Utils.pNote(result)
                        status = True
                    else:
                        status = False
                        result = child.before
                        testcase_Utils.pNote(child.before, "error")
            if stop_after: #For polling or streaming
                testcase_Utils.pNote("Will Kill the process after {}sec".format(stop_after))
                child.sendcontrol('C')
                try:
                    child.expect([pexpect.EOF, prompt], timeout=int(stop_after))
                except:
                    testcase_Utils.pNote("Sending Ctrl+Z")
                if "client had error while displaying results" not in child.before:
                    result = child.before.strip().strip("^Z")
                    testcase_Utils.pNote(result)
                status = True
        return status, result, child

    def verify(self, json_object, search_list):
        """
        Verify gnmi output JSON
        :param json_object:
        :param search_list:
        :return: True or False
        """
        status = True
        json_str = ""
        if isinstance(json_object, dict):
            json_str = json.dumps(json_object)
        else:
            json_str = json_object
        for search_pattern in [x.strip() for x in search_list.split(',')]:
            if re.search(search_pattern, json_str, re.DOTALL):
                status = status and True
                testcase_Utils.pNote("{} is Present in Output JSON".format(search_pattern))
            else:
                status = status and False
                testcase_Utils.pNote("{} is Not Present in Output JSON".format(search_pattern))
        return status

    def close(self, system_name=None, external_system=None, external_system_session=None):
        """
        close the gnmi streaming or polling
        :param system_name:
        :param external_system:
        :param external_system_session:
        :return:
        """
        status = False
        if system_name:
            __gnmi_obj = data_Utils.get_object_from_datarepository(str(system_name)+"_gnmi_session")
            if __gnmi_obj:
                gnmi_obj = __gnmi_obj
            else:
                gnmi_obj = None
        else:
            session_id = data_Utils.get_session_id(external_system, external_system_session)
            gnmi_obj = data_Utils.get_object_from_datarepository(session_id)
        gnmi_obj.sendcontrol('C')
        try:
            gnmi_obj.expect([pexpect.EOF, '.*(%|#|\$)'], timeout=2)
        except:
            testcase_Utils.pNote("Sending Ctrl+C")
        if "client had error while displaying results" not in gnmi_obj.before:
            if system_name:
                result = gnmi_obj.before.strip().strip("^C")
                testcase_Utils.pNote(result)
            else:
                result = gnmi_obj.after.strip().strip("^C")
                testcase_Utils.pNote(result)
            status = True
        return status, result

    def get_cmd_string(self, ip, gnmi_port, ca_crt, client_crt_path, client_key, q_query, option=None,
                       get=None, qt_querytype=None, polling_interval="30s", timestamp="",
                       streaming_duration="0s", user_arg="",
                       venv=None, operation=None, username=None, password=None):
        """
        Get the command string for gnmi operation
        :param binary:
        :param ip:
        :param gnmi_port:
        :param ca_crt:
        :param q_query:
        :param qt_querytype:
        :param polling_interval:
        :param timestamp:
        :param streaming_duration:
        :param user_arg:
        :param venv:
        :param operation:
        :param username:
        :param password:
        :return:
        """
        cmd_string = None
        
        if option != "proto" and qt_querytype:
            if qt_querytype == "once":
                cmd_string = " --address {}:{} --ca_crt {} --client_crt {} --client_key {}" \
                             " --{} {} -qt={} -with_user_pass --timestamp {} {}".format(ip,
                                                                                       gnmi_port,
                                                                                       ca_crt,
                                                                                       client_crt_path,
                                                                                       client_key, option,
                                                                                       q_query,
                                                                                       qt_querytype,
                                                                                       timestamp,
                                                                                       user_arg)
            elif qt_querytype == "polling":
                if polling_interval[-1] != "s":
                    polling_interval = polling_interval+'s'
                cmd_string = " --address {}:{} --ca_crt {} --client_crt {} --client_key {}" \
                             " --q {} -qt={} --polling_interval={}" \
                             " -with_user_pass --timestamp {} {}".format(ip, gnmi_port,
                                                                         ca_crt, client_crt_path,
                                                                         client_key, q_query,
                                                                         qt_querytype,
                                                                         polling_interval,
                                                                         timestamp, user_arg)
            elif qt_querytype == "streaming":
                if polling_interval[-1] != "s":
                    polling_interval = polling_interval+'s'
                if streaming_duration[-1] != "s":
                    streaming_duration = streaming_duration+'s'
                cmd_string = " --address {}:{} --ca_crt {} --client_crt {} --client_key {}" \
                             " --q {} -qt={} --polling_interval={} -with_user_pass" \
                             " --timestamp {} -streaming_duration {} {}".format(ip,
                                                                                gnmi_port, ca_crt,
                                                                                client_crt_path,
                                                                                client_key,q_query,
                                                                                qt_querytype,
                                                                                polling_interval,
                                                                                timestamp,
                                                                                streaming_duration,
                                                                                user_arg)
            else:
                testcase_Utils.pNote("The querytype do not match! qt_querytype"
                                     " must be one of: (once, polling, streaming)", "error")
        else:
            cmd_string = " --address {}:{} --ca_crt {} --client_crt {} --client_key {}" \
                         " --proto {}  -with_user_pass".format(ip, gnmi_port, ca_crt, 
                                                               client_crt_path, client_key,
                                                               q_query)
        if operation:
            if operation in "get":
                cmd_string = " --address {}:{} --ca_crt {} --client_crt {} --client_key {} --get" \
                             " --proto {} -with_user_pass --timestamp {} {}".format(ip, gnmi_port,
                                                                                    ca_crt,
                                                                                    client_crt_path,
                                                                                    client_key,
                                                                                    q_query,
                                                                                    timestamp,
                                                                                    user_arg)
            else:
                cmd_string = " --address {}:{} --ca_crt {} --client_crt {} --client_key {}" \
                             " --{} --proto {}  -with_user_pass".format(ip, gnmi_port,
                                                                        ca_crt, client_crt_path,
                                                                        client_key, operation,
                                                                        q_query)
        return cmd_string


    def build_gnmi_binary(self):
        """
        Build gnmi Binary
        """
        pass


