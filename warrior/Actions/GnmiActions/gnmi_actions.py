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
gRPC Network Management Interface (gNMI) defines gRPC-based protocol for the modification and
retrieval of configuration from a network element.
As well as the control and generation of telemetry streams from a network element
to a data collection system.
Warrior Keyword will support the gNMI Client Services.
gNMI Services:
1.	Capabilities:
Exchange gNMI version and model info (model name, version, organization)
2.	Get: (Subscribe once is Get)
Separation of config and state
3.	Set:
Delete /replace/update operations supported
4.	Subscribe
Once/Polling/Stream
"""

import os, re, sys
import Framework.Utils as Utils
from Framework.Utils import testcase_Utils, config_Utils, data_Utils, file_Utils
from Framework.Utils.print_Utils import print_info
from Framework.ClassUtils.gnmi_utils_class import gNMI
from time import sleep

class gnmiactions(object):
    """
    Class for gNMI Action Keywords
    """

    def __init__(self):
        """ Initializing logs,results and datafile paths """
        self.resultfile = Utils.config_Utils.resultfile
        self.datafile = Utils.config_Utils.datafile
        self.logsdir = Utils.config_Utils.logsdir
        self.filename = Utils.config_Utils.filename
        self.logfile = Utils.config_Utils.logfile
        self.tc_path = Utils.config_Utils.tc_path

 
    def gNMI_get(self, system_name, q_query, verify=None,
                 external_system=None, external_system_session=None, timestamp="''", user_arg=""):
        """
        When set, CLI will perform a Get request.
        """
        wdesc = "Executing gNMI Subscribe"
        testcase_Utils.pSubStep(wdesc)
        status = False
        result = None
        outputdict = {}
        gnmi_execute = gNMI()
        gnmi_param = ['ip', 'gNMI_port', 'username', 'password', 'prompt',
                      'ca_crt', 'client_crt', 'client_key']
        gnmi_param_dic = data_Utils.get_credentials(self.datafile,
                                                    system_name,
                                                    gnmi_param)
        __gnmi_obj = Utils.data_Utils.get_object_from_datarepository(str(system_name)+"_gnmi_session")
        if __gnmi_obj:
            gnmi_obj = __gnmi_obj
        else:
            gnmi_obj = None
        if external_system:
            ext_gnmi_param_dic = data_Utils.get_credentials(self.datafile,
                                                            external_system,
                                                            ['ca_crt', 'client_crt', 'client_key'])

        if external_system == None:
            ca_crt, client_crt, client_key = data_Utils.set_gnmi_cert_params(gnmi_param_dic)
        else:
            ca_crt, client_crt, client_key = data_Utils.set_gnmi_cert_params(ext_gnmi_param_dic)
 
        username = gnmi_param_dic.get('username')
        password = gnmi_param_dic.get('password')
        prompt = gnmi_param_dic.get('prompt')

        cmd_string = gnmi_execute.get_cmd_string(ip=gnmi_param_dic['ip'],
                                                 gNMI_port=gnmi_param_dic['gNMI_port'],
                                                 ca_crt=ca_crt,
                                                 client_crt_path=client_crt,
                                                 client_key=client_key,
                                                 get="get",
                                                 q_query=q_query,
                                                 timestamp=timestamp,
                                                 user_arg=user_arg)
        status, result, child = gnmi_execute.execute(cmd_string, username,
                                                     password, prompt, external_system,
                                                     external_system_session, gnmi_obj)
        if status and verify and result:
            status = gnmi_execute.verify(result, verify)

        outputdict = {'{}_gnmi_result'.format(system_name): result}
        return status, outputdict

    def gNMI_Subscribe(self, system_name, q_query, qt_querytype="once",
                       polling_interval="30s", stop_after=None, verify=None,
                       external_system=None, external_system_session=None,
                       streaming_duration="0s", timestamp="''", user_arg=""):
        """
        gNMI Subscribe Keyword Will perform get(subscribe once is get), Polling
        operation and store the output json in data dictionary.
        :param system_name: server System name as in data file, server where gNMI client
         will send out its request.
        :param q_query: query xpath as string e.g. "/system/services/sftp/sftp-server"
                        can have multiple query separated by ","
                         e.g. "/system/services/sftp/sftp-server,/interfaces/interface"
        :param qt_querytype: Tyep of query as string.
                            qt_querytype must be one of: once, polling or streaming.
                             (default "once")
        :param polling_interval: Interval at which to poll in seconds if polling
        is specified for query_type.(default 30s)
        :param stop_after: User can specify a time after that polling or streaming
        will be stopped. (default None)
        :param verify: user provided string to verify can provide multiple sting separated by ","
                       e.g. '"sftp-server-port": "2202", "sftp-server-enabled": "true"'.
                       Verify string also has regular expression support.
        :param external_system: External system name mentioned as in data file.
                                This is optional if user want to execute gNMI from a different
                                server other than the warrior framework host machine.
        :param external_system_session: External system system session.
        :param streaming_duration: Length of time to collect streaming queries (0 is infinite).
         (default 0s)
        :param timestamp:  Specify timestamp formatting in output.
                           One of (<empty string>, on, raw, <FORMAT>)
                           where <empty string> is disabled,
                           on is human readable,
                           raw is int64 nanos since epoch,
                           and <FORMAT> is according to golang time.Format(<FORMAT>)
        :param user_arg: Extra argument place for feature use
         if any new argument user wants to pass on.
        :return:  True or False and dictionary containing output string and gNMI session
        in case of streaming or polling
        """

        wdesc = "Executing gNMI Subscribe"
        testcase_Utils.pSubStep(wdesc)
        status = False
        result = None
        outputdict = {}
        gnmi_execute = gNMI()
        gnmi_param = ['ip', 'gNMI_port', 'username', 'password', 'prompt',
                      'ca_crt', 'client_crt', 'client_key']
        gnmi_param_dic = data_Utils.get_credentials(self.datafile,
                                                    system_name,
                                                    gnmi_param)
        __gnmi_obj = Utils.data_Utils.get_object_from_datarepository(str(system_name)+"_gnmi_session")
        if __gnmi_obj:
            gnmi_obj = __gnmi_obj
        else:
            gnmi_obj = None
        if external_system:
            ext_gnmi_param_dic = data_Utils.get_credentials(self.datafile,
                                                            external_system,
                                                            ['ca_crt', 'client_crt', 'client_key'])

        if external_system == None:
            ca_crt, client_crt, client_key = data_Utils.set_gnmi_cert_params(gnmi_param_dic)
        else:
            ca_crt, client_crt, client_key = data_Utils.set_gnmi_cert_params(ext_gnmi_param_dic)
 
        username = gnmi_param_dic.get('username')
        password = gnmi_param_dic.get('password')
        prompt = gnmi_param_dic.get('prompt')

        cmd_string = gnmi_execute.get_cmd_string(ip=gnmi_param_dic['ip'],
                                                 gNMI_port=gnmi_param_dic['gNMI_port'],
                                                 ca_crt=ca_crt,
                                                 client_crt_path=client_crt,
                                                 client_key=client_key,
                                                 qt_querytype=qt_querytype,
                                                 q_query=q_query,
                                                 polling_interval=polling_interval,
                                                 timestamp=timestamp,
                                                 streaming_duration=streaming_duration,
                                                 user_arg=user_arg)
        status, result, child = gnmi_execute.execute(cmd_string, username,
                                                      password, prompt, external_system,
                                                      external_system_session, stop_after, gnmi_obj)
        if status and verify and result:
            status = gnmi_execute.verify(result, verify)

        if external_system or qt_querytype not in ['polling', 'streaming']:
            outputdict = {'{}_gnmi_result'.format(system_name): result}
        else:
            outputdict = {'{}_gnmi_result'.format(system_name): result,
                         '{}_gnmi_session'.format(system_name):child}
        return status, outputdict

    def gNMI_Subscribe_close(self, system_name=None, external_system=None,
                             external_system_session=None, verify=None):
        """
        For Polling and Streaming this keyword will close/kill the process
        :param system_name: server System name as in data file, server where
         gNMI client will send out its request.
        :param external_system: External system name mentioned as in data file.
                                This is optional if user want to execute gNMI from a different
                                server other than the warrior framework host machine.
        :param external_system_session: External system system session.
        :param verify: user provided string to verify can provide multiple sting separated by ","
                       e.g. '"sftp-server-port": "2202", "sftp-server-enabled": "true"'.
                       Verify string also has regular expression support.
        :return: True or False and dictionary containing output string
        """
        wdesc = "For Polling and Streaming this keyword will close/kill the process"
        testcase_Utils.pSubStep(wdesc)
        status = False
        outputdict = {}
        gnmi_execute = gNMI()
        status, result = gnmi_execute.close(system_name, external_system, external_system_session)
        if status and verify:
            status = gnmi_execute.verify(result, verify)
        outputdict = {'{}_gnmi_result'.format(system_name): result}
        return status, outputdict

    def gNMI_Set(self, system_name, q_query, operation="set",
                 verify=None,
                 external_system=None, external_system_session=None, script="No"):
        """
        will perform set operation(types: delete/replace/update) and store
         the output JSON in a data dictionary
        :param system_name: server System name as in data file, server where gNMI client will
        send out its request.
        :param q_query: query xpath as string
        e.g. "/system/services/sftp/sftp-server[sftp-server-port=2202]"
        :param operation: Type of set operation.
        operation must be one of: (update, replace, delete). default update
        :param verify: user provided string to verify can provide multiple sting separated by ","
                       e.g. '"sftp-server-port": "2202", "sftp-server-enabled": "true"'.
                       Verify string also has regular expression support.
        :param external_system_session: External system system session.
        :param verify: user provided string to verify can provide multiple sting separated by ","
                       e.g. '"sftp-server-port": "2202", "sftp-server-enabled": "true"'.
                       Verify string also has regular expression support.
        :param script: This argument is temporary as long as gNMI cli binary
         is not equipped with set operation,
                       user need to pass "Yes/yes/No/no". (default is "No")

        :return: True or False and dictionary containing output string
        """

        wdesc = "Executing gNMI Set Keyword"
        testcase_Utils.pSubStep(wdesc)
        status = False
        result = None
        outputdict = {}
        gnmi_execute = gNMI()
        gnmi_param = ['ip', 'gNMI_port', 'username',
                      'password', 'prompt', 'ca_crt', 'client_crt', 'client_key']
        gnmi_param_dic = data_Utils.get_credentials(self.datafile,
                                                    system_name,
                                                    gnmi_param)
        __gnmi_obj = Utils.data_Utils.get_object_from_datarepository(str(system_name)+
                                                                     "_gnmi_session")
        if __gnmi_obj:
            gnmi_obj = __gnmi_obj
        else:
            gnmi_obj = None
        if external_system:
            ext_gnmi_param_dic = data_Utils.get_credentials(self.datafile,
                                                            external_system,
                                                            ['ca_crt', 'client_crt', 'client_key'])

        if external_system == None:
            ca_crt, client_crt, client_key = data_Utils.set_gnmi_cert_params(gnmi_param_dic)
        else:
            ca_crt, client_crt, client_key = data_Utils.set_gnmi_cert_params(ext_gnmi_param_dic)
 
        username = gnmi_param_dic.get('username')
        password = gnmi_param_dic.get('password')
        prompt = gnmi_param_dic.get('prompt')

        cmd_string = gnmi_execute.get_cmd_string(ip=gnmi_param_dic['ip'],
                                                 gNMI_port=gnmi_param_dic['gNMI_port'],
                                                 username=username, password=password,
                                                 ca_crt=ca_crt,
                                                 client_crt_path=client_crt,
                                                 operation=operation,
                                                 client_key=client_key,
                                                 q_query=q_query)
        if cmd_string:
            status, result, child = gnmi_execute.execute(cmd_string, username,
                                                         password, prompt, external_system,
                                                         external_system_session, None,
                                                         gnmi_obj)
        if status and verify:
            status = gnmi_execute.verify(result, verify)
        outputdict = {'{}_gnmi_result'.format(system_name): result}
        return status, outputdict
