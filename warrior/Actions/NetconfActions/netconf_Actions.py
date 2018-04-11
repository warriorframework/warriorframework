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
"""This is the netconf_actions module that has all netconf related keywords
ymizugaki 2017/07/11
"""

import time
from xml.dom.minidom import parseString
import Framework.Utils as Utils
from Framework.Utils.testcase_Utils import pNote, pSubStep, report_substep_status
from Framework.ClassUtils.netconf_utils_class import WNetConf
from Framework.Utils.encryption_utils import decrypt

class NetconfActions(object):
    """NetconfActions class which has methods(keywords)
    related to actions performed on basic netconf interface """

    def __init__(self):
        """ Constructor for NetconfActions class """
        self.resultfile = Utils.config_Utils.resultfile
        self.datafile = Utils.config_Utils.datafile
        self.logsdir = Utils.config_Utils.logsdir
        self.filename = Utils.config_Utils.filename
        self.logfile = Utils.config_Utils.logfile
        self.netconf_object = WNetConf()

    def request_rpc(self, system_name, session_name=None, request="",
                    xmlns="", request_type="", xmlns_tag="xmlns"):

        """ Request operations through Netconf interface.
        If value for 'request' is provided, it will be used for request
        operations else the XML input will be taken from the netconf_data
        file based on xmlns, request_type, xmlns_tag values.
        :Arguments:
            1. system_name(string) = Name of the system from the input datafile
            2. session_name(string) = Name of the session to the system
            3. request(string) = command to be sent as xml string
            4. xmlns(string) = XML namespace of the particular request
            5. Request_type(string) = The operation that we want to perform
            6. xmlns_tag(string) = xml tag for the particular request
            for eg:
            For request Type:
                <init-pm xmlns="urn:params:xml:ns:yang:perfmon">
            usage:
                xmlns_tag = xmlns(default value, no need pass this argument)
                xmlns = "urn:params:xml:ns:yang:perfmon"
                request_type= "init-pm"

            For Request Type :
            <org-openroadm-de-operations:restart xmlns:
             org-openroadm-de-operations="http://org/openroadm/de/operations">
            usage:
                xmlns_tag = "xmlns:org-openroadm-de-operations"
                xmlns = "http://org/openroadm/de/operations"
                request_type = "org-openroadm-de-operations:restart"
        :Returns:
            1. status = True/False/error
            2. RPC replies in a list & it will be updated in the data
               repository in key - [system_name]_request_rpc_reply.
        """

        wdesc = "Request particular operation from the system"
        pSubStep(wdesc)

        reply_key = '{}_request_rpc_reply'.format(system_name)
        reply_list = []
        pNote(system_name)
        pNote(self.datafile)
        self.clear_notification_buffer_all(system_name, session_name)
        session_id = Utils.data_Utils.get_session_id(system_name, session_name)
        netconf_object = Utils.data_Utils.\
            get_object_from_datarepository(session_id)
        config_data_list = []
        status = True

        if request:
            config_data_list = [request]
        elif all([xmlns != "", request_type != "", xmlns_tag != ""]):
            config_datafile = Utils.data_Utils.\
                get_filepath_from_system(self.datafile, system_name,
                                         'netconf_data')[0]
            if config_datafile and Utils.file_Utils.\
               fileExists(config_datafile):
                status, config_data_list = Utils.data_Utils.\
                    get_nc_request_rpc_string(config_datafile, xmlns,
                                              request_type, xmlns_tag)
            else:
                status = "error"
                pNote("Datafile does not have any value for netconf_data tag "
                      "or the filepath mentioned in the netconf_data tag "
                      "does not exist", 'error')
        else:
            status = "error"
            pNote("Please provide value(s) for 'request' or 'xmlns &"
                  " request_type'", 'error')
        if status is True and config_data_list:
            list_config_data = []
            if not isinstance(config_data_list, list):
                list_config_data.append(config_data_list)
            else:
                list_config_data = config_data_list
            for config_data in list_config_data:
                if config_data:
                    reply = netconf_object.request_rpc(config_data)
                    reply_list.append(reply)
                    pNote('Request RPC Reply= {}'.format(reply))
                    if netconf_object.isCOMPLD:
                        sub_status = True
                    else:
                        pNote('Request RPC Failed {}'.format(
                         netconf_object.ErrorMessage), "error")
                        sub_status = False
                else:
                    reply_list.append("error")
                    pNote('Request RPC Failed', "error")
                    sub_status = "error"
                status = status and sub_status if sub_status != "error" \
                    else sub_status

        report_substep_status(status)
        return status, {reply_key: reply_list}

    def connect_netconf(self, system_name, session_name=None):
        """
        Connects to the Netconf interface of the the given system or subsystems

        :Datafile usage:

            Tags or attributes to be used in input datafile for the system or subsystem
            If both tag and attribute is provided the attribute will be used.
            1. ip = IP address of the system/subsystem
            2. nc_port = use this tag to provide ssh port to connect to Netconf \
               interface, if not provided default port 830 will be used.
            3. username = username for the ssh session
            4. password = password for the ssh session
            5. hostkey_verify = enables hostkey verification from ~/.ssh/known_hosts,\
               if not provided the default value is to look into the path ~/.ssh/known_hosts.
            6. protocol_version = netconf protocol version (1.0 or 1.1)
            *** belows are not used, will be ignored. ***
            7. timeout = use if you want to set timeout while connecting
            8. allow_agent = enables querying SSH agent, if not provided the \
               default value is to allow.
            9. look_for_keys = enables looking in the usual locations for ssh keys,\
               if value is not provided the default value is to look for keys.
           10. unknown_host_cb = This would be used when the server host key is not \
               recognized.
           11. key_filename = where the private key can be found.
           12. ssh_config = Enables parsing of OpenSSH configuration file.
           13. device_params = netconf client device name, by default the name \
               "default" is used.

        :Arguments:
            1. system_name(string) = Name of the system from the input datafile.
            2. session_name(string) = Name of the session to the system

        :Returns:
            1. status(bool)= True / False
            2. session_id (dict element)= key, value


        :DESCRIPTION:
            This Keyword is used to connect to the netconf interface of the system.
            The keyword upon executing saves the System_name and Session_id,
            which can be used by all subsequent keywords in the test
            to interact with the system through netconf interface.
        """
        wdesc = "Connect to the netconf port of the system and creates a session"
        pSubStep(wdesc)
        output_dict = {}
        session_parameters = ['ip', 'nc_port', 'username', 'password',
                              'hostkey_verify', 'protocol_version']
        session_credentials = Utils.data_Utils.get_credentials(self.datafile,
                                                               system_name,
                                                               session_parameters)
        session_credentials["password"] = decrypt(session_credentials["password"])
        pNote(system_name)
        pNote(Utils.file_Utils.getDateTime())
        session_id = Utils.data_Utils.get_session_id(system_name, session_name)
        status = self.netconf_object.open(session_credentials)

        time.sleep(1)
        if status:
            temp = self.netconf_object.session_id
            if temp is None:
                status = False
            else:
                output_dict["netconf_session_id"] = self.netconf_object.session_id
                pNote("netconf session-id = %s" % self.netconf_object.session_id)
                output_dict[session_id] = self.netconf_object
        report_substep_status(status)
        if output_dict:
            return status, output_dict
        else:
            return status

    def close_netconf(self, system_name, session_name=None):
        """
        Request graceful termination of netconf session.
        :Arguments:
            1. system_name(string)  = Name of the system in the input datafile
            2. session_name(string) = Name of the session to the system
        :Returns:
            1. status(bool)= True / False
            2. Close response from the system to the data repository (data:reply.data(string)}
        """

        wdesc = "Request graceful termination of Netconf session"
        pSubStep(wdesc)
        pNote(system_name)
        pNote(self.datafile)

        session_id = Utils.data_Utils.get_session_id(system_name, session_name)
        netconf_object = Utils.data_Utils.get_object_from_datarepository(
            session_id)
        netconf_session_id = Utils.data_Utils.get_object_from_datarepository(
            "netconf_session_id")
        pNote("close session-id=%s" % netconf_session_id)
        reply = netconf_object.close()
        if reply:
            reply = parseString(reply).toprettyxml(
                indent="  ", encoding="UTF-8")
        pNote('close-session: Reply= {}'.format(reply))
        if netconf_object.isCOMPLD:
            status = True
        else:
            status = False
            pNote('Close Netconf Failed {}'.format(
                netconf_object.ErrorMessage), "error")

        report_substep_status(status)
        reply_key = '{}_close_netconf_reply'.format(system_name)
        return status, {reply_key: reply}

    def get_config(self, datastore, system_name,
                   session_name=None,
                   filter_string=None,
                   filter_type="subtree"):
        """ Retrieve all or part of a specified configuration through Netconf interface.
        :Arguments:
            1. datastore(string) = Name of the netconf datastore.
            2. system_name(string)  = Name of the system from the input datafile.
            3. session_name(string) = Name of the session to the system.
            4. filter_string(string) = xml string, by default entire configuration is \
	       retrieved.
            5. filter_type(string) = Type of the Filter , subtree or xpath, default is subtree.
        :Returns:
            1. status(bool)= True / False
            2. Get Response in the data repository {data:reply(xml)}
        """

        wdesc = "Get system configuration data from the provided system"
        pSubStep(wdesc)
        pNote(system_name)
        pNote(self.datafile)

        self.clear_notification_buffer_all(system_name, session_name)
        session_id = Utils.data_Utils.get_session_id(system_name, session_name)
        netconf_object = Utils.data_Utils.get_object_from_datarepository(
            session_id)
        reply = netconf_object.get_config(
            datastore, filter_string, filter_type)
        if reply:
            reply = parseString(reply).toprettyxml(
                indent="  ", encoding="UTF-8")
        pNote('get-config: Reply= {}'.format(reply))
        if netconf_object.isCOMPLD:
            status = True
        else:
            pNote("get-config: Failed {}".format(netconf_object.ErrorMessage))
            status = False
        report_substep_status(status)
        reply_key = '{}_get_config_reply'.format(system_name)
        return status, {reply_key: reply}

    def copy_config(self, source, target, system_name, session_name=None):

        """Create or replace an entire configuration datastore
            with the contents of another complete configuation datastore
        :Arguments:
            1. source(string) = name of the configuration datastore to use as the source of
                the copy operation or config element containing the configuration subtree to copy.
            2. target(string) = name of the configuration datastore to use as the destination
                of the copy operation
            3. system_name(string)  = Name of the system from the input datafile
            4. session_name(string) = Name of the session to the system
        :Returns:
            1. status(bool)= True / False
            2. Copy Response in the data repository {data:reply(xml)}
        """
        wdesc = "Create or replace an entire configuration datastore with another datastore"
        pSubStep(wdesc)
        pNote(system_name)
        pNote(self.datafile)

        self.clear_notification_buffer_all(system_name, session_name)
        session_id = Utils.data_Utils.get_session_id(system_name, session_name)
        netconf_object = Utils.data_Utils.get_object_from_datarepository(
            session_id)
        reply = netconf_object.copy_config(source, target)
        if reply:
            reply = parseString(reply).toprettyxml(
                indent="  ", encoding="UTF-8")
        pNote('copy-config: Reply= {}'.format(reply))
        if netconf_object.isCOMPLD:
            status = True
        else:
            status = False
            pNote('copy-config: Failed {}'.format(netconf_object.ErrorMessage), "error")
        report_substep_status(status)
        reply_key = '{}_copy_config_reply'.format(system_name)
        return status, {reply_key: reply}

    def delete_config(self, datastore, system_name, session_name=None):
        """Delete a configuration datastore

        :Arguments:
            1. datastore(string) = name of the configuration datastore to be deleted
            2. system_name(string)  = Name of the system from the input datafile
            3. session_name(string) = Name of the session to the system
        :Returns:
            1. status(bool)= True / False
            2. Delete Response in the data repository {data:reply(xml)}
         """
        wdesc = "Delete system configuration data from the provided system"
        pSubStep(wdesc)
        pNote(system_name)
        pNote(self.datafile)

        self.clear_notification_buffer_all(system_name, session_name)
        session_id = Utils.data_Utils.get_session_id(system_name, session_name)
        netconf_object = Utils.data_Utils.get_object_from_datarepository(
            session_id)
        reply = netconf_object.delete_config(datastore)
        if reply:
            reply = parseString(reply).toprettyxml(
                indent="  ", encoding="UTF-8")
        pNote('delete-config: Reply= {}'.format(reply))
        if netconf_object.isCOMPLD:
            status = True
        else:
            pNote('delete-config: Failed {}'.format(netconf_object.ErrorMessage), "error")
            status = False
        report_substep_status(status)
        reply_key = '{}_delete_config_reply'.format(system_name)
        return status, {reply_key: reply}

    def discard_changes(self, system_name, session_name=None):
        """Revert the candidate configuration to the currently running configuration.
        Uncommitted changes will be discarded.

        :Arguments:
            1. system_name(string)  = Name of the system from the input datafile
            2. session_name(string) = Name of the session to the system
        :Returns:
            1. status(bool)= True / False
            2. Discard Response in the data repository {data:reply(xml)}
         """
        wdesc = "Discard any uncommitted changes to the candidate configuration"
        pSubStep(wdesc)
        pNote(system_name)
        pNote(self.datafile)

        self.clear_notification_buffer_all(system_name, session_name)
        session_id = Utils.data_Utils.get_session_id(system_name, session_name)
        netconf_object = Utils.data_Utils.get_object_from_datarepository(
            session_id)
        reply = netconf_object.discard_changes()
        if reply:
            reply = parseString(reply).toprettyxml(
                indent="  ", encoding="UTF-8")
        pNote('discard-changes: Reply= {}'.format(reply))
        if netconf_object.isCOMPLD:
            status = True
        else:
            pNote(
                'discard-changes: Failed {}'.format(netconf_object.ErrorMessage), "error")
            status = False
        report_substep_status(status)
        reply_key = '{}_discard_changes_reply'.format(system_name)
        return status, {reply_key: reply}

    def edit_config(self, datastore, config, system_name,
                    session_name=None, default_operation=None, test_option=None, error_option=None):
        """ Loads all or part of the specified config(from file) to the datastore
        :Arguments:
            1. datastore(string) = Name of datastore being edited
            2. config(string) = The configuration.
                Must be rooted in the config element. May be a string or Element
            3. system_name(string)  = Name of the system from the input datafile
            4. session_name(string) = Name of the session to the system
            5. default_operation(string) = [merge | replace | none (default)]
            6. test_option(string) = [test-then-set | set | test-only | none (default)]
            7. error_option(string) =
               [stop-on-error | continue-on-error | rollback-on-error | none (default)]
               rollback-on-error depends on :rollback-on-error capability
        :Returns:
            1. status(bool)= True / False
            2. Edit Responses in the data repository {data:reply(xml)}
         """
        wdesc = "Edit system configuration data"
        pSubStep(wdesc)
        pNote(system_name)
        pNote(self.datafile)
        reply_key = '{}_edit_config_reply'.format(system_name)
        reply_list = []
        status = True
        self.clear_notification_buffer_all(system_name, session_name)
        session_id = Utils.data_Utils.get_session_id(system_name, session_name)
        netconf_object = Utils.data_Utils.get_object_from_datarepository(
            session_id)
        data_parameters = ['netconf_data']
        config_datafile = Utils.data_Utils.get_filepath_from_system(self.datafile, system_name, 'netconf_data')[0]
        var_configfile = Utils.data_Utils.get_filepath_from_system(self.datafile, system_name, 'variable_config')
        if len(var_configfile) > 0:
            var_configfile = var_configfile[0]
        else:
            var_configfile = None

        if Utils.file_Utils.fileExists(config_datafile):
            status, config_data_list = Utils.data_Utils.get_nc_config_string(config_datafile, config, var_configfile)
        else:
            config_data_list = []
            status = "error"
        if config_data_list:
            for config_data in config_data_list:
                if config_data:
                    reply = netconf_object.edit_config(datastore, config_data,
                                                       default_operation=default_operation,
                                                       test_option=test_option,
                                                       error_option=error_option)
                    reply_list.append(reply)
                    if netconf_object.isCOMPLD:
                        status = status and True if status != "error" else status
                    else:
                        pNote('Edit Config Failed {}'.format(netconf_object.ErrorMessage), "error")
                        status = status and False if status != "error" else status
                        break
                else:
                    reply = "error"
                    pNote('Edit Config Failed', "error")
                    status = status and False
        pNote('Edit Config Reply= {}'.format(reply_list))

        report_substep_status(status)
        return status, {reply_key: reply_list}

    def commit(self, system_name,
               confirmed=False, timeout=None, persist=None, persist_id=None, session_name=None):
        """Commit the candidate datastore as the device's new current configuration
        :Arguments:
            1. system_name(string)  = Name of the system from the input datafile
            2. confirmed(bool) = Commit is reverted if there is no followup commit
                within the timeout interval.
            3. timeout(int seconds) = The confirm timeout (Default=600 seconds)
            4. persist(string) = persist-id
            5. persist_id(string) = persist-id which specified in previous confirmed commit
            6. session_name(string) = Name of the session to the system
        :Returns:
            1. status(bool)= True / False
            2. Commit Response in the data repository {data:reply(xml)}
         """
        wdesc = "Commit the candidate datastore"
        pSubStep(wdesc)
        pNote(system_name)
        pNote(self.datafile)

        self.clear_notification_buffer_all(system_name, session_name)
        session_id = Utils.data_Utils.get_session_id(system_name, session_name)
        netconf_object = Utils.data_Utils.get_object_from_datarepository(
            session_id)
        reply = netconf_object.commit(confirmed, timeout, persist, persist_id)
        if reply:
            reply = parseString(reply).toprettyxml(
                indent="  ", encoding="UTF-8")
        pNote('commit: Reply= {}'.format(reply))
        if netconf_object.isCOMPLD:
            status = True
        else:
            pNote('commit: Failed {}'.format(
                netconf_object.ErrorMessage), "error")
            status = False
        report_substep_status(status)
        reply_key = '{}_commit_reply'.format(system_name)
        return status, {reply_key: reply}

    def lock(self, datastore, system_name, session_name=None):
        """Lock the configuration system

        :Arguments:
            1. datastore(string) = name of the configuration datastore to be locked
            2. system_name(string)  = Name of the system from the input datafile
            3. session_name(string) = Name of the session to the system
        :Returns:
            1. status(bool)= True / False
            2. Lock Response in the data repository {data:reply(xml)}
         """
        wdesc = "Lock the configuration datastore"
        pSubStep(wdesc)
        pNote(system_name)
        pNote(self.datafile)

        self.clear_notification_buffer_all(system_name, session_name)
        session_id = Utils.data_Utils.get_session_id(system_name, session_name)
        netconf_object = Utils.data_Utils.get_object_from_datarepository(
            session_id)
        reply = netconf_object.lock(datastore)
        if reply:
            reply = parseString(reply).toprettyxml(
                indent="  ", encoding="UTF-8")
        pNote('lock: Reply= {}'.format(reply))
        if netconf_object.isCOMPLD:
            status = True
        else:
            pNote('lock: Failed {}'.format(
                netconf_object.ErrorMessage), "error")
            status = False
        report_substep_status(status)
        reply_key = '{}_lock_reply'.format(system_name)
        return status, {reply_key: reply}

    def unlock(self, datastore, system_name, session_name=None):
        """Release the configuration lock

        :Arguments:
            1. datastore(string) = name of the configuration datastore to be unlocked
            2. system_name(string)  = Name of the system from the input datafile
            3. session_name(string) = Name of the session to the system
        :Returns:
            1. status(bool)= True / False
            2. Unlock Response in the data repository {data:reply(xml)}
         """
        wdesc = "Unlock the configuration datastore"
        pSubStep(wdesc)
        pNote(system_name)
        pNote(self.datafile)

        self.clear_notification_buffer_all(system_name, session_name)
        session_id = Utils.data_Utils.get_session_id(system_name, session_name)
        netconf_object = Utils.data_Utils.get_object_from_datarepository(
            session_id)
        reply = netconf_object.unlock(datastore)
        if reply:
            reply = parseString(reply).toprettyxml(
                indent="  ", encoding="UTF-8")
        pNote('unlock: Reply= {}'.format(reply))
        if netconf_object.isCOMPLD:
            status = True
        else:
            pNote('unlock: Failed {}'.format(
                netconf_object.ErrorMessage), "error")
            status = False
        report_substep_status(status)
        reply_key = '{}_unlock_reply'.format(system_name)
        return status, {reply_key: reply}

    def get(self, system_name, session_name=None, filter_string=None, filter_type=None):
        """Retrieve operational state information.

        :Arguments:
            1. system_name(string)  = Name of the system from the input datafile
            2. session_name(string) = Name of the session to the system
            3. filter_string(string) = specifies the portion of the state information to retrieve
               (by default entire state information is retrieved)
            4. filter_type(string) = subtree or xpath
        :Returns:
            1. status(bool)= True / False
            2. Retrieve Response in the data repository {data:reply(xml)}
         """
        wdesc = "Retrieve operational state information (get rpc)."
        pSubStep(wdesc)
        pNote(system_name)
        pNote(self.datafile)

        self.clear_notification_buffer_all(system_name, session_name)
        session_id = Utils.data_Utils.get_session_id(system_name, session_name)
        netconf_object = Utils.data_Utils.get_object_from_datarepository(
            session_id)
        reply = netconf_object.get(filter_string, filter_type)
        if reply:
            reply = parseString(reply).toprettyxml(
                indent="  ", encoding="UTF-8")
        pNote('get: Reply= {}'.format(reply))
        if netconf_object.isCOMPLD:
            status = True
        else:
            pNote('get: Failed {}'.format(netconf_object.ErrorMessage), "error")
            status = False
        report_substep_status(status)
        reply_key = '{}_get_config_reply'.format(system_name)
        return status, {reply_key: reply}

    def kill_session(self, system_name, netconf_session_id=None, session_name=None):
        """Force the termination of a NETCONF session (not the current one!)
        :Arguments:
            1. system_name(string)  = Name of the system from the input datafile
            2. netconf_session_id(string) = session-id of netconf
            3. session_name(string) = Name of the session to the system
        :Returns:
            1. status(bool)= True / False
            2. Kill Response in the data repository {data:reply(xml)}
         """
        wdesc = "Force the termination of a NETCONF session (not the current one!)"
        pSubStep(wdesc)
        pNote(system_name)
        pNote(self.datafile)

        self.clear_notification_buffer_all(system_name, session_name)
        session_id = Utils.data_Utils.get_session_id(system_name, session_name)
        netconf_object = Utils.data_Utils.get_object_from_datarepository(
            session_id)
        if not netconf_session_id:
            netconf_session_id = "0"
        reply = netconf_object.kill_session(netconf_session_id)
        if reply:
            reply = parseString(reply).toprettyxml(
                indent="  ", encoding="UTF-8")
        pNote('kill-session: Reply= {}'.format(reply))
        if netconf_object.isCOMPLD:
            status = True
        else:
            pNote('kill-session: Failed {}'.format(netconf_object.ErrorMessage), "error")
            status = False
        report_substep_status(status)
        reply_key = '{}_kill_session_netconf_reply'.format(system_name)
        return status, {reply_key: reply}

    def validate(self, datastore, system_name, session_name=None):
        """"Validate the contents of the specified configuration.
        :Arguments:
            1. datastore(string) = Name of the configuration datastore to be validated
            2. system_name(string)  = Name of the system from the input datafile
            3. session_name(string) = Name of the session to the system
        :Returns:
            1. status(bool)= True / False
            2. Validation Response in the data repository {data:reply(xml)}
         """
        wdesc = "Validate the contents of the specified configuration."
        pSubStep(wdesc)
        pNote(system_name)
        pNote(self.datafile)

        self.clear_notification_buffer_all(system_name, session_name)
        session_id = Utils.data_Utils.get_session_id(system_name, session_name)
        netconf_object = Utils.data_Utils.get_object_from_datarepository(
            session_id)
        reply = netconf_object.validate(datastore)
        if reply:
            reply = parseString(reply).toprettyxml(
                indent="  ", encoding="UTF-8")
        pNote('validate: Reply= {}'.format(reply))
        if netconf_object.isCOMPLD:
            status = True
        else:
            pNote('validate: Failed {}'.format(
                netconf_object.ErrorMessage), "error")
            status = False

        report_substep_status(status)
        reply_key = '{}_validate_netconf_reply'.format(system_name)
        return status, {reply_key: reply}

    def edit_config_from_string(self, datastore, config, system_name,
                                session_name=None, default_operation=None,
                                test_option=None, error_option=None):
        """ Loads all or part of the specified config(not file) to the datastore
        :Arguments:
            1. datastore(string) = Name of datastore being edited
            2. config(string) = The configuration xml string.
            3. system_name(string) = Name of the system from the input datafile
            4. session_name(string) = Name of the session to the system
            5. default_operation(string) = [merge | replace | none (default)]
            6. test_option(string) = [test_then_set | set | test-only | none (default)]
            7. error_option(string) = [stop-on-error | continue-on-error
                                      | rollback-on-error | none (default)]
                    rollback-on-error depends on :rollback-on-error capability
        :Returns:
            1. status(bool)= True / False
            2. Edit Response in the data repository {data:reply(xml)}
         """
        wdesc = "Edit system configuration data"
        pSubStep(wdesc)
        pNote(system_name)
        pNote(self.datafile)

        self.clear_notification_buffer_all(system_name, session_name)
        session_id = Utils.data_Utils.get_session_id(system_name, session_name)
        netconf_object = Utils.data_Utils.get_object_from_datarepository(
            session_id)

        reply = netconf_object.edit_config(datastore, config,
                                           default_operation=default_operation,
                                           test_option=test_option,
                                           error_option=error_option)
        if netconf_object.isCOMPLD:
            status = True
            if reply:
                reply = parseString(reply).toprettyxml(
                    indent="  ", encoding="UTF-8")
            pNote('edit-config: Reply= {}'.format(reply))
        else:
            pNote('edit-config: Reply= {}'.format(reply))
            pNote('edit-config: Failed {}'.format(netconf_object.ErrorMessage), "error")
            status = False
        report_substep_status(status)
        reply_key = '{}_edit_config_reply'.format(system_name)
        return status, {reply_key: reply}

    def create_subscription(self, system_name,
                            session_name=None,
                            stream_from=None,
                            filter_string=None,
                            filter_type="subtree",
                            start_time=None,
                            stop_time=None):
        """ create-subscription to receive netconf event notification
        :Arguments:
            1. system_name(string)  = Name of the system from the input datafile
            2. session_name(string) = Name of the session to the system
            3. stream_from(string) = NETCONF/SNMP/syslog ..
            4. filter_string(string) = specifies the portion of the events to receive notification
               by default entire events is reported
            5. filter_type(string) = xpath or subtree(default)
            6. start_time(string) = start time
            7. stop_time(string) = stop time
        :Returns:
            1. status(bool)= True / False
            2. Subscription Response in the data repository {data:reply(xml)}
         """
        wdesc = "create-subscription to receive netconf event notification"
        pSubStep(wdesc)
        pNote(system_name)
        pNote(self.datafile)

        self.clear_notification_buffer_all(system_name, session_name)
        session_id = Utils.data_Utils.get_session_id(system_name, session_name)
        netconf_object = Utils.data_Utils.get_object_from_datarepository(
            session_id)

        reply = netconf_object.create_subscription(stream_from,
                                                   filter_string,
                                                   filter_type,
                                                   start_time,
                                                   stop_time)
        if reply:
            reply = parseString(reply).toprettyxml(
                indent="  ", encoding="UTF-8")
        pNote('create-subscription: Reply= {}'.format(reply))
        if netconf_object.isCOMPLD:
            status = True
        else:
            pNote(
                'create-subscription: Failed {}'.format(netconf_object.ErrorMessage), "error")
            status = False
        report_substep_status(status)
        reply_key = '{}_create_subscription_reply'.format(system_name)
        return status, {reply_key: reply}

    def waitfor_subscription(self, system_name, wait_string, namespace_string,
                             namespace_prefix, timeout=600, session_name=None):
        """Wait for specified notification event
        :Arguments:
            1. system_name(string) = Name of the system from the input datafile
            2. waitString(string) = xpath string with namespace prefix
             e.g.
             for checking single data
             waitString = ".//ns:event[./ns:eventClass/text()='fault']"
             Note that "ns" = namespace prefix

             for checking multiple data
             waitString = ".//ns1:event1[text()='fault1'] and
                            .//ns1:event2[text()='fault2']"
            3. namespaceString(list of string) = list of namespace string
                                                 separated by comma
             e.g., namespaceString = "namespace_value1,namespace_value2"
            4. namespacePrefix(list of string) = list of namespace prefix
                                                 separated by comma
              e.g.,
              namespaceprefix = "ns1,ns2"
            5. timeout(integer) = timeout value in second, default=600
            6. session_name(string) = Name of the session to the system
        :Returns:
            1. status(bool)= True / False
        E.g., Assuming the following notification is the one received:
        ****************************
        <?xml version="1.0" encoding="UTF-8"?>
        <notification xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">
          <eventTime>2015-08-10T10:36:58.427756-07:00</eventTime>
          <netconf-config-change xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-notifications">
            <changed-by>
              <username>admin</username>
              <session-id>0</session-id>
              <source-host>127.0.0.1</source-host>
            </changed-by>
            <datastore>running</datastore>
            <edit>
              <target xmlns:notif="http://tail-f.com/ns/test/notif">/notif:test</target>
              <operation>replace</operation>
            </edit>
          </netconf-config-change>
        </notification>
        ****************************
        for the notification received above, please find the appropriate
        argument and its values for checking username, source-host and target
        in this notification as follows:
           waitstring = ".//ns1:username[text()='admin'] and
                         .//ns1:source-host[text()='127.0.0.1'] and
                         .//ns2:target[text()='/notif:test']"
           namespaceString = "urn:ietf:params:xml:ns:netconf:notification:1.0,
                                http://tail-f.com/ns/test/notif"
           namespacePrefix = "ns1,ns2"
        Caveat: This keyword does not validate XMLSchema for notification.
        """
        wdesc = ("waitfor_subscription to wait specified netconf event "
                 "notification")
        pSubStep(wdesc)
        pNote(system_name)
        pNote(self.datafile)

        session_id = Utils.data_Utils.get_session_id(system_name, session_name)
        netconf_object = Utils.data_Utils.get_object_from_datarepository(
                                                             session_id)
        namespace_dict = {}
        prefixes = [prefix.strip() for prefix in namespace_prefix.split(",")]
        namespaces = [ns.strip() for ns in namespace_string.split(",")]
        if len(prefixes) != len(namespaces):
            pNote("the number of prefixes and namespaces should match", "error")
            pNote("Number of prefixes ({}) != Number of namespaces({})".format(
                                len(prefixes), len(namespaces)), "error")
            return False
        for (prefix, namespace) in zip(prefixes, namespaces):
            namespace_dict[prefix] = namespace

        temp_waitstring = (wait_string, namespace_dict)
        pNote("waiting for %s timeout=%s ..." % (wait_string, str(timeout)))
        status = netconf_object.waitfor_subscription(temp_waitstring,
                                                     int(timeout))
        if status:
            pNote("waitfor %s received" % wait_string)
        else:
            pNote("waitfor %s timeouted" % wait_string, "error")
        report_substep_status(status)
        return status

    def testfor_killsession(self, system_name, session_name=None):
        """kill-session test keyword
           create another session to same NE and kills it.
        :Arguments:
            1. system_name(string) = Name of the system from the input datafile
            2. session_name(string) = Name of the session to the system
        :Returns:
            1. status(bool)= True / False
        """
        wdesc = "kill-session, create another session and kill it"
        pSubStep(wdesc)
        pNote(system_name)
        pNote(self.datafile)

        test_netconf = WNetConf()
        session_parameters = ['ip', 'nc_port', 'username', 'password',
                              'allow_agent', 'hostkey_verify', 'look_for_keys',
                              'timeout', 'device_name']
        session_credentials = Utils.data_Utils.get_credentials(self.datafile,
                                                               system_name,
                                                               session_parameters)
        session_credentials["password"] = decrypt(session_credentials["password"])
        if test_netconf.open(session_credentials):
            time.sleep(1)
            sid = test_netconf.session_id
            status, reply = self.kill_session(system_name, sid, session_name)
        else:
            status = False
        if status:
            pNote("kill-session PASS")
        else:
            pNote("kill-session FAIL", "error")
        report_substep_status(status)
        return status

    def cancel_commit(self, system_name, persist_id=None, session_name=None):
        """cancel-commit
        :Arguments:
            1. system_name(string) = Name of the system from the input datafile
            2. persist_id(string) = persist-id which specified in confirm-commit
            3. session_name(string) = name of the session to the system
        :Returns:
            1. command_status(bool)
            2. {data:reply.data(xml)}
        """
        wdesc = "cancel-commit"
        pSubStep(wdesc)
        pNote(system_name)
        pNote(self.datafile)

        self.clear_notification_buffer_all(system_name, session_name)
        session_id = Utils.data_Utils.get_session_id(system_name, session_name)
        netconf_object = Utils.data_Utils.get_object_from_datarepository(
            session_id)
        reply = netconf_object.cancel_commit(persist_id)
        if reply:
            reply = parseString(reply).toprettyxml(
                indent="  ", encoding="UTF-8")
        pNote('cancel-commit: Reply= {}'.format(reply))
        if netconf_object.isCOMPLD:
            status = True
        else:
            pNote('cancel-commit: Failed {}'.format(netconf_object.ErrorMessage), "error")
            status = False

        report_substep_status(status)
        reply_key = '{}_request_rpc_reply'.format(system_name)
        return status, {reply_key: reply}

    def clear_notification_buffer(self, system_name, session_name=None):
        """clear notification buffer
        :Arguments:
            1. system_name(string) = Name of the system from the input datafile
            2. session_name(string) = name of the session to the system
        :Returns:
            1. command_status(bool) = always true
        """
        wdesc = "clear notification buffer"
        pSubStep(wdesc)
        pNote(system_name)
        pNote(self.datafile)
        session_id = Utils.data_Utils.get_session_id(system_name, session_name)
        netconf_object = Utils.data_Utils.get_object_from_datarepository(
            session_id)
        netconf_object.clear_notification_buffer()
        report_substep_status(True)
        return True

    def clear_notification_buffer_all(self, system_name, session_name=None):
        """clear notification buffer for all netconf instances.
           (except this instance)
        :Arguments:
            1. system_name(string) = Name of the system from the input datafile
            2. session_name(string) = name of the session to the system
        :Returns:
            1. command_status(bool) = always true
        """
        wdesc = "clear notification buffer all"
        pSubStep(wdesc)
        pNote(system_name)
        pNote(self.datafile)
        session_id = Utils.data_Utils.get_session_id(system_name, session_name)
        temp_dict = Utils.config_Utils.data_repository
        for s0, s1 in temp_dict.items():
            if s0 != session_id and isinstance(s1, WNetConf):
                s1.clear_notification_buffer()
        report_substep_status(True)
        return True

    def get_schema(self, system_name, identifier, version_number=None, format_type=None, session_name=None):
        """get-schema rpc
        :Arguments:
            1. system_name(string) = Name of the system from the input datafile
            2. identifier(string) = schema id (name of a yang module, e.g. ietf-alarms)
            3. version_number(string) = version number (e.g. 1.0)
            4. format_type(string) = schema format (e.g. yang)
            5. session_name(string) = name if the session to the system
        :Returns:
            1. command_status(bool)
            2. {data:reply.data(xml)}
        """
        wdesc = "get-schema"
        pSubStep(wdesc)
        pNote(system_name)
        pNote(self.datafile)

        self.clear_notification_buffer_all(system_name, session_name)
        session_id = Utils.data_Utils.get_session_id(system_name, session_name)
        netconf_object = Utils.data_Utils.get_object_from_datarepository(
            session_id)
        reply = netconf_object.get_schema(
            identifier, version_number, format_type)
        if reply:
            reply = parseString(reply).toprettyxml(
                indent="  ", encoding="UTF-8")
        pNote('get-schema: Reply= {}'.format(reply))
        if netconf_object.isCOMPLD:
            status = True
        else:
            pNote('get-schema: Failed {}'.format(netconf_object.ErrorMessage), "error")
            status = False

        report_substep_status(status)
        reply_key = '{}_get_schema_reply'.format(system_name)
        return status, {reply_key: reply}

    def print_notification_buffer(self, system_name, notification_type=None, session_name=None):
        """print notification buffer
            :Arguments:
                1. system_name (string) = system name
                2. notification_type (string) = a notification type to be displayed.
                   e.g. netconf-config-change or netconf-session-end etc...
                       if empty then display all.
                3. session_name (string) = session name
            :Returns:
                1. status (bool)
        """
        if notification_type is not None:
            wdesc = "print notification buffer: type=%s" % notification_type
        else:
            wdesc = "print notification buffer all"
        pNote(wdesc)
        session_id = Utils.data_Utils.get_session_id(system_name, session_name)
        netconf_object = Utils.data_Utils.get_object_from_datarepository(session_id)
        notification_data = netconf_object.get_notification_buffer(notification_type)
        if len(notification_data) != 0:
            for notif in notification_data:
                pNote(notif)
        else:
            pNote("notification data is empty")
        return True

    def clear_notification_buffer_for_print(self, system_name, session_name=None):
        """clear the notification print buffer
            :Arguments:
                1. system_name (string) = system name
                2. session_name (string) = session name
            :Returns:
                1. status (bool)
        """
        wdesc = "clear the notification print buffer"
        pNote(wdesc)
        session_id = Utils.data_Utils.get_session_id(system_name, session_name)
        netconf_object = Utils.data_Utils.get_object_from_datarepository(session_id)
        return netconf_object.clear_notification_buffer_for_print()

