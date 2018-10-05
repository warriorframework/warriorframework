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
gRPC Network Management Interface (gnmi) defines gRPC-based protocol for the modification and
retrieval of configuration from a network element.
As well as the control and generation of telemetry streams from a network element
to a data collection system.
Warrior Keyword will support the gnmi Client Services.
gnmi Services:
1.	Capabilities:
Exchange gnmi version and model info (model name, version, organization)
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
from Framework.ClassUtils.gnmi_utils_class import gnmi
from time import sleep

class gnmiactions(object):
    """
    Class for gnmi Action Keywords
    """

    def __init__(self):
        """ Initializing logs,results and datafile paths """
        self.resultfile = Utils.config_Utils.resultfile
        self.datafile = Utils.config_Utils.datafile
        self.logsdir = Utils.config_Utils.logsdir
        self.filename = Utils.config_Utils.filename
        self.logfile = Utils.config_Utils.logfile
        self.tc_path = Utils.config_Utils.tc_path

    def gnmi_subscribe(self, system_name, option, q_query, qt_querytype="once",
                       polling_interval="30s", stop_after=None, verify=None,
                       external_system=None, external_system_session=None,
                       streaming_duration="0s", timestamp="''", user_arg=""):
        """
        gnmi Subscribe Keyword Will perform get(subscribe once is get), Polling
        operation and store the output json in data dictionary.
        :param system_name: server System name as in data file, server where gnmi client
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
                                This is optional if user want to execute gnmi from a different
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
        :return:  True or False and dictionary containing output string and gnmi session
        in case of streaming or polling
        """

        wdesc = "Executing gnmi Subscribe"
        testcase_Utils.pSubStep(wdesc)
        status = False
        result = None
        outputdict = {}
        gnmi_execute = gnmi()
        gnmi_param = ['ip', 'gnmi_port', 'username', 'password', 'prompt',
                      'ca_crt', 'client_crt', 'client_key']
        gnmi_param_dic = data_Utils.get_credentials(self.datafile,
                                                    system_name,
                                                    gnmi_param)
        __gnmi_obj = Utils.data_Utils.get_object_from_datarepository(str(system_name)+"_gnmi_session")
        file_dir = os.path.dirname(os.path.abspath(__file__))
        war_dir = os.path.abspath(os.path.join(file_dir, '../..'))
        binary = os.path.join(war_dir, 'Framework/Gnmi/gnmi_cli')
        
        testcase_Utils.pNote("***** Binary path: {0} *****".format(binary))
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
                                                 gnmi_port=gnmi_param_dic['gnmi_port'],
                                                 ca_crt=ca_crt,
                                                 client_crt_path=client_crt,
                                                 client_key=client_key,
                                                 option=option,
                                                 qt_querytype=qt_querytype,
                                                 q_query=q_query,
                                                 polling_interval=polling_interval,
                                                 timestamp=timestamp,
                                                 streaming_duration=streaming_duration,
                                                 user_arg=user_arg)
        status, result, child = gnmi_execute.execute(binary, cmd_string, username,
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

    def gnmi_subscribe_close(self, system_name=None, external_system=None,
                             external_system_session=None, verify=None):
        """
        For Polling and Streaming this keyword will close/kill the process
        :param system_name: server System name as in data file, server where
         gnmi client will send out its request.
        :param external_system: External system name mentioned as in data file.
                                This is optional if user want to execute gnmi from a different
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
        gnmi_execute = gnmi()
        status, result = gnmi_execute.close(system_name, external_system, external_system_session)
        if status and verify:
            status = gnmi_execute.verify(result, verify)
        outputdict = {'{}_gnmi_result'.format(system_name): result}
        return status, outputdict

    def gnmi_operations(self, system_name, q_query, operation, verify=None,
                        external_system=None, external_system_session=None, 
                        timestamp="''", user_arg=""):
        """
        will perform the following operations:
        1. Get
        2. Set operation(types: delete/replace/update)
        3. Capabilities
        and store the output JSON in a data dictionary.
        :param system_name: server System name as in data file, server where gnmi client will
        send out its request.
        :param q_query: query xpath as string
        e.g. "/system/services/sftp/sftp-server[sftp-server-port=2202]"
        :param operation: Type of operation(get/set/capabilities).
        :param verify: user provided string to verify can provide multiple sting separated by ","
                       e.g. '"sftp-server-port": "2202", "sftp-server-enabled": "true"'.
                       Verify string also has regular expression support.
        :param external_system_session: External system system session.
                       e.g. '"sftp-server-port": "2202", "sftp-server-enabled": "true"'.
                       Verify string also has regular expression support.
        :param timestamp:  Specify timestamp formatting in output.
                           One of (<empty string>, on, raw, <FORMAT>)
                           where <empty string> is disabled,
                           on is human readable,
                           raw is int64 nanos since epoch,
                           and <FORMAT> is according to golang time.Format(<FORMAT>)
        :param user_arg: Extra argument place for feature use
                         if any new argument user wants to pass on.
        :return: True or False and dictionary containing output string
        """

        wdesc = "***** Executing gnmi " + operation + " operation *****"
        testcase_Utils.pSubStep(wdesc)
        status = False
        result = None
        outputdict = {}
        gnmi_execute = gnmi()
        gnmi_param = ['ip', 'gnmi_port', 'username',
                      'password', 'prompt', 'ca_crt', 'client_crt', 'client_key']
        gnmi_param_dic = data_Utils.get_credentials(self.datafile,
                                                    system_name,
                                                    gnmi_param)
        __gnmi_obj = Utils.data_Utils.get_object_from_datarepository(str(system_name)+
                                                                     "_gnmi_session")
        file_dir = os.path.dirname(os.path.abspath(__file__))
        war_dir = os.path.abspath(os.path.join(file_dir, '../..'))
        binary = os.path.join(war_dir, 'Framework/Gnmi/gnmi_cli')
        testcase_Utils.pNote("***** Binary path: {0} *****".format(binary))
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

        if operation in "get":
            cmd_string = gnmi_execute.get_cmd_string(ip=gnmi_param_dic['ip'],
                                                     gnmi_port=gnmi_param_dic['gnmi_port'],
                                                     username=username, password=password,
                                                     ca_crt=ca_crt,
                                                     client_crt_path=client_crt,
                                                     client_key=client_key,
                                                     operation=operation, q_query=q_query,
                                                     timestamp=timestamp, user_arg=user_arg)
        else:
            cmd_string = gnmi_execute.get_cmd_string(ip=gnmi_param_dic['ip'],
                                                     gnmi_port=gnmi_param_dic['gnmi_port'],
                                                     username=username, password=password,
                                                     ca_crt=ca_crt,
                                                     client_crt_path=client_crt,
                                                     client_key=client_key,
                                                     operation=operation, q_query=q_query)
        print_info("** {0} Operation in progress **".format(operation))
        if cmd_string:
            status, result, child = gnmi_execute.execute(binary, cmd_string, username,
                                                         password, prompt, external_system,
                                                         external_system_session, None,
                                                         gnmi_obj)
        if status and verify:
            status = gnmi_execute.verify(result, verify)
        outputdict = {'{}_gnmi_result'.format(system_name): result}
        return status, outputdict
